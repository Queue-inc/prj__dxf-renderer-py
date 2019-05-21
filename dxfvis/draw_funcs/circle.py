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


def draw_circle(
        entity: ezdxf.legacy.graphics.Circle,
        drawing: ezdxf.drawing.Drawing) -> Optional[Tuple[OpenCVOp, BoundingBox]]:
    """円を描画します"""

    linetype = util.get_linetype(entity, drawing)
    pt_center = entity.dxf.center[:2]
    radius = int(entity.dxf.radius)
    if radius == 0:
        return None

    if linetype is None or linetype.dxf.length == 0:
        op = OpenCVOp(cv2.circle,
                      args=((pt_center, S.POINT_MAPPING), (radius, S.CONSTANT_MAPPING)),
                      kwargs={
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})
    elif 'pattern' in linetype.dxfattribs().keys():
        op = OpenCVOp(pattern_arc,
                      args=(
                          (pt_center, S.POINT_MAPPING),
                          ((radius, radius), S.SEQUENCE_MAPPING),
                          (entity.dxf.pattern, S.SEQUENCE_MAPPING),
                          (0, S.NO_MAPPING),
                          (360, S.NO_MAPPING)),
                      kwargs={
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})
    else:
        pattern_length = 1 if 'length' not in entity.dxfattribs() else entity.dxf.length
        op = OpenCVOp(textured_arc_approx,
                      args=(
                          (pt_center, S.POINT_MAPPING),
                          ((radius, radius), S.SEQUENCE_MAPPING),
                          (entity.dxf.description, S.NO_MAPPING),
                          (pattern_length, S.CONSTANT_MAPPING),
                          (0, S.NO_MAPPING),
                          (360, S.NO_MAPPING)),
                      kwargs={
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})

    bbox = ((pt_center[0] - radius, pt_center[1] - radius), (pt_center[0] + radius, pt_center[1] + radius))
    return op, bbox
