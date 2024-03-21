import re
import json
import os
from typing import Dict, List, Optional, Union

DEFAULT_REGEX_FILE = os.path.join(os.path.dirname(__file__), 'regex.json')


class RegexRequest:
    def __init__(self, p_type: str, p_subtype: str, pattern: str, flags: list, comment: str = '') -> None:
        self.p_type = p_type
        self.p_subtype = p_subtype
        self.pattern = pattern
        self.comment = comment
        self.flags = self._compile_flags(flags)

    def _compile_flags(self, flag_names: List[str]) -> int:
        compiled_flags = 0
        valid_flags = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
            "UNICODE": re.UNICODE,
            "VERBOSE": re.VERBOSE
        }
        for flag_name in flag_names:
            flag = valid_flags.get(flag_name.upper())
            if flag is not None:
                compiled_flags |= flag
            else:
                raise ValueError(f"Warning: {flag_name} is not a valid flag.")
        return compiled_flags

    def __len__(self):
        return 1

    def __repr__(self) -> str:
        # Show a part of the pattern for brevity
        pattern = self.pattern if len(
            self.pattern) < 25 else self.pattern[:25] + '...'
        # Show a part of the comment for brevity
        comment = self.comment if len(
            self.comment) < 25 else self.comment[:25] + '...'

        return f"RegexRequest(p_type={self.p_type}, p_subtype={self.p_subtype}, pattern={pattern}, flags={self.flags}, comment={comment}"


class RegexSettings:
    def __init__(self, settings_file: str = None, items=None, order=None) -> None:
        if items is None and order is None:
            if settings_file is not None:
                # load from file
                self.items = {}  # To hold both RegexRequest and RegexGroup objects
                self.order = []  # To hold the order of processing for items
                self.load_settings(settings_file)
            else:
                # empty class
                self.items = {}  # To hold both RegexRequest and RegexGroup objects
                self.order = []  # To hold the order of processing for items
        elif items is not None and order is not None:
            self.items = items  # To hold both RegexRequest and RegexGroup objects
            self.order = order  # To hold the order of processing for items
        else:
            raise ValueError(
                f'items: {items}, order: {items}. One of them is None, while the other is not.')

    def add_item(self, name: str, item: Union[RegexRequest, 'RegexSettings']) -> None:
        self.items[name] = item

    def set_order(self, order: List[str]) -> None:
        self.order = order

    def get_ordered_items(self) -> List[Union[RegexRequest, 'RegexSettings']]:
        ordered_items = []
        for name in self.order:
            item = self.items.get(name)
            if item:
                ordered_items.append(item)
            else:
                raise ValueError(f"No item found with name '{name}'")
        return ordered_items

    def to_list(self) -> List[Union[RegexRequest, 'RegexSettings']]:
        ordered_items = []
        for name in self.order:
            if name not in self.items:
                raise ValueError(
                    f'{name} is not in items {list(self.items.keys())}')
            item = self.items[name]
            if isinstance(item, RegexRequest):
                ordered_items.append(item)
            elif isinstance(item, RegexSettings):
                ordered_items.extend(item.to_list())
            else:
                raise TypeError(f'Unknown type of item {name}: {type(item)}')
        return ordered_items

    def load_settings(self, settings_file: str) -> None:
        with open(settings_file, "r") as file:
            settings = json.load(file)
            self.parse_settings(settings)

    def parse_settings(self, settings: Dict[str, Union[Dict, List, str]]) -> None:
        # To hold both RegexRequest and RegexGroup objects
        self.items: dict[str, RegexRequest | RegexSettings] = {}
        self.order: list[str] = []  # To hold the order of processing for items
        for name in settings['order']:
            item_settings = settings[name]
            if 'pattern' in item_settings:  # This is a RegexRequest
                request = RegexRequest(
                    p_type=item_settings.get('p_type'),
                    p_subtype=item_settings.get('p_subtype'),
                    pattern=item_settings['pattern'],
                    flags=item_settings.get('flags', []),
                    comment=item_settings.get('comment', '')
                )
                self.items[name] = request
                self.order.append(name)
            else:  # Nested RegexGroup
                subgroup = RegexSettings()
                subgroup.parse_settings(item_settings)
                self.items[name] = subgroup
                self.order.append(name)

    def tree(self, depth: int = 0) -> str:
        result = "  " * depth + "RegexGroup:\n"
        for name in self.order:
            item = self.items[name]
            if isinstance(item, RegexSettings):
                result += "  " * (depth + 1) + \
                    f"{name}:\n" + item.tree(depth + 2)
            else:
                result += "  " * (depth + 1) + f"{name}: {item}\n"
        return result

    def __repr__(self) -> str:
        return f"RegexGroup(Order: {self.order}, Items: {list(self.items.keys())})"

    def __len__(self) -> str:
        return sum(len(item) for item in self.items.values())

    def __str__(self) -> str:
        return self.tree()
