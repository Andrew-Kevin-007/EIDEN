class BaseCommand:
    def execute(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")