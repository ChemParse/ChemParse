import re
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd

from .data import Data
from .elements import AvailableBlocksGeneral, Block, Element, ExtractionError
from .units_and_constants import ureg


class AvailableBlocksVasp(AvailableBlocksGeneral):
    """
    A class to store all available blocks for Wasp.
    """
    blocks: dict[str, type[Element]] = {}
