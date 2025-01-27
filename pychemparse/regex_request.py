import re
import time
import warnings
from typing import Pattern, Union

from tqdm import tqdm

from .elements import Block, Element, Spacer
from .gpaw_elements import AvailableBlocksGpaw
from .logging_config import logger
from .orca_elements import AvailableBlocksOrca
from .vasp_elements import AvailableBlocksVasp


class RegexRequest:
    """
    Encapsulates a regular expression request for parsing structured text.

    This class defines a regular expression pattern along with associated metadata to identify and extract specific elements from text. It allows for the application of the regex pattern to text segments, facilitating the extraction of structured information based on the pattern.

    :ivar p_type: The general type of the regex request, often corresponding to a high-level category such as 'Block' or 'Element'.
    :vartype p_type: str
    :ivar p_subtype: A more specific identifier within the broader type, providing additional context or classification.
    :vartype p_subtype: str
    :ivar pattern: The actual regular expression pattern used for matching text.
    :vartype pattern: str
    :ivar flags: The combined regex flags compiled into an integer, determining how the regex pattern is applied.
    :vartype flags: int
    :ivar comment: An optional description or note about the purpose or nature of the regex request.
    :vartype comment: str
    """

    def __init__(self,
                 p_type: str,
                 p_subtype: str,
                 pattern: str,
                 flags: list[str],
                 comment: str = '') -> None:
        """
        Initializes a `RegexRequest` instance with a specified pattern, flags, and optional comment.

        :param p_type: The high-level category or type this regex request pertains to, e.g., 'Block'.
        :type p_type: str
        :param p_subtype: A more detailed classification within the type, e.g., 'Header' or 'Footer'.
        :type p_subtype: str
        :param pattern: The regular expression pattern to be used for text matching.
        :type pattern: str
        :param flags: A list of strings representing the regex flags to be applied, such as 'MULTILINE' or 'IGNORECASE'.
        :type flags: list[str]
        :param comment: A descriptive note or comment about the regex request, intended to provide clarity or context.
        :type comment: str, optional
        """
        self.p_type: str = p_type
        self.p_subtype: str = p_subtype
        self.pattern: str = pattern
        self.comment: str = comment
        self.flags: int = self._compile_flags(flags)

    def _compile_flags(self, flag_names: list[str]) -> int:
        """
        Compiles regex flag names into a combined integer representation.

        :param flag_names: A list of regex flag names to be compiled. Supported flags include 'IGNORECASE', 'MULTILINE', 'DOTALL', 'UNICODE', and 'VERBOSE'.
        :type flag_names: list[str]
        :return: The compiled integer value representing the combination of the provided regex flags.
        :rtype: int
        :raises ValueError: If an unsupported flag name is included in the input list.
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
        Decompile the combined integer flags into their individual string representations.

        :return: A list of flag names corresponding to the combined flags integer.
        :rtype: list[str]
        """
        valid_flags = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
            "UNICODE": re.UNICODE,
            "VERBOSE": re.VERBOSE
        }
        flag_names = [
            flag_str for flag_str, flag_val in valid_flags.items()
            if self.flags & flag_val
        ]
        return flag_names

    def validate_configuration(self) -> None:
        """
        Validates the RegexRequest configuration. Placeholder for future validation logic.

        Currently, this method does not perform any checks and exists as a placeholder for potential future validation requirements.
        """
        pass

    def to_dict(self) -> dict[str, Union[str, list[str]]]:
        """
        Converts the RegexRequest instance to a dictionary, including flag names as strings.

        :return: A dictionary representation of the RegexRequest, with keys for type, subtype, pattern, flags (as a list of strings), and optional comment.
        :rtype: dict[str, Union[str, list[str]]]
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
        Compiles the regex pattern with the specified flags into a regex pattern object.

        This compiled object can be used for various regex operations like `findall`, `search`, `match`, etc., enabling efficient pattern matching.

        :return: A compiled regex pattern object, ready for use in pattern matching operations.
        :rtype: Pattern
        """
        return re.compile(self.pattern, self.flags)

    def apply(self,
              marked_text: list[tuple[tuple[int, int], tuple[int, int],
                                      Element]] | str,
              mode: str = 'ORCA',
              show_progress: bool = False) -> tuple[str, dict[str, dict]]:
        """
        Applies the regex pattern to marked text or a raw string to identify and extract elements based on the pattern.

        This method iterates over the marked text or processes a string to identify matches to the regex pattern. Extracted elements are then organized based on their positions within the text.

        :param marked_text: The marked text or raw string to which the regex pattern will be applied. Marked text should be a list of tuples, each containing character positions, line numbers, and an associated `Element`. If a raw string is provided, it will be converted to the marked text.
        :type marked_text: Union[list[tuple[tuple[int, int], tuple[int, int], Element]], str]
        :param mode: The operational mode for element extraction, typically indicating the type of data being processed (e.g., 'ORCA' or 'GPAW').
        :type mode: str
        :param show_progress: Indicates whether a progress indicator should be shown during the extraction process. Useful for long-running operations.
        :type show_progress: bool

        :return: A tuple containing the updated marked text and a dictionary mapping extracted elements to their positions.
        :rtype: tuple[str, dict[str, dict]]
        """

        if mode == 'ORCA':
            AB = AvailableBlocksOrca
        elif mode == 'GPAW':
            AB = AvailableBlocksGpaw
        elif mode == 'VASP':
            AB = AvailableBlocksVasp
        else:
            raise ValueError(f"Mode '{mode}' is not recognized.")

        if isinstance(marked_text, str):
            marked_text = [((0, len(marked_text)),
                            (1, marked_text.count('\n') + 1), marked_text)]

        compiled_pattern = self.compile()
        elements_dict = {}

        total_chars = marked_text[-1][0][1]

        # Added prefix_text parameter
        def with_progress_bar(
                show_progress: bool,
                refresh_interval: float = 2,
                prefix_text: str = f"Processing {self.p_subtype}:"):

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
                                    f'Current block position: {block_position}'
                                )
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

        @with_progress_bar(show_progress=show_progress,
                           refresh_interval=2,
                           prefix_text=f"Processing {self.p_subtype}")
        def process_marked_text(marked_text,
                                elements_dict,
                                progress_callback=None):

            def break_block(block, elements_dict, progress_callback=None):
                char_pos, line_pos, text = block

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

                        result.append(((char_start, char_end),
                                       (line_start, line_end), item))

                    return result

                def convert_to_element(item,
                                       elements_dict,
                                       compiled_pattern,
                                       progress_callback=None):
                    if progress_callback:
                        progress_callback(item[0][1], block_position=item[0])
                    if compiled_pattern.fullmatch(item[2]):
                        char_pos, line_pos, extracted_text = item

                        if self.p_type == "Block":
                            if self.p_subtype in AB.blocks:
                                # Create an instance of the class with position parameter
                                element_instance = AB.blocks[self.p_subtype](
                                    extracted_text,
                                    char_position=char_pos,
                                    line_position=line_pos)
                            else:
                                logger.warning(
                                    (f"Subtype `{self.p_subtype}`"
                                     f" not recognized. Falling back to Block."
                                     ))
                                element_instance = Block(
                                    extracted_text,
                                    char_position=char_pos,
                                    line_position=line_pos)
                                element_instance.specified_class_name = self.p_subtype
                        elif self.p_type == "Spacer":
                            element_instance = Spacer(extracted_text,
                                                      char_position=char_pos,
                                                      line_position=line_pos)

                        elements_dict[hash(element_instance)] = {
                            'Element': element_instance,
                            'CharPosition': char_pos,
                            'LinePosition': line_pos
                        }

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

                text_list = [
                    convert_to_element(item,
                                       elements_dict,
                                       compiled_pattern,
                                       progress_callback=progress_callback)
                    for item in text_list
                ]

                return text_list, elements_dict

            i = 0
            while i < len(marked_text):
                # Assuming the structure is [(tuple, tuple, str/Element)]
                if isinstance(marked_text[i][2], str):
                    result, elements_dict = break_block(
                        marked_text[i],
                        elements_dict,
                        progress_callback=progress_callback)
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
        Returns a constant value representing the conceptual 'length' of a RegexRequest.

        Since a RegexRequest encapsulates a single regex pattern and its associated settings, its length is conceptually always 1.

        :return: The constant value 1, representing the 'length' of a RegexRequest.
        :rtype: int
        """
        return 1

    def __repr__(self) -> str:
        """
        Generates a concise string representation of the RegexRequest instance.

        This representation includes the type, subtype, a truncated version of the pattern and comment (if they are too long), and the combined regex flags.

        :return: A string that provides a brief overview of the RegexRequest instance, suitable for debugging and logging purposes.
        :rtype: str
        """
        pattern_preview = self.pattern[:22] + \
            '...' if len(self.pattern) > 25 else self.pattern
        comment_preview = self.comment[:22] + \
            '...' if len(self.comment) > 25 else self.comment
        return f"RegexRequest(p_type='{self.p_type}', p_subtype='{self.p_subtype}', pattern='{pattern_preview}', flags={self.flags}, comment='{comment_preview}')"
