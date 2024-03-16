import re
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd
from pint import Quantity

from .units_and_constants import ureg


class ExtractionError(Exception):
    """Custom exception for energy extraction errors."""
    pass


class OrcaElement:
    p_type = 'element'
    p_subtype = 'default'

    def __init__(self, raw_data: str, header_level: int = 1) -> None:
        self.raw_data = raw_data
        self.header_level = header_level

    def data(self) -> str:
        warnings.warn(
            "No procedure for analyzing the data found, returning the raw data"
        )
        return self.raw_data

    def to_html(self) -> str:
        class_name = f"{self.p_type.lower().replace(' ', '-')}-{self.p_subtype.lower().replace(' ', '-')}"
        data = self.raw_data
        return f'<span class="{class_name}" data-p-type="{self.p_type}" data-p-subtype="{self.p_subtype}"><pre>{data}</pre></span>'


class OrcaSpacer(OrcaElement):
    p_type = 'spacer'
    p_subtype = 'default'

    def __init__(self, raw_data: str, header_level: int = 1) -> None:
        super().__init__(raw_data=raw_data, header_level=header_level)

    def data(self) -> None:
        return None

    def to_html(self) -> str:
        class_name = f"{self.p_type.lower().replace(' ', '-')}-{self.p_subtype.lower().replace(' ', '-')}"
        data = self.raw_data.replace('\n', '<br>')+'<br>'
        return f'<div class="{class_name}" data-p-type="{self.p_type}" data-p-subtype="{self.p_subtype}">{data}</div>'


class OrcaText(OrcaElement):

    def __init__(self, raw_data: str, header_level: int = 1) -> None:
        super().__init__(raw_data=raw_data, header_level=header_level)

    def to_html(self) -> str:
        if self.raw_data is None or len(self.raw_data) == 0:
            return ''
        return f'<pre>{self.raw_data}</pre>'


class OrcaHeader(OrcaElement):

    def __init__(self, raw_data: str, header_level: int = 1) -> None:
        super().__init__(raw_data=raw_data, header_level=header_level)

    def to_html(self) -> str:
        return f'<h{self.header_level}><pre>{self.raw_data}</pre></h{self.header_level}>'


class OrcaBlock(OrcaElement):
    p_type = 'block'
    p_subtype = 'default'
    data_available = False

    def __init__(self, raw_data: str, header_level: int = 1, position: tuple | None = None) -> None:
        super().__init__(raw_data=raw_data, header_level=header_level)
        self.readable_name: str = 'Unknown'
        self.header = OrcaHeader(raw_data, self.header_level)
        self.body: OrcaText = OrcaText(None, self.header_level)
        self.position: tuple | None = position

    def to_html(self) -> str:
        class_name = f"{self.p_type.lower().replace(' ', '-')}-{self.p_subtype.lower().replace(' ', '-')}"
        header_html = self.header.to_html()
        body_html = self.body.to_html() if self.body else ''
        data = header_html+body_html
        line_start, line_finish = self.position or (-1, -1)
        can_extract_data = 1 if self.data_available else 0
        return f'<div class="{class_name}" data-p-type="{self.p_type}" data-p-subtype="{self.p_subtype}" readable-name="{self.readable_name}" start-line={line_start} finish-line={line_finish} data_available={can_extract_data}>{data}</div>'


class OrcaBlockUnrecognizedWithBody(OrcaBlock):
    p_subtype = 'unrecognized-with-header'

    def __init__(self, raw_data: str, header_level: int = 1, position: tuple | None = None) -> None:
        super().__init__(raw_data=raw_data, header_level=header_level, position=position)
        header_raw, body_raw = self.extract_header_and_body()
        self.header = OrcaHeader(header_raw, header_level)
        self.body = OrcaText(body_raw, header_level)
        print(f'{header_raw = }')
        self.readable_name: str = self.extract_readable_name(header_raw)

    def extract_readable_name(self, header_raw: str) -> str:
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
            warnings.warn(f'No readable name found in the header:{header_raw}')

        return readable_name

    def extract_header_and_body(self) -> tuple[str, str]:
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

            return header_raw, body_raw
        else:
            warnings.warn(
                f'No header found in {self.raw_data}, and that is really weird. Assuming that the whole block is the header')
            # If no match is found, put everything into header
            return self.raw_data, ''

    def data(self):
        warnings.warn('This block is not recognized, returning the raw data')
        return self.raw_data


class OrcaBlockUnrecognizedFormat(OrcaBlock):
    p_subtype = 'unrecognized-format'

    def data(self):
        warnings.warn(
            f'The extraction method for {self.p_subtype} block is not yet established, furthermore, the block looks not structured. Please contribute to the project if you have knowledge on how to extract data from it.')
        return self.raw_data


class OrcaBlockIcon(OrcaBlock):
    p_subtype = 'icon'

    def data(self):
        warnings.warn(
            f'The extraction method for {self.p_subtype} block is not yet established. Please contribute to the project if you have knowledge on how to extract data from it.')
        return self.raw_data


class OrcaBlockAllRightsReserved(OrcaBlock):
    p_subtype = 'all-rights-reserved'


class OrcaBlockFinalSinglePointEnergy(OrcaBlock):
    p_subtype = 'final-single-point-energy'
    data_available = True

    def data(self) -> Quantity:
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
            return float(energy) * ureg.Eh
        except ValueError:
            raise ExtractionError(
                f"Failed to convert the extracted energy {energy} to a floating-point number.")
        except Exception as e:
            # For any other unexpected exceptions, raise the original exception
            # You might want to log this exception or handle it differently depending on your application's needs
            raise e


class OrcaBlockScfConverged(OrcaBlock):
    p_subtype = 'scf-converged'
    data_available = True

    def data(self) -> dict:
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

        return result


class OrcaBlockDipoleMoment(OrcaBlock):
    p_subtype = 'dipole-moment'
    data_available = True

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

        return result


class OrcaBlockOrbitalEnergies(OrcaBlock):
    p_subtype = 'orbital-energies'
    data_available = True

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
        return {'Spin Up': spin_up_df, 'Spin Down': spin_down_df}


class OrcaBlockTerminatedNormally(OrcaBlock):
    p_subtype = 'terminated-normally'
    data_available = True

    def data(self) -> bool:
        '''
        returns True meaning that the block exists
        '''
        return True


class OrcaBlockTotalRunTime(OrcaBlock):
    p_subtype = 'total-run-time'
    data_available = True

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

            return run_time
        else:
            # Return None or raise an exception if no total run time data is found
            return None


class OrcaBlockTimingsForIndividualModules(OrcaBlock):
    p_subtype = 'timings-for-individual-modules'
    data_available = True

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

        return timings_dict
