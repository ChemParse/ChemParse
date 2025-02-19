import os
import re
from itertools import zip_longest

import pandas as pd
import pytest

import pychemparse as chp

rs = chp.DEFAULT_VASP_REGEX_SETTINGS
known_vasp_regexes = (rs.items["TypeKnownBlocks"].to_list() +
                      rs.items["TypeDefaultBlocks"].to_list())
known_vasp_regexes_subtypes = list(
    set([reg.p_subtype for reg in known_vasp_regexes]))

all_vasp_regexes = rs.to_list()

# Generate a list of all files in the 'tests/vasp_test_outputs' directory
vasp_output_files = [os.path.join("tests", "vasp_test_outputs", f) for f in os.listdir(
    "tests/vasp_test_outputs") if not os.path.isdir(os.path.join("tests", "vasp_test_outputs", f)) and not f.endswith(".csv")]


def anchor_pattern_maker(compiled_regex):
    """
    Takes a compiled regular expression object, adds '^' at the beginning and
    '$' at the end of its pattern, and returns a new compiled regex object
    with the same flags.

    Parameters:
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


def regex_check(vasp_out, regex):
    compiled_pattern = regex.compile()
    matches = compiled_pattern.finditer(vasp_out)
    anchor_pattern = anchor_pattern_maker(compiled_pattern)
    anchor_matches = anchor_pattern.finditer(vasp_out)

    for match, anchor_match in zip_longest(matches, anchor_matches, fillvalue=None):
        if match is None or anchor_match is None:
            raise ValueError(
                f"The number of matches in the anchor pattern "
                f"and the original pattern "
                f"do not match,\nmatch:\n{match}\n"
                f"anchor_match:\n{anchor_match}"
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


# Use pytest.mark.parametrize to create a test for each combination of regex pattern and file


@pytest.mark.parametrize("regex,vasp_output_file", [(regex, file) for regex in all_vasp_regexes for file in vasp_output_files])
def test_default_regex_known(regex, vasp_output_file):
    with open(vasp_output_file, "r") as file:
        vasp_output = file.read()
    regex_check(vasp_out=vasp_output, regex=regex)


@pytest.mark.parametrize("vasp_output_file", vasp_output_files)
def test_default_output_parsing(vasp_output_file):
    expected_result = pd.read_csv(vasp_output_file + ".csv")

    file = chp.File(vasp_output_file, mode='VASP')
    data = file.get_data(extract_only_raw=True)
    data = data.drop(columns=['Element'])
    data = data[data["Subtype"].isin(known_vasp_regexes_subtypes)]
    data = data.sort_values(by="CharPosition")

    # Reset index before comparison to ignore index differences
    data = data.reset_index(drop=True)
    expected_result = expected_result.reset_index(drop=True)

    # Assert that the column names are the same
    assert set(data.columns) == set(
        expected_result.columns), "Column names do not match."

    def convert_to_tuple_of_ints(s):
        # This function takes a string representation of a tuple and returns a tuple of ints
        # It expects a string in the format "(int, int)" and will strip whitespace, split by comma, and convert to int
        if isinstance(s, tuple):
            return s
        elif isinstance(s, int):
            return (s,)
        elif isinstance(s, list):
            return tuple(s)
        return tuple(int(x) for x in s.strip("()").split(","))

    # Convert 'Type', 'Subtype', 'ReadableName', and 'RawData' columns to string (str)
    for column in ['Type', 'Subtype', 'ReadableName', 'RawData']:
        data[column] = data[column].astype(str)
        expected_result[column] = expected_result[column].astype(str)

    # Convert 'CharPosition' and 'LinePosition' columns to tuples of ints
    for column in ['CharPosition', 'LinePosition']:
        data[column] = data[column].apply(convert_to_tuple_of_ints)
        expected_result[column] = expected_result[column].apply(
            convert_to_tuple_of_ints)

    try:
        # Use assert_frame_equal with check_index_type=False to ignore index in comparison
        pd.testing.assert_frame_equal(
            data, expected_result, check_index_type=False)
    except AssertionError as e:
        # If there's a mismatch, find the differences
        differences = data.compare(
            expected_result, keep_shape=True, keep_equal=False)

        # Format a message detailing the differences
        diff_message = (f"Data does not match expected result for {vasp_output_file}."
                        f" Differences found:\n{differences}")

        # Raise an AssertionError with the detailed message
        raise AssertionError(diff_message) from None


@pytest.mark.parametrize("vasp_output_file", vasp_output_files)
def test_default_get_data(vasp_output_file):
    file = chp.File(vasp_output_file, mode='VASP')
    data = file.get_data()
