import pandas as pd
import pytest

from pychemparse import Data
from pychemparse.elements import ExtractionError
from pychemparse.orca_elements import AvailableBlocksOrca

# Load the test data from the CSV file
test_data = pd.read_csv("tests/extraction_sample.csv")


@pytest.mark.parametrize("subtype, raw_data", test_data.values)
def test_blocks(subtype, raw_data):
    # Ensure the subtype exists in AvailableBlocksOrca
    assert (subtype in AvailableBlocksOrca.blocks,
            f"{subtype} is not a registered block type.")

    # Instantiate the block using the corresponding class from AvailableBlocksOrca
    block_class = AvailableBlocksOrca.blocks[subtype]
    block_instance = block_class(raw_data)

    # Test the 'data' method if it's supposed to return a Data object or specific data format
    if hasattr(block_instance, 'data'):
        try:
            data = block_instance.data()
            assert isinstance(
                data, Data), f"'data' method for {subtype} did not return a Data object."
        except ExtractionError:
            pytest.fail(
                f"ExtractionError occurred for {subtype} with data: {raw_data}")

    # Test 'extract_name_header_and_body' method if applicable
    if hasattr(block_instance, 'extract_name_header_and_body'):
        name, header, body = block_instance.extract_name_header_and_body()
        assert isinstance(
            name, str), f"'extract_name_header_and_body' method for {subtype} did not return a string for name."
        assert isinstance(header, (str, type(
            None))), f"'extract_name_header_and_body' method for {subtype} did not return a string or None for header."
        assert isinstance(body, (str, type(
            None))), f"'extract_name_header_and_body' method for {subtype} did not return a string or None for body."

    # Test the 'to_html' method
    html = block_instance.to_html()
    assert isinstance(
        html, str), f"'to_html' method for {subtype} did not return a string."
