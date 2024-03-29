import re
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd

from .data import Data
from .elements import AvailableBlocksGeneral, Block, Element, ExtractionError
from .units_and_constants import ureg


class AvailableBlocksOrca(AvailableBlocksGeneral):
    blocks: dict[str, type[Element]] = {}


@AvailableBlocksOrca.register_block
class BlockOrcaWithStandardHeader(Block):
    """
    A specialized type of Block that expects a standard header format.

    This class extends `Block` to handle cases where blocks of data include a standardized header section, marked by specific delimiter patterns. It provides a customized implementation of the `extract_name_header_and_body` method to parse such headers and separate the block into readable name, header, and body components.

    The standard header format is expected to be delimited by lines of repeating special characters (e.g., '-', '*', '#') and may contain multiple lines of text that are considered part of the header.
    """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        """
        Extract the block's name, header, and body based on a standard header format.

        This method uses regular expressions to identify and separate the header section from the body. It then processes the header to extract a readable name and the header content itself. The remaining text is considered the body of the block.

        Returns:
            tuple[str, str | None, str]: A tuple containing the block's name, header (or None if not applicable), and body.

        Raises:
            Warning: If no recognizable header is found, indicating an unexpected format.
        """
        # Define regex pattern to split header and body
        pattern = r"^(([ \t]*[-*#]{7,}[ \t]*\n)(.*?)(\n[ \t]*[-*#]{7,}[ \t]*\n|$))"

        # Search for the pattern in self.raw_data using re.DOTALL to make '.' match newlines
        match = re.search(pattern, self.raw_data, re.DOTALL)

        if match:
            # Header is the content between the first and second header delimiters

            # Body is the content after the second header delimiter
            # The end of the header delimiter is marked by the start of the body_raw
            body_start = match.end(1)
            header_raw = self.raw_data[:body_start]
            body_raw = self.raw_data[body_start:]

            readable_lines = []

            # Split the header into lines
            lines = header_raw.split('\n')

            # Iterate over lines to find readable content
            for line in lines:
                # Check if the line is not solely composed of whitespace or special symbols
                if not re.match(r"^[ \t]*[-*#=]*[ \t]*$", line):
                    # Extract the central text if the line is surrounded by a maximum of one special symbol on each side
                    central_text_match = re.match(
                        r"^[ \t]*[-*#=]{,1}[ \t]*(.*?)[ \t]*[-*#=]{,1}[ \t]*$", line)
                    if central_text_match:
                        # Check that something was found and collect the first group result
                        central_text = central_text_match.group(1).strip()
                        if central_text:  # Ensure central_text is not empty
                            readable_lines.append(central_text)

            # Combine readable lines into a single string
            readable_name = ' '.join(readable_lines).strip()

            if len(readable_name) < 2:
                warnings.warn(
                    f'No readable name found in the header: {header_raw}')
                readable_name = Element.process_invalid_name(self.raw_data)

            return readable_name, header_raw, body_raw
        else:
            warnings.warn(
                f'No header found in\n{self.raw_data}\n, and that is really weird as it was extracted based on the idea that there is a header in it')
            # If no match is found, put everything into header
            return Element.process_invalid_name(self.raw_data), None, self.raw_data


@AvailableBlocksOrca.register_block
class BlockOrcaUnrecognizedWithHeader(BlockOrcaWithStandardHeader):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaUnrecognizedNotification(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaUnrecognizedMessage(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaIcon(Block):
    data_available: bool = True

    def readable_name(self) -> str:
        return 'Icon'

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Orca Icon', None, self.raw_data

    def data(self) -> Data:
        '''
        Icon is icon, noting to extract except for the ascii symbols
        '''
        return Data(data={'Icon': self.raw_data}, comment="Raw `Icon` string")

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Orca Icon', None, self.raw_data


@AvailableBlocksOrca.register_block
class BlockOrcaAllRightsReserved(Block):
    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'All Rights Reserved', None, self.raw_data


@AvailableBlocksOrca.register_block
class BlockOrcaFinalSinglePointEnergy(Block):
    data_available: bool = True

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'FINAL SINGLE POINT ENERGY', None, self.raw_data

    def data(self) -> Data:
        '''
        returns FINAL SINGLE POINT ENERGY in Eh
        '''
        pattern = r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)"

        # Search for the pattern in the text
        match = re.search(pattern, self.raw_data)

        if not match:
            raise ExtractionError("No energy match found in the data.")

        # Extract the floating-point number from the first capturing group
        energy = match.group(1)

        try:
            energy = float(energy) * ureg.Eh
            return Data(data={'Energy': energy}, comment='`Energy` in pint format, to extract the value in Eh, use property .magnitude')
        except ValueError:
            raise ExtractionError(
                f"Failed to convert the extracted energy {energy} to a floating-point number.")
        except Exception as e:
            # For any other unexpected exceptions, raise the original exception
            # You might want to log this exception or handle it differently depending on your application's needs
            raise e


@AvailableBlocksOrca.register_block
class BlockOrcaScfConverged(Block):
    data_available: bool = True

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'SCF convergence message', None, self.raw_data

    def data(self) -> Data:
        # Check for the presence of "SUCCESS"
        success_match = re.search(r"SUCCESS", self.raw_data)

        # Define regex pattern to match the number of cycles
        cycles_pattern = r"(\d+)\s+CYCLES"

        # Search for the cycles pattern in self.raw_data
        cycles_match = re.search(cycles_pattern, self.raw_data)

        # Prepare the result dictionary
        result = {
            # True if "SUCCESS" is found, False otherwise
            'Success': bool(success_match),
            'Cycles': None  # Default value for Cycles
        }

        # If a match for cycles is found, extract and update the number of cycles in the result dictionary
        if cycles_match:
            result['Cycles'] = int(cycles_match.group(1))

        return Data(data=result, comment='bool for `Success` of the extraction and int for amount of `Cycles`')


@AvailableBlocksOrca.register_block
class BlockOrcaDipoleMoment(BlockOrcaWithStandardHeader):
    data_available: bool = True

    def data(self) -> dict:
        # Initialize the result dictionary
        result = {}

        # Define regex pattern for lines with "text: 3 numbers"
        pattern_three_numbers = r"([a-zA-Z \(\).]+):\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)[ \t]*\n"
        # Define regex pattern for lines with "text: 1 number"
        pattern_one_number = r"([a-zA-Z \(\).]+):\s*(-?\d+\.\d+)[ \t]*(?:\n|\Z)"

        # Find all matches for the three-number pattern
        matches_three_numbers = re.findall(
            pattern_three_numbers, self.raw_data)
        for match in matches_three_numbers:
            label, x, y, z = match
            result[label.strip()] = np.array([float(x), float(y), float(z)])

        # Find all matches for the one-number pattern
        matches_one_number = re.findall(pattern_one_number, self.raw_data)
        for match in matches_one_number:
            label, value = match
            if "(Debye)" in label:
                unit = "Debye"
            else:
                unit = "a.u."
            result[label.strip()] = float(
                value)*ureg.debye if unit == "Debye" else float(value)

        return Data(data=result, comment='Numpy arrays of contributions, total dipole moment and pint object of `Magnitude (Debye)`.\nThe magnitude of the magnitude in Debye can be extracted from pint with .magnitude property.')


@AvailableBlocksOrca.register_block
class BlockOrcaOrbitalEnergies(BlockOrcaWithStandardHeader):
    data_available: bool = True

    def data(self) -> dict[str, pd.DataFrame]:
        # Define regex pattern for extracting orbital data lines
        pattern_orbital_data = r"\s*(\d+)\s+([0-1]\.\d{4})\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*"

        # Split the raw data into lines
        lines = self.raw_data.split('\n')

        # Initialize containers for spin up and spin down data
        spin_up_data = []
        spin_down_data = []

        # Flag to switch between spin up and spin down data collection
        collecting_spin_down = False

        # Iterate over lines to fill spin_up_data and spin_down_data
        for line in lines:
            if "SPIN UP ORBITALS" in line:
                collecting_spin_down = False
                continue
            elif "SPIN DOWN ORBITALS" in line:
                collecting_spin_down = True
                continue

            match = re.match(pattern_orbital_data, line)
            if match:
                # Extract orbital data
                no, occ, e_eh, e_ev = match.groups()
                data_row = [int(no), float(occ), float(
                    e_eh) * ureg.Eh, float(e_ev) * ureg.eV]

                # Append to the correct list based on the current section
                if collecting_spin_down:
                    spin_down_data.append(data_row)
                else:
                    spin_up_data.append(data_row)

        # Convert lists to pandas DataFrames
        columns = ['NO', 'OCC', 'E(Eh)', 'E(eV)']
        spin_up_df = pd.DataFrame(spin_up_data, columns=columns)
        spin_down_df = pd.DataFrame(spin_down_data, columns=columns)

        # Return a dictionary containing both DataFrames
        return Data(data={'Spin Up': spin_up_df, 'Spin Down': spin_down_df}, comment='Pandas DataFrames `Spin Up` and `Spin Down`. Energy is represented by pint object. Magnitude cane be extracted with .magnitude property.')


@AvailableBlocksOrca.register_block
class BlockOrcaTerminatedNormally(Block):
    data_available: bool = True

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'ORCA TERMINATED NORMALLY', None, self.raw_data

    def data(self) -> bool:
        '''
        returns True meaning that the block exists
        '''
        return Data(data={'Termination status': True}, comment='`Termination status` is always `True`, otherwise you wound`t find this block.')


@AvailableBlocksOrca.register_block
class BlockOrcaTotalRunTime(Block):
    data_available: bool = True

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'TOTAL RUN TIME', None, self.raw_data

    def data(self):
        # Define the regex pattern to match the total run time
        pattern = r"TOTAL RUN TIME:\s*(\d+)\s*days\s*(\d+)\s*hours\s*(\d+)\s*minutes\s*(\d+)\s*seconds\s*(\d+)\s*msec"

        # Search for the pattern in self.raw_data
        match = re.search(pattern, self.raw_data)

        # Check if a match is found
        if match:
            # Extract the components of the total run time
            days, hours, minutes, seconds, msec = match.groups()

            # Convert the extracted values to integers and milliseconds to seconds
            days = int(days)
            hours = int(hours)
            minutes = int(minutes)
            # Convert milliseconds to seconds
            seconds = int(seconds) + int(msec) / 1000.0

            # Create a timedelta object representing the total run time
            run_time = timedelta(days=days, hours=hours,
                                 minutes=minutes, seconds=seconds)

            return Data(data={'Run Time': run_time}, comment='`Run Time` is timedelta object')
        else:
            # Return None or raise an exception if no total run time data is found
            return None


@AvailableBlocksOrca.register_block
class BlockOrcaTimingsForIndividualModules(Block):
    data_available: bool = True

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        match = re.search(
            '^([ \\t]*Timings for individual modules:[ \\t]*)\\n', self.raw_data)

        body_start = match.end(1)
        header_raw = self.raw_data[:body_start]
        body_raw = self.raw_data[body_start:]

        return 'Timings for individual modules', header_raw, body_raw

    def data(self):
        # Initialize a dictionary to store the results
        timings_dict = {}

        # Define the regex pattern to match each module's timing information
        pattern = r"([a-zA-Z ]+)\s+\.\.\.\s+([\d\.]+) sec"

        # Find all matches in self.raw_data
        matches = re.findall(pattern, self.raw_data)

        # Process each match
        for module_name, time_sec in matches:
            # Convert time in seconds to a float
            time_sec = float(time_sec)

            # Convert time in seconds to a timedelta object
            module_time = timedelta(seconds=time_sec)

            # Add the module name and timedelta to the dictionary
            timings_dict[module_name.strip()] = module_time

        return Data(data=timings_dict, comment='Timings for different modules as timedelta objects')
