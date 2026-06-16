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

`release.yml` builds the release APK and creates a GitHub Release `v1.0.0` with the
APK attached and generated changelog. Or trigger `release.yml` manually via
*Actions → Internal release → Run workflow*.

## Optional: signing for Play Store later

`release.yml` contains a commented-out signing section. To enable real signing, add
these repository secrets and uncomment that section:

- `KEYSTORE_BASE64` – base64 of your `.jks` keystore
- `STORE_PASSWORD`, `KEY_PASSWORD`, `KEY_ALIAS`

No keys are committed to the repo. Until configured, the build stays debug-signed and
fully functional for internal distribution.
