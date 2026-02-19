# AGENTS.md

This document provides information for coding agents and developers working on this project, which involves developing for an SH4-based microprocessor using the STLinux 2.4 toolchain.

## Project Overview

This repository serves as a backup for the STLinux 2.4 toolchain and related libraries, as the original archive (archive.stlinux.com) is no longer available. The tools are essential for cross-compiling applications for SH4 architecture, commonly used in embedded systems like set-top boxes.

## Environment Setup

The provided toolchain consists of RPM packages. To set up the development environment on a modern Linux distribution (e.g., Ubuntu/Debian), you may need to convert these RPMs to DEB packages.

### Prerequisites

-   A Linux environment (host).
-   `alien` package converter (for Debian/Ubuntu based systems).
-   Multiarch support for 32-bit binaries (the provided tools are `i386`).

### Installation Steps

1.  **Install `alien`**:
    ```bash
    sudo apt-get update
    sudo apt-get install alien
    ```

2.  **Convert and Install RPMs**:
    Convert the RPM files to DEB packages and install them. Start with binutils, then gcc, then libraries.
    ```bash
    # Example order (adjust as needed for dependencies)
    sudo alien -i stlinux24-cross-sh4-binutils-*.rpm
    sudo alien -i stlinux24-cross-sh4-gcc-*.rpm
    sudo alien -i stlinux24-sh4-glibc-*.rpm
    sudo alien -i stlinux24-sh4-linux-kernel-headers-*.rpm
    # Install C++ support if needed
    sudo alien -i stlinux24-cross-sh4-g++-*.rpm
    sudo alien -i stlinux24-sh4-libstdc++-*.rpm
    ```

3.  **Verify Installation**:
    Check if the cross-compiler is available in your path (usually installed to `/opt/STM/STLinux-2.4/devkit/sh4/bin` or similar; add this to your `PATH`).
    ```bash
    export PATH=$PATH:/opt/STM/STLinux-2.4/devkit/sh4/bin
    sh4-linux-gcc --version
    ```

## Cross-Compilation

-   **Target Architecture**: `sh4` (SuperH)
-   **Compiler Prefix**: `sh4-linux-`
-   **Kernel Version**: Linux 2.6.32
-   **C Library**: glibc 2.14

### U-Boot Tools
The repository also includes `stlinux24-host-u-boot-tools`, which contains tools like `mkimage` for creating U-Boot images.

### Usage Example

To compile a simple C program `hello.c`:

```c
#include <stdio.h>

int main() {
    printf("Hello, SH4 World!\n");
    return 0;
}
```

Compile with:

```bash
sh4-linux-gcc -o hello hello.c
```

Check the binary format:

```bash
file hello
# Output should indicate: ELF 32-bit LSB executable, Renesas SH, version 1 (SYSV), dynamically linked ...
```

## Documentation

The following documentation resources are referenced as being relevant for this project, though they may not be present in the repository root. Please check the `/tmp/file_attachments` directory or ask for them if missing:

-   **Datasheet**: Electrical characteristics, pinout, and hardware specifications for the specific microprocessor.
-   **Reference Manual**: Detailed information on the instruction set, registers, and peripherals.
-   **Markdown Index**: A file containing an index of gathered materials and notes.

If these files are unavailable, you may need to search for the specific microprocessor's documentation online (e.g., STMicroelectronics SH4 series).

## Notes

-   The tools are 32-bit binaries (`i386`). Ensure your host system can run 32-bit executables (install `libc6:i386`, `libstdc++6:i386`, etc., if on a 64-bit system).
-   The STLinux archive is offline, so preserve these RPMs carefully.
