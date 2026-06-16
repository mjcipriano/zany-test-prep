#!/usr/bin/env python3
"""Vendor the avatar customization pack into assets/avatar/.

The avatar/item/pet content lives in an external dataset repo:

    https://github.com/mjcipriano/zany-test-prep-avatars

This script pulls a given release tag's catalog + (optionally) images into the
app's assets so the app stays fully offline. It is the single extensibility
point: when the pack repo publishes a new release, bump --tag (and re-run) and
everything downstream — the Dart catalog loader, the store, avatar customizer —
picks up the new content automatically because nothing hardcodes asset lists.

Usage:
    python3 tools/sync_avatars.py                 # catalog + starter art (default, small)
    python3 tools/sync_avatars.py --tag v1.1.0    # pull a different release
    python3 tools/sync_avatars.py --full          # also vendor ALL images (~100MB+)
    python3 tools/sync_avatars.py --avatars-only  # catalog + every avatar image (no items/pets)

Requires the GitHub CLI (`gh`) to be authenticated, or set ZANY_GH_TOKEN.

This only writes files under assets/avatar/. After running, run `flutter pub get`
and rebuild. Image directories are already declared in pubspec.yaml, so adding
art never requires a pubspec edit.
"""
from __future__ import annotations

import argparse
import base64
import collections
import json
import os
import subprocess
import sys

REPO = "mjcipriano/zany-test-prep-avatars"
CATALOG_PATH = "assets/avatar/manifest/avatar_catalog.json"
ASSET_ROOT = os.path.join(os.path.dirname(__file__), "..")


def gh_api(path: str) -> bytes:
    """Fetch a repo file's raw bytes via the GitHub contents API."""
    result = subprocess.run(
        ["gh", "api", f"repos/{REPO}/contents/{path}", "--jq", ".content"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed for {path}: {result.stderr.strip()}")
    return base64.b64decode(result.stdout)


def fetch(path_in_repo: str, ref: str) -> bytes:
    return gh_api(f"{path_in_repo}?ref={ref}")


def write(rel_path: str, data: bytes) -> None:
    dest = os.path.normpath(os.path.join(ASSET_ROOT, rel_path))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(data)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", default="v1.0.0", help="release tag/ref to pull")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="vendor all images")
    group.add_argument(
        "--avatars-only",
        action="store_true",
        help="vendor every avatar image (skip items + pets)",
    )
    args = ap.parse_args()

    print(f"Syncing avatar pack {REPO}@{args.tag} ...")
    catalog_bytes = fetch(CATALOG_PATH, args.tag)
    write(CATALOG_PATH, catalog_bytes)
    catalog = json.loads(catalog_bytes)
    assets = catalog["assets"]
    print(f"  catalog: {len(assets)} assets")

    def wants(asset) -> bool:
        if args.full:
            return True
        if args.avatars_only:
            return asset["type"] == "avatar"
        # default: only the always-unlocked starter avatars
        return asset.get("default_unlocked") and asset["type"] == "avatar"

    bundled = []
    for asset in assets:
        if not wants(asset):
            continue
        path = asset["asset_path"]
        try:
            write(path, fetch(path, args.tag))
            bundled.append(asset["id"])
        except RuntimeError as exc:  # keep going; report at the end
            print(f"  WARN: {asset['id']}: {exc}", file=sys.stderr)
    print(f"  images: {len(bundled)} downloaded")

    version = {
        "source_repo": f"https://github.com/{REPO}",
        "tag": args.tag,
        "pack_id": catalog.get("pack_id"),
        "style_version": catalog.get("style_version"),
        "schema_version": catalog.get("schema_version"),
        "catalog_total": len(assets),
        "counts": dict(collections.Counter(a["type"] for a in assets)),
        "bundled_images": bundled,
        "note": (
            "Run tools/sync_avatars.py --full to vendor every image; the catalog "
            "lists all assets regardless of which art is bundled."
        ),
    }
    write("assets/avatar/pack_version.json", json.dumps(version, indent=2).encode())
    print("  wrote assets/avatar/pack_version.json")
    print("Done. Run `flutter pub get` and rebuild.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
