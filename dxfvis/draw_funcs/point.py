
#!/usr/bin/env python
# -*- coding:utf-8 -*-


from typing import Tuple
from typing import Optional

import cv2
import ezdxf
import numpy as np

from dxfvis import util
from dxfvis.types import OpenCVOp
from dxfvis.types import BoundingBox
from dxfvis.types import VariableStatus as S
from dxfvis.types import NPPoint


def draw_point(
        entity: ezdxf.legacy.graphics.Point,
        drawing: ezdxf.drawing.Drawing) -> Optional[Tuple[OpenCVOp, BoundingBox]]:
    """点を描画します"""
    pass
