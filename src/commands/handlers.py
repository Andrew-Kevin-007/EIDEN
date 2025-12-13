from commands.base import BaseCommand

class GreetCommand(BaseCommand):
    def execute(self):
        return "Hello! How can I assist you today?"

class FileOperationCommand(BaseCommand):
    def __init__(self, file_operations):
        self.file_operations = file_operations

    def execute(self, operation, filename):
        if operation == "read":
            return self.file_operations.read_file(filename)
        elif operation == "list":
            return self.file_operations.list_files()
        else:
            return "Invalid file operation."

class HelpCommand(BaseCommand):
    def execute(self):
        return "Available commands: greet, file operations, help."