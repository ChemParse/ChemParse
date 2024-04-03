import re
from datetime import timedelta

import numpy as np
import pandas as pd

from .data import Data
from .elements import AvailableBlocksGeneral, Block, Element, ExtractionError
from .logging_config import logger
from .units_and_constants import ureg


class AvailableBlocksOrca(AvailableBlocksGeneral):
    """
    A class to store all available blocks for ORCA.
    """
    blocks: dict[str, type[Element]] = {}


@AvailableBlocksOrca.register_block
class BlockOrcaWithStandardHeader(Block):
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
                logger.warning(
                    f'No readable name found in the header: {header_raw}')
                readable_name = Element.process_invalid_name(self.raw_data)

            return readable_name, header_raw, body_raw
        else:
            logger.warning(
                f'No header found in\n{self.raw_data}\n, and that is really weird as it was extracted based on the idea that there is a header in it')
            # If no match is found, put everything into header
            return Element.process_invalid_name(self.raw_data), None, self.raw_data


@AvailableBlocksOrca.register_block
class BlockOrcaUnrecognizedWithSingeLineHeader(BlockOrcaWithStandardHeader):
    pass


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
    """
    The block captures and stores All rights reserved message from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

                                            #,                                       
                                            ###                                      
                                            ####                                     
                                            #####                                    
                                            ######                                   
                                           ########,                                 
                                     ,,################,,,,,                         
                               ,,#################################,,                 
                          ,,##########################################,,             
                       ,#########################################, ''#####,          
                    ,#############################################,,   '####,        
                  ,##################################################,,,,####,       
                ,###########''''           ''''###############################       
              ,#####''   ,,,,##########,,,,          '''####'''          '####       
            ,##' ,,,,###########################,,,                        '##       
           ' ,,###''''                  '''############,,,                           
         ,,##''                                '''############,,,,        ,,,,,,###''
      ,#''                                            '''#######################'''  
     '                                                          ''''####''''         
             ,#######,   #######,   ,#######,      ##                                
            ,#'     '#,  ##    ##  ,#'     '#,    #''#        ######   ,####,        
            ##       ##  ##   ,#'  ##            #'  '#       #        #'  '#        
            ##       ##  #######   ##           ,######,      #####,   #    #        
            '#,     ,#'  ##    ##  '#,     ,#' ,#      #,         ##   #,  ,#        
             '#######'   ##     ##  '#######'  #'      '#     #####' # '####'        
    """
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
    """
    The block captures and stores All rights reserved message from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        #######################################################
        #                        -***-                        #
        #          Department of theory and spectroscopy      #
        #    Directorship and core code : Frank Neese         #
        #        Max Planck Institute fuer Kohlenforschung    #
        #                Kaiser Wilhelm Platz 1               #
        #                 D-45470 Muelheim/Ruhr               #
        #                      Germany                        #
        #                                                     #
        #                  All rights reserved                #
        #                        -***-                        #
        #######################################################
    """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'All Rights Reserved', None, self.raw_data


@AvailableBlocksOrca.register_block
class BlockOrcaFinalSinglePointEnergy(Block):
    """
    The block captures and stores Final single point energy from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        -------------------------   --------------------
        FINAL SINGLE POINT ENERGY      -379.259324337759
        -------------------------   --------------------
    """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'FINAL SINGLE POINT ENERGY', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`orcaparse.data.Data` object that contains:

            - :class:`pint.Quantity` `Energy`
        :rtype: Data
        """
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
    """
    The block captures and stores SCF convergence message from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        *****************************************************
        *                     SUCCESS                       *
        *           SCF CONVERGED AFTER  20 CYCLES          *
        *****************************************************
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'SCF convergence message', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`orcaparse.data.Data` object that contains:

            - :class:`bool` for `Success` of the extraction
            - :class:`int` for amount of `Cycles`
        :rtype: Data
        """
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
    """
    The block captures and stores Dipole moment from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        -------------
        DIPOLE MOMENT
        -------------
                                        X             Y             Z
        Electronic contribution:      0.00000       0.00000       4.52836
        Nuclear contribution   :      0.00000       0.00000      -8.26530
                                -----------------------------------------
        Total Dipole Moment    :      0.00000       0.00000      -3.73694
                                -----------------------------------------
        Magnitude (a.u.)       :      3.73694
        Magnitude (Debye)      :      9.49854
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """
        :return: :class:`orcaparse.data.Data` object that contains:

            - :class:`numpy.ndarray`'s of contributions
            - :class:`pint.Quantity` `Magnitude (Debye)` -- total dipole moment. The magnitude in Debye can be extracted from :class:`pint.Quantity` with .magnitude property.
        :rtype: Data
        """
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
class BlockOrcaTerminatedNormally(Block):
    """
    The block captures and stores Termination status from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        ****ORCA TERMINATED NORMALLY****
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'ORCA TERMINATED NORMALLY', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`orcaparse.data.Data` object that contains:

            - :class:`bool` `Termination status`
                is always `True`, otherwise you wound`t find this block.
        :rtype: Data
        """
        return Data(data={'Termination status': True}, comment='`Termination status` is always `True`, otherwise you wound`t find this block.')


@AvailableBlocksOrca.register_block
class BlockOrcaTotalRunTime(Block):
    """
    The block captures and stores Total run time from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        TOTAL RUN TIME: 0 days 0 hours 1 minutes 20 seconds 720 msec
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'TOTAL RUN TIME', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`orcaparse.data.Data` object that contains:

            - :class:`datetime.timedelta` `Run Time`
                representing the total run time in days, hours, minutes, seconds, and milliseconds.
        :rtype: Data
        """
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

    def data(self) -> Data:
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


@AvailableBlocksOrca.register_block
class BlockOrcaOrbitalEnergies(BlockOrcaWithStandardHeader):
    """
    The block captures and stores orbital energies and occupation numbers from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        ----------------
        ORBITAL ENERGIES
        ----------------
        NO   OCC          E(Eh)            E(eV)
        0   2.0000     -14.038014      -381.9938
        1   2.0000     -13.986101      -380.5812
        2   2.0000      -0.200360        -5.4521
        3   0.0000      -0.065149        -1.7728
        4   0.0000      -0.060749        -1.6531
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """
        :return: :class:`orcaparse.data.Data` object that contains:

            - :class:`pandas.DataFrame` `Orbitals`
                that includes the columns `NO`, `OCC`, `E(Eh)`, and `E(eV)`.
                The `E(Eh)` and `E(eV)` columns represent the same energy values in different units (Hartree and electronvolts, respectively).
                These values are extracted from the output file and should match unless there's an error in the ORCA output.
        :rtype: Data
        """
        # Define regex pattern for extracting orbital data lines
        pattern_orbital_data = r"\s*(\d+)\s+(\d+\.\d{4})\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*"

        # Split the raw data into lines
        lines = self.raw_data.split('\n')

        columns = ['NO', 'OCC', 'E(Eh)', 'E(eV)']

        if "SPIN UP ORBITALS" in self.raw_data:

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
            spin_up_df = pd.DataFrame(spin_up_data, columns=columns)
            spin_down_df = pd.DataFrame(spin_down_data, columns=columns)

            # Return a dictionary containing both DataFrames
            return Data(data={'Spin Up': spin_up_df, 'Spin Down': spin_down_df},
                        comment="""Pandas DataFrames `Spin Up` and `Spin Down` with columns `NO`, `OCC`, `E(Eh)`, `E(eV)`.
                        `E(Eh)` and `E(eV)` are captured from different columns in the file, but should represent the same quantity unless there is an error in ORCA.
                        Energy is represented by pint object. Magnitude cane be extracted with .magnitude method.""")
        else:
            spin_data = []
            for line in lines:
                match = re.match(pattern_orbital_data, line)
                if match:
                    # Extract orbital data
                    no, occ, e_eh, e_ev = match.groups()
                    data_row = [int(no), float(occ), float(
                        e_eh) * ureg.Eh, float(e_ev) * ureg.eV]
                    spin_data.append(data_row)

            spin_df = pd.DataFrame(spin_data, columns=columns)

            return Data(data={'Orbitals': spin_df}, comment="""Pandas DataFrame `Orbitals` with columns `NO`, `OCC`, `E(Eh)`, `E(eV)`.
                        `E(Eh)` and `E(eV)` are captured from different columns in the file, but should represent the same quantity unless there is an error in ORCA.
                        Energy is represented by pint object. Magnitude cane be extracted with .magnitude method.""")


@AvailableBlocksOrca.register_block
class BlockOrcaTotalScfEnergy(BlockOrcaWithStandardHeader):
    """
    The block captures and stores Total SCF Energy from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        ----------------
        TOTAL SCF ENERGY
        ----------------
        Total Energy       :         -379.43011624 Eh          -10324.81837 eV

        Components:
        Nuclear Repulsion  :          376.82729155 Eh           10253.99191 eV
        Electronic Energy  :         -756.25740779 Eh          -20578.81027 eV
        One Electron Energy:        -1258.15590029 Eh          -34236.16258 eV
        Two Electron Energy:          501.89849250 Eh           13657.35231 eV

        Virial components:
        Potential Energy   :         -757.03875139 Eh          -20600.07171 eV
        Kinetic Energy     :          377.60863515 Eh           10275.25335 eV
        Virial Ratio       :            2.00482373


        DFT components:
        N(Alpha)           :       31.000002566977 electrons
        N(Beta)            :       31.000002566977 electrons
        N(Total)           :       62.000005133953 electrons
        E(X)               :      -51.506470961700 Eh       
        E(C)               :       -2.061628237949 Eh       
        E(XC)              :      -53.568099199649 Eh       
        DFET-embed. en.    :        0.000000000000 Eh      
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`orcaparse.data.Data` object that contains:
            - Dictionary with different sections of the block as keys and their values as sub-dictionaries.
            The values are :class:`pint.Quantity`.If there are more then one value in a line, they are stored in a sub-dictionary with the unit as key.
            It is expected for the values to represent the same quantity, if they do not, there is an error in ORCA.

            Output blocks example from ORCA 6:

            .. code-block:: none

                {
                'Total Energy': {'Value in Eh': <Quantity(-379.430116, 'hartree')>, 'Value in eV': <Quantity(-10324.8184, 'electron_volt')>},
                'Components': {'Nuclear Repulsion': {'Value in Eh': <Quantity(376.827292, 'hartree')>, 'Value in eV': <Quantity(10253.9919, 'electron_volt')>}, 'Electronic Energy': {'Value in Eh': <Quantity(-756.257408, 'hartree')>, 'Value in eV': <Quantity(-20578.8103, 'electron_volt')>}, 'One Electron Energy': {'Value in Eh': <Quantity(-1258.1559, 'hartree')>, 'Value in eV': <Quantity(-34236.1626, 'electron_volt')>}, 'Two Electron Energy': {'Value in Eh': <Quantity(501.898492, 'hartree')>, 'Value in eV': <Quantity(13657.3523, 'electron_volt')>}},
                'Virial components': {'Potential Energy': {'Value in Eh': <Quantity(-757.038751, 'hartree')>, 'Value in eV': <Quantity(-20600.0717, 'electron_volt')>}, 'Kinetic Energy': {'Value in Eh': <Quantity(377.608635, 'hartree')>, 'Value in eV': <Quantity(10275.2534, 'electron_volt')>}, 'Virial Ratio': 2.00482373},
                'DFT components': {'N(Alpha)': <Quantity(31.0000026, 'electron')>, 'N(Beta)': <Quantity(31.0000026, 'electron')>, 'N(Total)': <Quantity(62.0000051, 'electron')>, 'E(X)': <Quantity(-51.506471, 'hartree')>, 'E(C)': <Quantity(-2.06162824, 'hartree')>, 'E(XC)': <Quantity(-53.5680992, 'hartree')>, 'DFET-embed. en.': <Quantity(0.0, 'hartree')>}
                }

        :rtype: Data
        """
        data_dict = {}
        current_section = None

        for line in self.raw_data.split("\n"):
            line = line.strip()
            if ":" in line:
                # Find all number positions and their corresponding values
                numbers = [
                    (m.start(0), m.group(0))
                    for m in re.finditer(r"-?\d+\.?\d*|\d*\.?\d+", line)
                ]

                if len(numbers) == 0:  # No numbers, so it's a new section
                    current_section = line.split(":")[0]
                    data_dict[current_section] = {}
                else:
                    key, values = line.split(":", 1)
                    key = key.strip()  # Remove leading/trailing whitespaces
                    if len(numbers) == 1:  # Single number, treat it directly
                        value = ureg.parse_expression(values.strip())
                        if current_section is not None:
                            data_dict[current_section][key] = value
                        else:
                            data_dict[key] = value
                    else:  # More than one number, split and process each
                        value_dict = {}
                        split = values.split()
                        assert len(
                            split) % 2 == 0, f"Odd number of values in {values}"
                        for i in range(0, len(split), 2):
                            value = ureg.parse_expression(
                                split[i]+' '+split[i+1])
                            unit = split[i+1]
                            value_dict['Value in '+unit] = value

                        if current_section is not None:
                            data_dict[current_section][key] = value_dict
                        else:
                            data_dict[key] = value_dict

        return Data(data=data_dict, comment="""Dictionary with different sections of the block as keys and their values as sub-dictionaries.
                    The values are pint objects.If there are more then one value in a line, they are stored in a sub-dictionary with the unit as key.
                    It is expected for the values to represent the same quantity, if they do not, there is an error in ORCA.
                    
                    Output blocks example from for ORCA 6:

                    Total Energy: {'Value in Eh': <Quantity(-379.430116, 'hartree')>, 'Value in eV': <Quantity(-10324.8184, 'electron_volt')>}
                    Components: {'Nuclear Repulsion': {'Value in Eh': <Quantity(376.827292, 'hartree')>, 'Value in eV': <Quantity(10253.9919, 'electron_volt')>}, 'Electronic Energy': {'Value in Eh': <Quantity(-756.257408, 'hartree')>, 'Value in eV': <Quantity(-20578.8103, 'electron_volt')>}, 'One Electron Energy': {'Value in Eh': <Quantity(-1258.1559, 'hartree')>, 'Value in eV': <Quantity(-34236.1626, 'electron_volt')>}, 'Two Electron Energy': {'Value in Eh': <Quantity(501.898492, 'hartree')>, 'Value in eV': <Quantity(13657.3523, 'electron_volt')>}}
                    Virial components: {'Potential Energy': {'Value in Eh': <Quantity(-757.038751, 'hartree')>, 'Value in eV': <Quantity(-20600.0717, 'electron_volt')>}, 'Kinetic Energy': {'Value in Eh': <Quantity(377.608635, 'hartree')>, 'Value in eV': <Quantity(10275.2534, 'electron_volt')>}, 'Virial Ratio': 2.00482373}
                    DFT components: {'N(Alpha)': <Quantity(31.0000026, 'electron')>, 'N(Beta)': <Quantity(31.0000026, 'electron')>, 'N(Total)': <Quantity(62.0000051, 'electron')>, 'E(X)': <Quantity(-51.506471, 'hartree')>, 'E(C)': <Quantity(-2.06162824, 'hartree')>, 'E(XC)': <Quantity(-53.5680992, 'hartree')>, 'DFET-embed. en.': <Quantity(0.0, 'hartree')>}
                    
                    """)
