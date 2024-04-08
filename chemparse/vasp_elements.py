import re
import warnings
from datetime import timedelta

import bitmath
import numpy as np
import pandas as pd

from .data import Data
from .elements import AvailableBlocksGeneral, Block, Element, ExtractionError
from .logging_config import logger
from .units_and_constants import ureg


class AvailableBlocksVasp(AvailableBlocksGeneral):
    """
    A class to store all available blocks for Wasp.
    """
    blocks: dict[str, type[Element]] = {}


@AvailableBlocksVasp.register_block
class BlockVaspWithStandardHeader(Block):
    """
    Handles blocks with a standard header format by extending the `Block` class.

    This class is designed to process data blocks that come with a standardized header marked by lines of repeating special characters (e.g., '-', '*', '#'). It overrides the `extract_name_header_and_body` method to parse these headers, facilitating the separation of the block into name, header, and body components for easier readability and manipulation.

    Parameters
    ----------
    None

    Methods
    -------
    extract_name_header_and_body()
        Parses the block's content to extract the name, header (if present), and body, adhering to a standard header format.

    Raises
    ------
    Warning
        If the block's content does not contain a recognizable header, indicating that the format may not conform to expectations.
    """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        """
        Identifies and separates the name, header, and body of the block based on a standard header format.

        Utilizes regular expressions to discern the header portion from the body, processing the header to extract a distinct name and the header content. The text following the header is treated as the body of the block.

        Returns
        -------
        tuple[str, str | None, str]
            The name of the block, the header content (or None if a header is not present), and the body of the block.

        """
        # Define regex pattern to split header and body
        pattern = r"((?:^[ \t]*\n)((?:^(?!\n).*\n){1,2})(?:^ {1,2}-{20,}[ \t]*$))"

        # Search for the pattern in self.raw_data
        match = re.search(pattern, self.raw_data, re.MULTILINE)

        if match:
            # Header is the content between the first and second header delimiters

            # Body is the content after the second header delimiter
            # The end of the header delimiter is marked by the start of the body_raw
            body_start = match.end(1)
            header_raw = self.raw_data[:body_start]
            body_raw = self.raw_data[body_start:]

            readable_name = match.group(2).strip()

            if len(readable_name) < 2:
                logger.warning(
                    f'No readable name found in the header: {header_raw}')
                readable_name = Element.process_invalid_name(self.raw_data)

            return readable_name, header_raw, body_raw
        else:
            logger.warning(
                f'No header found in\n{self.raw_data}\n, and that is really weird as it was extracted based on the idea that there is a header in it')
            # If no match is found, put everything into header
            return Element.process_invalid_name(self.raw_data), None, self.raw_data


@AvailableBlocksVasp.register_block
class BlockVaspWithSingleLineHeader(BlockVaspWithStandardHeader):
    pass


@AvailableBlocksVasp.register_block
class BlockVaspFreeEnergyOfTheIonElectronSystem(BlockVaspWithSingleLineHeader):
    """
    The block captures and stores TD-DFT excited states data for singlets from VASP output files.

    **Example of VASP Output:**

    .. code-block:: none

        Free energy of the ion-electron system (eV)
        ---------------------------------------------------
        alpha Z        PSCENC =       856.26359874
        Ewald energy   TEWEN  =    124561.82273922
        -Hartree energ DENC   =   -158586.56090100
        -exchange      EXHF   =         0.00000000
        -V(xc)+E(xc)   XCENC  =      1621.64044307
        PAW double counting   =     40935.10832877   -40536.82457645
        entropy T*S    EENTRO =        -0.11542442
        eigenvalues    EBANDS =     -6251.33904632
        atomic energy  EATOM  =     37032.80098409
        Solvation  Ediel_sol  =         0.00000000
        ---------------------------------------------------
        free energy    TOTEN  =      -367.20385430 eV

        energy without entropy =     -367.08842988  energy(sigma->0) =     -367.14614209




    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`chemparse.data.Data` object that contains:
            - :class:`pint.Quantity`'s for energy components in eV
            - :class:`tuple`'s of :class:`pint.Quantity`'s for `PAW double counting` in eV if present in the block


            Parsed data example:

            .. code-block:: none

                {'alpha Z        PSCENC': 856.26359874 <Unit('electron_volt')>,
                'Ewald energy   TEWEN': 124531.99989886 <Unit('electron_volt')>,
                '-Hartree energ DENC': -158146.11578475 <Unit('electron_volt')>,
                '-exchange      EXHF': 0.0 <Unit('electron_volt')>,
                '-V(xc)+E(xc)   XCENC': 1631.52209578 <Unit('electron_volt')>,
                'PAW double counting': (29408.33949787 <Unit('electron_volt')>,
                -29013.20232444 <Unit('electron_volt')>),
                'entropy T*S    EENTRO': -0.07591362 <Unit('electron_volt')>,
                'eigenvalues    EBANDS': -1504.38797381 <Unit('electron_volt')>,
                'atomic energy  EATOM': 37032.80098409 <Unit('electron_volt')>,
                'Solvation  Ediel_sol': 0.0 <Unit('electron_volt')>,
                'free energy    TOTEN': 4797.14407872 <Unit('electron_volt')>,
                'energy without entropy': 4797.21999234 <Unit('electron_volt')>,
                'energy(sigma->0)': 4797.18203553 <Unit('electron_volt')>
                }

        :rtype: Data
        """
        extracted_values = {}

        for line in self.raw_data.split("\n"):
            # Skip lines without "=" as they don't contain key-value pairs
            if "=" not in line:
                continue

            # Clean the line to remove potential "eV" and excess whitespaces
            cleaned_line = line.replace("eV", "").strip()

            # Handle special case for lines with two sets of key-value pairs
            if "energy(sigma->0)" in cleaned_line:
                # Split based on "energy(sigma->0)" to separate the two key-value pairs
                parts = cleaned_line.split("energy(sigma->0) =")
                # Extract the first key-value pair
                key_1, value_1 = parts[0].split("=")
                extracted_values[key_1.strip()] = float(
                    value_1.strip())*ureg.eV
                # Extract the second key-value pair
                extracted_values["energy(sigma->0)"] = float(
                    parts[1].strip())*ureg.eV
            else:
                # For regular and PAW double counting cases, split at "="
                parts = cleaned_line.split("=")
                key = parts[0].strip()

                value_parts = parts[1].split()

                # Check for PAW double counting case with two or more values
                if len(value_parts) > 1:
                    # Convert each value part to float and multiply by ureg.eV, then store as a tuple
                    values = tuple(
                        float(value) * ureg.eV for value in value_parts)
                    extracted_values[key] = values
                else:
                    # Regular case with a single value
                    extracted_values[key] = float(parts[1].strip()) * ureg.eV

        return Data(data=extracted_values, comment="""Parsed data from the block with energy components as pint.Quantity in eV and PAW double counting as a tuple of pint.Quantities in eV if present.""")


@AvailableBlocksVasp.register_block
class BlockVaspGeneralTiming(Block):
    """
    The block captures and stores the Timings for the VASP output files.

    **Example of VASP Output:**

    .. code-block:: none

        General timing and accounting informations for this job:
        ========================================================

                  Total CPU time used (sec):     1410.943
                            User time (sec):     1394.056
                          System time (sec):       16.888
                         Elapsed time (sec):     1460.875

                   Maximum memory used (kb):      201324.
                   Average memory used (kb):          N/A

                          Minor page faults:       310377
                          Major page faults:          212
                 Voluntary context switches:         5646

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`chemparse.data.Data` object that contains:
            - :class:`datetime.timedelta`'s for time components in seconds
            - :class:`bitmath.Byte`'s for memory components in bytes
            - :class:`bitmath.kB`'s for memory components in kilobytes
            - :class:`bitmath.MB`'s for memory components in megabytes
            - :class:`bitmath.GB`'s for memory components in gigabytes
            - :class:`pint.Quantity`'s for other components with units
            - `N/A` for non-applicable values
            - `str` for other values


            Parsed data example:

            .. code-block:: none

                {'Total CPU time used': datetime.timedelta(seconds=1410, microseconds=943000),
                'User time': datetime.timedelta(seconds=1394, microseconds=56000),
                'System time': datetime.timedelta(seconds=16, microseconds=888000),
                'Elapsed time': datetime.timedelta(seconds=1460, microseconds=875000),
                'Maximum memory used': kB(201324.0),
                'Average memory used': 'N/A',
                'Minor page faults': '310377',
                'Major page faults': '212',
                'Voluntary context switches': '5646'
                }

        :rtype: Data
        """

        # Define a dictionary to hold the extracted data
        extracted_data = {}

        # Split the string into lines for processing
        lines = self.raw_data.strip().split('\n')

        # Function to extract unit from the key if present
        def extract_unit(key):
            if '(' in key and ')' in key:
                start = key.find('(') + 1
                end = key.find(')')
                unit = key[start:end]
                # Adjust to remove the unit and preceding space
                key = key[:start-2]
                return key, unit
            return key, None

        # Iterate over each line and extract data
        for line in lines:
            # Split each line at the colon
            parts = line.split(':')
            if len(parts) == 2 and parts[1].strip() != "":
                raw_key = parts[0].strip()
                value = parts[1].strip()

                # Extract unit from the key if present
                key, unit = extract_unit(raw_key)

                # Check if a unit was found and process accordingly
                if unit:
                    if unit == "sec":  # Handle seconds separately
                        seconds = float(value)
                        extracted_data[key] = timedelta(seconds=seconds)
                    elif unit == "b":  # Handle bytes separately
                        if value != "N/A":
                            extracted_data[key] = bitmath.Byte(float(value))
                        else:
                            extracted_data[key] = value
                    elif unit == "kb":  # Handle kilobytes separately
                        if value != "N/A":
                            extracted_data[key] = bitmath.kB(float(value))
                        else:
                            extracted_data[key] = value
                    elif unit == "Mb":  # Handle megabytes separately
                        if value != "N/A":
                            extracted_data[key] = bitmath.MB(float(value))
                        else:
                            extracted_data[key] = value
                    elif unit == "Gb":  # Handle gigabytes separately
                        if value != "N/A":
                            extracted_data[key] = bitmath.GB(float(value))
                        else:
                            extracted_data[key] = value
                    else:  # For other units, use ureg to create Quantity objects
                        if value != "N/A":  # Check for non-applicable values
                            extracted_data[key] = float(value) * ureg(unit)
                        else:
                            extracted_data[key] = value
                else:
                    extracted_data[key] = value

        return Data(data=extracted_data, comment="""Parsed data from the block with energy components as pint.Quantity in eV and PAW double counting as a tuple of pint.Quantities in eV if present.""")
