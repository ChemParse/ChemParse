import json
import os
import re
import warnings
from typing import Dict, List, Optional, Pattern, Union
from .regex_request import RegexRequest


class RegexBlueprint:
    def __init__(self, order: List[str], pattern_structure: Dict[str, str], pattern_texts: Dict[str, str], comment: str) -> None:
        """
        Initializes a RegexBlueprint instance, which serves as a template for generating RegexRequest objects.

        Args:
            order (List[str]): The ordered list of keys that defines the sequence of generated RegexRequest objects.
            pattern_structure (Dict[str, str]): A dictionary defining the common structure of regex patterns,
                including 'beginning', 'ending', and 'flags' keys.
            pattern_texts (Dict[str, str]): A dictionary mapping each key in the 'order' list to a specific
                text snippet to be inserted into the pattern structure.
            comment (str): A comment or description associated with this blueprint.
        """
        self.order = order
        self.pattern_structure = pattern_structure
        self.pattern_texts = pattern_texts
        self.comment = comment
        self._initialize_items()

    def _initialize_items(self):
        self.items: dict[str, RegexRequest] = {}
        for name, text in self.pattern_texts.items():
            pattern = (f"{self.pattern_structure['beginning']}"
                       f"{text}{self.pattern_structure['ending']}")
            regex_request = RegexRequest(
                p_type="Block",
                p_subtype=name,
                pattern=pattern,
                flags=self.pattern_structure['flags'],
                comment=self.comment
            )
            self.items[name] = regex_request

    def to_list(self) -> List[RegexRequest]:
        """
        Generates a list of RegexRequest objects based on the blueprint.

        Returns:
            List[RegexRequest]: A list of generated RegexRequest objects following the blueprint's structure.
        """
        return [self.items[name] for name in self.order]

    def validate_configuration(self) -> None:
        """
        Validates the blueprint's configuration to ensure consistency and correctness.

        Raises:
            ValueError: If any configuration inconsistency or error is found.
        """
        # Check if all items in 'order' exist in 'pattern_texts'
        for name in self.order:
            if name not in self.pattern_texts:
                raise ValueError(
                    f"Item '{name}' in 'order' does not have a corresponding entry in 'pattern_texts'.")

        # Ensure 'pattern_structure' contains required keys
        required_keys = ['beginning', 'ending', 'flags']
        for key in required_keys:
            if key not in self.pattern_structure:
                raise ValueError(
                    f"'pattern_structure' is missing the required key: '{key}'.")

        # Validate 'flags' in 'pattern_structure'
        valid_flags = {"IGNORECASE", "MULTILINE",
                       "DOTALL", "UNICODE", "VERBOSE"}
        for flag in self.pattern_structure['flags']:
            if flag not in valid_flags:
                raise ValueError(
                    f"Invalid flag '{flag}' in 'pattern_structure'. Valid flags are: {', '.join(valid_flags)}.")

        # Validate that 'beginning' + 'ending' patterns are valid regex patterns
        try:
            re.compile(
                self.pattern_structure['beginning'] + self.pattern_structure['ending'])
        except re.error as e:
            raise ValueError(
                f"Invalid regex pattern in 'pattern_structure': {e}")

        # Confirm comment is a string
        if not isinstance(self.comment, str):
            raise ValueError("'comment' must be a string.")

    def add_item(self, name: str, pattern_text: str) -> None:
        """
        Adds a new pattern text to the blueprint and its corresponding key to the order.

        Args:
            name (str): The key name for the new pattern text.
            pattern_text (str): The specific text snippet to be inserted into the pattern structure for this new item.
        """
        self.pattern_texts[name] = pattern_text
        pattern = (f"{self.pattern_structure['beginning']}"
                   f"{pattern_text}{self.pattern_structure['ending']}")
        regex_request = RegexRequest(
            p_type="Block",
            p_subtype=name,
            pattern=pattern,
            flags=self.pattern_structure['flags'],
            comment=self.comment
        )
        self.items[name] = regex_request
        self.order.append(name)
        self.validate_configuration()

    def to_dict(self) -> Dict[str, Union[List[str], Dict[str, Union[str, List[str]]], str]]:
        """
        Converts the RegexBlueprint instance into a dictionary representation.

        Returns:
            Dict[str, Union[List[str], Dict[str, Union[str, List[str]]], str]]: A dictionary representation of the RegexBlueprint.
        """
        return {
            "order": self.order,
            "pattern_structure": self.pattern_structure,
            "pattern_texts": self.pattern_texts,
            "comment": self.comment
        }

    def __len__(self) -> int:
        """
        Returns the number of items defined in the blueprint's order.

        Returns:
            int: The length of the 'order' list.
        """
        return len(self.order)

    def __repr__(self) -> str:
        """
        Provides a detailed string representation of the RegexBlueprint instance for debugging.

        Returns:
            str: A string representation including the order, pattern structure, pattern texts, and comment.
        """
        return f"RegexBlueprint(Order: {self.order}, Pattern Structure: {self.pattern_structure}, Pattern Texts: {self.pattern_texts}, Comment: {self.comment})"

    def __str__(self) -> str:
        """
        Returns a string representation of the RegexBlueprint instance, using the tree method to illustrate the structure.

        Returns:
            str: A tree-like string representation of the blueprint.
        """
        return self.tree()

    def tree(self, depth: int = 0) -> str:
        """
        Generates a string representation of the blueprint hierarchy in a tree-like structure. This method is useful
        for visualizing the blueprint's pattern structure, pattern texts, and their hierarchical relationships.

        Args:
            depth (int): The current depth in the tree, used for indentation to represent hierarchy levels. Defaults to 0 at the root level.

        Returns:
            str: A string representation of the regex blueprint in a tree-like structure, showing nested patterns indented according to their depth.
        """
        result = "  " * depth + "RegexBlueprint:\n"
        for name in self.order:
            text = self.pattern_texts.get(name, '')
            pattern = (f"{self.pattern_structure['beginning']}"
                       f"{text}{self.pattern_structure['ending']}")
            result += "  " * (depth + 1) + f"{name}: Pattern: {pattern}\n"
        return result


class RegexSettings:
    def __init__(self, settings_file: Optional[str] = None, items: Optional[Dict[str, Union[RegexRequest, 'RegexSettings']]] = None, order: Optional[List[str]] = None) -> None:
        """
        Initializes a RegexSettings instance, which can either load settings from a file or be instantiated with provided items and order.

        Args:
            settings_file (Optional[str]): The path to a JSON file containing regex settings. If not provided, an empty or pre-defined configuration is used.
            items (Optional[Dict[str, Union[RegexRequest, 'RegexSettings']]]): A dictionary of items (RegexRequest objects or nested RegexSettings) keyed by their names.
            order (Optional[List[str]]): A list of item names specifying the order in which they should be processed.

        Raises:
            ValueError: If only one of items or order is provided, but not both.
        """
        if items is None and order is None:
            if settings_file is not None:
                # Load from file
                self.items = {}
                self.order = []
                self.load_settings(settings_file)
            else:
                # Empty class
                self.items = {}
                self.order = []
        elif items is not None and order is not None:
            self.items = items
            self.order = order
        else:
            raise ValueError(
                "Both 'items' and 'order' must be provided, or neither.")

        self.validate_configuration()

    def add_item(self, name: str, item: Union[RegexRequest, 'RegexSettings']) -> None:
        """
        Adds an item (RegexRequest or nested RegexSettings) to the settings.

        Args:
            name (str): The name/key associated with the item.
            item (Union[RegexRequest, 'RegexSettings']): The item to add, which can be a RegexRequest or another RegexSettings instance.

        Raises:
            ValueError: If the name already exists in the items.
        """
        if name in self.items:
            raise ValueError(f"Item with name '{name}' already exists.")
        self.items[name] = item
        if name not in self.order:
            self.order.append(name)
        self.validate_configuration()

    def set_order(self, order: List[str]) -> None:
        """
        Sets the order of items.

        Args:
            order (List[str]): A list of item names specifying the order.

        Raises:
            ValueError: If any name in the order list does not exist in the items.
        """
        for name in order:
            if name not in self.items:
                raise ValueError(
                    f"Item with name '{name}' does not exist in items.")
        self.order = order
        self.validate_configuration()

    def get_ordered_items(self) -> List[Union[RegexRequest, 'RegexSettings']]:
        """
        Returns a list of items in the specified order.

        Returns:
            List[Union[RegexRequest, 'RegexSettings']]: A list of ordered items.

        Raises:
            ValueError: If any name in the order list does not exist in the items.
        """
        ordered_items = [self.items[name]
                         for name in self.order if name in self.items]
        if len(ordered_items) != len(self.order):
            missing_items = set(self.order) - set(self.items.keys())
            raise ValueError(
                f"Missing items in 'items': {', '.join(missing_items)}")
        return ordered_items

    def to_list(self) -> List[Union[RegexRequest, 'RegexSettings']]:
        """
        Flattens the items to a list, expanding nested RegexSettings into their constituent RegexRequest objects.

        Returns:
            List[Union[RegexRequest, 'RegexSettings']]: A flattened list of RegexRequest objects and/or RegexSettings instances.
        """
        ordered_items = []
        for name in self.order:
            item = self.items[name]
            if isinstance(item, RegexRequest):
                ordered_items.append(item)
            elif isinstance(item, (RegexSettings, RegexBlueprint)):
                ordered_items.extend(item.to_list())
            else:
                raise TypeError(f"Unknown type of item '{name}': {type(item)}")
        return ordered_items

    def load_settings(self, settings_file: str) -> None:
        """
        Loads settings from a JSON file and populates the RegexSettings instance based on the file's content.

        Args:
            settings_file (str): The path to the JSON file containing the settings.
        """
        with open(settings_file, "r") as file:
            settings = json.load(file)
            self.parse_settings(settings)

    def parse_settings(self, settings: Dict[str, Union[Dict, List[str]]]) -> None:
        """
        Parses the given settings to populate this RegexSettings instance with
        RegexRequest objects, RegexBlueprint objects, or nested RegexSettings objects based on the settings structure.

        :param settings: The settings to parse, typically loaded from a JSON file.
        """
        self.items: Dict[str, Union[RegexRequest,
                                    RegexBlueprint, 'RegexSettings']] = {}
        self.order = settings.get('order', [])

        for name in self.order:
            item_settings = settings[name]

            # Handling a direct RegexRequest (defined by a 'pattern' key)
            if 'pattern' in item_settings:
                request = RegexRequest(
                    p_type=item_settings['p_type'],
                    p_subtype=item_settings['p_subtype'],
                    pattern=item_settings['pattern'],
                    flags=item_settings.get('flags', []),
                    comment=item_settings.get('comment', '')
                )
                self.items[name] = request

            # Handling a RegexBlueprint (defined by a 'pattern_structure' key)
            elif 'pattern_structure' in item_settings:
                blueprint = RegexBlueprint(
                    order=item_settings['order'],
                    pattern_structure=item_settings['pattern_structure'],
                    pattern_texts=item_settings['pattern_texts'],
                    comment=item_settings.get('comment', '')
                )
                self.items[name] = blueprint

            # Handling nested RegexSettings
            else:
                # If the item is a nested structure but not a direct RegexRequest or Blueprint
                subgroup = RegexSettings()
                subgroup.parse_settings(item_settings)
                self.items[name] = subgroup

        # Validate the configuration after parsing
        self.validate_configuration()

    def tree(self, depth: int = 0) -> str:
        """
        Generates a string representation of the settings hierarchy in a tree-like structure.
        This method is useful for visualizing the nested structure of regex settings and blueprints.

        Args:
            depth (int): The current depth in the tree, used for indentation to represent hierarchy levels. Defaults to 0 at the root level.

        Returns:
            str: A string representation of the regex settings in a tree-like structure, showing nested items indented according to their depth.
        """
        result = "  " * depth + "RegexGroup:\n"
        for name in self.order:
            item = self.items[name]
            # If the item is a RegexSettings or RegexBlueprint, recursively call the tree method to represent its nested structure
            if isinstance(item, (RegexSettings, RegexBlueprint)):
                result += "  " * (depth + 1) + \
                    f"{name}:\n" + item.tree(depth + 2)
            # If the item is a RegexRequest, simply append its string representation
            else:
                result += "  " * (depth + 1) + f"{name}: {item}\n"
        return result

    def validate_configuration(self) -> None:
        """
        Validates the regex configuration to ensure consistency between 'order' and 'items'.
        Also recursively validates the configuration of nested RegexSettings instances.

        Raises:
            ValueError: If an item in 'order' does not have a corresponding entry in 'items'.

        Warns:
            RuntimeWarning: If there are keys in 'items' not listed in 'order'.
        """
        # Check for items in 'order' that are not in 'items'
        for name in self.order:
            if name not in self.items:
                raise ValueError(
                    f"Error: Item '{name}' listed in 'order' but not found in 'items'.")

        for name, item in self.items.items():
            item.validate_configuration()
            if name not in self.order:
                warnings.warn(
                    f"Warning: Item '{name}' found in 'items' but not listed in 'order'.", RuntimeWarning)

    def to_dict(self) -> Dict[str, Union[Dict, List[str]]]:
        """Converts the RegexSettings instance and its nested structure to a dictionary."""
        result = {"order": self.order}
        for name in self.order:
            item = self.items[name]
            result[name] = item.to_dict() if isinstance(
                item, (RegexRequest, RegexSettings, RegexBlueprint)) else item
        return result

    def save_as_json(self, filename: str) -> None:
        """Saves the RegexSettings instance as a JSON file."""
        with open(filename, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)

    def __repr__(self) -> str:
        return f"RegexGroup(Order: {self.order}, Items: {list(self.items.keys())})"

    def __len__(self) -> str:
        return sum(len(item) for item in self.items.values())

    def __str__(self) -> str:
        return self.tree()


DEFAULT_ORCA_REGEX_FILE = os.path.join(
    os.path.dirname(__file__), 'orca_regex.json')
DEFAULT_ORCA_REGEX_SETTINGS: RegexSettings = RegexSettings(
    settings_file=DEFAULT_ORCA_REGEX_FILE)
