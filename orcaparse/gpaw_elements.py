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
    data_available: bool = True

    def data(self) -> Data:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", self.raw_data)
        # Convert extracted numbers to a numpy array of floats
        dipole_moment = np.array(numbers, dtype=float)
        return Data(data={'Dipole Moment': dipole_moment},
                    comment="`Dipole Moment` numpy array in |e|*Ang")
