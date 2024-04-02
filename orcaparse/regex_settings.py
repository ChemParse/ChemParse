from __future__ import annotations

import json
import os
import re
import warnings
from typing import Optional

from .regex_request import RegexRequest


class RegexBlueprint:
    """
    A class representing a blueprint for generating multiple RegexRequest objects with a shared structure.

    The RegexBlueprint class is useful for defining a common structure for multiple regex patterns that share a similar format.
    By defining a blueprint with a pattern structure and a set of pattern texts, you can generate multiple RegexRequest objects
    with the same structure but different text snippets. This is particularly useful when you have a set of related patterns
    that follow a consistent format but differ in specific details.

    :param list[str] order: The ordered list of keys that defines the sequence of generated RegexRequest objects.
    :param dict[str, str] pattern_structure: A dictionary defining the common structure of regex patterns,
        including `beginning`, `ending`, and `flags` keys.
    :param dict[str, str] pattern_texts: A dictionary mapping each key in the `order` list to a specific
        text snippet to be inserted into the pattern structure.
    :param str comment: A comment or description associated with this blueprint.

    **Attributes**

    .. attribute:: order
        :type: list[str]

        The ordered list of keys that defines the sequence of generated RegexRequest objects.

    .. attribute:: pattern_structure
        :type: dict[str, str]

        A dictionary defining the common structure of regex patterns, including 'beginning', 'ending', and 'flags' keys.

    .. attribute:: pattern_texts
        :type: dict[str, str]

        A dictionary mapping each key in the 'order' list to a specific text snippet to be inserted into the pattern structure.

    .. attribute:: comment
        :type: str

        A comment or description associated with this blueprint.

    **Examples**

    .. code-block:: python

        import orcaparse as op

        # Define a blueprint for extracting multiple blocks of text from an ORCA output file
        rb = op.RegexBlueprint(
            order=[
                "BlockOrcaVersion",
                "BlockOrcaContributions",
            ],
            pattern_structure={
                "beginning": r"^([ \\t]*",
                "ending": r".*?\\n(?:^(?!^[ \\t]*[\\-\\*\\#\\=]{5,}.*$|^[ \\t]*$).*\\n)*)",
                "flags": ["MULTILINE"],
            },
            pattern_texts={
                "BlockOrcaVersion": "Program Version",
                "BlockOrcaContributions": "With contributions from"
            },
            comment="Blueprint: Paragraph with the line that starts with specified text.",
        )

        # Generate a list of RegexRequest objects based on the blueprint
        regex_requests = rb.to_list()

        # Validate the blueprint configuration
        rb.validate_configuration()

    """

    def __init__(self, order: list[str], pattern_structure: dict[str, str], pattern_texts: dict[str, str], comment: str) -> None:
        """
        Initializes a RegexBlueprint instance, which serves as a template for generating RegexRequest objects.

        Parameters:
            order (list[str]): The ordered list of keys that defines the sequence of generated RegexRequest objects.
            pattern_structure (dict[str, str]): A dictionary defining the common structure of regex patterns,
                including 'beginning', 'ending', and 'flags' keys.
            pattern_texts (dict[str, str]): A dictionary mapping each key in the 'order' list to a specific
                text snippet to be inserted into the pattern structure.
            comment (str): A comment or description associated with this blueprint.
        """
        self.order: list[str] = order
        self.pattern_structure: dict[str, str] = pattern_structure
        self.pattern_texts: dict[str, str] = pattern_texts
        self.comment: str = comment
        self._initialize_items()

    def _initialize_items(self) -> None:
        """
        Initializes the `items` dictionary by creating `RegexRequest` objects for each pattern text defined in the blueprint.

        This method constructs each regex pattern by combining the predefined structure with the specific text snippets, and then initializes `RegexRequest` objects with these patterns.
        """
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

    def to_list(self) -> list[RegexRequest]:
        """
        Converts the blueprint's items into a list of `RegexRequest` objects ordered according to the blueprint's `order` attribute.

        :return: An ordered list of `RegexRequest` objects generated from the blueprint.
        :rtype: list[RegexRequest]
        """
        return [self.items[name] for name in self.order]

    def validate_configuration(self) -> None:
        """
        Checks the blueprint's configuration for consistency and correctness, ensuring all necessary components are correctly defined.

        This includes verifying the presence of each item in the `order` within the `pattern_texts`, the inclusion of required keys in the `pattern_structure`, the validity of specified regex flags, and the correctness of the regex pattern.

        :raises ValueError: If any aspect of the blueprint's configuration is found to be inconsistent or incorrect.
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
        Adds a new item to the blueprint, updating the pattern texts, items, and order accordingly.

        :param name: The key for the new pattern text.
        :type name: str
        :param pattern_text: The text snippet to be inserted into the pattern structure for the new item.
        :type pattern_text: str
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

    def to_dict(self) -> dict[str, list[str] | dict[str, str | list[str]] | str]:
        """
        Converts the RegexBlueprint instance into a dictionary representation.

        :return: A dictionary containing the blueprint's ordered keys, pattern structure, pattern texts, and an optional comment.
        :rtype: dict[str, list[str] | dict[str, str | list[str]] | str]
        """
        return {
            "order": self.order,
            "pattern_structure": self.pattern_structure,
            "pattern_texts": self.pattern_texts,
            "comment": self.comment
        }

    def __len__(self) -> int:
        """
        Returns the count of unique pattern text entries defined in the blueprint.

        :return: The total number of pattern text entries.
        :rtype: int
        """
        return len(self.order)

    def __repr__(self) -> str:
        """
        Generates a detailed string representation of the RegexBlueprint instance, including its main components.

        :return: A string representation that includes the blueprint's order, pattern structure, pattern texts, and comment.
        :rtype: str
        """
        return f"RegexBlueprint(Order: {self.order}, Pattern Structure: {self.pattern_structure}, Pattern Texts: {self.pattern_texts}, Comment: {self.comment})"

    def __str__(self) -> str:
        """
        Provides a simplified string representation of the RegexBlueprint instance.

        :return: A concise string summary of the blueprint.
        :rtype: str
        """
        return self.tree()

    def tree(self, depth: int = 0) -> str:
        """
        Generates a tree-like string representation of the blueprint, illustrating the hierarchy of pattern structures and texts.

        :param depth: The initial indentation depth, used to represent hierarchical levels in the output string. The root level starts at 0.
        :type depth: int
        :return: A string visualization of the blueprint, with patterns and texts formatted in a hierarchical, tree-like structure.
        :rtype: str
        """
        result = "  " * depth + "RegexBlueprint:\n"
        for name in self.order:
            text = self.pattern_texts.get(name, '')
            pattern = (f"{self.pattern_structure['beginning']}"
                       f"{text}{self.pattern_structure['ending']}")
            result += "  " * (depth + 1) + f"{name}: Pattern: {pattern}\n"
        return result


class RegexSettings:
    """
    Manages a collection of regex patterns and settings, supporting hierarchical organization and JSON-based configuration.

    This class facilitates the organization, storage, and retrieval of regex patterns and their configurations. It can be directly instantiated with regex patterns and an execution order or loaded from a JSON file containing the configurations.

    :ivar items: A mapping from names to `RegexRequest` objects or nested `RegexSettings`, representing individual regex patterns or groups of patterns.
    :vartype items: dict[str, RegexRequest | RegexSettings]
    :ivar order: The order in which the regex patterns or groups should be applied or processed.
    :vartype order: list[str]
    """

    items: dict[str, RegexRequest | RegexSettings]
    order: list[str]

    def __init__(self, settings_file: Optional[str] = None, items: Optional[dict[str, RegexRequest | RegexSettings]] = None, order: Optional[list[str]] = None) -> None:
        """
        Initializes a `RegexSettings` instance with optional configurations from a file or provided items and order.

        :param settings_file: The path to a JSON file containing regex settings. If specified, settings are loaded from this file.
        :type settings_file: Optional[str], optional
        :param items: A dictionary mapping names to `RegexRequest` objects or nested `RegexSettings`, specifying the regex patterns and configurations.
        :type items: Optional[dict[str, RegexRequest | RegexSettings]]
        :param order: A list of item names defining the order in which the regex patterns or groups should be applied.
        :type order: Optional[list[str]], optional
        :raises ValueError: If either `items` or `order` is provided without the other, raising a configuration inconsistency.
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

    def add_item(self, name: str, item: RegexRequest | RegexSettings, rewrite: bool = False) -> None:
        """
        Adds a new regex pattern or settings group to the `RegexSettings` instance.

        :param name: The unique name/key for the new item.
        :type name: str
        :param item: The `RegexRequest` or `RegexSettings` instance to be added.
        :type item: Union[RegexRequest, RegexSettings]
        :param rewrite: If `True`, an existing item with the same name will be overwritten. Defaults to `False`.
        :type rewrite: bool, optional
        :raises ValueError: If an item with the same name already exists and `rewrite` is `False`.
        """
        if name in self.items and not rewrite:
            raise ValueError(f"Item with name '{name}' already exists.")
        self.items[name] = item
        if name not in self.order:
            self.order.append(name)
        self.validate_configuration()

    def set_order(self, order: list[str]) -> None:
        """
        Defines the processing order for the regex items within this `RegexSettings` instance.

        :param order: The sequence of item names, determining the order in which items are processed.
        :type order: list[str]
        :raises ValueError: If any name in the provided order does not correspond to an existing item in `self.items`.
        """
        if any(name not in self.items for name in order):
            missing_items = [name for name in order if name not in self.items]
            raise ValueError(
                f"Item(s) '{', '.join(missing_items)}' not found in items.")
        self.order = order

    def get_ordered_items(self) -> list[RegexRequest | RegexSettings]:
        """
        Retrieves the regex items in the order specified by `self.order`.

        :return: An ordered list of `RegexRequest` objects and/or `RegexSettings` instances.
        :rtype: list[RegexRequest | RegexSettings]
        :raises ValueError: If the order list references names not present in the items dictionary.
        """
        if missing_items := [name for name in self.order if name not in self.items]:
            raise ValueError(
                f"Missing items in 'items': {', '.join(missing_items)}")
        return [self.items[name] for name in self.order]

    def to_list(self) -> list[RegexRequest | RegexSettings]:
        """
        Converts the `RegexSettings` instance to a flattened list of `RegexRequest` objects, including those from nested `RegexSettings`.

        :return: A list containing all `RegexRequest` objects and `RegexSettings` instances, expanded in order.
        :rtype: list[RegexRequest | RegexSettings]
        :raises TypeError: If an item within `self.items` is neither a `RegexRequest` nor a `RegexSettings` instance.
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
        Populates the `RegexSettings` instance with configurations from a specified JSON file.

        :param settings_file: The file path to the JSON file containing regex configurations.
        :type settings_file: str
        """
        with open(settings_file, "r") as file:
            settings = json.load(file)
            self.parse_settings(settings)

    def parse_settings(self, settings: dict[str, dict | list[str]]) -> None:
        """
        Parses a settings dictionary to populate the `RegexSettings` instance with `RegexRequest`, `RegexBlueprint`, or nested `RegexSettings`.

        :param settings: A dictionary containing the configuration for regex patterns. It may define `RegexRequest` objects directly, specify `RegexBlueprint` configurations, or contain nested `RegexSettings`.
        :type settings: dict[str, dict| list[str]]
        """
        self.items = {}
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
        Visualizes the regex settings hierarchy as a tree-like structure, showing the nested organization of patterns and groups.

        :param depth: The initial indentation level, used to visually represent the depth of nested structures.
        :type depth: int
        :return: A string visualization of the settings hierarchy, formatted as an indented tree structure.
        :rtype: str
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
        Ensures that each item listed in the order is present in the items dictionary and validates nested configurations.

        :raises ValueError: If an ordered item is missing from the items dictionary.
        :raises RuntimeWarning: If there are items not included in the order.
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

    def to_dict(self) -> dict[str, dict | list[str]]:
        """
        Serializes the `RegexSettings` instance, including its nested structure, into a dictionary format suitable for JSON serialization.

        :return: A dictionary representation of the `RegexSettings` instance, capturing the order of items and the nested regex configurations.
        :rtype: dict[str, dict| list[str]]
        """
        result = {"order": self.order}
        for name in self.order:
            item = self.items[name]
            result[name] = item.to_dict() if isinstance(
                item, (RegexRequest, RegexSettings, RegexBlueprint)) else item
        return result

    def save_as_json(self, filename: str) -> None:
        """
        Exports the `RegexSettings` configuration to a JSON file, preserving the nested structure and order of regex patterns.

        :param filename: The file path where the JSON representation of the regex settings should be saved.
        :type filename: str
        """
        with open(filename, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)

    def __repr__(self) -> str:
        """
        Generates a concise string representation of the `RegexSettings` instance for debugging and logging.

        :return: A string summary of the regex settings, including the order and a list of item keys.
        :rtype: str
        """
        return f"RegexSettings(Order: {self.order}, Items: {list(self.items.keys())})"

    def __len__(self) -> int:
        """
        Calculates the cumulative length of all regex items in the settings, considering the length of nested `RegexSettings`.

        :return: The total length of all contained regex items and groups.
        :rtype: int
        """
        return sum(len(item) for item in self.items.values())

    def __str__(self) -> str:
        """
        Provides a human-readable string representation of the `RegexSettings` instance, formatted as a nested tree structure.

        :return: A tree-like string visualization of the regex settings hierarchy.
        :rtype: str
        """
        return self.tree()

# Variable Documentation


DEFAULT_ORCA_REGEX_FILE = os.path.join(
    os.path.dirname(__file__), 'orca_regex.json')
"""
Path to the default ORCA regex settings JSON file, included with the package.
:type: str
"""

DEFAULT_ORCA_REGEX_SETTINGS = RegexSettings(
    settings_file=DEFAULT_ORCA_REGEX_FILE)
"""
The pre-loaded `RegexSettings` instance containing the default regex patterns for ORCA output parsing.
:type: RegexSettings
"""

DEFAULT_GPAW_REGEX_FILE = os.path.join(
    os.path.dirname(__file__), 'gpaw_regex.json')
"""
Path to the default GPAW regex settings JSON file, included with the package.
:type: str
"""

DEFAULT_GPAW_REGEX_SETTINGS = RegexSettings(
    settings_file=DEFAULT_GPAW_REGEX_FILE)
"""
The pre-loaded `RegexSettings` instance containing the default regex patterns for GPAW output parsing.
:type: RegexSettings
"""
