import json
import os
from typing import Optional


class RegexSettings:
    """
    A class to load and process regular expression settings from a configuration file.
    """

    def __init__(self, settings_file: Optional[str] = None) -> None:
        """
        Initializes the RegexSettings class by loading regex settings from a specified file.

        :param settings_file: Optional; the file path of the regex settings JSON file.
                              If not provided, it defaults to 'regex.json' in the current directory.
        """
        if settings_file is None:
            # Get the directory of this file
            directory = os.path.dirname(__file__)
            # Construct the path to the default settings file
            settings_file = os.path.join(directory, 'regex.json')
        self.regexes = self._load_settings(settings_file)

    def _load_settings(self, settings_file: str) -> dict[str, dict | list]:
        """
        Loads regex settings from a JSON file.

        :param settings_file: The file path of the regex settings JSON file.
        :return: A dictionary representing the loaded regex settings.
        """
        with open(settings_file, "r") as file:
            return json.load(file)

    def to_list(self) -> list[dict[str, str | list[str]]]:
        """
        Generates a list of regex patterns and their associated details from the settings.

        :return: A list of dictionaries, each containing details of a regex pattern.
        """
        # Initialize an empty list to hold all regex pattern details
        ordered_regexes: list[dict[str, str | list[str]]] = []

        # Recursive function to walk through the nested structure
        def walk_through_blocks(block_dict: dict[str, dict | list | str]) -> None:
            """
            Recursively processes blocks to extract regex patterns and their details.

            :param block_dict: The current block of regex settings to process.
            """
            # Check if 'order' is a key in the current block
            if 'order' in block_dict:
                # Iterate over the order list
                for item in block_dict['order']:
                    # Recursively process the nested blocks
                    walk_through_blocks(block_dict[item])
            else:
                # If there's no 'order', it means we're at a leaf node
                if 'pattern' in block_dict:
                    # Add the entire block (dictionary) to the list
                    ordered_regexes.append(block_dict)

        # Start the recursive walk from the root
        walk_through_blocks(self.regexes)
        return ordered_regexes

    def tree(self, block_dict: Optional[dict[str, dict | list | str]] = None, depth: int = 0) -> str:
        """
        Generates a string representation of the regex settings in a tree-like structure.

        :param block_dict: The current block of regex settings to process. Defaults to the root block.
        :param depth: The current depth in the tree, used for indentation. Defaults to 0.
        :return: A string representing the tree structure of the regex settings.
        """
        if block_dict is None:
            block_dict = self.regexes
            result = "Regex Settings Tree:\n"
        else:
            result = ""

        # Check if 'order' is in the current block
        if 'order' in block_dict:
            for item in block_dict['order']:
                # Add indentation based on the depth level
                indentation = '    ' * depth
                # Add the current item and a newline to the result
                result += f"{indentation}{item}\n"
                # Recursively call the function to process the nested blocks
                result += self.tree(block_dict[item], depth + 1)
        return result
