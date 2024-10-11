Contributing to ChemParse
=========================

Thank you for your interest in contributing to ChemParse! Please follow these guidelines to ensure that your contribution is effective and maintains the quality of the project.

Adding New Blocks
-----------------

1. **Check Block Existence**: Before adding a new block, verify whether it already exists. If the block isn’t recognized, ensure the issue isn’t caused by your software version.

2. **Modify or Add Pattern**: 
   - If the block exists but isn't detected, modify the existing pattern or add a new one to account for your software version.
   
3. **Check General Patterns**:
   - If your block isn’t recognized by existing patterns, check whether it is detected by a general pattern, such as `BlockOrcaUnrecognizedWithSingleLineHeader`.
   - If so, locate the appropriate blueprint (e.g., `BlueprintBlockWithSingleLineHeader`) and add your block according to the established guidelines.

4. **Create a New Regex**: If no existing pattern or general block applies, create a new regex specifically for detecting this block.

Testing Your Changes
--------------------

- When adding a new block for **ORCA**, **GPAW**, or **VASP** files, add a corresponding test file:
  - **ORCA**: Place test files in `tests/orca_test_outputs`
  - **GPAW**: Place test files in `tests/gpaw_test_outputs`
  - **VASP**: Place test files in `tests/vasp_test_outputs`

- Each new block must have an associated test output file demonstrating the extracted data, along with a CSV file showcasing the extracted data.

Requesting Additions
--------------------

If you encounter difficulties when adding a block, please submit the following:
- The output file containing the block.
- The block you want to extract, including the data fields that need extraction.

Commit Structure
----------------

- Ensure each commit related to a new block includes a corresponding test output file that demonstrates the change.

Thank you for helping improve ChemParse!
