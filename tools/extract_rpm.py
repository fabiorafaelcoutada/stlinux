#!/usr/bin/env python3
import sys
import os
import gzip
import glob
import struct

def align_4(n):
    return (n + 3) & ~3

def extract_cpio(data, dest_dir):
    offset = 0
    inodes = {} # Map (dev, ino) -> path
    placeholders = set() # Set of (dev, ino) that are placeholders (size 0)

    dest_dir_abs = os.path.abspath(dest_dir)

    while offset < len(data):
        if offset + 110 > len(data):
            break

        header_data = data[offset : offset + 110]
        magic = header_data[0:6]
        if magic != b'070701':
            print(f"Unknown magic at offset {offset}: {magic}")
            break

        try:
            ino = int(header_data[6:14], 16)
            mode = int(header_data[14:22], 16)
            uid = int(header_data[22:30], 16)
            gid = int(header_data[30:38], 16)
            nlink = int(header_data[38:46], 16)
            mtime = int(header_data[46:54], 16)
            filesize = int(header_data[54:62], 16)
            devmajor = int(header_data[62:70], 16)
            devminor = int(header_data[70:78], 16)
            rdevmajor = int(header_data[78:86], 16)
            rdevminor = int(header_data[86:94], 16)
            namesize = int(header_data[94:102], 16)
            check = int(header_data[102:110], 16)
        except ValueError:
            print("Error parsing header")
            break

        name_start = offset + 110
        name_end = name_start + namesize
        name_padding = (4 - (name_end % 4)) % 4
        content_start = name_end + name_padding

        filename = data[name_start : name_end - 1].decode('utf-8', errors='replace')

        if filename == 'TRAILER!!!':
            break

        content_end = content_start + filesize
        content_padding = (4 - (content_end % 4)) % 4
        next_header = content_end + content_padding

        offset = next_header

        full_path = os.path.join(dest_dir, filename.lstrip('/'))
        full_path_abs = os.path.abspath(full_path)

        if not full_path_abs.startswith(dest_dir_abs):
            print(f"Skipping potentially malicious path: {filename}")
            continue

        file_type = mode & 0o170000
        perms = mode & 0o7777

        parent_dir = os.path.dirname(full_path)
        if not os.path.exists(parent_dir) and parent_dir != '':
            os.makedirs(parent_dir, exist_ok=True)

        if file_type == 0o040000: # Directory
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
            try:
                os.chmod(full_path, perms)
            except:
                pass

        elif file_type == 0o100000: # Regular file
            dev = (devmajor, devminor)
            key = (dev, ino)

            content = data[content_start : content_end]

            if filesize > 0:
                if nlink > 1 and key in inodes and key not in placeholders:
                     # Duplicate content or hardlink to existing content
                    prev_path = inodes[key]
                    if os.path.lexists(full_path):
                        os.unlink(full_path)
                    try:
                        os.link(prev_path, full_path)
                    except Exception as e:
                        # Fallback
                        with open(full_path, 'wb') as f:
                            f.write(content)
                        os.chmod(full_path, perms)
                elif nlink > 1 and key in inodes and key in placeholders:
                    # Found content for placeholder
                    prev_path = inodes[key]

                    if os.path.lexists(full_path):
                        os.unlink(full_path)
                    with open(full_path, 'wb') as f:
                        f.write(content)
                    os.chmod(full_path, perms)

                    # Fix placeholder
                    if os.path.lexists(prev_path):
                        os.unlink(prev_path)
                    try:
                        os.link(full_path, prev_path)
                    except Exception as e:
                        print(f"Failed to fix placeholder {prev_path}: {e}")

                    placeholders.remove(key)
                    inodes[key] = full_path
                else:
                    # New file
                    if os.path.lexists(full_path):
                        os.unlink(full_path)
                    with open(full_path, 'wb') as f:
                        f.write(content)
                    os.chmod(full_path, perms)
                    if nlink > 1:
                        inodes[key] = full_path

            else: # filesize == 0
                if nlink > 1:
                    if key in inodes:
                        prev_path = inodes[key]
                        if os.path.lexists(full_path):
                            os.unlink(full_path)
                        try:
                            os.link(prev_path, full_path)
                        except Exception as e:
                            print(f"Failed to link {full_path} to {prev_path}: {e}")
                    else:
                        # Placeholder
                        if os.path.lexists(full_path):
                            os.unlink(full_path)
                        with open(full_path, 'wb') as f:
                            pass # empty
                        os.chmod(full_path, perms)
                        inodes[key] = full_path
                        placeholders.add(key)
                else:
                    # Just empty file
                    if os.path.lexists(full_path):
                        os.unlink(full_path)
                    with open(full_path, 'wb') as f:
                        pass
                    os.chmod(full_path, perms)

        elif file_type == 0o120000: # Symlink
            content = data[content_start : content_end]
            target = content.decode('utf-8').strip('\x00')
            if os.path.lexists(full_path):
                os.unlink(full_path)
            os.symlink(target, full_path)

        else:
            pass

def extract_rpm(rpm_path, dest_dir):
    print(f"Extracting {rpm_path}...")
    with open(rpm_path, 'rb') as f:
        data = f.read()

    # Find gzip magic
    idx = data.find(b'\x1f\x8b\x08')
    if idx == -1:
        print("No gzip signature found.")
        return

    compressed_data = data[idx:]
    try:
        decompressed_data = gzip.decompress(compressed_data)
    except Exception as e:
        print(f"Decompression failed: {e}")
        return

    extract_cpio(decompressed_data, dest_dir)

if __name__ == "__main__":
    dest_dir = os.path.abspath("toolchain")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    files = glob.glob("*.rpm")
    for f in files:
        extract_rpm(f, dest_dir)
