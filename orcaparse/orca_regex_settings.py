import json
import os


class RegexSettings:

    def __init__(self, settings_file=None):
        if settings_file is None:
            # Get the directory of this file
            directory = os.path.dirname(__file__)
            # Construct the path to orca_regex.json
            settings_file = os.path.join(directory, 'orca_regex.json')
        self.regexes = self.load_settings(settings_file)

    def load_settings(self, settings_file):
        with open(settings_file, "r") as file:
            return json.load(file)

    def update_regex(self, index, new_regex):
        if 0 <= index < len(self.regexes):
            self.regexes[index] = new_regex
        else:
            raise IndexError("Regex index out of range.")

    def add_regex(self, regex):
        self.regexes.append(regex)

    def remove_regex(self, index):
        if 0 <= index < len(self.regexes):
            del self.regexes[index]
        else:
            raise IndexError("Regex index out of range.")
