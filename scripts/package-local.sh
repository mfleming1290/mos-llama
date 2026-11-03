#!/usr/bin/env bash
# Build the same MOS package payload as the donor workflow, without publication.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
VERSION=${1:-0.0.1}
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo 'Numeric version required' >&2; exit 2; }
PKG_NAME="llama-${VERSION}-1+mos-plugin"
DEST="artifacts/$PKG_NAME"
mkdir -p artifacts
[[ ! -e "$DEST" ]] || { echo "Already exists: $DEST" >&2; exit 1; }
trap '[[ ! -d "$DEST" ]] || rm -rf "$DEST"' ERR
bash -n llama_swap llama_backend functions
npm --prefix page ci --ignore-scripts --no-audit --no-fund
PLUGIN_VERSION="$VERSION" npm --prefix page run build
mkdir -p "$DEST/usr/bin/plugins" "$DEST/var/www/mos-plugins/llama" "$DEST/DEBIAN"
install -m 755 llama_swap "$DEST/usr/bin/plugins/llama_swap"
install -m 755 llama_backend "$DEST/usr/bin/plugins/llama_backend"
cp -a page/dist/llama/. "$DEST/var/www/mos-plugins/llama/"
# MOS consumes plugin hooks and settings from the tagged plugin source; retain them separately.
cat > "$DEST/DEBIAN/control" <<CONTROL
Package: mos-llama-plugin
Version: ${VERSION}-1+mos-plugin
Architecture: all
Maintainer: mfleming1290
Description: MOS Llama plugin managing llama-swap and llama.cpp runtime
CONTROL
dpkg-deb --build "$DEST" "artifacts/${PKG_NAME}_all.deb"
dpkg-deb --info "artifacts/${PKG_NAME}_all.deb" | head -20
