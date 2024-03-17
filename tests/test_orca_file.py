import os
from orcaparse import OrcaFile
import pytest


@pytest.mark.parametrize("orca_output_file", os.listdir("tests/orca_test_outputs"))
def test_orca_output_files(orca_output_file):
    # Construct the full path to the file
    file_path = os.path.join("tests", "orca_test_outputs", orca_output_file)

    # Skip directories
    if os.path.isdir(file_path):
        pytest.skip(f"{orca_output_file} is a directory, not a file")

    # Create an OrcaFile object and call create_html
    orca_file = OrcaFile(file_path)
    orca_file.create_html()

    # Here you might want to add assertions to verify the results of create_html
    # For example, you could check if the HTML file was created successfully in the expected location
