import os

import pytest

from orcaparse.scripts import orca_parse, orca_to_html

# Test data directory
TEST_DATA_DIR = "tests/orca_test_outputs"


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir(TEST_DATA_DIR) if not os.path.isdir(os.path.join(TEST_DATA_DIR, f))])
def test_orca_to_html_defaults(orca_output_file, tmp_path):
    input_file = os.path.join(TEST_DATA_DIR, orca_output_file)
    # Use tmp_path for creating a temporary output file
    output_file = tmp_path / "temp.html"

    # Convert to string if necessary
    orca_to_html(input_file, str(output_file))
    assert output_file.exists(), "HTML file was not created"
    # Additional checks for the HTML file content can be added here


@pytest.mark.parametrize("orca_output_file", [f for f in os.listdir(TEST_DATA_DIR) if not os.path.isdir(os.path.join(TEST_DATA_DIR, f))])
def test_orca_parse_auto(orca_output_file, tmp_path):
    input_file = os.path.join(TEST_DATA_DIR, orca_output_file)
    # Supported formats plus 'xlsx' for Excel
    formats = ['csv', 'json', 'html', 'xlsx']

    for file_format in formats:
        # Use tmp_path for each temporary output file
        temp_output_file = tmp_path / f"temp_output.{file_format}"
        # Convert to string if necessary
        orca_parse(input_file, str(temp_output_file))
        assert temp_output_file.exists(
        ), f"{file_format.upper()} file was not created"
        # Additional checks for the output file content based on the format can be added here
