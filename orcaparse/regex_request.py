import re
import warnings
from typing import Pattern, Union

from .elements import AvailableBlocks, Block, Spacer


class RegexRequest:
    def __init__(self, p_type: str, p_subtype: str, pattern: str, flags: list[str], comment: str = '') -> None:
        """
        Initializes a new RegexRequest object.

        Args:
            p_type (str): The type of the regex request, e.g., 'Block'.
            p_subtype (str): The subtype of the regex request, providing more specific identification.
            pattern (str): The regex pattern.
            flags (list[str]): A list of strings representing regex flags, e.g., ['MULTILINE', 'IGNORECASE'].
            comment (str): An optional comment describing the regex request.
        """
        self.p_type = p_type
        self.p_subtype = p_subtype
        self.pattern = pattern
        self.comment = comment
        self.flags = self._compile_flags(flags)

    def _compile_flags(self, flag_names: list[str]) -> int:
        """
        Compiles a list of flag names into a single integer representing the combined flags.

        Args:
            flag_names (list[str]): A list of flag names as strings.

        Returns:
            int: The combined flags as a single integer.

        Raises:
            ValueError: If an invalid flag name is provided.
        """
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
                raise ValueError(f"Invalid flag: {flag_name}")
        return compiled_flags

    def _decompile_flags(self) -> list[str]:
        """
        Decompile the integer flags into a list of their string representations.

        Returns:
            list[str]: A list of flag names as strings.
        """
        valid_flags = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
            "UNICODE": re.UNICODE,
            "VERBOSE": re.VERBOSE
        }
        flag_names = [flag_str for flag_str,
                      flag_val in valid_flags.items() if self.flags & flag_val]
        return flag_names

    def validate_configuration(self) -> None:
        """
        Validates the configuration of the RegexRequest. Currently, this method does not perform any checks.
        """
        pass

    def to_dict(self) -> dict[str, Union[str, list[str]]]:
        """
        Converts the RegexRequest instance to a dictionary, including string representations for flags.

        Returns:
            dict[str, Union[str, list[str]]]: A dictionary representation of the RegexRequest.
        """
        return {
            "p_type": self.p_type,
            "p_subtype": self.p_subtype,
            "pattern": self.pattern,
            "flags": self._decompile_flags(),
            "comment": self.comment
        }

    def compile(self) -> Pattern:
        """
        Compiles the regex pattern with the specified flags and returns a compiled regex pattern object.

        This method allows the user to utilize the compiled pattern object for various regex operations such as `findall`, `search`, `match`, etc.

        Returns:
            Pattern: A compiled regex pattern object.
        """
        return re.compile(self.pattern, self.flags)

    def apply(self, text: str, original_text: str | None = None) -> tuple[str, dict[str, dict]]:
        """
            Processes the input text using regular expressions to identify and replace specified patterns
            with unique markers, while also creating corresponding element instances based on the identified patterns.

            This method compiles a pattern using the instance's `compile` method, then iterates over all matches
            in the `text`. For each match, it:
            - Extracts the relevant text and information.
            - Ensures unique identification and non-overlap of markers.
            - Dynamically instantiates elements based on the pattern's subtype or falls back to a default type if necessary.
            - Updates a dictionary with the instantiated elements and their positions in the text.

            Nested functions within this method include:
            - `replace_with_marker`: Called for each regex match to handle the replacement of text with a marker and instantiation of the corresponding element.
            - `find_substring_positions`: Locates all occurrences of a substring within a given text, used to find the exact position of matched patterns in the original text.

            Parameters:
            - text (str): The text to be processed.
            - original_text (str, optional): The original text before any processing, used for accurate position mapping. Defaults to `None`, in which case `text` is used as the original text.

            Returns:
            - tuple[str, dict[str, dict]]: A tuple containing the processed text with markers and a dictionary of elements keyed by their unique identifiers. Each dictionary entry contains the instantiated element and its position in the original text.

            Raises:
            - Warnings for various edge cases, such as multiple matches for a pattern in the original text, or when a pattern subtype is not recognized and a default is used instead.
        """

        original_text = original_text or text
        compiled_pattern = self.compile()

        elements_dict = {}

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
                    f'Attempt to replace the marker in {self.p_type, self.p_subtype}:{extracted_text}')
                return full_match

            if self.p_type == 'Block':

                # Find all positions of the extracted text in the original text
                positions = find_substring_positions(
                    original_text, extracted_text)

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
                    start_line = original_text.count(
                        '\n', 0, start_index) + 1
                    end_line = original_text.count('\n', 0, end_index) + 1
                    # Tuple containing start and end lines
                    position = (start_line, end_line)
            else:
                position = None

            # Dynamically instantiate the class based on p_subtype or fall back to OrcaDefaultBlock
            class_name = self.p_subtype  # Directly use p_subtype as class name
            if class_name in AvailableBlocks.blocks:
                if self.p_type == "Block":
                    # Create an instance of the class, block have position parameter
                    element_instance = AvailableBlocks.blocks[class_name](
                        extracted_text, position=position)
                else:
                    # Create an instance of the class, block have position parameter
                    element_instance = AvailableBlocks.blocks[class_name](
                        extracted_text)
            elif self.p_type == "Spacer":
                element_instance = Spacer(extracted_text)
            elif self.p_type == "Block":
                # Fall back to OrcaDefaultBlock and raise a warning
                warnings.warn(
                    (f"Subtype `{self.p_subtype}`"
                        f" not recognized. Falling back to OrcaBlock.")
                )
                element_instance = Block(
                    extracted_text, position=position)

            else:
                # Handle other types or raise a generic warning
                warnings.warn(
                    (f"Subtype `{self.p_subtype}`"
                        f" not recognized and type `{self.p_type}`"
                        f" does not have a default.")
                )
                element_instance = None

            if element_instance:
                unique_id = hash(element_instance)
                elements_dict[unique_id] = {
                    'Element': element_instance, 'Position': position}

                # Replace the extracted text within the full match with the marker
                text_with_markers = full_match.replace(
                    extracted_text,
                    f"<@%{self.p_type}|{self.p_subtype}|{unique_id}%@>"
                )

            else:
                text_with_markers = full_match

            return text_with_markers

        text = compiled_pattern.sub(
            replace_with_marker, text)

        return text, elements_dict

    def __len__(self) -> int:
        """
        Returns the length of the RegexRequest, which is always 1 for a single request.

        Returns:
            int: The length of the RegexRequest.
        """
        return 1

    def __repr__(self) -> str:
        """
        Provides a string representation of the RegexRequest.

        Returns:
            str: A string representation of the RegexRequest.
        """
        pattern = self.pattern if len(
            self.pattern) < 25 else self.pattern[:25] + '...'
        comment = self.comment if len(
            self.comment) < 25 else self.comment[:25] + '...'
        return f"RegexRequest(p_type={self.p_type}, p_subtype={self.p_subtype}, pattern={pattern}, flags={self.flags}, comment={comment})"
