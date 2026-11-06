#!/usr/bin/env bash
# Download a pinned MP-SPDZ binary release into third_party/mp-spdz and
# prepare it for a 3-server run on localhost (SSL certs + data directories).
set -euo pipefail

VERSION="${MPSPDZ_VERSION:-0.4.3}"
NPARTIES="${NPARTIES:-3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/third_party/mp-spdz"

if [ -x "$DEST/replicated-ring-party.x" ]; then
    echo "MP-SPDZ already installed at $DEST"
else
    mkdir -p "$ROOT/third_party"
    TARBALL="$ROOT/third_party/mp-spdz-$VERSION.tar.xz"
    curl -fL -o "$TARBALL" \
        "https://github.com/data61/MP-SPDZ/releases/download/v$VERSION/mp-spdz-$VERSION.tar.xz"
    tar -xJf "$TARBALL" -C "$ROOT/third_party"
    mv "$ROOT/third_party/mp-spdz-$VERSION" "$DEST"
    rm "$TARBALL"
fi

cd "$DEST"
# The release ships CPU-specific binaries; this picks the right ones for the host.
if [ -x Scripts/tldr.sh ]; then
    Scripts/tldr.sh
fi
mkdir -p Player-Data
Scripts/setup-ssl.sh "$NPARTIES"
echo "MP-SPDZ $VERSION ready at $DEST"
