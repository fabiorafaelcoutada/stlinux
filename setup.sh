#!/bin/bash
set -e

# Function to check for commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 could not be found. Please install it."
        exit 1
    fi
}

echo "Checking prerequisites..."
check_command python3

echo "Extracting RPMs..."
python3 tools/extract_rpm.py

echo "Generating environment script..."
cat > env.sh << 'EOF'
#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLCHAIN_ROOT="${SCRIPT_DIR}/toolchain/opt/STM/STLinux-2.4/devkit/sh4"
SYSROOT="${TOOLCHAIN_ROOT}/target"

export PATH="${TOOLCHAIN_ROOT}/bin:${PATH}"

export CC="sh4-linux-gcc --sysroot=${SYSROOT}"
export CXX="sh4-linux-g++ --sysroot=${SYSROOT}"
export LD="sh4-linux-ld --sysroot=${SYSROOT}"
export AR="sh4-linux-ar"
export NM="sh4-linux-nm"
export RANLIB="sh4-linux-ranlib"
export STRIP="sh4-linux-strip"
export OBJCOPY="sh4-linux-objcopy"
export OBJDUMP="sh4-linux-objdump"

export CFLAGS="--sysroot=${SYSROOT}"
export CXXFLAGS="--sysroot=${SYSROOT}"
export LDFLAGS="--sysroot=${SYSROOT}"

# Additional flags for configure scripts
export CROSS_COMPILE="sh4-linux-"
export ARCH="sh4"

echo "Environment set up for STLinux 2.4 (SH4)"
echo "CC=${CC}"
echo "SYSROOT=${SYSROOT}"
EOF

chmod +x env.sh

echo "Done! Run 'source env.sh' to activate the environment."
