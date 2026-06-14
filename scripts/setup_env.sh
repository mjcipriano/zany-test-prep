#!/usr/bin/env bash
#
# Sets up the full toolchain for the Zany Test Prep project.
#
# 1. Creates/updates the `zany-test-prep` mamba env (JDK + Python tooling).
# 2. Installs the Flutter SDK into .tooling/flutter (pinned version).
# 3. Installs the Android command-line tools + SDK packages into .tooling/android-sdk.
#
# Everything project-specific lives under .tooling/ (git-ignored) so it stays
# isolated from the rest of the machine. After running this, `source
# scripts/activate.sh` to put flutter/dart/sdkmanager on your PATH.
#
# Safe to re-run: each step is idempotent.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLING="$REPO_ROOT/.tooling"
FLUTTER_VERSION="3.35.5"
FLUTTER_CHANNEL="stable"
ANDROID_CMDLINE_VERSION="11076708"   # cmdline-tools 19.0
ANDROID_PLATFORM="android-35"
ANDROID_BUILD_TOOLS="35.0.0"

mkdir -p "$TOOLING"

echo "==> [1/4] Creating/updating mamba env 'zany-test-prep'"
if mamba env list | grep -q "zany-test-prep"; then
  mamba env update -f "$REPO_ROOT/environment.yml" --prune
else
  mamba env create -f "$REPO_ROOT/environment.yml"
fi

echo "==> [2/4] Installing Flutter $FLUTTER_VERSION ($FLUTTER_CHANNEL)"
if [ ! -x "$TOOLING/flutter/bin/flutter" ]; then
  ARCHIVE="flutter_linux_${FLUTTER_VERSION}-${FLUTTER_CHANNEL}.tar.xz"
  URL="https://storage.googleapis.com/flutter_infra_release/releases/${FLUTTER_CHANNEL}/linux/${ARCHIVE}"
  echo "    downloading $URL"
  curl -fSL "$URL" -o "$TOOLING/$ARCHIVE"
  tar xf "$TOOLING/$ARCHIVE" -C "$TOOLING"
  rm -f "$TOOLING/$ARCHIVE"
else
  echo "    flutter already present, skipping"
fi
export PATH="$TOOLING/flutter/bin:$PATH"

echo "==> [3/4] Installing Android command-line tools + SDK"
export ANDROID_SDK_ROOT="$TOOLING/android-sdk"
CMDLINE_DIR="$ANDROID_SDK_ROOT/cmdline-tools/latest"
if [ ! -x "$CMDLINE_DIR/bin/sdkmanager" ]; then
  mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools"
  ZIP="commandlinetools-linux-${ANDROID_CMDLINE_VERSION}_latest.zip"
  curl -fSL "https://dl.google.com/android/repository/$ZIP" -o "$TOOLING/$ZIP"
  rm -rf "$TOOLING/cmdline-tools-tmp"
  mkdir -p "$TOOLING/cmdline-tools-tmp"
  ( cd "$TOOLING/cmdline-tools-tmp" && unzip -q "$TOOLING/$ZIP" )
  mkdir -p "$CMDLINE_DIR"
  mv "$TOOLING/cmdline-tools-tmp/cmdline-tools/"* "$CMDLINE_DIR/"
  rm -rf "$TOOLING/cmdline-tools-tmp" "$TOOLING/$ZIP"
else
  echo "    cmdline-tools already present, skipping"
fi

# Use the env's JDK for sdkmanager.
export JAVA_HOME="$(mamba run -n zany-test-prep bash -c 'echo $CONDA_PREFIX')/lib/jvm"
[ -d "$JAVA_HOME" ] || JAVA_HOME="$(dirname "$(dirname "$(mamba run -n zany-test-prep which java)")")"
export PATH="$JAVA_HOME/bin:$CMDLINE_DIR/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH"

echo "    accepting licenses + installing platform/build-tools"
yes | sdkmanager --sdk_root="$ANDROID_SDK_ROOT" --licenses >/dev/null || true
sdkmanager --sdk_root="$ANDROID_SDK_ROOT" \
  "platform-tools" \
  "platforms;${ANDROID_PLATFORM}" \
  "build-tools;${ANDROID_BUILD_TOOLS}" >/dev/null

echo "==> [4/4] Configuring Flutter"
flutter config --no-analytics >/dev/null 2>&1 || true
flutter config --android-sdk "$ANDROID_SDK_ROOT" >/dev/null 2>&1 || true
flutter precache --android --no-ios >/dev/null 2>&1 || true

echo
echo "Setup complete. Run:  source scripts/activate.sh"
