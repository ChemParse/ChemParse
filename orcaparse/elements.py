import re
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd
from typing_extensions import Self

from .data import Data
from .logging_config import logger
from .units_and_constants import ureg


class ExtractionError(Exception):
    """
    Custom exception class for errors encountered during energy extraction processes.

    This exception is raised when there is a problem with extracting energy-related data from a given source or dataset.
    """
    pass


class Element:
    """
    Represents a basic element within a structured document, serving as a fundamental unit of data.

    An `Element` encapsulates raw data, positional information, and provides methods for data extraction and presentation. It acts as a base class for more specialized elements tailored to specific data types or structures within a document.

    :param raw_data: The raw text data associated with the element.
    :type raw_data: str
    :param char_position: The character position range (start, end) of the element within the larger data structure, if applicable.
    :type char_position: tuple[int, int] | None, optional
    :param line_position: The line position range (start, end) of the element within the larger data structure, if applicable.
    :type line_position: tuple[int, int] | None, optional

    :ivar raw_data: The raw text data associated with this element.
    :vartype raw_data: str
    :ivar char_position: The character position range of the element within the data structure, or `None`.
    :vartype char_position: tuple[int, int] | None
    :ivar line_position: The line position range of the element within the data structure, or `None`.
    :vartype line_position: tuple[int, int] | None
    """

    def __init__(self, raw_data: str, char_position: tuple[int, int] | None = None, line_position: tuple[int, int] | None = None) -> None:
        """
        Initializes an `Element` instance with raw data and optional positional information.
        """
        self.raw_data: str = raw_data
        self.char_position: tuple[int, int] | None = char_position
        self.line_position: tuple[int, int] | None = line_position

    def readable_name(self) -> None:
        """
        Generate a readable name for the element based on its data.

        This method is intended to be overridden by subclasses to provide a meaningful, human-readable name derived from the element's content.

        :return: `None` by default, indicating the method has not been implemented. Subclasses should override this method.
        :rtype: None
        """
        return None

    def get_structure(self) -> dict[Self, tuple | None]:
        """
        Retrieve the structural representation of the element as a nested dictionary.

        This method provides a way to represent the hierarchical relationships within data, where each element can contain nested sub-elements.

        :return: A dictionary with the element itself as the key and an empty tuple as the value, indicating no nested structure by default.
        :rtype: dict[Self, tuple | None]
        """
        return {self: []}

    def data(self) -> Data:
        """
        Process the raw data of the element to extract meaningful information.

        This method is designed to be overridden by subclasses to implement specific data extraction logic tailored to the element's structure and content.

        :return: An instance of the `Data` class containing 'raw data' as its content, accompanied by a comment indicating the absence of specific data extraction procedures.
        :rtype: Data
        :raises Warning: Indicates that no specific procedure for analyzing the data was implemented.
        """
        logger.warning(
            f"No procedure for analyzing the data "
            f"found in type `{type(self).__name__}`, "
            f"returning the raw data:\n{self.raw_data}"
        )
        return Data(data={'raw data': self.raw_data},
                    comment=("No procedure for analyzing the data found, `raw data` collected.\n"
                             "Please contribute to the project if you have knowledge on how to extract data from it."))

    @staticmethod
    def data_preformat(data_raw: str) -> str:
        """
        Format the raw data for HTML display.

        This static method wraps the raw data in HTML <pre> tags for better readability when displayed as HTML.

        :param data_raw: The raw text to be formatted.
        :type data_raw: str
        :return: The formatted text wrapped in HTML <pre> tags.
        :rtype: str
        """
        return f'<pre>{data_raw}</pre>'

    def to_html(self) -> str:
        """
        Generate an HTML representation of the element.

        This method provides a basic HTML structure for displaying the element's data. Subclasses may override this method to provide more specialized HTML representations tailored to the element's specific characteristics.

        :return: A string containing the HTML representation of the element, incorporating the preformatted raw data.
        :rtype: str
        """
        data = self.raw_data
        is_block = isinstance(self, Block)
        line_start, line_finish = self.line_position or (-1, -1)
        return (f'<div class="element" '
                f'python-class-name="{self.__class__.__name__}" '
                f'start-line={line_start} finish-line={line_finish} '
                f'is-block="{is_block}">\n{self.data_preformat(data)}</div>')

    def depth(self) -> int:
        """
        Calculate the depth of nested structures within the element.

        This method computes the maximum depth of nested lists representing the hierarchical structure of the element, indicating the complexity of its structure.

        :return: The maximum depth of the element's nested list structure.
        :rtype: int
        """
        return Element.max_depth(self.get_structure())

    @staticmethod
    def max_depth(d) -> int:
        """
        Compute the maximum depth of a nested list structure.

        This utility method assists in determining the complexity of an element's structural hierarchy by calculating the depth of nested lists.

        :param d: A nested list or dictionary representing the structure of an element or a complex data structure.
        :type d: list | dict
        :return: The maximum depth of the nested list or dictionary structure.
        :rtype: int
        """
        if isinstance(d, list) and len(d) > 0:
            return 1 + max(Element.max_depth(v) for v in d)
        return 0

    @staticmethod
    def process_invalid_name(input_string: str) -> str:
        """
        Clean and process an input string to generate a valid name or identifier.

        This method sanitizes input strings that may contain invalid characters or formatting, ensuring the output is suitable for use as a name or identifier. It handles strings without letters by labeling them as "Unknown" and removes non-alphabetic characters from other strings.

        :param input_string: The input string to be processed.
        :type input_string: str
        :return: A cleaned and possibly truncated version of the input string, made suitable for use as a name or identifier.
        :rtype: str
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
        Indicate that no data is associated with a Spacer element.

        Overrides the `data` method from the `Element` class to return `None`, reflecting the intended use of a `Spacer` as a representation of empty space or a separator without meaningful data.

        :return: `None`, indicating the absence of data.
        :rtype: None
        """
        return None

    @staticmethod
    def data_preformat(data_raw: str) -> str:
        """
        Format raw Spacer content for HTML display by replacing newlines with HTML line breaks.

        :param data_raw: The raw text content of the spacer.
        :type data_raw: str
        :return: The formatted content with newlines converted to HTML line breaks.
        :rtype: str
        """
        return data_raw.replace('\n', '<br>')


class Block(Element):
    """
    Represents a complex data block within a structured document.

    Extends the `Element` class to encapsulate a more structured unit of data, potentially including identifiable components such as a name, header, and body. It provides methods to extract and present these components, with a default implementation for name extraction.

    :ivar data_available: Indicates whether the block contains extractable data. Defaults to `False`.
    :vartype data_available: bool
    :ivar position: The position of the block within the larger document structure, often expressed as a range of line numbers.
    :vartype position: tuple | None
    """
    data_available: bool = False

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        """
        Extract the block's name, header, and body components.

        Offers a basic implementation for separating the block's name from its content based on naming conventions. This method is intended to be overridden by subclasses for more specialized extraction logic.

        :return: A tuple containing the block's name, optional header, and body content.
        :rtype: tuple[str, str | None, str]
        """
        return Element.process_invalid_name(self.raw_data), None, self.raw_data

    def readable_name(self) -> str:
        """
        Generate a readable name for the block based on its content.

        Utilizes the `extract_name_header_and_body` method to derive a name for the block, suitable for display or identification purposes.

        :return: The extracted name of the block.
        :rtype: str
        """
        return self.extract_name_header_and_body()[0]

    def header(self) -> str | None:
        """
        Retrieve the block's header, if it exists.

        Uses the `extract_name_header_and_body` method to determine the presence and content of a header within the block.

        :return: The block's header if present, otherwise `None`.
        :rtype: str | None
        """
        return self.extract_name_header_and_body()[1]

    def body(self) -> str:
        """
        Retrieve the body content of the block.

        Utilizes the `extract_name_header_and_body` method to extract the body of the block, which contains the main content.

        :return: The body content of the block.
        :rtype: str
        """
        return self.extract_name_header_and_body()[2]

    @staticmethod
    def header_preformat(header_raw: str) -> str:
        """
        Format the raw header content for HTML display.

        This static method wraps the raw header text in HTML <pre> tags to enhance its presentation in HTML format.

        :param header_raw: The raw text of the header.
        :type header_raw: str
        :return: The formatted header text, suitable for HTML display.
        :rtype: str
        """
        return f'<pre>{header_raw}</pre>'

    @staticmethod
    def body_preformat(body_raw: str) -> str:
        """
        Format the raw body content for HTML display.

        This static method wraps the raw body text in HTML <pre> tags to enhance its presentation in HTML format.

        :param body_raw: The raw text of the body.
        :type body_raw: str
        :return: The formatted body text, suitable for HTML display.
        :rtype: str
        """
        return f'<pre>{body_raw}</pre>'

    def to_html(self) -> str:
        """
        Generate an HTML representation of the block.

        Constructs an HTML structure for the block, incorporating the name, header (if present), and body. The depth of the block within the document structure influences the header's HTML level.

        :return: A string containing the HTML representation of the block, with header and body sections formatted and wrapped in appropriate HTML tags.
        :rtype: str
        """
        readable_name, header, body = self.extract_name_header_and_body()
        header_level = max(7-self.depth(), 1)
        header_html = (f'<div class="header"><h{header_level}>\n'
                       f'{self.header_preformat(header)}'
                       f'</h{header_level}></div>'
                       f'<hr class="hr-in-block"></hr>') if header else ''
        body_html = (f'<div class="data">\n'
                     f'{self.body_preformat(body)}'
                     f'</div>') if body else ''
        line_start, line_finish = self.line_position or (-1, -1)
        can_extract_data = self.data_available
        return (f'<div class="element block" '
                f'python-class-name="{self.__class__.__name__}" '
                f'readable-name="{readable_name}" '
                f'start-line={line_start} finish-line={line_finish} '
                f'data_available={can_extract_data}>'
                f'{header_html+body_html}</div>'
                f'<hr class = "hr-between-blocks"></hr>')


class AvailableBlocksGeneral:
    """
    Manages a registry of different types of block elements within a structured document.

    This class provides a dynamic registry for block types, allowing for modular extension of block element capabilities. New block classes can be registered to the system using the class methods provided, enhancing the system's modularity and extensibility.

    :cvar blocks: A mapping of block names to their corresponding block class definitions.
    :vartype blocks: dict[str, type[Element]]
    """
    blocks: dict[str, type[Element]] = {}

    @classmethod
    def register_block(cls, block_cls: type[Element]) -> type[Element]:
        """
        Registers a new block type in the `blocks` registry.

        This method acts as a decorator for registering block classes. It raises a `ValueError` if a block class with the same name is already registered, preventing unintentional overwrites.

        :param block_cls: The block class to be registered.
        :type block_cls: type[Element]
        :return: The block class, facilitating use as a decorator.
        :rtype: type[Element]
        :raises ValueError: If a block with the same class name is already registered.
        """
        block_name = block_cls.__name__
        if block_name in cls.blocks:
            raise ValueError(f"Block type '{block_name}' is already defined.")
        cls.blocks[block_name] = block_cls
        return block_cls

    @classmethod
    def rewrite_block(cls, block_cls: type[Element]) -> type[Element]:
        """
        Registers or redefines a block type in the `blocks` registry.

        Unlike `register_block`, this method allows the redefinition of existing block types by overwriting them if necessary. It is used when an update or replacement for an existing block definition is required.

        :param block_cls: The block class to be registered or redefined.
        :type block_cls: type[Element]
        :return: The block class, enabling use as a decorator.
        :rtype: type[Element]
        """
        block_name = block_cls.__name__
        cls.blocks[block_name] = block_cls
        return block_cls


class BlockUnknown(Block):
    """
    Represents a block of an unrecognized or unknown type within a structured document.

    This class is used as a fallback for blocks that do not match any of the registered block types, allowing for generic handling of unknown or unstructured data.
    """

    def data(self) -> Data:
        """
        Warns about the unstructured nature of the block and returns its raw data encapsulated in a `Data` instance.

        This method is called when attempting to process an unknown block type, issuing a warning about the lack of a structured extraction process and suggesting contributions for handling such blocks.

        :return: A `Data` instance containing the block's raw data and a comment about its unstructured nature.
        :rtype: Data
        """
        logger.warning("The block looks unstructured. "
                       "Please contribute to the project if you have knowledge"
                       " on how to extract data from it.")
        return Data(data={'raw data': self.raw_data},
                    comment=("No procedure for analyzing the data found, furthermore, the block looks not structured `raw data` collected.\n"
                             "Please contribute to the project if you have knowledge on how to extract data from it."))
