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
    python3 tools/sync_avatars.py --full          # also vendor ALL images
    python3 tools/sync_avatars.py --avatars-only  # catalog + every avatar image (no items/pets)
    python3 tools/sync_avatars.py --local ../zany-test-prep-avatars --full
                                                  # copy from a local checkout instead

Vendored item/pet sprites are downscaled to --max-side pixels (default 384) to
keep the APK small; the app places sprites with contain-fit so this is lossless
for layout (the catalog's sprite_size keeps the source dimensions). Pass
--max-side 0 to keep originals.

Images are re-encoded as WebP by default (--format webp): lossy colour at
--webp-quality with a *lossless* alpha channel, so every transparency edge and
the placement maths stay identical while the art shrinks ~80% (the pack's PNGs
were ~97 MB of a 152 MB APK). The vendored catalog's asset paths are rewritten
to the .webp files. Pass --format png to vendor the originals. Needs Pillow
(falls back to copying PNGs if it is missing).

This only writes files under assets/avatar/. After running, run `flutter pub get`
and rebuild. Image directories are already declared in pubspec.yaml, so adding
art never requires a pubspec edit.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import sys
import urllib.request

REPO = "mjcipriano/zany-test-prep-avatars"
CATALOG_PATH = "assets/avatar/manifest/avatar_catalog.json"
ASSET_ROOT = os.path.join(os.path.dirname(__file__), "..")


RAW_BASE = "https://raw.githubusercontent.com"


def fetch(path_in_repo: str, ref: str) -> bytes:
    """Fetch a repo file's raw bytes from raw.githubusercontent.com.

    Uses raw (not the contents API) so it works for files over 1 MB — the
    catalog exceeds that as of schema 2.1.0 — and needs no auth for a public repo.
    """
    url = f"{RAW_BASE}/{REPO}/{ref}/{path_in_repo}"
    with urllib.request.urlopen(url) as resp:  # noqa: S310 (trusted host)
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} for {url}")
        return resp.read()


def write(rel_path: str, data: bytes) -> None:
    dest = os.path.normpath(os.path.join(ASSET_ROOT, rel_path))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(data)


def read_local(root: str, path_in_repo: str) -> bytes:
    with open(os.path.join(root, path_in_repo), "rb") as fh:
        return fh.read()


def to_webp(data: bytes, quality: int) -> bytes:
    """Re-encode PNG bytes as WebP: lossy colour, lossless alpha."""
    from PIL import Image
    with Image.open(io.BytesIO(data)) as im:
        buf = io.BytesIO()
        im.convert("RGBA").save(buf, format="WEBP", quality=quality,
                                alpha_quality=100, method=4)
        return buf.getvalue()


def webp_path(path: str) -> str:
    return path[:-4] + ".webp" if path.lower().endswith(".png") else path


def downscale_png(data: bytes, max_side: int) -> bytes:
    """Shrink a PNG so its longer side is at most ``max_side`` (keeps alpha).
    Returns the original bytes when already small enough or Pillow is absent."""
    if max_side <= 0:
        return data
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover - optional dependency
        return data
    with Image.open(io.BytesIO(data)) as im:
        w, h = im.size
        if max(w, h) <= max_side:
            return data
        scale = max_side / max(w, h)
        out = im.convert("RGBA").resize(
            (max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        buf = io.BytesIO()
        out.save(buf, format="PNG", optimize=True)
        return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", default="v3.2.1", help="release tag/ref to pull")
    ap.add_argument("--local", help="path to a local checkout of the pack repo "
                                    "(copies files instead of downloading)")
    ap.add_argument("--max-side", type=int, default=384,
                    help="downscale item/pet sprites to this many pixels on the "
                         "longer side (0 = keep originals)")
    ap.add_argument("--format", choices=["webp", "png"], default="webp",
                    help="image format to vendor (default webp: ~80%% smaller)")
    ap.add_argument("--webp-quality", type=int, default=85,
                    help="WebP colour quality (alpha is always lossless)")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="vendor all images")
    group.add_argument(
        "--avatars-only",
        action="store_true",
        help="vendor every avatar image (skip items + pets)",
    )
    args = ap.parse_args()

    if args.local:
        print(f"Syncing avatar pack from local checkout {args.local} (tag label {args.tag}) ...")

        def get(path):
            return read_local(args.local, path)
    else:
        print(f"Syncing avatar pack {REPO}@{args.tag} ...")

        def get(path):
            return fetch(path, args.tag)

    catalog_bytes = get(CATALOG_PATH)
    catalog = json.loads(catalog_bytes)
    assets = catalog["assets"]
    use_webp = args.format == "webp"
    if use_webp:
        try:
            import PIL  # noqa: F401
        except ImportError:
            print("  Pillow missing: vendoring PNGs instead of WebP", file=sys.stderr)
            use_webp = False
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
            data = get(path)
            if asset["type"] != "avatar":
                data = downscale_png(data, args.max_side)
            if use_webp:
                data = to_webp(data, args.webp_quality)
                path = webp_path(path)
            write(path, data)
            bundled.append(asset["id"])
        except (RuntimeError, OSError) as exc:  # keep going; report at the end
            print(f"  WARN: {asset['id']}: {exc}", file=sys.stderr)
    print(f"  images: {len(bundled)} downloaded")

    # Point the vendored catalog at the files actually shipped.
    if use_webp:
        def retarget(entries):
            for a in entries:
                if isinstance(a, dict):
                    for key in ("asset_path", "preview_asset_path"):
                        if isinstance(a.get(key), str):
                            a[key] = webp_path(a[key])
        for key in ("assets", "avatars", "items", "pets"):
            if isinstance(catalog.get(key), list):
                retarget(catalog[key])
        catalog_bytes = json.dumps(catalog, indent=2, ensure_ascii=False).encode() + b"\n"
    write(CATALOG_PATH, catalog_bytes)

    version = {
        "source_repo": f"https://github.com/{REPO}",
        "tag": args.tag,
        "pack_id": catalog.get("pack_id"),
        "style_version": catalog.get("style_version"),
        "schema_version": catalog.get("schema_version"),
        "catalog_total": len(assets),
        "counts": dict(collections.Counter(a["type"] for a in assets)),
        "sprite_max_side": args.max_side,
        "image_format": "webp" if use_webp else "png",
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
