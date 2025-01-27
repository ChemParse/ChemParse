import os

import pytest

from pychemparse.scripts import chem_parse, chem_to_html

# Test data directory
orca_output_files = [os.path.join("tests", "orca_test_outputs", f) for f in os.listdir(
    "tests/orca_test_outputs") if not os.path.isdir(os.path.join("tests", "orca_test_outputs", f)) and f.endswith(".out")]


@pytest.mark.parametrize("orca_output_file", orca_output_files)
def test_orca_to_html_defaults(orca_output_file, tmp_path):
    # Use tmp_path for creating a temporary output file
    output_file = tmp_path / "temp.html"

    # Convert to string if necessary
    chem_to_html(orca_output_file, str(output_file))
    assert output_file.exists(), "HTML file was not created"
    # Additional checks for the HTML file content can be added here


@pytest.mark.parametrize("orca_output_file", orca_output_files)
def test_chem_parse_auto(orca_output_file, tmp_path):
    # Supported formats plus 'xlsx' for Excel
    formats = ['csv', 'json', 'html', 'xlsx']

    for file_format in formats:
        # Use tmp_path for each temporary output file
        temp_output_file = tmp_path / f"temp_output.{file_format}"
        # Convert to string if necessary
        chem_parse(orca_output_file, str(temp_output_file))
        assert (temp_output_file.exists(),
                f"{file_format.upper()} file was not created")
        # Additional checks for the output file content based on the format can be added here
