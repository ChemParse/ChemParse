import re
import warnings
from datetime import timedelta
from io import StringIO

import numpy as np
import pandas as pd

from .data import Data
from .elements import AvailableBlocksGeneral, Block, Element, ExtractionError
from .units_and_constants import ureg


class AvailableBlocksGpaw(AvailableBlocksGeneral):
    """
    A class to store all available blocks for GPAW.
    """
    blocks: dict[str, type[Element]] = {}


@AvailableBlocksGpaw.register_block
class BlockGpawIcon(Block):
    data_available: bool = True

    def readable_name(self) -> str:
        return 'Icon'

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Gpaw Icon', None, self.raw_data

    def data(self) -> Data:
        '''
        Icon is icon, noting to extract except for the ascii symbols
        '''
        return Data(data={'Icon': self.raw_data}, comment="Raw `Icon` string")

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Gpaw Icon', None, self.raw_data


@AvailableBlocksGpaw.register_block
class BlockGpawDipole(Block):
    """
    The block captures and stores Dipole from GPAW output files.

    **Example of GPAW Output:**

    .. code-block:: none

        Dipole moment: (-0.000000, 0.000000, -1.948262) |e|*Ang

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`pint.Quantity` `Dipole Moment` in \|e\|*Ang. Can be converted to Debye with ``.to('D')``.

            Parsed data example:

            .. code-block:: none

                {'Dipole Moment': <Quantity([ 0.       -0.       -1.128191], 'angstrom * elementary_charge')>}


        :rtype: Data
        """
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", self.raw_data)
        # Convert extracted numbers to a numpy array of floats
        dipole_moment = np.array(numbers, dtype=float) * \
            ureg.elementary_charge * ureg.angstrom
        return Data(data={'Dipole Moment': dipole_moment},
                    comment="`Dipole Moment` numpy array in |e|*Ang, can be converted to Debye with .to('D')")


@AvailableBlocksGpaw.register_block
class BlockGpawEnergyContributions(Block):
    """
    The block captures and stores Energy contributions from GPAW output files.

    **Example of GPAW Output:**

    .. code-block:: none

        Energy contributions relative to reference atoms: (reference = -10231.780790)

        Kinetic:       +111.119958
        Potential:     -114.654058
        External:        +0.000000
        XC:             -93.096053
        Entropy (-ST):   +0.000000
        Local:           +0.390037
        --------------------------
        Free energy:    -96.240117
        Extrapolated:   -96.240117

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`pint.Quantity` `Reference` in eV
            - :class:`pint.Quantity` `Free energy` in eV
            - :class:`pint.Quantity` `Extrapolated` in eV
            - :class:`dict` `Contributions` with :class:`pint.Quantity`'s. Data is in eV

            Parsed data example:

            .. code-block:: none

                {'Contributions': {'Kinetic': <Quantity(106.291868, 'electron_volt')>, 
                                   'Potential': <Quantity(-113.401291, 'electron_volt')>,
                                   'External': <Quantity(0.0, 'electron_volt')>,
                                   'XC': <Quantity(-93.210989, 'electron_volt')>,
                                   'Entropy (-ST)': <Quantity(0.0, 'electron_volt')>, 
                                   'Local': <Quantity(0.39059, 'electron_volt')>},
                'Reference': <Quantity(-10231.7808, 'electron_volt')>,
                'Free energy': <Quantity(-99.929821, 'electron_volt')>,
                'Extrapolated': <Quantity(-99.929821, 'electron_volt')>
                }


        :rtype: Data
        """
        energy_data_lines = self.raw_data.split('\n')
        energy_dict = {'Contributions': {}}

        # Iterating over each line to extract relevant data
        for line in energy_data_lines:
            if 'reference' in line:
                energy_dict['Reference'] = float(
                    line.split('=')[-1].strip().split(')')[0]) * ureg.eV
            elif 'Free energy' in line:
                energy_dict['Free energy'] = float(
                    line.split(':')[-1].strip()) * ureg.eV
            elif 'Extrapolated' in line:
                energy_dict['Extrapolated'] = float(
                    line.split(':')[-1].strip()) * ureg.eV
            elif ':' in line:
                key, value = line.split(':')
                energy_dict['Contributions'][key.strip()] = float(
                    value.strip()) * ureg.eV

        return Data(data=energy_dict, comment="""`Reference`, `Free energy`, `Extrapolated` are pint.Quantity objects
                                                and `Contributions` is a nested dict of pint.Quantity objects.
                                                Data is in eV.
                                                """)


@AvailableBlocksGpaw.register_block
class BlockGpawConvergedAfter(Block):
    """
    The block captures and stores Converged after from GPAW output files.

    **Example of GPAW Output:**

    .. code-block:: none

        Converged after 12 iterations.

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def data(self) -> Data:
        """

        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`int` `Iterations`
            - :class:`bool` `Converged` is always `True`, as the block is only extracted if the calculation is converged

            Parsed data example:

            .. code-block:: none

                {'Iterations': 12, 'Converged': True}

        :rtype: Data
        """
        numbers = re.findall(r'\d+', self.raw_data)

        assert len(numbers) == 1, f"Expected 1 number, got {len(numbers)}"
        iterations = int(numbers[0])

        return Data(data={'Iterations': iterations, 'Converged': True}, comment="`Iterations` is an integer and `Converged` is always True")


@AvailableBlocksGpaw.register_block
class BlockGpawOrbitalEnergies(Block):
    """
    The block captures and stores Orbitals from GPAW output files.

    **Example of GPAW Output:**

    .. code-block:: none

                                Up                     Down
        Band  Eigenvalues  Occupancy  Eigenvalues  Occupancy
            0    -24.42908    1.00000    -24.57211    1.00000
            1    -22.16252    1.00000    -22.18228    1.00000
            2    -21.55401    1.00000    -21.60131    1.00000

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Orbitals', None, self.raw_data

    def data(self) -> Data:
        """

        :return: :class:`pychemparse.data.Data` object that contains:

            - :class:`pandas.DataFrame` `UpDownOrbitals` with columns: Band, Eigenvalues_Up, Occupancy_Up, Eigenvalues_Down, Occupancy_Down. Eigenvalues are in eV.

            Parsed data example:

            .. code-block:: none

                {'UpDownOrbitals':      Band  Eigenvalues_Up  Occupancy_Up  Eigenvalues_Down  Occupancy_Down
                0       0       -24.42908           1.0         -24.57211             1.0
                1       1       -22.16252           1.0         -22.18228             1.0
                2       2       -21.55401           1.0         -21.60131             1.0
                3       3       -19.15063           1.0         -19.19201             1.0
                4       4       -19.10920           1.0         -19.10168             1.0
                ..    ...             ...           ...               ...             ...
                247   247        81.59782           0.0          81.62746             0.0
                248   248        81.85757           0.0          81.83158             0.0
                249   249        83.60243           0.0          83.51849             0.0
                250   250        87.94628           0.0          87.90765             0.0
                251   251        95.86929           0.0          95.86901             0.0

                [252 rows x 5 columns]}

        :rtype: Data
        """
        # Using StringIO to simulate a file
        data_io = StringIO(self.raw_data)

        # Column names need to be adjusted due to duplicate 'Eigenvalues' and 'Occupancy'
        column_names = ['Band', 'Eigenvalues_Up',
                        'Occupancy_Up', 'Eigenvalues_Down', 'Occupancy_Down']

        # Reading the data using read_csv from the simulated file
        df = pd.read_csv(data_io, sep='\s+',
                         names=column_names, skiprows=2)

        df['Eigenvalues_Up'] *= ureg.eV
        df['Eigenvalues_Down'] *= ureg.eV

        return Data(data={'UpDownOrbitals': df}, comment="`UpDownOrbitals` is pandas DataFrame with columns: Band, Eigenvalues_Up, Occupancy_Up, Eigenvalues_Down, Occupancy_Down")


@AvailableBlocksGpaw.register_block
class BlockGpawTiming(Block):
    """
    The block captures and stores Timing from GPAW output files.

    **Example of GPAW Output:**

    .. code-block:: none

                Timing:                               incl.     excl.
        ------------------------------------------------------------
        Basic WFS set positions:              0.000     0.000   0.0% |
        Redistribute:                        0.000     0.000   0.0% |
        Basis functions set positions:        0.003     0.003   0.0% |
        ...
        ST tci:                               0.001     0.001   0.0% |
        Set symmetry:                         0.000     0.000   0.0% |
        TCI: Evaluate splines:                0.182     0.182   2.4% ||
        mktci:                                0.001     0.001   0.0% |
        Other:                                0.803     0.803  10.5% |---|
        ------------------------------------------------------------
        Total:                                          7.661 100.0%

    """
    data_available: bool = True
    """ Formatted data is available for this block. """

    def extract_name_header_and_body(self) -> tuple[str, str | None, str]:
        return 'Timing', None, self.raw_data

    def data(self) -> Data:
        """
        Parses the timing data, maintains the hierarchy, and extracts the total time separately.

        :return: :class:`pychemparse.data.Data` object that contains:

            - `Total`: A dictionary with 'Total Time' and 'Percentage'.
            - `TimingHierarchy`: A list of timing data entries maintaining the hierarchy.

        :rtype: Data
        """

        # Define the Node class to represent each entry in the timing data
        class Node:
            def __init__(self, name, incl_time, excl_time, percentage, level):
                self.name = name
                self.incl_time = timedelta(seconds=float(incl_time))
                self.excl_time = timedelta(seconds=float(excl_time))
                self.percentage = percentage  # Keep percentage as it is
                self.level = level
                self.children = []

            def to_dict(self):
                """Converts the node and its children to a dictionary."""
                return {
                    'name': self.name,
                    'incl_time': self.incl_time,
                    'excl_time': self.excl_time,
                    'percentage': self.percentage,
                    'children': [child.to_dict() for child in self.children]
                }

            def __repr__(self):
                return (f"Node(name='{self.name}', incl_time={self.incl_time}, "
                        f"excl_time={self.excl_time}, percentage='{self.percentage}', level={self.level})")

        # Function to parse the timing data text and build the hierarchy
        def parse_timing_data(text):
            lines = text.strip().split('\n')
            root = Node('Root', 0, 0, '0%', -1)  # Dummy root node
            stack = [root]
            total_time = None
            total_percentage = None

            for line in lines:
                # Check for the Total line
                if line.strip().startswith('Total:'):
                    total_match = re.search(
                        r'Total:\s+([\d\.]+)\s+([\d\.]+)%', line)
                    if total_match:
                        total_time = timedelta(
                            seconds=float(total_match.group(1)))
                        total_percentage = total_match.group(2) + '%'
                    continue  # Skip processing the Total line further

                # Skip lines that don't contain a colon (e.g., separators)
                if ':' not in line:
                    continue

                # Count leading spaces to determine the level
                stripped_line = line.lstrip()
                leading_spaces = len(line) - len(stripped_line)
                level = leading_spaces

                # Split the line at the colon
                name_part, rest = line.split(':', 1)
                name = name_part.strip()

                # Extract the incl_time, excl_time, and percentage
                tokens = rest.strip().split()
                # Check if this line contains timing data
                if len(tokens) >= 3 and re.match(r'[\d\.]+', tokens[0]):
                    incl_time = tokens[0]
                    excl_time = tokens[1]
                    percentage = tokens[2]
                else:
                    # If tokens are missing or not numbers, skip this line
                    continue

                # Create a new node
                node = Node(name, incl_time, excl_time, percentage, level)

                # Adjust the stack to maintain the hierarchy
                while level <= stack[-1].level and len(stack) > 1:
                    stack.pop()

                # Append the new node to the current parent
                stack[-1].children.append(node)
                # Push the new node onto the stack
                stack.append(node)

            # Return the list of top-level nodes and total time
            return root.children, total_time, total_percentage

        # Parse the timing data
        timing_entries, total_time, total_percentage = parse_timing_data(
            self.raw_data)

        # Convert the hierarchical timing data to a list of dictionaries for easier handling
        def nodes_to_dicts(nodes):
            return [node.to_dict() for node in nodes]

        timing_hierarchy = nodes_to_dicts(timing_entries)

        # Prepare the data to return
        data_dict = {
            'Total': {
                'Total Time': total_time,
                'Percentage': total_percentage
            },
            'TimingHierarchy': timing_hierarchy
        }

        return Data(
            data=data_dict,
            comment="`Total` contains the total time and percentage. `TimingHierarchy` is a list of timing entries maintaining the hierarchy, with times as timedelta objects."
        )
