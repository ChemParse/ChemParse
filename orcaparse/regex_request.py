import re
import time
import warnings
from typing import Pattern, Union

from tqdm import tqdm

from .elements import Block, Element, Spacer
from .gpaw_elements import AvailableBlocksGpaw
from .orca_elements import AvailableBlocksOrca


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

    def apply(self, marked_text: list[tuple[tuple[int, int], tuple[int, int], Element]] | str, mode: str = 'ORCA', show_progress: bool = False) -> tuple[str, dict[str, dict]]:
        """
        Apply the regular expression pattern to the marked text and extract elements.

        Args:
            marked_text (list[tuple[tuple[int, int], tuple[int, int], Element]] | str): The marked text to apply the pattern to.
                It can be either a list of tuples containing the position, line numbers, and element, or a string.
            mode (str): The mode to use for element extraction, either 'ORCA' or 'GPAW'.
            show_progress (bool): A flag indicating whether to show a progress bar during the extraction process.

        Returns:
            tuple[str, dict[str, dict]]: A tuple containing the modified marked text and a dictionary
                of extracted elements with their positions.
        """
        if mode == 'ORCA':
            AB = AvailableBlocksOrca
        elif mode == 'GPAW':
            AB = AvailableBlocksGpaw
        else:
            raise ValueError(f"Mode '{mode}' is not recognized.")

        if isinstance(marked_text, str):
            marked_text = [
                ((0, len(marked_text)), (1, marked_text.count('\n') + 1), marked_text)]

        compiled_pattern = self.compile()
        elements_dict = {}

        total_chars = marked_text[-1][0][1]

        # Added prefix_text parameter
        def with_progress_bar(show_progress: bool, refresh_interval: float = 2, prefix_text: str = f"Processing {self.p_subtype}:"):
            def decorator(func):
                if not show_progress:
                    return func

                def wrapper(*args, **kwargs):
                    nonlocal total_chars  # Assuming total_chars is defined in the outer scope
                    # Set prefix text using desc parameter
                    pbar = tqdm(total=total_chars, desc=prefix_text)

                    last_update_time = time.time()

                    # Added optional block_position
                    def update_progress(current_char_pos, block_position=None):
                        nonlocal last_update_time
                        current_time = time.time()
                        if current_time - last_update_time >= refresh_interval:
                            pbar.n = current_char_pos
                            if block_position:  # Update postfix text if provided
                                pbar.set_postfix_str(
                                    f'Current block position: {block_position}')
                            pbar.refresh()
                            last_update_time = current_time

                    kwargs['progress_callback'] = update_progress
                    result = func(*args, **kwargs)
                    pbar.n = total_chars  # Ensure the progress bar completes if not already
                    pbar.refresh()
                    pbar.close()
                    return result

                return wrapper
            return decorator

        @with_progress_bar(show_progress=show_progress, refresh_interval=2, prefix_text=f"Processing {self.p_subtype}")
        def process_marked_text(marked_text, elements_dict, progress_callback=None):
            def break_block(block, elements_dict, progress_callback=None):
                char_pos, line_pos, text = block
                result = []
                last_match_end = 0  # Tracks the end of the last match

                def convert_to_tuples(text_list, progress_callback=None):
                    result = []
                    # Start from the first character
                    current_char_pos = char_pos[0]
                    current_line_pos = line_pos[0]  # Start from the first line

                    for item in text_list:
                        if item is None or len(item) == 0:
                            continue
                        char_start = current_char_pos
                        # -1 because end is inclusive
                        char_end = current_char_pos + len(item) - 1

                        # Count the lines in the current segment
                        lines_in_item = item.count('\n')
                        line_start = current_line_pos
                        line_end = current_line_pos + lines_in_item

                        # Update for the next iteration
                        current_char_pos = char_end + 1
                        current_line_pos = line_end + 1 if lines_in_item > 0 else current_line_pos

                        result.append(
                            ((char_start, char_end), (line_start, line_end), item))

                    return result

                def convert_to_element(item, elements_dict, compiled_pattern, progress_callback=None):
                    if progress_callback:
                        progress_callback(item[0][1], block_position=item[0])
                    if compiled_pattern.fullmatch(item[2]):
                        char_pos, line_pos, extracted_text = item

                        if self.p_type == "Block":
                            if self.p_subtype in AB.blocks:
                                # Create an instance of the class with position parameter
                                element_instance = AB.blocks[self.p_subtype](
                                    extracted_text, char_position=char_pos, line_position=line_pos)
                            else:
                                warnings.warn(
                                    (f"Subtype `{self.p_subtype}`"
                                        f" not recognized. Falling back to Block.")
                                )
                                element_instance = Block(
                                    extracted_text, char_position=char_pos, line_position=line_pos)
                        elif self.p_type == "Spacer":
                            element_instance = Spacer(
                                extracted_text, char_position=char_pos, line_position=line_pos)

                        elements_dict[hash(element_instance)] = {
                            'Element': element_instance, 'CharPosition': char_pos, 'LinePosition': line_pos}

                        return (char_pos, line_pos, element_instance)

                    return item

                def split_by_full_matches(text, compiled_pattern):
                    segments = []
                    start = 0

                    for match in compiled_pattern.finditer(text):
                        # Add the text leading up to the match (if any)
                        if match.start() > start:
                            segments.append(text[start:match.start()])

                        # Add the matched text
                        segments.append(match.group())

                        # Update the start position for the next iteration
                        start = match.end()

                    # Add any remaining text after the last match
                    if start < len(text):
                        segments.append(text[start:])

                    return segments

                # split by full matches instead of re split to allow the internal groups in regex
                text_list = split_by_full_matches(text, compiled_pattern)

                text_list = convert_to_tuples(
                    text_list, progress_callback=progress_callback)

                text_list = [convert_to_element(
                    item, elements_dict, compiled_pattern, progress_callback=progress_callback) for item in text_list]

                return text_list, elements_dict

            i = 0
            while i < len(marked_text):
                # Assuming the structure is [(tuple, tuple, str/Element)]
                if isinstance(marked_text[i][2], str):
                    result, elements_dict = break_block(
                        marked_text[i], elements_dict, progress_callback=progress_callback)
                    if result:
                        # Remove the original item
                        del marked_text[i]

                        # Insert the new items from 'result' at position 'i'
                        # for item in reversed(result):
                        #     marked_text.insert(i, item)
                        marked_text[i:i] = result

                        # Increment 'i' by the number of new items inserted
                        i += len(result)
                    else:
                        # No blocks found, move to the next item
                        i += 1
                else:
                    # The item is not a string, move to the next item
                    i += 1

            return marked_text, elements_dict

        marked_text, elements_dict = process_marked_text(
            marked_text=marked_text, elements_dict=elements_dict)

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
