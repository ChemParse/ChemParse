import re
import uuid
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd
from pint import Quantity
from typing_extensions import Self

from .data import Data
from .units_and_constants import ureg


class ExtractionError(Exception):
    """Custom exception for energy extraction errors."""
    pass


class Element:
    p_type: str = 'element'
    p_subtype: str = 'default'

    def __init__(self, raw_data: str) -> None:
        self.raw_data = raw_data

    def get_structure(self) -> dict[Self, tuple | None]:
        '''
            Structure in a form of nested list
        '''
        return [self, []]

    def data(self) -> Data:
        warnings.warn(
            f"No procedure for analyzing the data found in type `{self.p_type}` subtype `{self.p_subtype}`, returning the raw data: {self.raw_data}"
        )
        return Data(data={'raw data': self.raw_data}, comment="No procedure for analyzing the data found, `raw data` collected.\nPlease contribute to the project if you have knowledge on how to extract data from it.")

    def to_html(self) -> str:
        class_name = f"{self.p_type.lower().replace(
            ' ', '-')}-{self.p_subtype.lower().replace(' ', '-')}"
        data = self.raw_data
        return f'<div class="{class_name}" data-p-type="{self.p_type}" data-p-subtype="{self.p_subtype}"><pre>{data}</pre></div>'

    def depth(self) -> int:
        return Element.max_depth(self.get_structure())

    @staticmethod
    def max_depth(d) -> int:
        if isinstance(d, list) and len(d) > 0:
            return 1 + max(Element.max_depth(v) for v in d)
        return 0

    @staticmethod
    def process_invalid_name(input_string: str) -> str:
        # Check if the string contains any letters; if not, return "unknown"
        if not any(char.isalpha() for char in input_string):
            return "Unknown: " + input_string[:21]

        # Remove all characters that are not letters or spaces
        cleaned_string = ''.join(
            char for char in input_string if char.isalpha() or char.isspace())

        # Return the first 30 characters of the cleaned string
        return cleaned_string[:30]


class Spacer(Element):
    p_type: str = 'spacer'

    def __init__(self, raw_data: str) -> None:
        super().__init__(raw_data=raw_data)

    def data(self) -> None:
        return None

class Block(Element):
    p_type: str = 'block'
    data_available: bool = False

    def __init__(self, raw_data: str, position: tuple | None = None) -> None:
        super().__init__(raw_data=raw_data)
        self.position: tuple | None = position

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return Element.process_invalid_name(self.raw_data), None, self.raw_data

    @staticmethod
    def header_preformat(header_raw: str) -> str:
        return header_raw

    @staticmethod
    def body_preformat(body_raw: str) -> str:
        return body_raw

    def to_html(self) -> str:
        readable_name, header, body = self.extract_name_header_and_body()
        class_name = f"{self.p_type.lower().replace(
            ' ', '-')}-{self.p_subtype.lower().replace(' ', '-')}"
        header_level = max(7-self.depth(), 1)
        header_html = f'<h{header_level}><pre>{self.header_preformat(
            header)}</pre></h{header_level}>' if header else ''
        body_html = f'<div class = data><pre>{
            self.body_preformat(body)}</pre></div>' if body else ''
        line_start, line_finish = self.position or (-1, -1)
        can_extract_data = 1 if self.data_available else 0
        return (f'<div class="{class_name}" data-p-type="{self.p_type}" '
                f'data-p-subtype="{self.p_subtype}" readable-name="{readable_name}" '
                f'start-line={line_start} finish-line={line_finish} '
                f'data_available={can_extract_data}>'
                f'{header_html+body_html}</div>')


class BlockUnrecognizedWithHeader(Block):
    p_subtype: str = 'unrecognized-with-header'

    def __init__(self, raw_data: str, position: tuple | None = None) -> None:
        super().__init__(raw_data=raw_data, position=position)

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        # Define regex pattern to split header and body
        pattern = r"^(([ \t]*[-*#]{7,}[ \t]*\n)(.*?)(\n[ \t]*[-*#]{7,}[ \t]*\n|$))"

        # Search for the pattern in self.raw_data using re.DOTALL to make '.' match newlines
        match = re.search(pattern, self.raw_data, re.DOTALL)

        if match:
            # Header is the content between the first and second header delimiters
            header_raw = match.group(1)

            # Body is the content after the second header delimiter
            # The end of the header delimiter is marked by the start of the body_raw
            body_start = match.end(1)
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
                        r"^[ \t]*[-*#=]{,1}(.*?)[ \t]*[-*#=]{,1}[ \t]*$", line)
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
                f'No header found in {self.raw_data}, and that is really weird as it was extracted based on the idea that there is a header in it')
            # If no match is found, put everything into header
            return Element.process_invalid_name(self.raw_data), None, self.raw_data


class BlockUnrecognizedFormat(Block):
    p_subtype: str = 'unrecognized-format'

    def data(self):
        warnings.warn(
            f'The extraction method for `{self.p_subtype}` block is not yet established, furthermore, the block looks not structured. Please contribute to the project if you have knowledge on how to extract data from it.')
        return self.raw_data


class BlockIcon(Block):
    p_subtype: str = 'icon'
    readable_name = 'Icon'
    data_available: bool = True

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Orca Icon', None, self.raw_data

    def data(self) -> Data:
        '''
        Icon is icon, noting to extract except for the ascii symbols
        '''
        Data(data={'Icon': self.raw_data}, comment="Raw `Icon` string")

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Orca Icon', None, self.raw_data


class BlockAllRightsReserved(Block):
    p_subtype: str = 'all-rights-reserved'

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Orca Icon', None, self.raw_data


class BlockFinalSinglePointEnergy(Block):
    p_subtype: str = 'final-single-point-energy'
    data_available: bool = True

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
            return Data(data={'Energy': energy}, comment='`Energy` in pint format, to extract the value in Eh, use method .magnitude')
        except ValueError:
            raise ExtractionError(
                f"Failed to convert the extracted energy {energy} to a floating-point number.")
        except Exception as e:
            # For any other unexpected exceptions, raise the original exception
            # You might want to log this exception or handle it differently depending on your application's needs
            raise e


class BlockScfConverged(Block):
    p_subtype: str = 'scf-converged'
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


# class BlockDipoleMoment(Block):
#     p_subtype: str = 'dipole-moment'
#     data_available: bool = True

#     def data(self) -> dict:
#         # Initialize the result dictionary
#         result = {}

#         # Define regex pattern for lines with "text: 3 numbers"
#         pattern_three_numbers = r"([a-zA-Z \(\).]+):\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)[ \t]*\n"
#         # Define regex pattern for lines with "text: 1 number"
#         pattern_one_number = r"([a-zA-Z \(\).]+):\s*(-?\d+\.\d+)[ \t]*(?:\n|\Z)"

#         # Find all matches for the three-number pattern
#         matches_three_numbers = re.findall(
#             pattern_three_numbers, self.raw_data)
#         for match in matches_three_numbers:
#             label, x, y, z = match
#             result[label.strip()] = np.array([float(x), float(y), float(z)])

#         # Find all matches for the one-number pattern
#         matches_one_number = re.findall(pattern_one_number, self.raw_data)
#         for match in matches_one_number:
#             label, value = match
#             if "(Debye)" in label:
#                 unit = "Debye"
#             else:
#                 unit = "a.u."
#             result[label.strip()] = float(
#                 value)*ureg.debye if unit == "Debye" else float(value)

#         return result


# class BlockOrbitalEnergies(Block):
#     p_subtype: str = 'orbital-energies'
#     data_available: bool = True

#     def data(self) -> dict[str, pd.DataFrame]:
#         # Define regex pattern for extracting orbital data lines
#         pattern_orbital_data = r"\s*(\d+)\s+([0-1]\.\d{4})\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*"

#         # Split the raw data into lines
#         lines = self.raw_data.split('\n')

#         # Initialize containers for spin up and spin down data
#         spin_up_data = []
#         spin_down_data = []

#         # Flag to switch between spin up and spin down data collection
#         collecting_spin_down = False

#         # Iterate over lines to fill spin_up_data and spin_down_data
#         for line in lines:
#             if "SPIN UP ORBITALS" in line:
#                 collecting_spin_down = False
#                 continue
#             elif "SPIN DOWN ORBITALS" in line:
#                 collecting_spin_down = True
#                 continue

#             match = re.match(pattern_orbital_data, line)
#             if match:
#                 # Extract orbital data
#                 no, occ, e_eh, e_ev = match.groups()
#                 data_row = [int(no), float(occ), float(
#                     e_eh) * ureg.Eh, float(e_ev) * ureg.eV]

#                 # Append to the correct list based on the current section
#                 if collecting_spin_down:
#                     spin_down_data.append(data_row)
#                 else:
#                     spin_up_data.append(data_row)

#         # Convert lists to pandas DataFrames
#         columns = ['NO', 'OCC', 'E(Eh)', 'E(eV)']
#         spin_up_df = pd.DataFrame(spin_up_data, columns=columns)
#         spin_down_df = pd.DataFrame(spin_down_data, columns=columns)

#         # Return a dictionary containing both DataFrames
#         return {'Spin Up': spin_up_df, 'Spin Down': spin_down_df}


# class BlockTerminatedNormally(Block):
#     p_subtype: str = 'terminated-normally'
#     data_available: bool = True

#     def data(self) -> bool:
#         '''
#         returns True meaning that the block exists
#         '''
#         return True


# class BlockTotalRunTime(Block):
#     p_subtype: str = 'total-run-time'
#     data_available: bool = True

#     def data(self):
#         # Define the regex pattern to match the total run time
#         pattern = r"TOTAL RUN TIME:\s*(\d+)\s*days\s*(\d+)\s*hours\s*(\d+)\s*minutes\s*(\d+)\s*seconds\s*(\d+)\s*msec"

#         # Search for the pattern in self.raw_data
#         match = re.search(pattern, self.raw_data)

#         # Check if a match is found
#         if match:
#             # Extract the components of the total run time
#             days, hours, minutes, seconds, msec = match.groups()

#             # Convert the extracted values to integers and milliseconds to seconds
#             days = int(days)
#             hours = int(hours)
#             minutes = int(minutes)
#             # Convert milliseconds to seconds
#             seconds = int(seconds) + int(msec) / 1000.0

#             # Create a timedelta object representing the total run time
#             run_time = timedelta(days=days, hours=hours,
#                                  minutes=minutes, seconds=seconds)

#             return run_time
#         else:
#             # Return None or raise an exception if no total run time data is found
#             return None


# class BlockTimingsForIndividualModules(Block):
#     p_subtype: str = 'timings-for-individual-modules'
#     data_available: bool = True

#     def data(self):
#         # Initialize a dictionary to store the results
#         timings_dict = {}

#         # Define the regex pattern to match each module's timing information
#         pattern = r"([a-zA-Z ]+)\s+\.\.\.\s+([\d\.]+) sec"

#         # Find all matches in self.raw_data
#         matches = re.findall(pattern, self.raw_data)

#         # Process each match
#         for module_name, time_sec in matches:
#             # Convert time in seconds to a float
#             time_sec = float(time_sec)

#             # Convert time in seconds to a timedelta object
#             module_time = timedelta(seconds=time_sec)

#             # Add the module name and timedelta to the dictionary
#             timings_dict[module_name.strip()] = module_time

#         return timings_dict
