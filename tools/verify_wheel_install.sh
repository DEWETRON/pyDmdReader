#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
wheel_spec="${1:-}"
if [[ -z "${wheel_spec}" ]]; then
  echo "Usage: tools/verify_wheel_install.sh <wheel-path-or-url>"
  exit 2
fi

pip_args=()
if python3 -m pip install --help | grep -q -- "--break-system-packages"; then
  pip_args+=(--break-system-packages)
fi

python3 -m pip install "${pip_args[@]}" "${wheel_spec}"
python3 "${repo_root}/tools/smoke_read.py" "${repo_root}/tests/data/simple.dmd"

(
  cd /tmp
  python3 - <<'PY'
from pathlib import Path
import os
import subprocess
import sys

import pyDmdReader

print(f"IMPORT_OK version={pyDmdReader.__version__}")
pkg_dir = Path(pyDmdReader.__file__).resolve().parent
runtime_lib = pkg_dir / "bin" / "linux_x86_64" / "libdmd_reader_api_x64.so"
deps_dir = runtime_lib.parent / "deps"

if not runtime_lib.exists():
    raise SystemExit(f"Runtime library not found: {runtime_lib}")

if sys.platform.startswith("linux"):
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = f"{deps_dir}:{env.get('LD_LIBRARY_PATH', '')}"
    subprocess.run(["ldd", str(runtime_lib)], check=True, env=env)
PY
)
