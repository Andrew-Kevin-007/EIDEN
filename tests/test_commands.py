import unittest
from src.commands.handlers import CommandHandler

class TestCommandHandler(unittest.TestCase):

    def setUp(self):
        self.handler = CommandHandler()

    def test_handle_valid_command(self):
        command = "open file"
        response = self.handler.handle(command)
        self.assertEqual(response, "Opening file...")

    def test_handle_invalid_command(self):
        command = "unknown command"
        response = self.handler.handle(command)
        self.assertEqual(response, "Command not recognized.")

    def test_handle_file_operation_command(self):
        command = "list files"
        response = self.handler.handle(command)
        self.assertIn("Files listed successfully.", response)

if __name__ == '__main__':
    unittest.main()