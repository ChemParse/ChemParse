import pandas as pd
import pytest
import orcaparse as op
import os
import re

block_marker = '<@%Spacer|Spacer|7986898590462%@>'

rs = op.DEFAULT_ORCA_REGEX_SETTINGS
known_regexes = (rs.items["TypeKnownBlocks"].to_list() +
                 rs.items["TypeDefaultBlocks"].to_list())


def extract_raw_text_from_apply_with_check(apply):
    _, block = apply
    assert len(block) == 1
    element = list(block.values())[0]['Element']
    return element.raw_data


def consistency_check(regex, text, additional_text):
    output = extract_raw_text_from_apply_with_check(
        regex.apply('\n\n'+text+'\n'+additional_text))
    assert output == text, (f'Pattern can not identify the block'
                            f' with the {additional_text} after it')
    output = extract_raw_text_from_apply_with_check(
        regex.apply(additional_text+'\n'+text+'\n'+additional_text+'\n'))
    assert output == text, (f'Pattern can not identify the pattern'
                            f' surrounded by {additional_text}')


# Generate a list of all files in the 'tests/orca_test_outputs' directory
orca_output_files = [f for f in os.listdir(
    "tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))]

# Use pytest.mark.parametrize to create a test for each combination of regex pattern and file


@pytest.mark.parametrize("regex,orca_output_file", [(regex, file) for regex in known_regexes for file in orca_output_files])
def test_default_regex_known(regex, orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)
    with open(file_path, "r") as file:
        orca_output = file.read()
    _, new_blocks = regex.apply(orca_output)
    for block in new_blocks.values():
        element: op.elements.Element = block['Element']
        consistency_check(regex, element.raw_data, block_marker)
