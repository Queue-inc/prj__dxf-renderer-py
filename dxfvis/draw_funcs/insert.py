#!/usr/bin/env python
# -*- coding:utf-8 -*-


from typing import Optional
from typing import Tuple

import cv2
import ezdxf
import numpy as np

from dxfvis import util
from dxfvis.types import OpenCVOp
from dxfvis.types import BoundingBox
from dxfvis.types import VariableStatus as S
from dxfvis.types import NPPoint

from .arc import pattern_arc
from .arc import textured_arc_approx


def draw_insert(
        entity: ezdxf.legacy.insert.Insert,
        drawing: ezdxf.drawing.Drawing) -> Optional[Tuple[OpenCVOp, BoundingBox]]:
    """Blockを挿入します"""
    pass
