import re
import warnings
from datetime import timedelta

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

        :return: :class:`orcaparse.data.Data` object that contains:

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
    The block captures and stores TD-DFT excited states data for singlets from GPAW output files.

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

        :return: :class:`orcaparse.data.Data` object that contains:

            - :class:`pint.Quantity` `Reference` in Eh
            - :class:`pint.Quantity` `Free energy` in Eh
            - :class:`pint.Quantity` `Extrapolated` in Eh
            - :class:`dict` `Contributions` with :class:`pint.Quantity`'s. Data is in Eh

            Parsed data example:

            .. code-block:: none

                {'Contributions': {'Kinetic': <Quantity(98.027982, 'hartree')>,
                    'Potential': <Quantity(-102.525405, 'hartree')>,
                    'External': <Quantity(0.0, 'hartree')>,
                    'XC': <Quantity(-86.298926, 'hartree')>,
                    'Entropy (-ST)': <Quantity(0.0, 'hartree')>,
                    'Local': <Quantity(0.41107, 'hartree')>},
                'Reference': <Quantity(-11791.6456, 'hartree')>,
                'Free energy': <Quantity(-90.385279, 'hartree')>,
                'Extrapolated': <Quantity(-90.385279, 'hartree')>
                }

        :rtype: Data
        """
        energy_data_lines = self.raw_data.split('\n')
        energy_dict = {'Contributions': {}}

        # Iterating over each line to extract relevant data
        for line in energy_data_lines:
            if 'reference' in line:
                energy_dict['Reference'] = float(
                    line.split('=')[-1].strip().split(')')[0]) * ureg.Eh
            elif 'Free energy' in line:
                energy_dict['Free energy'] = float(
                    line.split(':')[-1].strip()) * ureg.Eh
            elif 'Extrapolated' in line:
                energy_dict['Extrapolated'] = float(
                    line.split(':')[-1].strip()) * ureg.Eh
            elif ':' in line:
                key, value = line.split(':')
                energy_dict['Contributions'][key.strip()] = float(
                    value.strip()) * ureg.Eh

        return Data(data=energy_dict, comment="""`Reference`, `Free energy`, `Extrapolated` are pint.Quantity objects
                                                and `Contributions` is a nested dict of pint.Quantity objects.
                                                Data is in Eh.
                                                """)
