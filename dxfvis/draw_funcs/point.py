
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

    pt = entity.dxf.location[:2]
    color = util.get_color(entity, drawing)
    radius = util.get_dot_radius(entity, drawing)

    op = OpenCVOp(cv2.circle,
                  args=((pt, S.POINT_MAPPING), (radius, S.CONSTANT_MAPPING)),
                  kwargs={
                      'color': (color, S.NO_MAPPING),
                      'thickness': -1})  # fill in the circle

    bbox = (pt, pt)

    return op, bbox
