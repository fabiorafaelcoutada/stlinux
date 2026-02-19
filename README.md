# STLinux SH4 Toolchain for Enigma2

This repository contains the STLinux 2.4 toolchain (RPM packages) for cross-compiling applications for STi7111 and other SH4-based set-top boxes. It is designed to help you build software like Enigma2 and other satellite TV applications.

## Getting Started

### Prerequisites

This toolchain contains 32-bit x86 binaries. To run it on a 64-bit Linux host, you must have 32-bit compatibility libraries installed.

On Ubuntu/Debian:
```bash
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install libc6:i386 libstdc++6:i386 zlib1g:i386
```

### Installation

1.  Run the setup script to extract the RPMs and configure the environment:
    ```bash
    ./setup.sh
    ```
    This will create a `toolchain/` directory and an `env.sh` file.

2.  Activate the environment:
    ```bash
    source env.sh
    ```
    This sets `CC`, `CXX`, `LD` and other variables to point to the cross-compiler.

### Verification

To verify the installation, you can build the "Hello World" example:

```bash
cd examples/hello_world
make
```

If successful, you will see a `hello_world` executable (SH4 binary). You can verify its architecture with `file hello_world`.

### Building Enigma2

See [docs/ENIGMA2_BUILD.md](docs/ENIGMA2_BUILD.md) for detailed instructions on how to set up the build system for Enigma2 and cross-compile dependencies.

## Contents

- `stlinux24-cross-sh4-*`: Cross-compiler toolchain (gcc 4.8.4).
- `stlinux24-sh4-*`: Target libraries (glibc, libstdc++).
- `tools/extract_rpm.py`: Python script to extract RPM contents.
- `setup.sh`: Setup script.
- `env.sh`: Environment configuration script (generated).
- `examples/`: Example projects.
- `docs/`: Documentation.

## License

The files in this repository are backups of the original STLinux distribution. Check individual packages for license information (mostly GPL).
