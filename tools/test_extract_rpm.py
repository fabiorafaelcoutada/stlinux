import unittest
import os
import shutil
import tempfile
import gzip
from unittest.mock import patch, MagicMock

# Import the functions to be tested
from extract_rpm import align_4, extract_cpio, extract_rpm

class TestExtractRPM(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_align_4(self):
        self.assertEqual(align_4(0), 0)
        self.assertEqual(align_4(1), 4)
        self.assertEqual(align_4(2), 4)
        self.assertEqual(align_4(3), 4)
        self.assertEqual(align_4(4), 4)
        self.assertEqual(align_4(5), 8)

    def _make_cpio_entry(self, filename, mode, content, ino=1, nlink=1, devmajor=1, devminor=1):
        namesize = len(filename) + 1 # including trailing null
        filesize = len(content)
        header = f"070701{ino:08x}{mode:08x}{0:08x}{0:08x}{nlink:08x}{0:08x}{filesize:08x}{devmajor:08x}{devminor:08x}{0:08x}{0:08x}{namesize:08x}{0:08x}"
        data = header.encode('ascii')
        data += filename.encode('ascii') + b'\x00'
        # Padding for name
        name_padding = (4 - (len(data) % 4)) % 4
        data += b'\x00' * name_padding

        data += content
        # Padding for content
        content_padding = (4 - (len(data) % 4)) % 4
        data += b'\x00' * content_padding
        return data

    def test_extract_cpio_regular_file(self):
        filename = "testfile.txt"
        content = b"Hello World"
        mode = 0o100644

        cpio_data = self._make_cpio_entry(filename, mode, content)
        cpio_data += self._make_cpio_entry("TRAILER!!!", 0, b"")

        extract_cpio(cpio_data, self.test_dir)

        target_path = os.path.join(self.test_dir, filename)
        self.assertTrue(os.path.isfile(target_path))
        with open(target_path, 'rb') as f:
            self.assertEqual(f.read(), content)
        # On some systems/environments, chmod might not work as expected or umask might interfere
        # But we check the core functionality
        self.assertEqual(os.stat(target_path).st_mode & 0o777, 0o644)

    def test_extract_cpio_directory(self):
        dirname = "testdir"
        mode = 0o040755

        cpio_data = self._make_cpio_entry(dirname, mode, b"")
        cpio_data += self._make_cpio_entry("TRAILER!!!", 0, b"")

        extract_cpio(cpio_data, self.test_dir)

        target_path = os.path.join(self.test_dir, dirname)
        self.assertTrue(os.path.isdir(target_path))
        self.assertEqual(os.stat(target_path).st_mode & 0o777, 0o755)

    def test_extract_cpio_symlink(self):
        linkname = "mylink"
        target = "testfile.txt"
        mode = 0o120777

        cpio_data = self._make_cpio_entry(linkname, mode, target.encode('ascii'))
        cpio_data += self._make_cpio_entry("TRAILER!!!", 0, b"")

        extract_cpio(cpio_data, self.test_dir)

        target_path = os.path.join(self.test_dir, linkname)
        self.assertTrue(os.path.islink(target_path))
        self.assertEqual(os.readlink(target_path), target)

    def test_extract_cpio_hardlink(self):
        file1 = "file1"
        file2 = "file2"
        content = b"Shared content"
        mode = 0o100644
        ino = 123

        # In CPIO, hardlinks are represented by same inode and multiple entries.
        # Usually one has the content, others have filesize 0.
        cpio_data = self._make_cpio_entry(file1, mode, content, ino=ino, nlink=2)
        cpio_data += self._make_cpio_entry(file2, mode, b"", ino=ino, nlink=2)
        cpio_data += self._make_cpio_entry("TRAILER!!!", 0, b"")

        extract_cpio(cpio_data, self.test_dir)

        path1 = os.path.join(self.test_dir, file1)
        path2 = os.path.join(self.test_dir, file2)

        self.assertTrue(os.path.isfile(path1))
        self.assertTrue(os.path.isfile(path2))

        with open(path2, 'rb') as f:
            self.assertEqual(f.read(), content)

        # Check if they are actually hardlinks (same inode on disk)
        self.assertEqual(os.stat(path1).st_ino, os.stat(path2).st_ino)

    def test_extract_cpio_path_traversal(self):
        filename = "../outside.txt"
        content = b"Malicious"

        cpio_data = self._make_cpio_entry(filename, 0o100644, content)
        cpio_data += self._make_cpio_entry("TRAILER!!!", 0, b"")

        # It should skip and print a message
        with patch('builtins.print') as mocked_print:
            extract_cpio(cpio_data, self.test_dir)
            mocked_print.assert_any_call(f"Skipping potentially malicious path: {filename}")

        target_path = os.path.abspath(os.path.join(self.test_dir, filename))
        self.assertFalse(os.path.exists(target_path))

    @patch('extract_rpm.gzip.decompress')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('extract_rpm.extract_cpio')
    def test_extract_rpm(self, mock_extract_cpio, mock_open_func, mock_decompress):
        rpm_data = b"some headers" + b"\x1f\x8b\x08" + b"compressed data"
        mock_open_func.return_value.__enter__.return_value.read.return_value = rpm_data

        mock_decompress.return_value = b"decompressed_cpio"

        extract_rpm("dummy.rpm", self.test_dir)

        mock_open_func.assert_called_with("dummy.rpm", 'rb')
        mock_decompress.assert_called_with(b"\x1f\x8b\x08" + b"compressed data")
        mock_extract_cpio.assert_called_with(b"decompressed_cpio", self.test_dir)

if __name__ == '__main__':
    unittest.main()
