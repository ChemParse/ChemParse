import re
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd

from .data import Data
from .elements import AvailableBlocks, Block, Element, ExtractionError
from .units_and_constants import ureg


class AvailableBlocksGpaw(AvailableBlocks):
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
class BlockGpawUnknown(Block):
    def data(self):
        warnings.warn(
            f'The block looks not structured. Please contribute to the project if you have knowledge on how to extract data from it.')
        return Data(data={'raw data': self.raw_data},
                    comment=("No procedure for analyzing the data found, furthermore, the block looks not structured `raw data` collected.\n"
                             "Please contribute to the project if you have knowledge on how to extract data from it."))
