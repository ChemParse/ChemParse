import os
import re
from typing import Optional

import pandas as pd
from typing_extensions import Iterable, Self

from .data import Data
from .elements import BlockUnknown, Element
from .logging_config import logger
from .regex_settings import (DEFAULT_GPAW_REGEX_SETTINGS,
                             DEFAULT_ORCA_REGEX_SETTINGS, RegexSettings)


class File:
    """
    Manages the processing of a file within the OrcaParser framework.

    This class is responsible for parsing a given file, identifying and extracting elements based on predefined regex patterns, and facilitating the generation of an HTML representation of the file's content.

    :ivar file_path: The path to the input file being processed.
    :vartype file_path: str
    :ivar regex_settings: The regex settings utilized for pattern processing within the file.
    :vartype regex_settings: RegexSettings
    :ivar initialized: A flag indicating whether the instance has been properly initialized with file content and regex settings.
    :vartype initialized: bool
    :ivar original_text: The original textual content read from the file.
    :vartype original_text: str
    :ivar _blocks: A DataFrame storing the processed elements identified within the file.
    :vartype _blocks: pd.DataFrame
    :ivar _marked_text: A list of marked text segments, each containing character and line positions alongside the corresponding text or Element object.
    :vartype _marked_text: list[tuple[tuple[int, int], tuple[int, int], str | Element]]
    :ivar mode: The operational mode of the file, which may affect regex settings and processing behavior. Common modes include 'ORCA' and 'GPAW'.
    :vartype mode: str

    :param file_path: The path to the file to be processed.
    :type file_path: str
    :param regex_settings: Custom regex settings for pattern processing. If not provided, default settings based on the specified mode will be used.
    :type regex_settings: Optional[RegexSettings], optional
    :param mode: The processing mode, influencing default regex settings and behavior. Supported modes include 'ORCA' and 'GPAW'.
    :type mode: Optional[str], optional
    :raises ValueError: If an invalid mode is specified.
    """

    def __init__(self, file_path: str, regex_settings: Optional[RegexSettings | None] = None, mode: Optional[str] = 'ORCA') -> None:
        """
        Initializes a `File` instance for processing.

        :param file_path: The path to the file to be processed.
        :type file_path: str
        :param regex_settings: Custom regex settings for pattern processing. If not provided, default settings based on the specified mode will be used.
        :type regex_settings: Optional[RegexSettings], optional
        :param mode: The processing mode, influencing default regex settings and behavior. Supported modes include 'ORCA' and 'GPAW'.
        :type mode: Optional[str], optional
        :raises ValueError: If an invalid mode is specified.
        """
        self.mode: str = mode

        if regex_settings is None:
            if mode == 'ORCA':
                self.regex_settings: RegexSettings = DEFAULT_ORCA_REGEX_SETTINGS
            elif mode == 'GPAW':
                self.regex_settings: RegexSettings = DEFAULT_GPAW_REGEX_SETTINGS
            else:
                raise ValueError(
                    f"Invalid mode '{mode}'. Must be 'ORCA' or 'GPAW'.")
        else:
            self.regex_settings: RegexSettings = regex_settings

        self.initialized: bool = False

        # Reading the content of the file.
        with open(file_path, "r") as file:
            self.original_text: str = file.read()

        # Initializing the DataFrame to store elements.
        self._blocks: pd.DataFrame = pd.DataFrame(
            columns=['Type', 'Subtype', 'Element', 'CharPosition', 'LinePosition'])

        self._marked_text: list[tuple[tuple[int, int], tuple[int, int], str | Element]] = [
            ((0, len(self.original_text)),
             (1, self.original_text.count('\n') + 1), self.original_text)
        ]

    def get_structure(self) -> dict[Self, list]:
        """
        Retrieves the hierarchical structure of the `File` instance, representing the organization of processed elements.

        :return: A dictionary mapping the `File` instance to a list of its elements' structures.
        :rtype: dict[Self, list]
        """
        blocks = self.get_blocks()
        return {self: list(blocks['Element'].apply(lambda x: x.get_structure()))}

    def depth(self) -> int:
        """
        Calculates the maximum depth of nested structures within the `File` instance.

        :return: The maximum depth of nested elements' structures.
        :rtype: int
        """
        return Element.max_depth(self.get_structure())

    def get_blocks(self, show_progress: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieves all processed blocks as a DataFrame, ensuring the file has been initialized.

        :param show_progress: Optionally displays a progress bar during initialization.
        :type show_progress: Optional[bool], optional
        :return: A DataFrame containing processed blocks with their metadata.
        :rtype: pd.DataFrame
        """
        self.initialize(show_progress=show_progress)
        return self._blocks

    def get_marked_text(self, show_progress: Optional[bool] = False) -> list[tuple[tuple[int, int], tuple[int, int], str | Element]]:
        """
        Retrieves the text segments with associated markers after processing patterns, ensuring the file has been initialized.

        :param show_progress: Optionally displays a progress bar during initialization.
        :type show_progress: Optional[bool], optional
        :return: A list of text segments marked with their character and line positions, alongside the corresponding text or `Element` object.
        :rtype: list[tuple[tuple[int, int], tuple[int, int], str | Element]]
        """
        self.initialize(show_progress=show_progress)
        return self._marked_text

    def initialize(self, show_progress: Optional[bool] = False) -> None:
        """
        Initializes the `File` instance by processing patterns, if not already done, to identify and categorize text segments.

        :param show_progress: Optionally displays a progress bar during the pattern processing phase.
        :type show_progress: Optional[bool], optional
        """
        if not self.initialized:
            self.process_patterns(show_progress=show_progress)
            self.initialized = True

    def process_patterns(self, show_progress: Optional[bool] = False) -> None:
        """
        Identifies and categorizes text segments based on predefined regex patterns, updating the internal storage of blocks and marked text.

        :param show_progress: Optionally displays a progress bar during the processing of regex patterns.
        :type show_progress: Optional[bool], optional
        """
        # Resetting the blocks and marked text to ensure a clean state
        self._blocks = pd.DataFrame(
            columns=['Type', 'Subtype', 'Element', 'CharPosition', 'LinePosition'])
        self._marked_text: list[tuple[tuple[int, int], tuple[int, int], str | Element]] = [
            ((0, len(self.original_text)),
             (1, self.original_text.count('\n') + 1), self.original_text)
        ]

        # Processing each regex pattern and updating blocks and marked text
        for regex in self.regex_settings.to_list():
            self._marked_text, new_blocks = regex.apply(
                self._marked_text, mode=self.mode, show_progress=show_progress)
            new_blocks_df = pd.DataFrame.from_dict(new_blocks, orient="index")
            new_blocks_df['Type'] = regex.p_type
            new_blocks_df['Subtype'] = regex.p_subtype
            self._blocks = pd.concat([self._blocks, new_blocks_df])

        # Handling unknown blocks
        unknown_blocks = {}
        for i, (char_position, line_position, block) in enumerate(self._marked_text):
            if isinstance(block, str):
                unknown_block = BlockUnknown(
                    block, char_position=char_position, line_position=line_position)
                self._marked_text[i] = (
                    char_position, line_position, unknown_block)
                unknown_blocks[hash(unknown_block)] = {
                    'Element': unknown_block, 'CharPosition': char_position, 'LinePosition': line_position}

        unknown_blocks_df = pd.DataFrame.from_dict(
            unknown_blocks, orient="index")
        unknown_blocks_df['Type'] = 'Block'
        unknown_blocks_df['Subtype'] = 'BlockUnknown'

        self._blocks = pd.concat([self._blocks, unknown_blocks_df])

    @staticmethod
    def extract_raw_data_errors_to_none(orca_element: Element) -> str | None:
        """
        Tries to extract raw data from an `Element`, returning `None` in case of errors.

        This method is designed to handle errors gracefully during the extraction of raw data from an `Element`. If an error occurs, a warning is issued and `None` is returned.

        :param orca_element: An instance of `Element` from which raw data is to be extracted.
        :type orca_element: Element
        :return: The extracted raw data from the `Element`, or `None` if an error occurred.
        :rtype: str | None
        """
        try:
            return orca_element.raw_data
        except Exception as e:
            logger.warning(
                f"An unexpected error occurred while extracting raw_data from {orca_element}: {e}, returning None instead of data.\n That is really weird")
            return None

    @staticmethod
    def extract_data_errors_to_none(orca_element: Element) -> Data | None:
        """
        Tries to extract data from an `Element`, handling errors by returning `None`.

        This method encapsulates error handling during data extraction from an `Element`. If an error occurs, the issue is logged, and `None` is returned.

        :param orca_element: An `Element` instance from which data is to be extracted.
        :type orca_element: Element
        :return: The extracted data in `Data` format from the `Element`, or `None` if an error occurred.
        :rtype: Data | None
        """
        try:
            return orca_element.data()
        except Exception as e:
            logger.warning(
                f"An unexpected error occurred while extracting data from {orca_element}: {e}. Returning None.")
            return None

    def search_elements(self, element_type: type[Element] | None = None, readable_name: str | None = None, raw_data_substring: str | Iterable[str] | None = None, raw_data_not_substring: str | Iterable[str] | None = None, show_progress: bool = False) -> pd.DataFrame:
        """
        Searches for `Element` instances based on specified criteria, such as element type, readable name, and raw data content.

        :param element_type: The class type of `Element` to search for, if filtering by type.
        :type element_type: type[Element] | None, optional
        :param readable_name: The exact term to search for in the `readable_name` attribute of `Element`.
        :type readable_name: str | None, optional
        :param raw_data_substring: The substring(s) to search for within the `raw_data` attribute of `Element`.
        :type raw_data_substring: str | Iterable[str] | None, optional
        :param raw_data_not_substring: The substring(s) whose absence within the `raw_data` attribute is required.
        :type raw_data_not_substring: str | Iterable[str] | None, optional
        :param show_progress: Whether to display a progress bar during initialization.
        :type show_progress: bool, optional
        :return: A DataFrame containing filtered `Element` instances based on the provided criteria.
        :rtype: pd.DataFrame
        """
        self.initialize(show_progress=show_progress)
        blocks_copy = self._blocks.copy()
        blocks_copy['ReadableName'] = blocks_copy['Element'].apply(
            lambda x: x.readable_name())
        blocks_copy['RawData'] = blocks_copy['Element'].apply(
            lambda x: self.extract_raw_data_errors_to_none(x))

        if element_type is not None and len(blocks_copy) > 0:
            blocks_copy = blocks_copy[blocks_copy['Element'].apply(
                lambda x: isinstance(x, element_type))]

        if readable_name is not None and len(blocks_copy) > 0:

            blocks_copy = blocks_copy[blocks_copy['ReadableName']
                                      == readable_name]

        if raw_data_substring is not None and len(blocks_copy) > 0:
            def contains_all_substrings(x_raw_data, substrings):
                # If substrings is a string, convert it to a list for uniformity
                if isinstance(substrings, str):
                    substrings = [substrings]

                # Check if all elements in substrings are in x_raw_data
                return all(substring in x_raw_data for substring in substrings)

            # Filter rows where all substrings are present in the RawData
            matches = blocks_copy['RawData'].apply(
                lambda x: contains_all_substrings(x, raw_data_substring))
            blocks_copy = blocks_copy[matches]

        if raw_data_not_substring is not None and len(blocks_copy) > 0:
            def contains_no_substrings(x_raw_data, substrings):
                # If substrings is a string, convert it to a list for uniformity
                if isinstance(substrings, str):
                    substrings = [substrings]

                # Check if all elements in substrings are not in x_raw_data
                return all(substring not in x_raw_data for substring in substrings)

            # Filter rows where all substrings are not present in the RawData
            matches = blocks_copy['RawData'].apply(
                lambda x: contains_no_substrings(x, raw_data_not_substring))
            blocks_copy = blocks_copy[matches]

        return blocks_copy

    def get_data(self, extract_only_raw: Optional[bool] = False,
                 element_type: Optional[type[Element] | None] = None,
                 readable_name: Optional[str | None] = None,
                 raw_data_substring: Optional[str |
                                              Iterable[str] | None] = None,
                 raw_data_not_substring: Optional[str |
                                                  Iterable[str] | None] = None,
                 show_progress: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieves and extracts data from `Element` instances based on search criteria, with an option to extract raw or processed data.

        :param extract_only_raw: If True, only raw data will be extracted, bypassing any custom data extraction logic defined in `Element` subclasses.
        :type extract_only_raw: Optional[bool], optional
        :param element_type: The type of `Element` to filter by; only elements of this type will be considered.
        :type element_type: Optional[type[Element]], optional
        :param readable_name: A filter for elements that have this exact `readable_name`.
        :type readable_name: Optional[str], optional
        :param raw_data_substring: A filter for elements whose `raw_data` contains this substring.
        :type raw_data_substring: Optional[str | Iterable[str]], optional
        :param raw_data_not_substring: A filter for elements whose `raw_data` does not contain this substring.
        :type raw_data_not_substring: Optional[str | Iterable[str]], optional
        :param show_progress: If True, displays a progress bar during the operation.
        :type show_progress: Optional[bool], optional
        :return: A DataFrame of the filtered elements with their extracted data.
        :rtype: pd.DataFrame
        """
        blocks = self.search_elements(element_type=element_type,
                                      readable_name=readable_name,
                                      raw_data_substring=raw_data_substring,
                                      raw_data_not_substring=raw_data_not_substring,
                                      show_progress=show_progress)
        if not extract_only_raw:
            # Implement the logic to extract processed data from blocks
            extracted_data = blocks['Element'].apply(
                lambda x: self.extract_data_errors_to_none(x))
            blocks['ExtractedData'] = extracted_data
        return blocks

    def create_html(self, css_content: Optional[str | None] = None,
                    js_content: Optional[str | None] = None,
                    insert_css: Optional[bool] = True,
                    insert_js: Optional[bool] = True,
                    insert_left_sidebar: Optional[bool] = True,
                    insert_colorcomment_sidebar: Optional[bool] = True,
                    show_progress: Optional[bool] = False) -> str:
        """
        Constructs a complete HTML document from processed text, integrating optional CSS and JavaScript content.

        :param css_content: Custom CSS to be included in the HTML document. Defaults to predefined CSS if not provided.
        :type css_content: Optional[str], optional
        :param js_content: Custom JavaScript to be included in the HTML document. Defaults to predefined JavaScript if not provided.
        :type js_content: Optional[str], optional
        :param insert_css: Determines whether to include CSS content in the HTML document.
        :type insert_css: Optional[bool], optional
        :param insert_js: Determines whether to include JavaScript content in the HTML document.
        :type insert_js: Optional[bool], optional
        :param insert_left_sidebar: Specifies whether to include a left sidebar for the Table of Contents (TOC) in the HTML document.
        :type insert_left_sidebar: Optional[bool], optional
        :param insert_colorcomment_sidebar: Specifies whether to include a comment sidebar for additional annotations in the HTML document.
        :type insert_colorcomment_sidebar: Optional[bool], optional
        :param show_progress: Specifies whether to display a progress bar during operation.
        :type show_progress: Optional[bool], optional
        :return: The complete HTML document as a string.
        :rtype: str
        """
        if css_content is None:
            # Get the directory of this file
            directory = os.path.dirname(__file__)
            # Construct the path to default.css
            css_file = os.path.join(directory, 'default.css')
            with open(css_file, "r") as file:
                css_content = file.read()

        if js_content is None:
            # Get the directory of this file
            directory = os.path.dirname(__file__)
            # Construct the path to default.js
            js_file = os.path.join(directory, 'default.js')
            with open(js_file, "r") as file:
                js_content = file.read()

        # Process the text to ensure all elements are captured
        processed_text = self.get_marked_text(show_progress=show_progress)

        body_content = ''.join(element[2].to_html()
                               for element in processed_text)

        # Construct the full HTML Document with CSS and JS if requested
        html_content = "<!DOCTYPE html>\n"
        html_content += "<html lang=\"en\">\n<head>\n"
        html_content += "    <meta charset=\"UTF-8\">\n"
        html_content += "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        html_content += "    <title>ORCA</title>\n"

        if insert_css:
            html_content += "    <style>\n        " + \
                (css_content if css_content else "") + "\n    </style>\n"

        html_content += "</head>\n<body>\n"
        html_content += "    <div class=\"container\">\n"

        if insert_left_sidebar:
            html_content += "        <div class=\"sidebar\">\n"
            html_content += "            <!-- Left sidebar content (TOC) -->\n"
            html_content += "            <div class=\"toc\">\n    <!-- JavaScript will populate this area -->\n</div>"
            html_content += "        </div>\n"

        if insert_colorcomment_sidebar:
            html_content += "        <div class=\"comment-sidebar\">\n"
            html_content += "            <!-- comment sidebar for color-comment sections -->\n"
            html_content += "            <!-- JavaScript will populate this area -->\n        </div>\n"

        html_content += "        <div class=\"content\">\n            " + \
            body_content + "\n        </div>\n"
        html_content += "    </div>\n"

        if insert_js:
            html_content += "    <script>\n        " + \
                (js_content if js_content else "") + "\n    </script>\n"

        html_content += "</body>\n</html>"

        return html_content

    def save_as_html(self, output_file_path: str,
                     insert_css: Optional[bool] = True,
                     insert_js: Optional[bool] = True,
                     insert_left_sidebar: Optional[bool] = True,
                     insert_colorcomment_sidebar: Optional[bool] = True,
                     show_progress: Optional[bool] = False):
        """
        Generates and saves an HTML document based on the processed content of the `File` instance, with customizable display options.

        This method leverages `create_html` to construct the HTML content, including optional CSS and JavaScript, as well as sidebars for navigation and comments. The complete HTML is then saved to the specified file path.

        :param output_file_path: The file path, including the name and extension, where the HTML document will be saved. Existing files will be overwritten.
        :type output_file_path: str
        :param insert_css: If True, includes CSS content in the HTML document for styling. Defaults to True.
        :type insert_css: Optional[bool], optional
        :param insert_js: If True, includes JavaScript content in the HTML document for interactivity. Defaults to True.
        :type insert_js: Optional[bool], optional
        :param insert_left_sidebar: If True, includes a left sidebar in the HTML document, typically used for a Table of Contents (TOC). Defaults to True.
        :type insert_left_sidebar: Optional[bool], optional
        :param insert_colorcomment_sidebar: If True, includes a sidebar for additional annotations or comments in the HTML document. Defaults to True.
        :type insert_colorcomment_sidebar: Optional[bool], optional
        :param show_progress: If True, displays a progress indicator during the HTML content generation process. Defaults to False.
        :type show_progress: Optional[bool], optional

        Note:
            This method allows exporting the processed content to an HTML format, facilitating viewing in web browsers or further processing with HTML-compatible tools. The inclusion of CSS and JavaScript enhances the document's appearance and interactivity, while optional sidebars provide navigation and annotation capabilities.
        """
        html_content = self.create_html(insert_css=insert_css, insert_js=insert_js,
                                        insert_left_sidebar=insert_left_sidebar, insert_colorcomment_sidebar=insert_colorcomment_sidebar, show_progress=show_progress)

        with open(output_file_path, 'w') as output_file:
            output_file.write(html_content)
