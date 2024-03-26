import re
import warnings
from typing import Pattern, Union

from .elements import AvailableBlocks, Block, Element, Spacer


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

    def apply(self, marked_text: list[tuple[tuple[int, int], tuple[int, int], Element]] | str) -> tuple[str, dict[str, dict]]:
        """
        Apply the regular expression pattern to the marked text and extract elements.

        Args:
            marked_text (list[tuple[tuple[int, int], tuple[int, int], Element]] | str): The marked text to apply the pattern to.
                It can be either a list of tuples containing the position, line numbers, and element, or a string.

        Returns:
            tuple[str, dict[str, dict]]: A tuple containing the modified marked text and a dictionary
                of extracted elements with their positions.
        """
        if isinstance(marked_text, str):
            marked_text = [
                ((0, len(marked_text)), (1, marked_text.count('\n') + 1), marked_text)]

        compiled_pattern = self.compile()
        elements_dict = {}

        def break_block(block):
            char_pos, line_pos, text = block
            result = []
            last_match_end = 0  # Tracks the end of the last match

            def count_newlines(text_segment):
                return text_segment.count('\n')

            def update_line_pos(start, end):
                # Calculate new line start position by adding the number of newlines up to the start of the block
                new_line_start = line_pos[0] + count_newlines(text[:start])
                # Calculate new line end position by adding the number of newlines within the block
                new_line_end = new_line_start + count_newlines(text[start:end])
                return (new_line_start, new_line_end)

            for match in compiled_pattern.finditer(text):
                if match.start() > last_match_end:
                    text_between_matches = text[last_match_end:match.start()]
                    # Adjust both start and end positions for the text between matches
                    interim_line_pos = update_line_pos(
                        last_match_end, match.start())
                    result.append(
                        ((char_pos[0] + last_match_end, char_pos[0] + match.start()), interim_line_pos, text_between_matches))

                # Adjust the position for the current match using a tuple
                block_position = (
                    char_pos[0] + match.start(), char_pos[0] + match.end())
                # Calculate the updated line position for the current block
                current_line_pos = update_line_pos(match.start(), match.end())
                # Use group(1) for the extracted text
                extracted_text = match.group(1)

                if self.p_type == "Block":
                    if self.p_subtype in AvailableBlocks.blocks:
                        # Create an instance of the class with position parameter
                        element_instance = AvailableBlocks.blocks[self.p_subtype](
                            extracted_text, char_position=block_position, line_position=current_line_pos)
                    else:
                        warnings.warn(
                            (f"Subtype `{self.p_subtype}`"
                                f" not recognized. Falling back to OrcaBlock.")
                        )
                        element_instance = Block(
                            extracted_text, char_position=block_position, line_position=current_line_pos)
                elif self.p_type == "Spacer":
                    element_instance = Spacer(
                        extracted_text, char_position=block_position, line_position=current_line_pos)

                if element_instance:
                    # Add the element instance to the result, using the block position tuple
                    result.append(
                        (block_position, current_line_pos, element_instance))
                    # Update the last match end position
                    last_match_end = match.end()
                    elements_dict[hash(element_instance)] = {
                        'Element': element_instance, 'CharPosition': block_position, 'LinePosition': current_line_pos}

            # Handle any remaining text after the last match
            if last_match_end < len(text):
                remaining_text = text[last_match_end:]
                # Adjust both start and end positions for the remaining text
                remaining_text_position = (
                    char_pos[0] + last_match_end, char_pos[0] + len(text))
                # Calculate the line position for the remaining text
                remaining_line_pos = update_line_pos(last_match_end, len(text))
                result.append((remaining_text_position,
                              remaining_line_pos, remaining_text))

            return result

        i = 0
        while i < len(marked_text):
            # Assuming the structure is [(tuple, tuple, str/Element)]
            if isinstance(marked_text[i][2], str):
                result = break_block(marked_text[i])
                if result:
                    # Remove the original item
                    del marked_text[i]

                    # Insert the new items from 'result' at position 'i'
                    for item in reversed(result):
                        marked_text.insert(i, item)

                    # Increment 'i' by the number of new items inserted
                    i += len(result)
                else:
                    # No blocks found, move to the next item
                    i += 1
            else:
                # The item is not a string, move to the next item
                i += 1

        return marked_text, elements_dict

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
