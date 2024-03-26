import re
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd
from typing_extensions import Self

from .data import Data
from .units_and_constants import ureg


class ExtractionError(Exception):
    """Custom exception for energy extraction errors."""
    pass


class Element:
    def __init__(self, raw_data: str, char_position: tuple[int, int] | None = None, line_position: tuple[int, int] | None = None) -> None:
        """
        Initialize an Element with raw data.

        Args:
            raw_data (str): The raw string data associated with this element.
        """
        self.raw_data = raw_data
        self.char_position = char_position
        self.line_position = line_position

    def readable_name(self):
        """
        Generate a readable name for the element.

        This method should be implemented by subclasses to provide a meaningful name based on the element's data.

        Returns:
            None by default, indicating the method has not been implemented. Subclasses should override this.
        """
        return None

    def get_structure(self) -> dict[Self, tuple | None]:
        """
        Retrieve the structural representation of the element.

        The structure is intended as a nested list to represent hierarchical relationships within data.

        Returns:
            A dictionary with the element itself as the key and an empty list as the value, indicating no nested structure by default.
        """
        return [self, []]

    def data(self) -> Data:
        """
        Process the raw data of the element to extract meaningful information.

        This method should be overridden by subclasses to implement specific data extraction logic.

        Returns:
            Data: An instance of the Data class containing 'raw data' as its content, with a comment indicating the absence of specific data extraction procedures.

        Raises:
            Warning: Indicates that no specific procedure for analyzing the data was found.
        """
        warnings.warn(
            (f"No procedure for analyzing the data found in type `{type(self)}`,"
             f"returning the raw data:\n{self.raw_data}")
        )
        return Data(data={'raw data': self.raw_data},
                    comment=("No procedure for analyzing the data found, `raw data` collected.\n"
                             "Please contribute to the project if you have knowledge on how to extract data from it."))

    def to_html(self) -> str:
        """
        Generate an HTML representation of the element.

        This method provides a basic HTML structure for displaying the element's data. Subclasses may override this method for more specialized HTML representations.

        Returns:
            str: A string containing the HTML representation of the element.
        """
        data = self.raw_data
        is_block = isinstance(self, Block)
        return (f'<div class="element" '
                f'python-class-name="{self.__class__.__name__}" '
                f'is-block="{is_block}"><pre>{data}</pre></div>')

    def depth(self) -> int:
        """
        Calculate the depth of nested structures within the element.

        This method recursively computes the maximum depth of nested lists representing the structure of the element.

        Returns:
            int: The maximum depth of the element's structure.
        """
        return Element.max_depth(self.get_structure())

    @staticmethod
    def max_depth(d) -> int:
        """
        Compute the maximum depth of a nested list structure.

        This static method assists in calculating the depth of an element's structure.

        Args:
            d (list): A nested list representing the structure of an element.

        Returns:
            int: The maximum depth of the nested list structure.
        """
        if isinstance(d, list) and len(d) > 0:
            return 1 + max(Element.max_depth(v) for v in d)
        return 0

    @staticmethod
    def process_invalid_name(input_string: str) -> str:
        """
        Clean and process an input string to generate a valid name.

        This method is used to sanitize input strings that may contain invalid characters or formatting. It ensures the output is suitable for use as a name or identifier.

        Args:
            input_string (str): The input string to be processed.

        Returns:
            str: A cleaned and truncated version of the input string, made suitable for use as a name or identifier.
        """
        # Check if the string contains any letters; if not, return "unknown"
        if not any(char.isalpha() for char in input_string):
            cleaned_string = ''.join(
                char for char in input_string if not char.isspace())
            return "Unknown: " + cleaned_string[:21] + ('' if len(cleaned_string) < 19 else '...')

        # Remove all characters that are not letters or spaces
        cleaned_string = ''.join(
            char for char in input_string if char.isalpha() or char.isspace())
        single_spaced_text = re.sub(r'\s+', ' ', cleaned_string)
        if single_spaced_text.startswith(' '):
            single_spaced_text = single_spaced_text[1:]

        # Return the first 30 characters of the cleaned string
        return single_spaced_text[:30] + ('' if len(single_spaced_text) < 28 else '...')


class Spacer(Element):
    def data(self) -> None:
        """
        Override the data method to return None for a Spacer.

        Since a Spacer is intended to represent empty space or a separator, it does not contain meaningful data to be processed or extracted.

        Returns:
            None: Indicating that there is no data associated with this Spacer.
        """
        return None


class Block(Element):
    """
    Represents a block of data within a structured document.

    A Block is an extension of the Element class, intended to encapsulate a more complex structure that may include a name, header, and body. This class provides methods to extract and present these components in various formats, including HTML.

    Attributes:
        data_available (bool): Indicates whether the block contains data that can be extracted. Defaults to False.
        position (tuple | None): The position of the block within the larger data structure, typically as a line number range.
    """
    data_available: bool = False

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        """
        Extract and separate the block's name, header, and body components.

        This method provides a basic implementation that simply identifies the block's name using a naming convention. Subclasses should override this method to implement more complex extraction logic.

        Returns:
            tuple[str, str | None, str]: A tuple containing the block's name, header (or None if not applicable), and body.
        """
        return Element.process_invalid_name(self.raw_data), None, self.raw_data

    def readable_name(self) -> str:
        """
        Retrieve a readable name for the block.

        Returns:
            str: The name of the block, extracted using the `extract_name_header_and_body` method.
        """
        return self.extract_name_header_and_body()[0]

    def header(self) -> str | None:
        """
        Retrieve the header of the block, if present.

        Returns:
            str | None: The header of the block or None if no header is present. Determined using the `extract_name_header_and_body` method.
        """
        return self.extract_name_header_and_body()[1]

    def body(self) -> str:
        """
        Retrieve the body content of the block.

        Returns:
            str: The body of the block, determined using the `extract_name_header_and_body` method.
        """
        return self.extract_name_header_and_body()[2]

    @staticmethod
    def header_preformat(header_raw: str) -> str:
        """
        Format the raw header content for HTML display.

        Args:
            header_raw (str): The raw header text to be formatted.

        Returns:
            str: The formatted header text wrapped in HTML <pre> tags.
        """
        return f'<pre>{header_raw}</pre>'

    @staticmethod
    def body_preformat(body_raw: str) -> str:
        """
        Format the raw body content for HTML display.

        Args:
            body_raw (str): The raw body text to be formatted.

        Returns:
            str: The formatted body text wrapped in HTML <pre> tags.
        """
        return f'<pre>{body_raw}</pre>'

    def to_html(self) -> str:
        """
        Generate an HTML representation of the block.

        This method constructs the HTML structure for the block, including its name, header (if present), and body. The depth of the block within the document structure is considered when determining the header's level.

        Returns:
            str: A string containing the HTML representation of the block.
        """
        readable_name, header, body = self.extract_name_header_and_body()
        header_level = max(7-self.depth(), 1)
        header_html = (f'<div class="header"><h{header_level}>'
                       f'{self.header_preformat(header)}'
                       f'</h{header_level}></div>'
                       f'<hr class="hr-in-block"></hr>') if header else ''
        body_html = (f'<div class="data">'
                     f'{self.body_preformat(body)}'
                     f'</div>') if body else ''
        line_start, line_finish = self.line_position or (-1, -1)
        can_extract_data = self.data_available
        is_block = True
        return (f'<div class="element block" '
                f'python-class-name="{self.__class__.__name__}" '
                f'readable-name="{readable_name}" '
                f'start-line={line_start} finish-line={line_finish} '
                f'data_available={can_extract_data}>'
                f'{header_html+body_html}</div>'
                f'<hr class = "hr-between-blocks"></hr>')


class AvailableBlocks:
    """
    A registry for managing different types of block elements.

    This class maintains a dictionary of all available block types that can be dynamically extended. New block classes can be registered using the provided class methods, facilitating modularity and extensibility.
    """
    # Dictionary to hold all available block types.
    blocks: dict[str, type[Element]] = {}

    @classmethod
    def register_block(cls, block_cls: type[Element]) -> type[Element]:
        """
        Decorator to register a new block type in the blocks dictionary.

        If a block class with the same name is already registered, this method raises a ValueError to prevent unintentional overwrites.

        Args:
            block_cls (type[Element]): The block class to be registered.

        Returns:
            type[Element]: The same block class that was passed in, enabling this method to be used as a decorator.

        Raises:
            ValueError: If a block with the same class name is already registered.
        """
        block_name = block_cls.__name__
        if block_name in cls.blocks:
            raise ValueError(f"Block type {block_name} is already defined.")
        cls.blocks[block_name] = block_cls
        return block_cls

    @classmethod
    def rewrite_block(cls, block_cls: type[Element]) -> type[Element]:
        """
        Decorator to register or overwrite an existing block type in the blocks dictionary.

        Unlike `register_block`, this method allows for the redefinition of block types. If a block with the same name already exists, it will be overwritten with the new definition.

        Args:
            block_cls (type[Element]): The block class to be registered or redefined.

        Returns:
            type[Element]: The same block class that was passed in, enabling this method to be used as a decorator.
        """
        block_name = block_cls.__name__
        cls.blocks[block_name] = block_cls
        return block_cls
