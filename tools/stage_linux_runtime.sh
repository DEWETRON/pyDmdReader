#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runtime_root="${DMDREADER_RUNTIME_ROOT:-${repo_root}/pyDmdReader/bin/linux_x86_64}"
deps_root="${runtime_root}/deps"

dmd_api_tag="${DMDREADER_API_TAG:-v.7.3.2}"
dmd_api_asset="${DMDREADER_API_ASSET:-dewetron-dmd-reader-api-7.3.473.release-1.el9.x86_64.rpm}"
dmd_api_url="https://github.com/DEWETRON/pyDmdReader/releases/download/${dmd_api_tag}/${dmd_api_asset}"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

prefix=()
if [[ "${EUID}" -ne 0 ]] && command -v sudo >/dev/null 2>&1; then
  prefix=(sudo)
fi

pkg_install() {
  "${prefix[@]}" dnf install -y "$@"
}

echo "Staging Linux runtime from ${dmd_api_url}"
mkdir -p "${runtime_root}" "${deps_root}"

pkg_install \
  zstd \
  xz \
  binutils \
  rpm \
  cpio \
  libcap \
  boost-atomic \
  boost-chrono \
  boost-date-time \
  boost-filesystem \
  boost-locale \
  boost-log \
  boost-program-options \
  boost-regex \
  boost-system \
  boost-thread

curl -fsSL "${dmd_api_url}" -o "${tmp_dir}/reader.rpm"
mkdir -p "${tmp_dir}/extract"
if command -v bsdtar >/dev/null 2>&1; then
  bsdtar -xf "${tmp_dir}/reader.rpm" -C "${tmp_dir}/extract"
else
  (cd "${tmp_dir}/extract" && rpm2cpio "${tmp_dir}/reader.rpm" | cpio -idm --quiet)
fi

main_lib_src="$(find "${tmp_dir}/extract" -name libdmd_reader_api_x64.so -type f | head -n1)"
if [[ -z "${main_lib_src}" ]]; then
  echo "ERROR: libdmd_reader_api_x64.so not found in package ${dmd_api_asset}"
  exit 1
fi

main_lib_dst="${runtime_root}/libdmd_reader_api_x64.so"
cp "${main_lib_src}" "${main_lib_dst}"
chmod 755 "${main_lib_dst}"

ldd "${main_lib_dst}" > "${tmp_dir}/main-lib-ldd.txt"
if grep -q "not found" "${tmp_dir}/main-lib-ldd.txt"; then
  echo "ERROR: Missing shared libraries for ${main_lib_dst}"
  cat "${tmp_dir}/main-lib-ldd.txt"
  exit 1
fi

rm -f "${deps_root}"/*.so* 2>/dev/null || true
while IFS= read -r line; do
  dep_path="$(echo "${line}" | awk '/=>/ {print $3}')"
  [[ -z "${dep_path}" ]] && continue
  dep_name="$(basename "${dep_path}")"
  case "${dep_name}" in
    libc.so.6|libm.so.6|libpthread.so.0|libdl.so.2|librt.so.1|ld-linux-*.so.*|libstdc++.so.6|libgcc_s.so.1)
      continue
      ;;
  esac
  cp -L "${dep_path}" "${deps_root}/${dep_name}"
done < "${tmp_dir}/main-lib-ldd.txt"

if command -v patchelf >/dev/null 2>&1; then
  patchelf --set-rpath '$ORIGIN/deps:$ORIGIN' "${main_lib_dst}"
  for dep_file in "${deps_root}"/*.so*; do
    [[ -e "${dep_file}" ]] || continue
    patchelf --set-rpath '$ORIGIN' "${dep_file}" || true
  done
fi

echo "Staged runtime files:"
find "${runtime_root}" -maxdepth 2 -type f | sort
