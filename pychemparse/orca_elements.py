import re
from datetime import timedelta
from io import StringIO
from typing import Optional

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


@AvailableBlocksOrca.register_block
class BlockOrcaVersion(Block):
    """
    The block captures and stores ORCA version from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

                        Program Version 5.0.0 -  RELEASE  -
                                (SVN: $Rev: 19529$)
                ($Date: 2021-06-28 11:36:33 +0200 (Mo, 28 Jun 2021) $)
    """

    data_available: bool = True

    def readable_name(self) -> str:
        return 'Program Version'

    def data(self) -> Data:
        """
        :return: :class:`pychemparse.data.Data` object that contains:

                - :class:`str` `Version`
        :rtype: Data
        """

        def extract_version(data):

            pattern = r'Program Version ([^\s]+)'

            match = re.search(pattern, data)

            if match:
                return match.group(1)
            else:
                return None

        version = extract_version(self.raw_data)

        return Data(data={'Version': version}, comment='`Version` is a string with the version number')


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
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'FINAL SINGLE POINT ENERGY', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`pychemparse.data.Data` object that contains:

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
        :return: :class:`pychemparse.data.Data` object that contains:

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
class BlockOrcaErrorMessage(Block):
    """
    The block captures and stores ORCA error message from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        ----------------------------------------------------------------------------
                                    ERROR !!!
            The TS optimization did not converge but reached the maximum
            number of optimization cycles.
            As a subsequent Frequencies calculation has been requested
            ORCA will abort at this point of the run.
        ----------------------------------------------------------------------------



    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Orca Error', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`str` for the `Error` message if present

        Parsed data example:

        .. code-block:: none

            {'Error': 'ERROR !!!
            The optimization did not converge but reached the maximum
            number of optimization cycles.
            As a subsequent Frequencies calculation has been requested
            ORCA will abort at this point of the run.
            Please restart the calculation with the lowest energy geometry and/or
            a larger maxiter for the geometry optimization.'}

        :rtype: Data

        """
        # Define regex pattern to match the error message using the provided pattern
        error_pattern = r"(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)(?:[ \t]*ERROR !!![ \t]*\n)(?:^(?!^[ \t]*[\-\*\#\=]{5,}.*$).*\n)*(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)"

        # Search for the error message in self.raw_data
        error_match = re.search(error_pattern, self.raw_data, re.MULTILINE)

        # Prepare the result dictionary
        result = {
            'Error': None  # Default value for Error message
        }

        # If a match for error is found, extract and clean the error message in the result dictionary
        if error_match:
            # Clean the extracted message by removing the leading and trailing lines of dashes or equal signs
            error_message = error_match.group(0)
            # Removing the delimiters from the start and end
            error_message = re.sub(
                r"^[ \t]*[\-\*\#\=]{5,}[ \t]*\n|[ \t]*[\-\*\#\=]{5,}[ \t]*\n$", "", error_message, flags=re.MULTILINE).strip()
            result['Error'] = error_message

        return Data(data=result, comment='str for the `Error` message')


@AvailableBlocksOrca.register_block
class BlockOrcaErrorTermination(Block):
    """
    The block captures and stores ORCA error termination messages from ORCA output files.

    This block captures single-line messages indicating that ORCA finished with an error
    in a specific module or process.

    **Example of ORCA Output:**

    .. code-block:: none

        ORCA finished by error termination in PROPERTIES
        ORCA finished by error termination in LEANSCF
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'ORCA Error Termination', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`str` `Module`: The module/process where the error occurred
            - :class:`str` `Error Message`: The full error termination message
        :rtype: Data
        """
        # Define the regex pattern to match ORCA error termination
        pattern = r"ORCA finished by error termination in (\w+)"

        # Search for the pattern in self.raw_data
        match = re.search(pattern, self.raw_data)

        # Prepare the result dictionary
        result = {
            'Module': None,
            'Error Message': None
        }

        # If a match is found, extract the module name and full message
        if match:
            result['Module'] = match.group(1)
            result['Error Message'] = self.raw_data.strip()

        return Data(data=result, comment='Module name and error termination message')


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

    or

    .. code-block:: none

        -------------
        DIPOLE MOMENT
        -------------

        Method             : SCF
        Type of density    : Electron Density
        Multiplicity       :   1
        Irrep              :   0
        Energy             :  -379.2946629874107884 Eh
        Relativity type    :
        Basis              : AO
                                        X                 Y                 Z
        Electronic contribution:     -0.000041430       0.000000017       4.661630904
        Nuclear contribution   :      0.000000009       0.000000000      -8.265300471
                                -----------------------------------------
        Total Dipole Moment    :     -0.000041422       0.000000017      -3.603669567
                                -----------------------------------------
        Magnitude (a.u.)       :      3.603669567
        Magnitude (Debye)      :      9.159800098

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """
        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`pint.Quantity`'s with :class:`numpy.ndarray`'s of contributions
            - :class:`pint.Quantity` `Total Dipole Moment` with :class:`numpy.ndarray`'s of contributions in a.u.
            - :class:`pint.Quantity` `Magnitude (a.u.)` -- total dipole moment. The magnitude in a.u. can be extracted from :class:`pint.Quantity` with .magnitude property.
            - :class:`pint.Quantity` `Magnitude (Debye)` -- total dipole moment. The magnitude in Debye can be extracted from :class:`pint.Quantity` with .magnitude property.

            Parsed data example:

            .. code-block:: none

                {
                'Electronic contribution': <Quantity([0.      0.      5.37241], 'bohr * elementary_charge')>,
                'Nuclear contribution': <Quantity([ 0.      0.     -8.2653], 'bohr * elementary_charge')>,
                'Total Dipole Moment': <Quantity([ 0.       0.      -2.89289], 'bohr * elementary_charge')>,
                'Magnitude (a.u.)': <Quantity(2.89289, 'bohr * elementary_charge')>,
                'Magnitude (Debye)': <Quantity(7.35314, 'debye')>
                }

        :rtype: Data
        """
        # extract the data after the XYZ line

        pattern = r"([ \t]*X[ \t]+Y[ \t]+Z[ \t]*\n)"

        match = re.search(pattern, self.raw_data, re.MULTILINE)
        data_after_xyz = self.raw_data[match.end():]

        # Initialize the result dictionary
        result = {}

        # Define regex pattern for lines with "text: 3 numbers"
        pattern_three_numbers = r"([a-zA-Z \(\).]+):\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)[ \t]*\n"
        # Define regex pattern for lines with "text: 1 number"
        pattern_one_number = r"([a-zA-Z \(\).]+):\s*(-?\d+\.\d+)[ \t]*(?:\n|\Z)"

        # Find all matches for the three-number pattern
        matches_three_numbers = re.findall(
            pattern_three_numbers, data_after_xyz)
        for match in matches_three_numbers:
            label, x, y, z = match
            result[label.strip()] = np.array([float(x), float(y), float(z)]
                                             ) * ureg.elementary_charge * ureg.bohr_radius

        # Find all matches for the one-number pattern
        matches_one_number = re.findall(pattern_one_number, data_after_xyz)
        for match in matches_one_number:
            label, value = match
            if "(Debye)" in label:
                unit = "Debye"
            else:
                unit = "a.u."
            result[label.strip()] = float(
                value)*ureg.debye if unit == "Debye" else float(value) * ureg.elementary_charge * ureg.bohr_radius

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
        :return: :class:`pychemparse.data.Data` object that contains:

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
        :return: :class:`pychemparse.data.Data` object that contains:

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
class BlockOrcaGeometryConvergence(Block):
    """
    The block captures and stores Total run time from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

                              .--------------------.
        ----------------------|Geometry convergence|-------------------------
        Item                value                   Tolerance       Converged
        ---------------------------------------------------------------------
        Energy change       0.0000035570            0.0000050000      YES
        RMS gradient        0.0000436223            0.0001000000      YES
        MAX gradient        0.0002094156            0.0003000000      YES
        RMS step            0.0022222022            0.0020000000      NO
        MAX step            0.0170204003            0.0040000000      NO
        ........................................................
        Max(Bonds)      0.0003      Max(Angles)    0.02
        Max(Dihed)        0.98      Max(Improp)    0.00
        ---------------------------------------------------------------------
    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'TOTAL RUN TIME', None, self.raw_data

    def data(self) -> Data:
        """
        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`pandas.DataFrame` `Geometry convergence data`
        :rtype: Data
        """
        # Split the raw_data by the line containing only spaces and dots
        parts = re.split(r'\n\s*\.{2,}\s*\n', self.raw_data)

        if len(parts) < 2:
            return Data(data={}, comment='Data format is incorrect')

        # Extract the main data part
        main_data_part = parts[0]

        # Define the regex pattern to match the main data
        pattern = r"Item\s+value\s+Tolerance\s+Converged\s+[-]+\s+(.*?)\s+[-]+\s+"
        match = re.search(pattern, main_data_part, re.DOTALL)

        if match:
            data_str = match.group(1)
            data_lines = data_str.strip().split('\n')
            data = [re.split(r'\s{2,}', line.strip()) for line in data_lines]
            main_df = pd.DataFrame(
                data, columns=["Item", "Value", "Tolerance", "Converged"])
        else:
            main_df = pd.DataFrame()

        # Extract additional fields from the part after the main data part
        additional_data_part = parts[1]
        additional_data = {}
        additional_lines = additional_data_part.strip().split('\n')
        for line in additional_lines:
            numbers = re.findall(r'\d+\.\d+', line)
            labels = re.findall(r'[A-Za-z()]+', line)
            for label, number in zip(labels, numbers):
                additional_data[label] = float(number)

        # Combine all data into the final Data object
        final_data = {
            'Covregence data': main_df,
            **additional_data
        }

        return Data(data=final_data, comment='`Covregence data` is a pandas DataFrame and additional fields are extracted values.')


@AvailableBlocksOrca.register_block
class BlockOrcaTimingsForIndividualModules(Block):
    """
    The block captures and stores CI-NEB convergence data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        Timings for individual modules:

        Sum of individual times         ...      509.556 sec (=   8.493 min)
        GTO integral calculation        ...        7.722 sec (=   0.129 min)   1.5 %
        SCF iterations                  ...      123.801 sec (=   2.063 min)  24.3 %
        SCF Gradient evaluation         ...       26.450 sec (=   0.441 min)   5.2 %
        Geometry relaxation             ...        0.826 sec (=   0.014 min)   0.2 %
        Analytical frequency calculation...      350.758 sec (=   5.846 min)  68.8 %

    """

    data_available: bool = True
    """ Formatted data is available for this block. """

    def readable_name(self) -> str:
        return 'Timings for individual modules'

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        match = re.search(
            '^([ \\t]*Timings for individual modules:[ \\t]*)\\n', self.raw_data)

        body_start = match.end(1)
        header_raw = self.raw_data[:body_start]
        body_raw = self.raw_data[body_start:]

        return 'Timings for individual modules', header_raw, body_raw

    def data(self) -> Data:
        """
        :return: :class:`pychemparse.data.Data` object that contains:

                - :class:`dict` `Timings`
                    with module names as keys and timings as :class:`datetime.timedelta` objects.
        :rtype: Data

        Parsed data example:

        .. code-block:: none

            'Sum of individual times': datetime.timedelta(seconds=24, microseconds=36000),
            'GTO integral calculation': datetime.timedelta(seconds=8, microseconds=80000),
            'SCF iterations': datetime.timedelta(seconds=15, microseconds=956000)

        """
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

        return Data(data={"Timings": timings_dict}, comment='Timings for different modules as timedelta objects')


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
        :return: :class:`pychemparse.data.Data` object that contains:

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

        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`dict` `Total Energy` with

                -:class:`pint.Quantity` `Value in Eh`

                -:class:`pint.Quantity` `Value in eV`

            - :class:`dict` `Components`, `Virial components`, and `DFT components` (may differ in different versions of ORCA) with :class:`dict` subdicts with data.

            If data has representation in multiple units, they are stored in the subdicts with the unit as key. Othervise, the value is stored directly in the dict as :class:`pint.Quantity`.

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


class BlockOrcaTddftExcitations(BlockOrcaWithStandardHeader):
    """
    The block captures and stores TD-DFT excited states data for singlets from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        --------------------------------
        TD-DFT EXCITED STATES (SINGLETS)
        --------------------------------
        the weight of the individual excitations are printed if larger than 0.01

        STATE  1:  E=   0.154808 au      4.213 eV    33976.3 cm**-1  =   0.000000
            29a ->  31a  :     0.078253
            30a ->  32a  :     0.907469

    or

    .. code-block:: none

        -------------------------
        TD-DFT/TDA EXCITED STATES
        -------------------------
        the weight of the individual excitations are printed if larger than 1.0e-02

        UHF/UKS reference: multiplicity estimated based on rounded  value, RELEVANCE IS LIMITED!

        STATE  1:  E=   0.077106 au      2.098 eV    16922.9 cm**-1  =   2.000000 Mult 3
            90a ->  91a  :     0.468442 (c=  0.68442790)
            90b ->  91b  :     0.468442 (c= -0.68442790)

        STATE  2:  E=   0.101930 au      2.774 eV    22371.1 cm**-1  =   2.000000 Mult 3
            89a ->  91a  :     0.418245 (c=  0.64671829)
            89a ->  92a  :     0.050001 (c= -0.22360974)
            89b ->  91b  :     0.418245 (c= -0.64671829)
            89b ->  92b  :     0.050001 (c=  0.22360974)

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`pychemparse.data.Data` object that contains:
            - (:class:`int`) states as keys, and their respective details as sub-dictionaries. The `Energy (eV)` values are stored as :class:`pint.Quantity`. The `Transitions` are stored in a :class:`list`, with each transition represented as a :class:`dict` containing the `From Orbital` (:class:`str`: number+a|b), `To Orbital` (:class:`str`: number+a|b), and `Coefficient` (:class:`float`).

            Parsed data example:

            .. code-block:: none

                {
                1: {
                    'Energy (eV)': <Quantity(4.647, 'electron_volt')>,
                    'Transitions': [
                            {'From Orbital': '29a', 'To Orbital': '32a',
                                'Coefficient': 0.055845},
                            {'From Orbital': '30a', 'To Orbital': '31a',
                                'Coefficient': 0.906577}
                        ]
                    },
                # Additional states follow the same structure
                }

        :rtype: Data
        """
        states_data = {}

        state_number = None
        energy_ev = None
        transitions = []

        # Regular expression to match state lines and extract information
        state_pattern = re.compile(r"STATE\s+(\d+):.*?(\d+\.\d+)\s+eV")

        # Regular expression to match orbital transitions
        transition_pattern = re.compile(
            r"(\d+[ab])\s+->\s+(\d+[ab])\s+:\s+(\d+\.\d+)")

        for line in self.raw_data.split("\n"):
            # Check if the line is a state line
            state_match = state_pattern.search(line)
            if state_match:
                if state_number is not None:
                    # Append the previous state's data before starting a new state
                    states_data[int(state_number)] = {
                        'Energy (eV)': energy_ev,
                        'Transitions': transitions
                    }
                    transitions = []  # Reset the transitions list for the next state

                # Start capturing data for the new state
                state_number = int(state_match.group(1))
                energy_ev = float(state_match.group(2))*ureg.eV
            else:
                # If the line is not a state line, check for orbital transitions
                transition_match = transition_pattern.search(line)
                if transition_match:
                    transitions.append({
                        'From Orbital': transition_match.group(1),
                        'To Orbital': transition_match.group(2),
                        'Coefficient': float(transition_match.group(3))
                    })

        # Append the last state's data
        if state_number is not None:
            states_data[int(state_number)] = {
                'Energy (eV)': energy_ev,
                'Transitions': transitions
            }

        return Data(data=states_data, comment="""Collects a dict with keys - integers - STATE numbers, and values - dict with elements: `Energy (eV)` -- pint.
                    Quantity and, `Transitions`: dict with elements: `From Orbital`: string - number+a|b, `To Orbital`: string - number+a|b, `Coefficient`: float.
                    Parsed data example: {1:{'Energy (eV)': <Quantity(4.647, 'electron_volt')>, 'Transitions': [{'From Orbital': '29a', 'To Orbital': '32a', 'Coefficient': 0.055845}, {'From Orbital': '30a', 'To Orbital': '31a', 'Coefficient': 0.906577}]}}
                    """)


@AvailableBlocksOrca.register_block
class BlockOrcaTddftExcitedStatesSinglets(BlockOrcaTddftExcitations):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaTddftTdaExcitedStates(BlockOrcaTddftExcitations):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaScfType(Block):
    """
    The block captures and stores SCF data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        -------------------------------------S-C-F---------------------------------------
        Iteration    Energy (Eh)           Delta-E    RMSDP     MaxDP     Damp  Time(sec)
        ---------------------------------------------------------------------------------
                    ***  Starting incremental Fock matrix formation  ***
                                    *** Initializing SOSCF ***
                                    *** Constraining orbitals ***
                                    *** Switching to L-BFGS ***
        Constrained orbitals (energetic order)
        30 31
        Constrained orbitals (compact order)
        31 30

    or

    .. code-block:: none

        ---------------------------------------S-O-S-C-F--------------------------------------
        Iteration    Energy (Eh)            Delta-E     RMSDP    MaxDP     MaxGrad    Time(sec)
        --------------------------------------------------------------------------------------
            1    -379.2796837014277571     0.00e+00  0.00e+00  0.00e+00  3.00e-02   0.3
                    *** Restarting incremental Fock matrix formation ***
            2    -379.2796837014277571     0.00e+00  5.39e-03  2.36e-01  3.00e-02   0.3
            3    -379.2788786204820326     8.05e-04  2.96e-03  1.30e-01  3.68e-02   0.3
            4    -379.2897810987828962    -1.09e-02  1.69e-03  1.37e-01  9.46e-03   0.2
            5    -379.2878642728886689     1.92e-03  8.10e-04  7.42e-02  1.68e-02   0.2
            6    -379.2909711775516826    -3.11e-03  7.04e-04  3.11e-02  4.12e-03   0.2
                            ***Gradient convergence achieved***
                                *** Unconstraining orbitals ***
                *** Restarting Hessian update and switching to L-SR1 ***
            7    -379.2904844538218185     4.87e-04  1.27e-03  4.23e-02  1.72e-02   0.2
            8    -379.2892451088814596     1.24e-03  9.18e-04  7.40e-02  2.70e-02   0.3
            9    -379.2943354063930883    -5.09e-03  3.93e-04  1.30e-02  2.96e-03   0.2
            10    -379.2945957143243731    -2.60e-04  2.02e-04  7.28e-03  1.37e-03   0.2
            11    -379.2946565737383935    -6.09e-05  7.77e-04  4.26e-02  4.79e-04   0.2
            12    -379.2946442625134296     1.23e-05  3.75e-03  2.20e-01  9.99e-04   0.2
            13    -379.2946572622200847    -1.30e-05  8.03e-04  4.98e-02  7.21e-04   0.2
            14    -379.2946626618473829    -5.40e-06  4.17e-04  2.11e-02  1.05e-04   0.2
            15    -379.2946629954453783    -3.34e-07  1.04e-03  5.09e-02  4.80e-05   0.2
                                ***Gradient convergence achieved***

        or

        ---------------------------------------S-O-S-C-F--------------------------------------
        Iteration    Energy (Eh)           Delta-E    RMSDP     MaxDP     MaxGrad    Time(sec)
        --------------------------------------------------------------------------------------
            1    -379.7506727530962962     0.00e+00  0.00e+00  0.00e+00  6.98e-06     1.3
                    *** Restarting incremental Fock matrix formation ***
                Solving for 3 Hessian eigenvectors
                    It.    Root MAX Err.:          1          2          3
                    1                      8.686e-02  3.025e-02  2.075e-01 
                    2                      4.391e-02  2.910e-02  1.353e-01 
                    3                      1.159e-02  2.716e-03  6.115e-02 
                    4                      1.624e-02  7.596e-03  3.988e-03 
                    5                      1.416e-02  1.238e-02  4.792e-03 
                    6                      9.504e-03  8.714e-03  2.169e-03 
                    Eigenvalues:          -1.198e-01  7.680e-03  1.116e-02 
        Target saddle point order set to 1
            2    -379.7506727530962962     0.00e+00  3.76e-06  5.08e-05  6.98e-06    25.5
                        *** Gradient check signals convergence ***

    """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        """
        Identifies and separates the name, header, and body of the block based on a SCF header format.

        Utilizes regular expressions to discern the header portion from the body, processing the header to extract a distinct name and the header content. The text following the header is treated as the body of the block.

        Returns
        -------
        tuple[str, str | None, str]
            The name of the block, the header content (or None if a header is not present), and the body of the block.

        """

        lines = self.raw_data.strip().split('\n')
        # Take the first line
        first_line = lines[0]
        # Strip unwanted characters from the start and end
        readable_name = first_line.strip('-*#= \t')
        readable_name = readable_name if len(
            readable_name) > 2 else Element.process_invalid_name(self.raw_data)

        # Define regex pattern to split header and body
        pattern = r"^((?:(?:[ \t]*([\-\*\#\=]){5,})[ \t]*[a-zA-Z0-9](?!\n).*?[ \t]*\2{7,}\n)(?:(?!^[ \t]*[\-\*\#\=]{5,}.*$|^[ \t]*$).*\n){1,2}(?:\2*\n))"

        match = re.search(pattern, self.raw_data)

        if match:
            # Header is the content between the first and second header delimiters

            # Body is the content after the second header delimiter
            # The end of the header delimiter is marked by the start of the body_raw
            body_start = match.end(1)
            header_raw = self.raw_data[:body_start]
            body_raw = self.raw_data[body_start:]

            return readable_name, header_raw, body_raw
        else:
            logger.warning(
                f'No header found in\n{self.raw_data}\n, and that is really weird as it was extracted based on the idea that there is a header in it')
            # If no match is found, put everything into header
            return readable_name, None, self.raw_data


@AvailableBlocksOrca.register_block
class BlockOrcaUnrecognizedScf(BlockOrcaScfType):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaScf(BlockOrcaScfType):
    """
    The block captures and stores SCF data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        -------------------------------------S-C-F---------------------------------------
        Iteration    Energy (Eh)           Delta-E    RMSDP     MaxDP     Damp  Time(sec)
        ---------------------------------------------------------------------------------
                    ***  Starting incremental Fock matrix formation  ***
                                    *** Initializing SOSCF ***
                                    *** Constraining orbitals ***
                                    *** Switching to L-BFGS ***
        Constrained orbitals (energetic order)
        30 31
        Constrained orbitals (compact order)
        31 30

    """

    data_available: bool = True
    """ Formatted data is available for this block. """

    _HESSIAN_RE = re.compile(
        r"(Solving\s+for\s+\d+\s+Hessian\s+eigenvectors.*?Eigenvalues:[^\n]*\n)",
        re.DOTALL,
    )

    @staticmethod
    def _extract_hessian_blocks(text: str):
        """Remove Hessian blocks from *text* and return (clean_text, eigenvalues_list).

        ``eigenvalues_list`` is a list of ``list[float]`` – one sub‑list per
        diagnostic block encountered in *text*.
        """

        eigenvalues = []

        for match in BlockOrcaScf._HESSIAN_RE.finditer(text):
            diag_block = match.group(0)
            m = re.search(r"Eigenvalues:\s+([\d\-eE\.\s]+)", diag_block)
            if m:
                try:
                    eigenvalues.append([float(v) for v in m.group(1).split()])
                except ValueError:
                    # If conversion fails we still proceed but skip the block’s eigenvalues.
                    pass

        clean_text = BlockOrcaScf._HESSIAN_RE.sub("", text)
        return clean_text, eigenvalues

    def data(self) -> Data:
        """
        Returns a :class:`pychemparse.data.Data` object containing:

        - :class:`pandas.DataFrame` `Data` with columns `Iteration`, `Energy (Eh)`, `Delta-E`, `RMSDP`, `MaxDP`, `Damp`, `Time(sec)`:
            - `Time(sec)` is represented as a timedelta object.
            - `Energy (Eh)` is represented by a pint object. Magnitude can be extracted with the .magnitude method.
        - :class:`pandas.DataFrame` `Comments` with columns `Iteration` and `Comment`.
        - :class:`str` `Name` of the block.

        Parsed data example:

        .. code-block:: none

            {'Data': Empty DataFrame
            Columns: [Iteration, Energy (
                Eh), Delta-E, RMSDP, MaxDP, Damp, Time(sec)]
            Index: [],
            'Comments':    Iteration                                            Comment
            0          0  ***  Starting incremental Fock matrix formatio...
            1          0                         *** Initializing SOSCF ***
            2          0                      *** Constraining orbitals ***
            3          0                        *** Switching to L-BFGS ***,
            'Name': 'S-C-F'}

        :rtype: Data
        """
        # *extract_name_header_and_body* is provided by BlockOrcaScfType.
        readable_name, header_raw, body_raw = self.extract_name_header_and_body()

        # Sanity‑check: header must contain exactly three non‑empty lines.
        if header_raw is None or len([ln for ln in header_raw.split("\n") if ln.strip()]) != 3:
            return Data(data=None, comment="No header found")

        # Strip Hessian eigenvector diagnostics and harvest eigenvalues.
        body_clean, eigenvalues = self._extract_hessian_blocks(body_raw)

        # -----------------------------------------------------------------
        # Column name parsing (from the second line of the header)
        # -----------------------------------------------------------------
        header_lines = header_raw.split("\n")
        column_names = [s.strip() for s in re.split(
            r"\s{2,}", header_lines[1].strip()) if s.strip()]

        # -----------------------------------------------------------------
        # Main loop: iterate over body lines collecting data rows & comments
        # -----------------------------------------------------------------
        data_lines = []
        comments = []
        current_iteration = 0

        for raw_line in body_clean.split("\n"):
            line = raw_line.rstrip()
            if not line:
                continue  # skip blank lines

            if line.startswith("***"):
                comments.append((current_iteration, line))
                continue

            split = line.split()
            if split and split[0].isdigit():
                # New SCF iteration row.
                current_iteration = int(split[0])
                data_lines.append(line)
            else:
                # Any other non‑blank line is treated as a comment bound to the
                # current iteration index.
                comments.append((current_iteration, line))

        # -----------------------------------------------------------------
        # Convert numeric rows into a DataFrame
        # -----------------------------------------------------------------
        if data_lines:
            df = pd.read_csv(StringIO("\n".join(data_lines)),
                             sep="\s+", names=column_names)
        else:
            df = pd.DataFrame(columns=column_names)

        # Post‑processing: convert time to timedelta and energy to pint units.
        if "Time(sec)" in df.columns:
            df["Time(sec)"] = df["Time(sec)"].apply(
                lambda s: timedelta(seconds=s))
        if "Energy (Eh)" in df.columns:
            df["Energy (Eh)"] = df["Energy (Eh)"].apply(
                lambda e: e * ureg.hartree)

        # -----------------------------------------------------------------
        # Assemble the Data object expected by callers
        # -----------------------------------------------------------------
        data_dict = {
            "Data": df,
            "Comments": pd.DataFrame(comments, columns=["Iteration", "Comment"]),
            "Name": readable_name,
            "Eigenvalues": eigenvalues,
        }

        return Data(
            data=data_dict,
            comment=(
                "Pandas DataFrame with columns `Iteration`, `Energy (Eh)`, `Delta-E`, `RMSDP`, "
                "`MaxDP`, `MaxGrad`/`Damp`, `Time(sec)`. Time is `timedelta`, energy is a Pint "
                "quantity. Any Hessian diagnostic eigenvalues are available via the `Eigenvalues` "
                "key (list of float lists)."
            ),
        )


@AvailableBlocksOrca.register_block
class BlockOrcaSoscf(BlockOrcaScf):
    """
    The block captures and stores SOSCF data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        ---------------------------------------S-O-S-C-F--------------------------------------
        Iteration    Energy (Eh)            Delta-E     RMSDP    MaxDP     MaxGrad    Time(sec)
        --------------------------------------------------------------------------------------
            1    -379.2796837014277571     0.00e+00  0.00e+00  0.00e+00  3.00e-02   0.3
                    *** Restarting incremental Fock matrix formation ***
            2    -379.2796837014277571     0.00e+00  5.39e-03  2.36e-01  3.00e-02   0.3
            3    -379.2788786204820326     8.05e-04  2.96e-03  1.30e-01  3.68e-02   0.3
            4    -379.2897810987828962    -1.09e-02  1.69e-03  1.37e-01  9.46e-03   0.2
            5    -379.2878642728886689     1.92e-03  8.10e-04  7.42e-02  1.68e-02   0.2
            6    -379.2909711775516826    -3.11e-03  7.04e-04  3.11e-02  4.12e-03   0.2
                            ***Gradient convergence achieved***
                                *** Unconstraining orbitals ***
                *** Restarting Hessian update and switching to L-SR1 ***
            7    -379.2904844538218185     4.87e-04  1.27e-03  4.23e-02  1.72e-02   0.2
            8    -379.2892451088814596     1.24e-03  9.18e-04  7.40e-02  2.70e-02   0.3
            9    -379.2943354063930883    -5.09e-03  3.93e-04  1.30e-02  2.96e-03   0.2
            10    -379.2945957143243731    -2.60e-04  2.02e-04  7.28e-03  1.37e-03   0.2
            11    -379.2946565737383935    -6.09e-05  7.77e-04  4.26e-02  4.79e-04   0.2
            12    -379.2946442625134296     1.23e-05  3.75e-03  2.20e-01  9.99e-04   0.2
            13    -379.2946572622200847    -1.30e-05  8.03e-04  4.98e-02  7.21e-04   0.2
            14    -379.2946626618473829    -5.40e-06  4.17e-04  2.11e-02  1.05e-04   0.2
            15    -379.2946629954453783    -3.34e-07  1.04e-03  5.09e-02  4.80e-05   0.2
                                ***Gradient convergence achieved***

    or

        ---------------------------------------S-O-S-C-F--------------------------------------
        Iteration    Energy (Eh)           Delta-E    RMSDP     MaxDP     MaxGrad    Time(sec)
        --------------------------------------------------------------------------------------
            1    -379.7506727530962962     0.00e+00  0.00e+00  0.00e+00  6.98e-06     1.3
                    *** Restarting incremental Fock matrix formation ***
                Solving for 3 Hessian eigenvectors
                    It.    Root MAX Err.:          1          2          3
                    1                      8.686e-02  3.025e-02  2.075e-01 
                    2                      4.391e-02  2.910e-02  1.353e-01 
                    3                      1.159e-02  2.716e-03  6.115e-02 
                    4                      1.624e-02  7.596e-03  3.988e-03 
                    5                      1.416e-02  1.238e-02  4.792e-03 
                    6                      9.504e-03  8.714e-03  2.169e-03 
                    Eigenvalues:          -1.198e-01  7.680e-03  1.116e-02 
        Target saddle point order set to 1
            2    -379.7506727530962962     0.00e+00  3.76e-06  5.08e-05  6.98e-06    25.5
                        *** Gradient check signals convergence ***

    """

    def data(self) -> Data:
        """

        Returns a :class:`pychemparse.data.Data` object containing:

        - :class:`pandas.DataFrame` `Data` with columns `Iteration`, `Energy (Eh)`, `Delta-E`, `RMSDP`, `MaxDP`, `Damp`, `Time(sec)`:
            - `Time(sec)` is represented as a timedelta object.
            - `Energy (Eh)` is represented by a pint object. Magnitude can be extracted with the .magnitude method.
        - :class:`pandas.DataFrame` `Comments` with columns `Iteration` and `Comment`.
        - :class:`str` `Name` of the block.
        - :class:`list` list of eigenvectors if available, if not - emply list.

        Parsed data example:

        .. code-block:: none

            {'Data':
            Iteration                  Energy (Eh)       Delta-E     RMSDP   MaxDP      MaxGrad              Time(sec)
            0           1  -440.42719635301455 hartree  0.000000e+00  0.000000  0.0000   0.029500 0 days 00:00:00.500000
            1           2  -440.42719635301455 hartree  0.000000e+00  0.004710  0.2320   0.029500 0 days 00:00:00.400000
            2           3     -440.49687163902 hartree -6.970000e-02  0.012600  1.1300   0.011100 0 days 00:00:00.400000,

            'Comments':
            Iteration                                            Comment
            0          1  *** Restarting incremental Fock matrix formati...
            1         13         **** Energy Check signals convergence ****
            2         13                    *** Unconstraining orbitals ***
            3         13  *** Restarting Hessian update and switching to...
            4         21  *** Restarting incremental Fock matrix formati...
            5         33         **** Energy Check signals convergence ****,
            'Name': 'S-O-S-C-F',
            'Eigenvalues': [-1.198e-01  7.680e-03  1.116e-02]}


        :rtype: Data

        """

        return super().data()


@AvailableBlocksOrca.register_block
class BlockOrcaPathSummaryForNebTs(BlockOrcaWithStandardHeader):
    """
    The block captures and stores NEB-TS path summary data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        ---------------------------------------------------------------
                      PATH SUMMARY FOR NEB-TS
        ---------------------------------------------------------------
        All forces in Eh/Bohr. Global forces for TS.

        Image     E(Eh)   dE(kcal/mol)  max(|Fp|)  RMS(Fp)
        0   -1040.28151     0.00       0.00024   0.00008
        1   -1040.26641     9.48       0.00357   0.00076
        2   -1040.25443    17.00       0.00387   0.00111
        3   -1040.24519    22.79       0.00279   0.00095
        4   -1040.23692    27.98       0.00459   0.00133
        5   -1040.23342    30.18       0.00189   0.00067 <= CI
        TS   -1040.23850    26.99       0.00022   0.00005 <= TS
        6   -1040.23665    28.15       0.00216   0.00079
        7   -1040.24833    20.82       0.00200   0.00076
        8   -1040.26217    12.14       0.00200   0.00058
        9   -1040.27575     3.62       0.00012   0.00004

    """

    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`pychemparse.data.Data` object that contains:
            - (:class:`int`) states as keys, and their respective details as sub-dictionaries. The `Energy (eV)` values are stored as :class:`pint.Quantity`. The `Transitions` are stored in a :class:`list`, with each transition represented as a :class:`dict` containing the `From Orbital` (:class:`str`: number+a|b), `To Orbital` (:class:`str`: number+a|b), and `Coefficient` (:class:`float`).

            Parsed data example:

            .. code-block:: none

                {'Data':    Image                      E(Eh)              dE(kcal/mol)  \
                    0      0  -1040.28151 electron_volt    0.0 kilocalorie / mole
                    1      1  -1040.27082 electron_volt   6.71 kilocalorie / mole
                    2      2   -1040.2608 electron_volt   13.0 kilocalorie / mole
                    3      3   -1040.2518 electron_volt  18.64 kilocalorie / mole
                    4      4  -1040.24453 electron_volt  23.21 kilocalorie / mole
                    5      5  -1040.24169 electron_volt  24.99 kilocalorie / mole
                    6     TS  -1040.24272 electron_volt  24.34 kilocalorie / mole
                    7      6  -1040.24575 electron_volt  22.44 kilocalorie / mole
                    8      7  -1040.25472 electron_volt  16.81 kilocalorie / mole
                    9      8  -1040.26597 electron_volt   9.75 kilocalorie / mole
                    10     9  -1040.27575 electron_volt   3.62 kilocalorie / mole

                                    max(|Fp|)                 RMS(Fp) Comment
                    0   0.00023 hartree / bohr    7e-05 hartree / bohr
                    1   0.00068 hartree / bohr  0.00023 hartree / bohr
                    2   0.00072 hartree / bohr  0.00023 hartree / bohr
                    3   0.00073 hartree / bohr  0.00022 hartree / bohr
                    4   0.00067 hartree / bohr   0.0002 hartree / bohr
                    5   0.00063 hartree / bohr  0.00021 hartree / bohr   <= CI
                    6     7e-05 hartree / bohr    2e-05 hartree / bohr   <= TS
                    7   0.00058 hartree / bohr  0.00021 hartree / bohr
                    8   0.00055 hartree / bohr  0.00019 hartree / bohr
                    9   0.00065 hartree / bohr  0.00019 hartree / bohr
                    10  0.00018 hartree / bohr    5e-05 hartree / bohr
                }

        :rtype: Data
        """

        # Extracting data from the text
        if "Dist.(Ang.)" in self.raw_data:
            pattern = re.compile(
                r'(\d+)\s+(\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)(?:\s+(<= CI|<= TS))?')
            columns = ["Image", "Dist.(Ang.)", "E(Eh)", "dE(kcal/mol)",
                       "max(|Fp|)", "RMS(Fp)", "Comment"]
        else:
            pattern = re.compile(
                r'(\d+|TS)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)(?:\s+(<= CI|<= TS))?')
            columns = ["Image", "E(Eh)", "dE(kcal/mol)",
                       "max(|Fp|)", "RMS(Fp)", "Comment"]

        matches = pattern.findall(self.raw_data)

        # Convert matches to dataframe
        df_extracted = pd.DataFrame(matches, columns=columns)

        # Convert numerical columns to appropriate data types with units
        df_extracted["Image"] = df_extracted["Image"].apply(
            lambda x: int(x) if x.isdigit() else x)
        if "Dist.(Ang.)" in df_extracted.columns:
            df_extracted["Dist.(Ang.)"] = df_extracted["Dist.(Ang.)"].astype(
                float).apply(lambda x: x * ureg.angstrom)
        df_extracted["E(Eh)"] = df_extracted["E(Eh)"].astype(
            float).apply(lambda x: x * ureg.Eh)
        df_extracted["dE(kcal/mol)"] = df_extracted["dE(kcal/mol)"].astype(
            float).apply(lambda x: x * (ureg.kilocalorie / ureg.mole))
        df_extracted["max(|Fp|)"] = df_extracted["max(|Fp|)"].astype(
            float).apply(lambda x: x * (ureg.hartree / ureg.bohr))
        df_extracted["RMS(Fp)"] = df_extracted["RMS(Fp)"].astype(
            float).apply(lambda x: x * (ureg.hartree / ureg.bohr))

        return Data(data={'Data': df_extracted}, comment="""Collects a DataFrame with columns `Image`, `Dist.(Ang.)`, `E(Eh)`, `dE(kcal/mol)`, `max(|Fp|)`, `RMS(Fp)`, `Comment`.""")


@AvailableBlocksOrca.register_block
class BlockOrcaPathSummaryForNebCi(BlockOrcaPathSummaryForNebTs):
    """
    The block captures and stores NEB-TS path summary data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        ---------------------------------------------------------------
                                PATH SUMMARY
        ---------------------------------------------------------------
        All forces in Eh/Bohr.

        Image Dist.(Ang.)    E(Eh)   dE(kcal/mol)  max(|Fp|)  RMS(Fp)
        0     0.000   -1040.28151      0.00       0.00024   0.00008
        1     4.329   -1040.26830      8.29       0.00103   0.00025
        2     6.607   -1040.25791     14.81       0.00120   0.00029
        3     8.283   -1040.25022     19.64       0.00174   0.00042
        4     9.599   -1040.24240     24.54       0.00116   0.00026
        5    10.780   -1040.23790     27.37       0.00047   0.00015 <= CI
        6    12.215   -1040.24200     24.80       0.00098   0.00026
        7    13.815   -1040.25258     18.16       0.00076   0.00021
        8    16.040   -1040.26419     10.87       0.00043   0.00013
        9    19.933   -1040.27575      3.62       0.00012   0.00004

        Straight line distance between images along the path:
                D( 0- 1) =   4.3288 Ang.
                D( 1- 2) =   2.2782 Ang.
                D( 2- 3) =   1.6757 Ang.
                D( 3- 4) =   1.3168 Ang.
                D( 4- 5) =   1.1801 Ang.
                D( 5- 6) =   1.4358 Ang.
                D( 6- 7) =   1.5995 Ang.
                D( 7- 8) =   2.2254 Ang.
                D( 8- 9) =   3.8933 Ang.


    """


@AvailableBlocksOrca.register_block
class BlockOrcaVibrationalFrequencies(BlockOrcaWithStandardHeader):
    """
    The block captures and stores vibrational frequencies data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        -----------------------
        VIBRATIONAL FREQUENCIES
        -----------------------

        Scaling factor for frequencies =  1.000000000  (already applied!)

        0:         0.00 cm**-1
        1:         0.00 cm**-1
        2:         0.00 cm**-1
        3:         0.00 cm**-1
        4:         0.00 cm**-1
        5:         0.00 cm**-1
        6:       -15.28 cm**-1 ***imaginary mode***
        7:        32.56 cm**-1
        8:        38.76 cm**-1
        9:        48.22 cm**-1
        10:        89.12 cm**-1
        11:       101.15 cm**-1
        12:       114.47 cm**-1
        13:       135.76 cm**-1

    """

    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return:

        :rtype: Data
        """
        lines = self.raw_data.strip().split('\n')
        data_lines = [line for line in lines if 'cm**-1' in line]

        # Prepare data for DataFrame
        data = {
            'Index': [],
            'Frequency': [],
            'Type': []
        }

        for line in data_lines:
            parts = line.split(':')
            index = int(parts[0].strip())
            frequency_part = parts[1].strip()
            frequency_value = frequency_part.split(' ')[0]
            if "***imaginary mode***" in frequency_part:
                mode_type = 'Imaginary'
            else:
                mode_type = 'Real'

            data['Index'].append(index)
            data['Frequency'].append(float(frequency_value))
            data['Type'].append(mode_type)

        df = pd.DataFrame(data)

        df['Frequency'] = df['Frequency'].apply(
            lambda x: x * ureg.cm**-1)

        return Data(data={'Data': df}, comment="""Collects a DataFrame with columns `Index`, `Frequency`, `Type`.
        """)


@AvailableBlocksOrca.register_block
class BlockOrcaCiNebConvergence(Block):
    """
    The block captures and stores CI-NEB convergence data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

                                .--------------------.
          ----------------------| CI-Neb convergence |-------------------------
          Item                value                   Tolerance       Converged
          ---------------------------------------------------------------------
          RMS(Fp)             0.0002797716            0.0100000000      YES
          MAX(|Fp|)           0.0014572463            0.0200000000      YES
          RMS(FCI)            0.0001842330            0.0010000000      YES
          MAX(|FCI|)          0.0005858110            0.0020000000      YES
          ---------------------------------------------------------------------

    """

    data_available: bool = True
    """ Formatted data is available for this block. """

    def readable_name(self) -> str:
        return 'CI-Neb convergence'

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return self.readable_name(), None, self.raw_data

    def data(self) -> Data:
        """
        Returns a :class:`pychemparse.data.Data` object containing:

        - :class:`pandas.DataFrame` `Data` with columns `Item`, `Value`, `Tolerance`, `Converged`.
        - :class:`str` `Comment`.

        Parsed data example:

        .. code-block:: none

                        'Data':          Item     Value  Tolerance Converged
                0     RMS(Fp)  0.000188      0.010       YES
                1   MAX(|Fp|)  0.000727      0.020       YES
                2    RMS(FCI)  0.000212      0.001       YES
                3  MAX(|FCI|)  0.000644      0.002       YES

        :rtype: Data
        """
        # Extracting the table part of the string
        table_data = re.findall(
            r"(\S+)\s+([\d\.]+)\s+([\d\.]+)\s+(\S+)", self.raw_data)

        # Create a pandas dataframe
        df = pd.DataFrame(table_data, columns=[
                          "Item", "Value", "Tolerance", "Converged"])

        # Convert numeric columns to float
        df["Value"] = df["Value"].astype(float)
        df["Tolerance"] = df["Tolerance"].astype(float)

        return Data(data={'Data': df}, comment="""Collects a DataFrame with columns `Item`, `Value`, `Tolerance`, `Converged`.""")


@AvailableBlocksOrca.register_block
class BlockOrcaInputFile(Block):
    """
    The block captures and stores the input file content from ORCA output files.
    """
    data_available: bool = True

    def readable_name(self) -> str:
        """
        Return a readable name for the block.
        """
        return "INPUT FILE"

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return self.readable_name(), None, self.raw_data

    def data(self) -> Data:
        """
        Extract the input file name and content.
        """
        raw_data = self.raw_data

        # Extract file name
        file_name_match = re.search(r"NAME = (.*)", raw_data)
        file_name = file_name_match.group(
            1).strip() if file_name_match else None

        # Extract and clean input content
        lines = raw_data.split('\n')
        input_lines = []
        for line in lines:
            if line.strip().startswith('|'):
                # remove the prefix like |  1>
                clean_line = re.sub(r'\|\s*\d*>\s*', '', line).rstrip()
                input_lines.append(clean_line)

        # Join the cleaned lines
        input_text = "\n".join(input_lines)

        # Remove the end of input marker
        input_text = re.sub(r'\*+END OF INPUT\*+', '', input_text).strip()

        return Data(
            data={'file_name': file_name, 'input_text': input_text},
            comment="Extracted input file name and content."
        )


@AvailableBlocksOrca.register_block
class BlockOrcaShark(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaWarnings(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaContributions(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaAcknowledgement(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaLibint2(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaLibXc(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaUses(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaOrbitalBasis(Block):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaAuxJBasis(Block):
    pass


class BlockOrcaHurray(Block):
    def readable_name(self) -> str:
        pattern = r"(?:[ \t]*\*{5,}[ \t]*H[ \t]*U[ \t]*R[ \t]*R[ \t]*A[ \t]*Y[ \t]*\*{5,}[ \t]*\n)(?:[ \t]*\*+[ \t]*([a-zA-Z0-9](?!\n).*?)[ \t]*\*+[ \t]*\n)(?:[ \t]*\*{5,}\n)"
        extracted_texts = list(re.findall(pattern, self.raw_data))
        assert len(
            extracted_texts) == 1, f"Expected 1 match, found {len(extracted_texts)} matches"

        return extracted_texts[0]

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return self.readable_name(), None, self.raw_data


@AvailableBlocksOrca.register_block
class BlockOrcaUnrecognizedHurray(BlockOrcaHurray):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaHurrayTS(BlockOrcaHurray):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaHurrayCI(BlockOrcaHurray):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaHurrayOptimization(BlockOrcaHurray):
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaSpectrumType(Block):
    """
    The block captures and stores spectrum data from ORCA output files.

    **Example of ORCA Output:**

    .. code-block:: none

        -----------------------------------------------------------------------------
         ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS
        -----------------------------------------------------------------------------
        State   Energy    Wavelength  fosc         T2        TX        TY        TZ  
                (cm-1)      (nm)                 (au**2)    (au)      (au)      (au) 
        -----------------------------------------------------------------------------
        1   16903.5    591.6   0.000000000   0.00000   0.00000  -0.00000  -0.00000
        2   22365.6    447.1   0.000000000   0.00000  -0.00000  -0.00000   0.00000
        3   23649.8    422.8   0.000000000   0.00000   0.00000   0.00000   0.00000
        4   25396.9    393.7   0.002096634   0.02718  -0.13602   0.04159   0.08336
        5   26409.5    378.7   0.626104251   7.80481  -1.15488  -2.10174   1.43308
        6   28468.1    351.3   0.000000000   0.00000   0.00000   0.00000  -0.00000
        7   28944.3    345.5   0.000000000   0.00000   0.00000  -0.00000  -0.00000
        8   28964.5    345.3   0.000000000   0.00000  -0.00000   0.00000   0.00000
        9   29986.3    333.5   0.025998669   0.28543  -0.44658  -0.18107   0.23069
        10   30178.3    331.4   0.000000000   0.00000   0.00000   0.00000  -0.00000
        11   31055.6    322.0   0.000000000   0.00000  -0.00000  -0.00000   0.00000
        12   32047.8    312.0   0.000000000   0.00000  -0.00000  -0.00000   0.00000
        13   32343.8    309.2   0.000000000   0.00000  -0.00000   0.00000  -0.00000
        14   32365.6    309.0   0.012474234   0.12688  -0.23853   0.23551  -0.12051
        15   32454.2    308.1   0.023480417   0.23818   0.00690  -0.48392   0.06292
        16   33446.2    299.0   0.001756413   0.01729  -0.06205   0.06809  -0.09382
        17   34637.6    288.7   0.000000000   0.00000   0.00000  -0.00000  -0.00000
        18   35255.9    283.6   0.000000000   0.00000   0.00000  -0.00000  -0.00000
        ...

    """
    data_available: bool = True
    """Formatted data is available for this block."""

    def extract_name_header_and_body(self) -> tuple[str, Optional[str], str]:
        """
        Identifies and separates the name, header, and body of the block.

        Returns
        -------
        Tuple[str, Optional[str], str]
            The name of the block, the header content (or None if a header is not present),
            and the body of the block.
        """
        raw_data = self.raw_data

        # Define the separator pattern
        separator_pattern = r"(?:[ \t]*[\-\*\#\=]{5,}[ \t]*\n)"
        # Find all occurrences of the separator pattern
        separators = list(re.finditer(separator_pattern, raw_data))

        if len(separators) >= 2:
            # The header is everything up to the end of the second separator
            header_end = separators[1].end()
            header_raw = raw_data[:header_end]
            body_raw = raw_data[header_end:]

            # Extract the name from the second line of the header
            header_lines = header_raw.strip().split('\n')
            if len(header_lines) > 1:
                readable_name = header_lines[1].strip('-*#= \t')
            else:
                readable_name = ''

            return readable_name, header_raw, body_raw
        else:
            logger.warning('No proper separators found in the block.')
            # If separators are not found, treat the entire raw_data as body
            readable_name = self.raw_data.strip('-*#= \t\n')
            return readable_name, None, self.raw_data

    def data(self) -> Data:
        """
        Parses the spectrum block and returns a Data object containing a DataFrame with units applied.

        Returns
        -------
        Data
            The parsed data.

        Parsed data example:

        .. code-block:: none

            'Data':         Transition             Energy (eV)         Energy (cm-1)  \
            0     0-1A -> 1-3A   2.09817 electron_volt  16922.9 / centimeter   
            1     0-1A -> 2-3A  2.773662 electron_volt  22371.1 / centimeter   
            2     0-1A -> 3-3A  2.932123 electron_volt  23649.2 / centimeter   
            3     0-1A -> 4-1A  3.149596 electron_volt  25403.2 / centimeter   
            4     0-1A -> 5-1A  3.275905 electron_volt  26422.0 / centimeter   
            ..             ...                     ...                   ...   
            95   0-1A -> 96-1A  6.641358 electron_volt  53566.2 / centimeter   
            96   0-1A -> 97-3A  6.656552 electron_volt  53688.7 / centimeter   
            97   0-1A -> 98-3A  6.701102 electron_volt  54048.0 / centimeter   
            98   0-1A -> 99-3A  6.727343 electron_volt  54259.7 / centimeter   
            99  0-1A -> 100-1A  6.746272 electron_volt  54412.4 / centimeter   

                Wavelength (nm)  fosc(D2)                                  D2 (au**2)  \
            0   590.9 nanometer  0.000000      0.0 bohr ** 2 * elementary_charge ** 2   
            1   447.0 nanometer  0.000000      0.0 bohr ** 2 * elementary_charge ** 2   
            2   422.8 nanometer  0.000000      0.0 bohr ** 2 * elementary_charge ** 2   
            3   393.7 nanometer  0.002212  0.02866 bohr ** 2 * elementary_charge ** 2   
            4   378.5 nanometer  0.624346  7.77921 bohr ** 2 * elementary_charge ** 2   
            ..              ...       ...                                         ...   
            95  186.7 nanometer  0.191542   1.1772 bohr ** 2 * elementary_charge ** 2   
            96  186.3 nanometer  0.000000      0.0 bohr ** 2 * elementary_charge ** 2   
            97  185.0 nanometer  0.000000      0.0 bohr ** 2 * elementary_charge ** 2   
            98  184.3 nanometer  0.000000      0.0 bohr ** 2 * elementary_charge ** 2   
            99  183.8 nanometer  0.233894  1.41514 bohr ** 2 * elementary_charge ** 2   

                                        DX (au)                            DY (au)  \
            0        0.0 bohr * elementary_charge      -0.0 bohr * elementary_charge   
            1        0.0 bohr * elementary_charge       0.0 bohr * elementary_charge   
            2       -0.0 bohr * elementary_charge      -0.0 bohr * elementary_charge   
            3   -0.14047 bohr * elementary_charge   0.03394 bohr * elementary_charge   
            4   -1.15138 bohr * elementary_charge  -2.09801 bohr * elementary_charge   
            ..                                ...                                ...   
            95   0.94121 bohr * elementary_charge  -0.11391 bohr * elementary_charge   
            96       0.0 bohr * elementary_charge      -0.0 bohr * elementary_charge   
            97       0.0 bohr * elementary_charge      -0.0 bohr * elementary_charge   
            98      -0.0 bohr * elementary_charge      -0.0 bohr * elementary_charge   
            99   0.60355 bohr * elementary_charge   -0.5407 bohr * elementary_charge   

                                        DZ (au)  
            0       0.0 bohr * elementary_charge  
            1       0.0 bohr * elementary_charge  
            2       0.0 bohr * elementary_charge  
            3   0.08819 bohr * elementary_charge  
            4   1.43244 bohr * elementary_charge  
            ..                               ...  
            95  0.52758 bohr * elementary_charge  
            96      0.0 bohr * elementary_charge  
            97      0.0 bohr * elementary_charge  
            98      0.0 bohr * elementary_charge  
            99  0.87092 bohr * elementary_charge  

        """
        def process_column_names_and_units(column_names: list, units_list: list) -> list:
            """
            Processes the column names and units, adjusting units according to specified rules.

            Parameters
            ----------
            column_names : list
                List of column names extracted from the subheader.
            units_list : list
                List of units extracted from the subheader.

            Returns
            -------
            list
                List of tuples (name, unit) after processing.
            """
            from pint import UnitRegistry
            ureg = UnitRegistry()

            # Manual mapping of column names to units (unitless columns mapped to None)
            unitless_columns = {'State', 'Transition',
                                'fosc', 'fosc(D2)', 'fosc(P2)'}
            manual_unit_mapping = {name: None for name in unitless_columns}

            # Additional manual unit mapping for units not recognized by Pint
            manual_unit_mapping_units = {
                'cm-1': ureg('1/cm'),
                'cm^-1': ureg('1/cm'),
                'au': ureg.bohr * ureg.elementary_charge,  # au as bohr * elementary charge
                'au^2': (ureg.bohr * ureg.elementary_charge) ** 2,
                'au**2': (ureg.bohr * ureg.elementary_charge) ** 2,
                # Add more mappings as needed
            }

            units_index = 0  # Index to track units_list
            name_unit_pairs = []

            for name in column_names:
                # Check if the column name is in the manual mapping (unitless columns)
                if name in manual_unit_mapping:
                    unit = manual_unit_mapping[name]
                    final_name = name  # Keep the name as is for manual mapping
                else:
                    # Try to get the next unit from units_list
                    if units_index < len(units_list):
                        unit_str = units_list[units_index]
                        units_index += 1
                        # Remove external brackets if present and strip whitespace
                        unit_str_clean = unit_str.strip('()').strip()
                        if unit_str_clean == '':
                            unit = None  # Empty unit string implies dimensionless
                            final_name = name  # No unit, so final name is just the name
                        else:
                            # Use the cleaned unit string directly for the final name
                            final_name = f"{name} ({unit_str_clean})"
                            # Map to a manual unit if available or parse with Pint (optional)
                            if unit_str_clean in manual_unit_mapping_units:
                                unit = manual_unit_mapping_units[unit_str_clean]
                            else:
                                try:
                                    unit = ureg.parse_units(unit_str_clean)
                                except Exception:
                                    unit = None  # Parsing failed, assume dimensionless
                    else:
                        # No more units available in units_list
                        unit = None
                        final_name = name  # No unit, so final name is just the name
                        logger.warning(
                            f'No unit provided for column "{name}", defaulting to None.')

                name_unit_pairs.append((final_name, unit))

            # Check if any units remain unused
            if units_index < len(units_list):
                logger.warning(
                    'Units list has more entries than columns with units. Extra units will be ignored.')

            return name_unit_pairs

        # Extract the readable name, header, and body from the raw data
        readable_name, header_raw, body_raw = self.extract_name_header_and_body()

        if body_raw is None:
            return Data(data=None, comment="No data found")

        # Split the body into lines
        body_lines = body_raw.strip().split('\n')

        # Identify the separator line in the body (line consisting of '-')
        separator_indices = [i for i, line in enumerate(
            body_lines) if set(line.strip()) == {'-'}]

        if separator_indices:
            separator_index = separator_indices[0]
            # Lines before the separator are subheader (column names and units)
            subheader_lines = body_lines[:separator_index]
            # Lines after the separator are data
            data_lines = body_lines[separator_index + 1:]
        else:
            logger.warning('No separator line found in the body.')
            return Data(data=None, comment="Could not parse body to get column names and data")

        if len(subheader_lines) >= 2:
            # Extract column names from the first line of subheader
            colnames_line = subheader_lines[0]
            column_names = colnames_line.strip().split()

            N = len(column_names)  # Number of columns

            # Extract units from the second line of subheader
            units_line = subheader_lines[1]
            units_list = units_line.strip().split()

            # Process column names and units to adjust units according to rules
            column_name_unit_pairs = process_column_names_and_units(
                column_names, units_list)

            # Unzip the pairs into separate lists
            column_names, units = zip(*column_name_unit_pairs)

            # Ensure that lengths match
            assert len(column_names) == len(
                units), "Column names and units lists must have the same length."

        else:
            logger.warning(
                'Not enough lines in subheader to extract column names and units.')
            return Data(data=None, comment="Could not parse subheader to get column names and units")

        # Parse data lines
        parsed_rows = []
        for line_num, line in enumerate(data_lines):
            if not line.strip() or set(line.strip()) == {'-'}:
                continue  # Skip empty lines and separator lines

            parts = line.strip().split()

            # Check if the line has at least N parts
            if len(parts) < N:
                logger.error(
                    f'Line {line_num + 1} does not have enough columns: {line}')
                continue

            # The last N-1 parts should be numeric values
            numeric_parts = parts[-(N - 1):]
            text_parts = parts[:-(N - 1)] if N > 1 else parts

            # Join text parts into a single string for the first column
            first_col_value = ' '.join(text_parts).strip()

            # Convert numeric parts to floats
            try:
                float_values = [float(f.replace('D', 'E'))
                                for f in numeric_parts]
            except ValueError:
                logger.error(
                    f'Error parsing numeric data on line {line_num + 1}: {line}')
                continue

            # Combine data into a single row
            row = [first_col_value] + float_values
            parsed_rows.append(row)

        # Create DataFrame
        df_columns = column_names
        df = pd.DataFrame(parsed_rows, columns=df_columns)

        # Apply units to DataFrame columns
        for col_name, unit in zip(df.columns, units):
            if unit is not None:
                # Multiply the column values by the unit to create Pint Quantities
                df[col_name] = df[col_name].astype(
                    float).apply(lambda x: x * unit)

        # Return the DataFrame in the Data object
        return Data(data={'Data': df}, comment=f"Parsed {readable_name} data.")


@AvailableBlocksOrca.register_block
class BlockOrcaAbsorptionSpectrumViaTransitionElectricDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaAbsorptionSpectrumViaTransitionVelocityDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaCdSpectrumViaTransitionElectricDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'CD SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaCdSpectrumViaTransitionVelocityDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'CD SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaSpinFlipAbsorptionSpectrumViaTransitionElectricDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'SPIN-FLIP ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaSpinFlipAbsorptionSpectrumViaTransitionVelocityDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'SPIN-FLIP ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaSpinFlipCdSpectrumViaTransitionElectricDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'SPIN-FLIP CD SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaSpinFlipCdSpectrumViaTransitionVelocityDipoleMoments(BlockOrcaSpectrumType):
    """
    Parses the 'SPIN-FLIP CD SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaCdSpectrum(BlockOrcaSpectrumType):
    """
    Parses the 'CD SPECTRUM' block.
    """
    pass


@AvailableBlocksOrca.register_block
class BlockOrcaRotationalSpectrum(Block):
    pass
