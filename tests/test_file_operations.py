import unittest
from src.file_operations.safe_ops import read_file, list_files

class TestFileOperations(unittest.TestCase):

    def setUp(self):
        self.whitelisted_directory = "Downloads"  # Example whitelisted directory

    def test_read_file_valid(self):
        # Assuming a test file exists in the whitelisted directory
        test_file_path = f"{self.whitelisted_directory}/test_file.txt"
        content = read_file(test_file_path)
        self.assertIsInstance(content, str)

    def test_read_file_invalid(self):
        invalid_file_path = "Documents/invalid_file.txt"
        with self.assertRaises(PermissionError):
            read_file(invalid_file_path)

    def test_list_files(self):
        files = list_files(self.whitelisted_directory)
        self.assertIsInstance(files, list)
        for file in files:
            self.assertTrue(file.endswith('.txt'))  # Assuming we only want .txt files

if __name__ == '__main__':
    unittest.main()