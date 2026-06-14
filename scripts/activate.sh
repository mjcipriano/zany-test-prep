#!/usr/bin/env bash
#
# Source this file (don't execute it) to put the project toolchain on PATH:
#   source scripts/activate.sh
#
# It activates the mamba env and exposes flutter / dart / android sdk tools
# from the repo-local .tooling/ directory.

_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
_TOOLING="$_REPO_ROOT/.tooling"

# Activate mamba env (provides JDK 17 + python tooling).
if command -v mamba >/dev/null 2>&1; then
  eval "$(mamba shell hook -s bash 2>/dev/null)" || true
  mamba activate zany-test-prep 2>/dev/null || micromamba activate zany-test-prep 2>/dev/null || true
fi

export ANDROID_SDK_ROOT="$_TOOLING/android-sdk"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export PATH="$_TOOLING/flutter/bin:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH"

# Point Gradle/Flutter at the env JDK.
if [ -n "${CONDA_PREFIX:-}" ]; then
  if [ -d "$CONDA_PREFIX/lib/jvm" ]; then
    export JAVA_HOME="$CONDA_PREFIX/lib/jvm"
  else
    export JAVA_HOME="$CONDA_PREFIX"
  fi
  export PATH="$JAVA_HOME/bin:$PATH"
fi

echo "zany-test-prep toolchain activated."
echo "  flutter: $(command -v flutter || echo 'NOT FOUND — run scripts/setup_env.sh')"
echo "  java:    $(command -v java || echo 'NOT FOUND')"
