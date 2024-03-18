import os
import re
import warnings
from typing import Dict, Optional, Type

import pandas as pd
from typing_extensions import Self

from .data import Data
from .elements import Block, Element
from .regex_settings import RegexSettings


class File:
    # Load default settings for all instances of OrcaFile.
    default_regex_settings: RegexSettings = RegexSettings()

    # Collect all available subclasses of OrcaElement for dynamic instantiation.
    available_types: Dict[str, Type[Element]] = {
        cls.__name__: cls for cls in (
            lambda f: (
                lambda x: x(x)
            )(
                lambda y: f(lambda *args: y(y)(*args))
            )
        )(
            lambda f: lambda cls: [
                cls] + [sub for c in cls.__subclasses__() for sub in f(c)]
        )(Element)
    }

    def __init__(self, file_path: str, regex_settings: Optional[RegexSettings] = None) -> None:
        """
        Initializes the OrcaFile instance.

        Args:
            file_path (str): Path to the file to be processed.
            regex_settings (Optional[RegexSettings]): Custom regex settings for pattern processing. Defaults to None.

        Attributes:
            file_path (str): Path to the input file.
            regex_settings (RegexSettings): Regex settings used for pattern processing.
            initialized (bool): Flag indicating whether the instance has been initialized.
            original_text (str): The original text read from the file.
            _blocks (pd.DataFrame): DataFrame containing processed elements.
            _marked_text (str): The text with markers after processing patterns.
        """
        self.file_path: str = file_path
        self.regex_settings: RegexSettings = regex_settings or File.default_regex_settings
        self.initialized: bool = False

        # Reading the content of the file.
        with open(self.file_path, "r") as file:
            self.original_text: str = file.read()

        # Initializing the DataFrame to store OrcaElements.
        self._blocks: pd.DataFrame = pd.DataFrame(
            columns=['Type', 'Subtype', 'Element', 'Position'])
        self._marked_text: str = self.original_text

    def get_structure(self) -> dict[Self, tuple | None]:
        '''
            Structure in a form of nested dict
        '''
        blocks = self.get_blocks()
        return [self, list(blocks['Element'].apply(lambda x: x.get_structure()))]

    def depth(self) -> int:
        return Element.max_depth(self.get_structure())

    def get_blocks(self) -> pd.DataFrame:
        """
        Returns the DataFrame containing all processed blocks.

        Ensures initialization has occurred before returning the blocks.

        Returns:
            pd.DataFrame: DataFrame containing the processed blocks.
        """
        self.initialize()
        return self._blocks

    def get_marked_text(self) -> str:
        """
        Returns the text with markers after processing patterns.

        Ensures initialization has occurred before returning the marked text.

        Returns:
            str: The marked text.
        """
        self.initialize()
        return self._marked_text

    def initialize(self) -> None:
        """
        Initializes the instance by processing patterns if not already done.

        This method sets `self.initialized` to True after processing to avoid redundant initializations.
        """
        if not self.initialized:
            self.process_patterns()
            self.initialized = True

    def process_patterns(self):
        """
        Processes the regex patterns defined in the OrcaFile's regex settings to identify, extract, and
        instantiate OrcaElements from the file's text. It updates the internal _blocks DataFrame with the
        extracted elements and their metadata, and replaces identified patterns in the text with unique markers.

        This method performs several steps:
        1. Resets the _blocks DataFrame to ensure it's ready for new data.
        2. Iterates over each regex pattern defined in the file's regex settings.
        3. Uses each pattern to search through the original text, identifying matches.
        4. For each match, extracts relevant data and uses it to instantiate the corresponding OrcaElement subclass.
        5. Generates a unique ID for each extracted element and uses it to replace the original text with a marker.
        6. Updates the _blocks DataFrame with new rows containing the element data, type, subtype, and its position within the text.
        7. Replaces identified patterns in the text with markers that include the type, subtype, and unique ID of the extracted elements.

        The method employs a nested function, replace_with_marker, which is called for each regex match. This function:
        - Extracts the necessary data from each match.
        - Handles potential issues such as marker overlap.
        - Generates a unique identifier for each element.
        - Instantiates OrcaElements or falls back to a default if necessary.
        - Updates the _blocks DataFrame and the marked text.

        Another nested function, find_substring_positions, is used to locate the position of each extracted element within the original text, aiding in accurate data extraction and element instantiation.

        Upon completion, the text is fully processed, with all elements identified and instantiated, and the original text is updated with markers indicating the positions of these elements.
        """
        self._blocks = pd.DataFrame(
            columns=['Type', 'Subtype', 'Element', 'Position'])
        self._marked_text = self.original_text
        self.initialized = True

        def replace_with_marker(match):

            def find_substring_positions(text, substring):
                # method to search for the block position in the original text
                positions = [(m.start(), m.end())
                             for m in re.finditer(re.escape(substring), text)]
                return positions
            # The entire matched text
            full_match = match.group(0)

            # The specific part you want to replace (previously match.group(1))
            extracted_text = match.group(1)

            if '<@%' in extracted_text or '%@>' in extracted_text:
                warnings.warn(
                    f'Attempt to replace the marker in {p_type, p_subtype}:{extracted_text}')
                return full_match

            if p_type == 'Block':

                # Find all positions of the extracted text in the original text
                positions = find_substring_positions(
                    self.original_text, extracted_text)

                if not positions:
                    warnings.warn(
                        f"No match found for the extracted text: '{extracted_text}' in the original text.")
                    position, start_index, end_index = None, None, None

                elif len(positions) > 1:
                    warnings.warn(
                        f"Multiple matches found for the extracted text: '{extracted_text}' in the original text. Using the first match.")
                    start_index, end_index = positions[0]
                else:
                    start_index, end_index = positions[0]

                if start_index is not None and end_index is not None:
                    start_line = self.original_text.count(
                        '\n', 0, start_index) + 1
                    end_line = self.original_text.count('\n', 0, end_index) + 1
                    # Tuple containing start and end lines
                    position = (start_line, end_line)

            # Dynamically instantiate the class based on p_subtype or fall back to OrcaDefaultBlock
            class_name = p_subtype  # Directly use p_subtype as class name
            if class_name in self.available_types:
                if p_type == "Block":
                    # Create an instance of the class, block have position parameter
                    element_instance = self.available_types[class_name](
                        extracted_text, position=position)
                else:
                    # Create an instance of the class, block have position parameter
                    element_instance = self.available_types[class_name](
                        extracted_text)

            else:
                if p_type == "Block":
                    # Fall back to OrcaDefaultBlock and raise a warning
                    warnings.warn(
                        (f"Subtype `{p_subtype}`"
                         f" not recognized. Falling back to OrcaBlock.")
                    )
                    element_instance = Block(
                        extracted_text, position=position)
                else:
                    # Handle other types or raise a generic warning
                    warnings.warn(
                        (f"Subtype `{p_subtype}`"
                         f" not recognized and type `{p_type}`"
                         f" does not have a default.")
                    )
                    element_instance = None

            if element_instance:
                unique_id = hash(element_instance)
                # Create a DataFrame for the new row
                new_row_df = pd.DataFrame({
                    'Type': [p_type],
                    'Subtype': [p_subtype],
                    'Element': [element_instance],
                    'Position': [position] if p_type == "Block" else [None]
                }, index=[unique_id])  # Set the index to the unique ID

                # Concatenate the new row DataFrame with the existing DataFrame
                self._blocks = pd.concat([self._blocks, new_row_df])

                # Replace the extracted text within the full match with the marker
                text_with_markers = full_match.replace(
                    extracted_text, f"<@%{p_type}|{p_subtype}|{unique_id}%@>"
                )

            else:
                text_with_markers = full_match

            return text_with_markers

        for regex in self.regex_settings.regexes:
            pattern = regex["pattern"]
            p_type = regex["p_type"]
            p_subtype = regex["p_subtype"]
            flag_names = regex["flags"]
            flags = 0
            for flag_name in flag_names:
                flags |= getattr(re, flag_name)
            compiled_pattern = re.compile(pattern, flags)
            self._marked_text = compiled_pattern.sub(
                replace_with_marker, self._marked_text)

    @staticmethod
    def extract_raw_data_errors_to_none(orca_element: Element) -> str | None:
        """
        Attempts to extract data from an OrcaElement, handling any errors by returning None.

        This nested function is designed to be applied to each row of the DataFrame, specifically to each
        OrcaElement in the 'Element' column. It encapsulates the error-handling logic, ensuring that any
        exceptions raised during data extraction are caught and processed appropriately.

        Parameters:
            orca_element (OrcaElement): An instance of OrcaElement from which data is to be extracted.

        Returns:
            The extracted data from the OrcaElement, or None if an error occurred during the extraction process.
        """
        try:
            # return Data(orca_element.data())
            return orca_element.raw_data
        except Exception as e:
            warnings.warn(
                f"An unexpected error occurred while extracting raw_data from {orca_element}: {e}, returning None instead of data.\n That is really weird")
            return None

    @staticmethod
    def extract_data_errors_to_none(orca_element: Element) -> Data | None:
        """
        Attempts to extract data from an OrcaElement, handling any errors by returning None.

        This nested function is designed to be applied to each row of the DataFrame, specifically to each
        OrcaElement in the 'Element' column. It encapsulates the error-handling logic, ensuring that any
        exceptions raised during data extraction are caught and processed appropriately.

        Parameters:
            orca_element (OrcaElement): An instance of OrcaElement from which data is to be extracted.

        Returns:
            The extracted data from the OrcaElement in orcaparse.Data format, or None if an error occurred during the extraction process.
        """
        try:
            # return Data(orca_element.data())
            return orca_element.data()
        except Exception as e:
            warnings.warn(
                f"An unexpected error occurred while extracting data from {orca_element}: {e}, returning None instead of data.\n Raw context of the element is {orca_element.raw_data}")
            return None

    def search_elements(self, element_type: type[Element] = None, readable_name: str = None, raw_data_substring: str = None) -> pd.DataFrame:
        """
        Searches for OrcaElement instances based on various criteria.

        Parameters:
            element_type (type[Element], optional): The class type of the OrcaElement to search for.
            readable_name (str, optional): The exact term to search for in the readable_name attribute.
            raw_data_substring (str, optional): The substring to search for within the raw_data attribute.

        Returns:
            pd.DataFrame: A DataFrame containing the filtered OrcaElements based on the provided criteria.
        """
        self.initialize()
        blocks_copy = self._blocks.copy()

        if element_type is not None:
            blocks_copy = blocks_copy[blocks_copy['Element'].apply(
                lambda x: isinstance(x, element_type))]

        if readable_name is not None:
            blocks_copy['ReadableName'] = blocks_copy['Element'].apply(
                lambda x: x.readable_name)
            blocks_copy = blocks_copy[blocks_copy['ReadableName']
                                      == readable_name]

        if raw_data_substring is not None:
            matches = blocks_copy['Element'].apply(
                lambda x: raw_data_substring in x.raw_data)
            blocks_copy = blocks_copy[matches]

        return blocks_copy

    def get_data(self, extract_raw: bool = False, element_type: type[Element] = None, readable_name: str = None, raw_data_substring: str = None) -> pd.DataFrame:
        """
        Retrieves and extracts data or raw data strings from OrcaElement instances based on specified search criteria and extraction type.

        This method first searches for OrcaElement instances based on the provided search criteria, which can include the element's type, readable name, or a substring of its raw data. After filtering the elements, it extracts either raw data strings or processed data from them, depending on the 'extract_raw' flag.

        Parameters:
            extract_raw (bool, optional): Determines the type of data to extract. If True, raw data strings are extracted. If False, processed data is extracted. Defaults to False.
            element_type (type[Element], optional): The class type of the OrcaElements to filter by. Only elements that are instances of this type or derived from it will be included. Defaults to None, which skips this filter.
            readable_name (str, optional): The exact name to match against the 'readable_name' attribute of OrcaElements. Only elements with a matching readable name are included. Defaults to None, which skips this filter.
            raw_data_substring (str, optional): A substring to search for within the 'raw_data' attribute of OrcaElements. Only elements whose raw data contains this substring are included. Defaults to None, which skips this filter.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted data or raw data strings from the filtered OrcaElements. The DataFrame includes an 'ExtractedData' column with the extracted information. If no elements match the search criteria, an empty DataFrame is returned.
        """
        blocks = self.search_elements(element_type=element_type,
                                      readable_name=readable_name, raw_data_substring=raw_data_substring)
        if extract_raw:
            # Implement the logic to extract raw data from blocks
            extracted_data = blocks['Element'].apply(
                lambda x: self.extract_raw_data_errors_to_none(x))
        else:
            # Implement the logic to extract processed data from blocks
            extracted_data = blocks['Element'].apply(
                lambda x: self.extract_data_errors_to_none(x))

        blocks['ExtractedData'] = extracted_data
        return blocks

    def create_html(self, css_content: str | None = None, js_content: str | None = None, insert_css: bool = True, insert_js: bool = True, insert_left_sidebar: bool = True, insert_colorcomment_sidebar: bool = True) -> str:
        """
        Generates a complete HTML document from the processed text, incorporating optional CSS and JavaScript content.

        This method operates in several key steps:
        1. It first ensures that CSS and JavaScript content are set, either to the provided arguments or to default values.
        2. The method then retrieves the processed text with markers using the `get_marked_text` method.
        3. A nested function `replace_marker_with_html` is defined to handle the replacement of each marker within the text
        with the corresponding HTML content generated from the associated OrcaElement. This function:
        - Extracts the type, subtype, and unique ID from each marker.
        - Retrieves the corresponding OrcaElement from the _blocks DataFrame using the unique ID.
        - Calls the `to_html` method on the OrcaElement to generate its HTML representation.
        4. A regular expression is used to find all markers in the processed text, and the `replace_marker_with_html` function
        is applied to replace each marker with its HTML content.
        5. The full HTML document is assembled using the provided or default CSS and JavaScript, along with the body content
        that now includes the HTML representations of the OrcaElements.

        Parameters:
            css_content (str | None): Optional CSS content to include in the <style> tag of the HTML document. If None,
                                    a default CSS content is used.
            js_content (str | None): Optional JavaScript content to include in a <script> tag at the end of the document.
                                    If None, default JavaScript content is used.

        Returns:
            str: A string containing the complete HTML document.

        Raises:
            Exception: If an OrcaElement referenced by a marker cannot be found in the _blocks DataFrame, an exception is raised.

        Note:
            The HTML document includes a structure with a container div, a sidebar for a table of contents (TOC),
            a comment sidebar for additional annotations, and a content area where the main body content is placed.
            The TOC and comment sidebar are expected to be populated by the provided JavaScript.
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
        processed_text = self.get_marked_text()

        # Function to replace markers with corresponding HTML
        def replace_marker_with_html(match: re.Match) -> str:
            """
            Generates a complete HTML document from the processed text, incorporating optional CSS and JavaScript content and conditional elements like sidebars.

            This method operates with several key steps and additional flexibility provided by boolean flags to include or exclude specific parts of the HTML structure:
            1. It first checks the 'insert_css' and 'insert_js' flags. If True, the method ensures that CSS and JavaScript content are set, either to the provided arguments or to default values.
            2. The method then retrieves the processed text with markers using the `get_marked_text` method.
            3. A nested function `replace_marker_with_html` is defined to handle the replacement of each marker within the text with the corresponding HTML content generated from the associated OrcaElement. This function extracts the type, subtype, and unique ID from each marker, retrieves the corresponding OrcaElement from the _blocks DataFrame using the unique ID, and calls the `to_html` method on the OrcaElement to generate its HTML representation.
            4. A regular expression is used to find all markers in the processed text, and the `replace_marker_with_html` function is applied to replace each marker with its HTML content.
            5. The full HTML document is assembled using the provided or default CSS and JavaScript, along with the body content that now includes the HTML representations of the OrcaElements. The inclusion of the left sidebar (TOC) and the color-comment sidebar is controlled by the 'insert_left_sidebar' and 'insert_colorcomment_sidebar' flags, respectively.

            Parameters:
                css_content (str | None): Optional CSS content to include in the <style> tag of the HTML document. If None and 'insert_css' is True, a default CSS content is used.
                js_content (str | None): Optional JavaScript content to include in a <script> tag at the end of the document. If None and 'insert_js' is True, default JavaScript content is used.
                insert_css (bool): Flag to determine whether CSS content (provided or default) should be included in the HTML document. Default is True.
                insert_js (bool): Flag to determine whether JavaScript content (provided or default) should be included at the end of the HTML document. Default is True.
                insert_left_sidebar (bool): Flag to determine whether a left sidebar for the Table of Contents (TOC) should be included in the HTML document. Default is True.
                insert_colorcomment_sidebar (bool): Flag to determine whether a comment sidebar for additional annotations should be included in the HTML document. Default is True.

            Returns:
                str: A string containing the complete HTML document.

            Raises:
                Exception: If an OrcaElement referenced by a marker cannot be found in the _blocks DataFrame, an exception is raised.

            Note:
                The HTML document includes a structure with a container div, optionally a sidebar for a table of contents (TOC), optionally a comment sidebar for additional annotations, and a content area where the main body content is placed. The TOC and comment sidebar are populated by the provided JavaScript if included.
            """
            # Extract pattern type, subtype, and unique ID from the marker
            p_type, p_subtype, unique_id = match.groups()
            unique_id = int(unique_id)

            # Retrieve the corresponding OrcaElement
            if unique_id in self._blocks.index:
                element: Element = self._blocks.loc[unique_id, 'Element']
                # Convert the OrcaElement to HTML
                return element.to_html()
            else:
                raise IndexError(f'Failed to find the element {unique_id}')

        # Use a regex to find and replace all markers in the processed text
        marker_regex = re.compile(r'<@%([^|]+)\|([^|]+)\|([^%]+)%@>')
        body_content = marker_regex.sub(
            replace_marker_with_html, processed_text)

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
            html_content += "            <div class=\"toc\">\n                <h2>TOC</h2>\n                <!-- JavaScript will populate this area -->\n            </div>\n"
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

    def save_as_html(self, output_file_path: str, insert_css: bool = True, insert_js: bool = True, insert_left_sidebar: bool = True, insert_colorcomment_sidebar: bool = True):
        """
        Generates an HTML document from the OrcaFile instance with customizable options and saves it to the specified file path.

        This method performs the following actions:
        1. Calls the `create_html` method to generate the complete HTML content based on the processed text, optional CSS and JavaScript content, and conditional inclusion of the left sidebar (TOC) and the color-comment sidebar. The `create_html` method assembles the HTML document, incorporating the specified elements and transforms markers within the text into corresponding HTML elements.
        2. Opens the specified output file in write mode. If the file does not exist, it will be created; if it already exists, its content will be overwritten.
        3. Writes the generated HTML content to the file, effectively saving the entire content of the OrcaFile instance as an HTML document at the specified location.

        Parameters:
            output_file_path (str): The file path where the HTML document should be saved. This path includes the file name and extension, for example, 'output/document.html'.
            insert_css (bool, optional): Specifies whether CSS content should be included in the HTML document. Defaults to True.
            insert_js (bool, optional): Specifies whether JavaScript content should be included in the HTML document. Defaults to True.
            insert_left_sidebar (bool, optional): Specifies whether a left sidebar for the Table of Contents (TOC) should be included in the HTML document. Defaults to True.
            insert_colorcomment_sidebar (bool, optional): Specifies whether a comment sidebar for additional annotations should be included in the HTML document. Defaults to True.

        Note:
            This method provides a flexible way to export the content of an OrcaFile instance to a standard HTML format, making it accessible for viewing in web browsers or for further processing with tools that accept HTML input. It allows for the customization of the exported HTML document through parameters that control the inclusion of CSS, JavaScript, and additional structural elements like sidebars.
        """
        html_content = self.create_html(insert_css=insert_css, insert_js=insert_js,
                                        insert_left_sidebar=insert_left_sidebar, insert_colorcomment_sidebar=insert_colorcomment_sidebar)

        with open(output_file_path, 'w') as output_file:
            output_file.write(html_content)
