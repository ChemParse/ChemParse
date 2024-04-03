import logging


class InMemoryHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(InMemoryHandler, self).__init__(*args, **kwargs)
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)

    def get_logs(self):
        return self.logs

    def clear_logs(self):
        self.logs = []


# Configure package-level logger
logger = logging.getLogger('orcaparse')
logger.setLevel(logging.DEBUG)  # Capture all logs, regardless of level

# Create and configure the in-memory handler to store all logs
memory_handler = InMemoryHandler()
memory_handler.setLevel(logging.DEBUG)  # Store every log regardless of level
logger.addHandler(memory_handler)

# Create and configure a stream handler (console output) with a higher level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Change this level as needed
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Functions to interact with the log storage


def get_logs():
    return memory_handler.get_logs()


def print_logs():
    for log in get_logs():
        print(log)


def clear_logs():
    memory_handler.clear_logs()
