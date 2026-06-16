# Build & release

The primary deliverable is a **private internal Android APK** published via GitHub
Releases. Google Play / App Bundle support is structured for but not required.

## Local builds

```bash
source scripts/activate.sh
flutter build apk --debug      # build/app/outputs/flutter-apk/app-debug.apk
flutter build apk --release    # build/app/outputs/flutter-apk/app-release.apk
flutter build appbundle --release   # (optional) .aab for Play
```

By default the release APK is debug-signed (no keystore required), so builds never
block on secrets.

## GitHub Actions

Workflows live in `.github/workflows/`:

| Workflow            | Trigger                          | Output |
|---------------------|----------------------------------|--------|
| `ci.yml`            | push & PR (any branch)           | format check, analyze, content validation, bundle-freshness check, `flutter test` |
| `android-apk.yml`   | push to `master`/`main`, manual  | debug APK uploaded as a build artifact |
| `release.yml`       | `v*` tag, or manual dispatch     | release APK (+ optional `.aab`) artifacts; on a tag, a GitHub Release with auto-generated notes |

### Where artifacts land

- **CI / debug builds:** the run's *Artifacts* section (`android-apk.yml`).
- **Releases:** attached to the GitHub Release for the tag, and as run artifacts
  (`release.yml`).

## Cutting a private release

Before tagging, bump the version in **two places that must stay in sync**:

- `version:` in `pubspec.yaml` (the `+N` build/versionCode must only increase).
- `kAppVersion` in `lib/features/settings/about_screen.dart` (shown on the About
  screen). The content version on About is read from the bundle automatically.

```bash
git tag v1.0.0
git push origin v1.0.0
```

`release.yml` then builds the **stable-signed** release APK (using the signing
secrets, see below) and creates a GitHub Release with a single tag-named asset,
`zany-test-prep-v1.0.0.apk`, plus a generated changelog.

**Let CI do the release build — don't also upload one by hand.** Pushing the tag
already triggers the workflow; a second manual `gh release create`/upload would add
a duplicate (and possibly differently-signed) asset to the same release.

The signing secrets are configured on the repo (`KEYSTORE_BASE64`, `KEY_ALIAS`,
`KEY_PASSWORD`, `STORE_PASSWORD`), so CI signs with the same stable key as local
builds. To rotate or re-add them, base64 the keystore and set the secrets:

```bash
base64 -w0 android/app/zany-release.jks | gh secret set KEYSTORE_BASE64
gh secret set KEY_ALIAS --body zany
gh secret set STORE_PASSWORD   # paste when prompted
gh secret set KEY_PASSWORD     # paste when prompted
```

## Release signing (stable key) — why updates install in place

Android refuses to update an installed app when the new APK is signed with a
**different key** ("App not installed as package conflicts with an existing
package"). The old default here signed releases with the **debug** key, which is
generated per-machine, so APKs from different builds/CI had different signatures and
could not update over each other.

Now `android/app/build.gradle.kts` signs release builds with a **stable keystore**:

- `android/app/zany-release.jks` — the release key (**git-ignored**, lives on the
  build machine only). Backed up at `~/zany-keystore-backup/`.
- `android/key.properties` — alias + passwords (**git-ignored**).

`build.gradle.kts` loads `key.properties` when present and falls back to debug
signing when absent. **Always release from a machine that has this keystore**, or
every release would change the signature and force users to reinstall.

> ⚠️ One-time transition: the first stable-signed release (v1.7.3) has a *different*
> signature than the older debug-signed installs, so users must uninstall once to
> move onto the stable key. Every update after that installs in place and keeps all
> data. **Do not lose the keystore** — without it you cannot ship updatable builds.

Key fingerprint (SHA-256): `1D:9D:03:EB:A0:CA:CD:A8:31:A2:DE:E5:7E:21:57:0A:0B:77:81:B5:61:2F:31:F5:C9:4E:B6:D4:F2:9F:D2:05`

To build/release on another machine or in CI, copy `zany-release.jks` +
`key.properties` there (e.g. via CI secrets — see below), don't commit them.

## Optional: signing for Play Store later

`release.yml` contains a commented-out signing section. To enable real signing, add
these repository secrets and uncomment that section:

- `KEYSTORE_BASE64` – base64 of your `.jks` keystore
- `STORE_PASSWORD`, `KEY_PASSWORD`, `KEY_ALIAS`

No keys are committed to the repo. Until configured, the build stays debug-signed and
fully functional for internal distribution.
