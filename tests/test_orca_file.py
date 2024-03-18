import os
from io import StringIO

import pandas as pd
import pytest
from lxml import etree

import orcaparse as op


def is_html_valid(html):
    try:
        parser = etree.HTMLParser()
        etree.parse(StringIO(html), parser)
        return True
    except etree.XMLSyntaxError:
        return False


def test_orca_available_types():
    # Retrieve the available types from the op.File class
    # This should return a dictionary where keys are type names and values are descriptions or classes associated with these types
    available_types = op.File.available_types

    # Assert that available_types is an instance of a dictionary
    # This checks that the structure used to store available types is indeed a dictionary, which is expected for mapping type names to their descriptions or classes
    assert isinstance(
        available_types, dict), "Expected available_types to be a dictionary"

    # Assert that the dictionary is not empty
    # This checks that there are actually types defined and available, ensuring the functionality related to type handling is implemented and not just an empty placeholder
    assert len(
        available_types) > 0, "Expected available_types to contain at least one type definition"


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir("tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))])
def test_orca_blocks(orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)

    orca_file = op.File(file_path)

    blocks = orca_file.get_blocks()
    # Assert that blocks is an instance of pd.DataFrame
    assert isinstance(
        blocks, pd.DataFrame), f"Expected blocks to be a pandas DataFrame, but got {type(blocks)}"

    # Assert that the DataFrame is not empty (has at least one row of data)
    assert not blocks.empty, "Expected blocks DataFrame to be non-empty"

    # Assert that the DataFrame contains more than just column names (at least one row of data)
    assert len(
        blocks.index) > 0, "Expected blocks DataFrame to have at least one row of data"


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir("tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))])
def test_orca_marked_text(orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)

    orca_file = op.File(file_path)

    marked_text = orca_file.get_marked_text()
    # Assert that blocks is an instance of pd.DataFrame
    assert isinstance(
        marked_text, str), f"Expected marked_text to be string, but got {type(marked_text)}"

    # Assert that the DataFrame contains more than just column names (at least one row of data)
    assert len(marked_text) > 0, "Expected marked_text not to be empty"


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir("tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))])
def test_orca_raw_data_collection(orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)

    orca_file = op.File(file_path)
    data = orca_file.get_raw_data()

    assert isinstance(
        data, pd.DataFrame), f"Expected data to be a pandas DataFrame, but got {type(data)}"

    # Assert that the DataFrame is not empty (has at least one row of data)
    assert not data.empty, "Expected data DataFrame to be non-empty"

    # Assert that the DataFrame contains more than just column names (at least one row of data)
    assert len(
        data.index) > 0, "Expected data DataFrame to have at least one row of data"


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir("tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))])
def test_orca_data_collection(orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)

    orca_file = op.File(file_path)
    data = orca_file.get_data()

    assert isinstance(
        data, pd.DataFrame), f"Expected data to be a pandas DataFrame, but got {type(data)}"

    # Assert that the DataFrame is not empty (has at least one row of data)
    assert not data.empty, "Expected data DataFrame to be non-empty"

    # Assert that the DataFrame contains more than just column names (at least one row of data)
    assert len(
        data.index) > 0, "Expected data DataFrame to have at least one row of data"


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir("tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))])
def test_orca_html(orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)

    orca_file = op.File(file_path)
    # Assuming this returns a string of HTML content
    html_content = orca_file.create_html()

    assert is_html_valid(
        html_content), f"HTML content from {orca_output_file} is not valid"
