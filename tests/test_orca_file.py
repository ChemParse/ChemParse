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
def test_orca_raw_data_extraction(orca_output_file):
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)

    orca_file = op.File(file_path)
    data = orca_file.get_data(extract_raw=True)

    assert isinstance(
        data, pd.DataFrame), f"Expected data to be a pandas DataFrame, but got {type(data)}"

    # Assert that the DataFrame is not empty (has at least one row of data)
    assert not data.empty, "Expected data DataFrame to be non-empty"

    # Assert that the DataFrame contains more than just column names (at least one row of data)
    assert len(
        data.index) > 0, "Expected data DataFrame to have at least one row of data"


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir("tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f))])
def test_orca_data_extraction(orca_output_file):
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
