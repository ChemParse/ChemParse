
# Contributing Guidelines for ChemParse

Thank you for your interest in contributing to ChemParse! Please follow these guidelines to ensure that your contribution is effective and maintains the quality of the project.

## Adding New Blocks

1. **Check Block Existence**: First, verify whether the block you want to add already exists. Ensure that your software version isn't causing the issue.

2. **Modify or Add Pattern**: If the block exists but isn't recognized, either modify the pattern or add a new one that detects the block in your specific software version.

3. **Check General Patterns**: 
   - If your block isn't recognized by existing patterns, check if it's detected by a general pattern such as `BlockOrcaUnrecognizedWithSingleLineHeader`.
   - If yes, locate the corresponding blueprint, like `BlueprintBlockWithSingleLineHeader`, and add your block accordingly, respecting the established guidelines.

4. **Create a New Regex**: If the block isn't recognized by any general patterns, create a new regex specifically tailored to detect it.

## Testing Your Changes

- Whenever you introduce a new block for **ORCA**, **GPAW**, or **VASP** files, ensure you add the respective test file under `tests/orca_test_outputs`, `tests/gpaw_test_outputs`, or `tests/vasp_test_outputs`.
- Each new block must have an associated output file where the new block is introduced, alongside a CSV demonstrating the extracted data.

## Requesting Additions

If you're struggling with adding a block:
- Submit the output file along with the block you want to extract and the data that needs extraction.

## Commit Structure

- Ensure every commit related to a new block includes a test output file showcasing the change.