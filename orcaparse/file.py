import os
import re
import warnings
from typing import Dict, Optional, Type

import pandas as pd
from typing_extensions import Self

from .data import Data
from .elements import Block, Element
from .regex_settings import RegexSettings


class Data:
    def __init__(self, data) -> None:
        self.data = data


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

    def search_elements_by_type(self, element_type: type[Element]) -> pd.DataFrame:
        """
        Searches for OrcaElement instances by their type.

        This method filters the elements based on the specified type and returns a new DataFrame containing
        only the elements that are instances of the specified type.

        Parameters:
            element_type (type[OrcaElement]): The class type of the OrcaElement to search for.

        Returns:
            pd.DataFrame: A new DataFrame containing the filtered OrcaElements.
        """
        self.initialize()

        # Create a copy of the _blocks DataFrame to avoid modifying the original.
        blocks_copy = self._blocks.copy()

        # Filter the DataFrame for rows where the 'Element' column instances are of the specified type.
        filtered_blocks = blocks_copy[blocks_copy['Element'].apply(
            lambda x: isinstance(x, element_type))]

        return filtered_blocks

    def search_elements_by_readable_name(self, search_term: str) -> pd.DataFrame:
        """
        Searches for OrcaElement instances by their readable_name.

        This method filters the elements based on the exact match of the readable_name attribute and returns
        a new DataFrame containing only the elements that match the search term.

        Parameters:
            search_term (str): The exact term to search for in the readable_name attribute of each OrcaElement.

        Returns:
            pd.DataFrame: A new DataFrame containing the filtered OrcaElements.
        """
        self.initialize()

        # Create a copy of the _blocks DataFrame to avoid modifying the original.
        blocks_copy = self._blocks.copy()

        blocks_copy['ReadableName'] = blocks_copy['Element'].apply(
            lambda x: x.readable_name)

        # Filter the DataFrame copy to include only those rows where the ReadableName column matches the search term exactly.
        filtered_blocks = blocks_copy[blocks_copy['ReadableName']
                                      == search_term]

        return filtered_blocks

    def search_elements_by_raw_data(self, substring: str) -> pd.DataFrame:
        """
        Searches for OrcaElement instances based on a substring of their raw_data.

        This method filters the elements based on the presence of the specified substring within the raw_data attribute
        and returns a new DataFrame containing only the elements that contain the substring.

        Parameters:
            substring (str): The substring to search for within the raw_data of each OrcaElement.

        Returns:
            pd.DataFrame: A new DataFrame containing the filtered OrcaElements.
        """
        self.initialize()

        # Create a copy of the _blocks DataFrame to avoid modifying the original.
        blocks_copy = self._blocks.copy()

        # Use the DataFrame's apply method on the 'Element' column to check if the substring is in the raw_data of each element.
        matches = blocks_copy['Element'].apply(
            lambda x: substring in x.raw_data)

        # Filter the DataFrame copy using the boolean Series to get only the rows where the condition is True.
        filtered_blocks = blocks_copy[matches]

        return filtered_blocks

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

    def _extract_raw_data_with_errors_handled(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes and extracts data from OrcaElement instances within a DataFrame, handling any errors gracefully.

        This method iterates over each OrcaElement in the 'Element' column of the provided DataFrame. It attempts
        to extract data from each element using the element's raw_data . If an error occurs during this process,
        a warning is issued, and None is returned for that element's extracted data. This approach ensures that a
        single problematic element does not halt the entire data extraction process for all elements.

        Parameters:
            df (pd.DataFrame): A DataFrame containing OrcaElement instances in its 'Element' column. This DataFrame
            is expected to be a copy or a subset of the main _blocks DataFrame of the OrcaFile instance, tailored
            to specific needs such as filtering by type or attributes.

        Returns:
            pd.DataFrame: The same DataFrame passed as input, but with an additional column named 'ExtractedData'.
            This column contains the data extracted from each OrcaElement. In cases where data extraction was
            unsuccessful, the corresponding entry in the 'ExtractedData' column will be None.

        Note:
            The method ensures the OrcaFile instance is initialized by calling `self.initialize()` before proceeding
            with data extraction. This is crucial to ensure that all necessary preprocessing has been completed.
        """

        self.initialize()
        df['ExtractedData'] = df['Element'].apply(
            self.extract_raw_data_errors_to_none)

        return df

    def _extract_data_with_errors_handled(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes and extracts data from OrcaElement instances within a DataFrame, handling any errors gracefully.

        This method iterates over each OrcaElement in the 'Element' column of the provided DataFrame. It attempts
        to extract data from each element using the element's `data()` method. If an error occurs during this process,
        a warning is issued, and None is returned for that element's extracted data. This approach ensures that a
        single problematic element does not halt the entire data extraction process for all elements.

        Parameters:
            df (pd.DataFrame): A DataFrame containing OrcaElement instances in its 'Element' column. This DataFrame
            is expected to be a copy or a subset of the main _blocks DataFrame of the OrcaFile instance, tailored
            to specific needs such as filtering by type or attributes.

        Returns:
            pd.DataFrame: The same DataFrame passed as input, but with an additional column named 'ExtractedData'.
            This column contains the data extracted from each OrcaElement. In cases where data extraction was
            unsuccessful, the corresponding entry in the 'ExtractedData' column will be None.

        Note:
            The method ensures the OrcaFile instance is initialized by calling `self.initialize()` before proceeding
            with data extraction. This is crucial to ensure that all necessary preprocessing has been completed.
        """

        self.initialize()
        # df['ExtractedData'] = pd.Series([extract_data_errors_to_none(
        #     element) for element in df['Element']], dtype='object')
        df['ExtractedData'] = df['Element'].apply(
            self.extract_data_errors_to_none)

        return df

    def get_raw_data(self) -> pd.DataFrame:
        """
        Retrieves raw data strings from all elements within the file, focusing on data integrity and error resilience.

        The method encompasses the following steps:
        1. Invokes self.initialize() to ensure the file instance is adequately prepared for raw data retrieval, which includes processing necessary patterns and populating the internal DataFrame with element instances.
        2. Operates on a copy of the internal DataFrame to prevent any changes to the original data, thus maintaining its integrity throughout the process.
        3. Employs self._extract_raw_data_with_errors_handled on the duplicated DataFrame to extract raw data strings from each element. This procedure is designed to handle any extraction errors with grace, issuing warnings for troubled elements and continuing the extraction process uninterrupted.
        4. Constructs and returns a new DataFrame that houses the raw data strings for each element, potentially along with additional metadata gleaned during the extraction phase. This DataFrame provides a clear and comprehensive view of the raw data within the file.

        Returns:
            pd.DataFrame: A new DataFrame containing raw data strings for each element, supplemented with any relevant metadata. Entries for elements from which raw data could not be retrieved will be marked as None, ensuring the dataset's completeness and clarity.
        """
        self.initialize()
        return self._extract_raw_data_with_errors_handled(self._blocks.copy())

    def get_data(self) -> pd.DataFrame:
        """
        Retrieves and processes data from all elements within the file, ensuring data integrity and robust error handling.

        The method executes several critical steps:
        1. Initializes the file instance via self.initialize(), setting up the necessary environment for data handling by preparing patterns and populating the internal DataFrame with element instances.
        2. Works on a duplicate of the internal DataFrame to safeguard the original data against any inadvertent modifications during processing, thus preserving data integrity.
        3. Utilizes self._extract_data_with_errors_handled on the cloned DataFrame to methodically extract data from each element. This function is designed to gracefully manage any extraction errors by issuing warnings and returning None for the affected elements, thereby ensuring continuity in data processing.
        4. Compiles and returns a DataFrame comprising extracted data for each element, augmented with additional metadata as processed by the extraction function. This resulting DataFrame serves as a comprehensive aggregation of the processed data.

        Returns:
            pd.DataFrame: A compilation of extracted data from each element within the file, enhanced with relevant metadata. Entries corresponding to elements from which data could not be extracted will contain None, ensuring clarity and completeness of the processed data.
        """
        self.initialize()
        return self._extract_data_with_errors_handled(self._blocks.copy())

    def get_raw_data_by_type(self, element_type: type[Element]) -> pd.DataFrame:
        """
        Filters OrcaElement instances by their type and extracts raw data strings from the matching elements.

        This method operates in two main steps:
        1. It first utilizes the `search_elements_by_type` method to filter out the elements that are instances
        of the specified type. Only elements that are exactly of the provided `element_type` or are derived from it
        will be considered a match.
        2. After obtaining a DataFrame of filtered elements, it then extracts raw data strings from these elements using the
        `_extract_raw_data_with_errors_handled` method. This step ensures that raw data is extracted in a robust manner,
        with any errors encountered during the extraction process being handled gracefully. Specifically, if an
        error occurs while extracting raw data from an element (due to unexpected data formats, missing information,
        or any other issue), a warning is issued, and None is returned for that element's raw data. This approach ensures
        that the presence of problematic elements does not prevent the extraction of raw data from other, non-problematic elements.

        Parameters:
            element_type (type[Element]): The type of OrcaElement to search for. Elements that are instances of this type
                                        or are derived from this type will be included in the raw data extraction process.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted raw data strings from the filtered OrcaElements. Each row corresponds
                        to one of the filtered elements, and there is an 'ExtractedRawData' column that contains the raw data string
                        extracted from each element. If raw data extraction was unsuccessful for any element (due to errors),
                        the corresponding entry in the 'ExtractedRawData' column will be None.

        """
        filtered_blocks = self.search_elements_by_type(element_type)
        return self._extract_raw_data_with_errors_handled(filtered_blocks)

    def get_data_by_type(self, element_type: type[Element]) -> pd.DataFrame:
        """
        Filters OrcaElement instances by their type and extracts data from the matching elements.

        This method operates in two main steps:
        1. It first utilizes the `search_elements_by_type` method to filter out the elements that are instances
        of the specified type. Only elements that are exactly of the provided `element_type` or are derived from it
        will be considered a match.
        2. After obtaining a DataFrame of filtered elements, it then extracts data from these elements using the
        `_extract_data_with_errors_handled` method. This step ensures that data is extracted in a robust manner,
        with any errors encountered during the extraction process being handled gracefully. Specifically, if an
        error occurs while extracting data from an element (due to unexpected data formats, missing information,
        or any other issue), a warning is issued, and None is returned for that element's data. This approach ensures
        that the presence of problematic elements does not prevent the extraction of data from other, non-problematic elements.

        Parameters:
            element_type (type[Element]): The type of OrcaElement to search for. Elements that are instances of this type
                                        or are derived from this type will be included in the data extraction process.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted data from the filtered OrcaElements. Each row corresponds
                        to one of the filtered elements, and there is an 'ExtractedData' column that contains the data
                        extracted from each element in orcaparse.Data format. If data extraction was unsuccessful for any element (due to errors),
                        the corresponding entry in the 'ExtractedData' column will be None.

        """
        filtered_blocks = self.search_elements_by_type(element_type)
        return self._extract_data_with_errors_handled(filtered_blocks)

    def get_raw_data_by_readable_name(self, search_term: str) -> pd.DataFrame:
        """
        Retrieves raw data strings for OrcaElement instances based on their readable_name.

        This method filters elements by matching their readable_name attribute with the provided search term and extracts raw data strings from these elements, preserving the original _blocks DataFrame integrity.

        Parameters:
            search_term (str): The exact term to match against the readable_name attribute of each OrcaElement.

        Returns:
            pd.DataFrame: A DataFrame containing the raw data strings from the filtered OrcaElements. If no elements match the search term, an empty DataFrame is returned.
        """
        # Filter _blocks by readable_name.
        filtered_blocks = self.search_elements_by_readable_name(search_term)

        # Extract raw data strings from the filtered elements.
        return self._extract_raw_data_with_errors_handled(filtered_blocks)

    def get_data_by_readable_name(self, search_term: str) -> pd.DataFrame:
        """
        Retrieves data for OrcaElement instances by their readable_name.

        This method filters elements based on their readable_name and extracts data from the matching elements,
        without altering the original _blocks DataFrame.

        Parameters:
            search_term (str): The exact term to search for in the readable_name attribute of each OrcaElement.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted data from the filtered OrcaElements. If no elements are found, returns an empty DataFrame.
        """
        # Use the search method to get a filtered copy of _blocks.
        filtered_blocks = self.search_elements_by_readable_name(search_term)

        # Extract data from the filtered elements.
        return self._extract_data_with_errors_handled(filtered_blocks)

    def get_raw_data_by_raw_data(self, substring: str) -> pd.DataFrame:
        """
        Retrieves raw data strings from OrcaElement instances by searching for a specified substring within their raw data.

        This method involves two main steps:
        1. Utilizing the `search_elements_by_raw_data` method to identify elements whose raw data includes the specified substring, without requiring exact matches. Any element containing the substring within its raw data is considered a match.
        2. Extracting raw data strings from these filtered elements using the `_extract_raw_data_with_errors_handled` method. This process is designed to ensure robust data extraction, with graceful handling of any extraction errors. If an issue arises during the extraction from an element (e.g., due to unexpected data formats or missing information), a warning is issued, and None is returned for that element's raw data, allowing for uninterrupted extraction from other elements.

        Parameters:
            substring (str): The substring to search within the raw data of each OrcaElement. Elements with raw data containing this substring are included in the extraction process.

        Returns:
            pd.DataFrame: A DataFrame containing the raw data strings from the filtered OrcaElements. Each row corresponds to an element, with a column for the raw data strings. In cases where raw data extraction was unsuccessful (due to errors), the respective entry will be None.
        """
        filtered_blocks = self.search_elements_by_raw_data(substring)
        return self._extract_raw_data_with_errors_handled(filtered_blocks)

    def get_data_by_raw_data(self, substring: str) -> pd.DataFrame:
        """
        Filters OrcaElement instances by a specified substring in their raw data and extracts data from the matching elements.

        This method operates in two main steps:
        1. It first utilizes the `search_elements_by_raw_data` method to filter out the elements whose raw data
        contains the specified substring. This search is not limited to exact matches; any element whose raw data
        includes the substring anywhere within it will be considered a match.
        2. After obtaining a DataFrame of filtered elements, it then extracts data from these elements using the
        `_extract_data_with_errors_handled` method. This step ensures that data is extracted in a robust manner,
        with any errors encountered during the extraction process being handled gracefully. Specifically, if an
        error occurs while extracting data from an element (due to unexpected data formats, missing information,
        or any other issue), a warning is issued, and None is returned for that element's data. This approach ensures
        that the presence of problematic elements does not prevent the extraction of data from other, non-problematic elements.

        Parameters:
            substring (str): The substring to search for within the raw data of each OrcaElement. Elements whose raw data
                            contains this substring will be included in the data extraction process.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted data from the filtered OrcaElements. Each row corresponds
                        to one of the filtered elements, and there is an 'ExtractedData' column that contains the data
                        extracted from each element in orcaparse.Data format. If data extraction was unsuccessful for any element (due to errors),
                        the corresponding entry in the 'ExtractedData' column will be None.

        """
        filtered_blocks = self.search_elements_by_raw_data(substring)
        return self._extract_data_with_errors_handled(filtered_blocks)

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
        html_content += "    <title>Document</title>\n"

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
