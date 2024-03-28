import pandas as pd
import pytest
import orcaparse as op
import os
import re
from itertools import zip_longest


rs = op.DEFAULT_ORCA_REGEX_SETTINGS
# known_regexes = (rs.items["TypeKnownBlocks"].to_list() +
#                  rs.items["TypeDefaultBlocks"].to_list())
known_regexes = rs.to_list()


def anchor_pattern_maker(compiled_regex):
    """
    Takes a compiled regular expression object, adds '^' at the beginning and
    '$' at the end of its pattern, and returns a new compiled regex object
    with the same flags.

    Args:
        compiled_regex (re.Pattern): The original compiled regular expression object.

    Returns:
        re.Pattern: The new compiled regular expression object with '^' and '$' added.
    """
    # Access the original pattern and flags
    original_pattern = compiled_regex.pattern
    original_flags = compiled_regex.flags

    # Add '^' at the beginning and '$' at the end of the pattern
    new_pattern = "^" + original_pattern

    # Recompile the new pattern with the original flags
    new_compiled_regex = re.compile(new_pattern, original_flags)

    return new_compiled_regex


def regex_check(orca_out, regex):
    compiled_pattern = regex.compile()
    matches = compiled_pattern.finditer(orca_out)
    anchor_pattern = anchor_pattern_maker(compiled_pattern)
    anchor_matches = anchor_pattern.finditer(orca_out)

    for match, anchor_match in zip_longest(matches, anchor_matches, fillvalue=None):
        if match is None or anchor_match is None:
            raise ValueError(
                f"The number of matches in the anchor pattern and the original pattern do not match,\n{match = }\n{anchor_match = }"
            )
        # The entire matched text
        full_match = match.group(0)
        anchor_full_match = anchor_match.group(0)
        assert (
            full_match == anchor_full_match
        ), f"The full match:\n{full_match}\ndoes not match the anchor full match:\n{anchor_full_match}"

        # The first extracted group
        extracted_text = match.group(1)

        assert (
            extracted_text == full_match
        ), "The extracted text does not match the full match"
        reextracted_match = compiled_pattern.search(extracted_text)
        reextracted_full_match = reextracted_match.group(0)
        reextracted_extracted_text = reextracted_match.group(1)
        assert (
            reextracted_full_match == extracted_text
        ), "The reextracted full match does not match the extracted text"
        assert (
            reextracted_extracted_text == extracted_text
        ), "The reextracted extracted text does not match the extracted text"

        assert full_match[-1] == "\n", (
            "The full match does not end with a newline character:\n" + full_match
        )


# Generate a list of all files in the 'tests/orca_test_outputs' directory
orca_output_files = [f for f in os.listdir(
    "tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))]

# Use pytest.mark.parametrize to create a test for each combination of regex pattern and file


@pytest.mark.parametrize("regex,orca_output_file", [(regex, file) for regex in known_regexes for file in orca_output_files])
def test_default_regex_known(regex, orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)
    with open(file_path, "r") as file:
        orca_output = file.read()
    regex_check(orca_out=orca_output, regex=regex)
