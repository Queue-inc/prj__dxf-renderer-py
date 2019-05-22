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

from .line import pattern_line
from .line import textured_line


def draw_polyline(
        entity: ezdxf.legacy.polyline.Polyline,
        drawing: ezdxf.drawing.Drawing) -> Optional[Tuple[OpenCVOp, BoundingBox]]:
    """多角実線を描画します"""

    if entity.is_3d_polyline:
        raise NotImplementedError

    color = util.get_color(entity, drawing)
    thickness = util.get_linewidth(entity, drawing)
    linetype = util.get_linetype(entity, drawing)
    vertices = [v.dxf.location[:2] for v in entity.vertices()]

    if linetype is None or linetype.dxf.length == 0:
        op = OpenCVOp(_draw_pl_op,
                      args=((vertices, S.SEQUENCE_MAPPING),),
                      kwargs={
                          'color': (color, S.NO_MAPPING),
                          'thickness': (thickness, S.CONSTANT_MAPPING),
                          'is_closed': (entity.is_closed, S.NO_MAPPING)})
    elif 'pattern' in linetype.dxfattribs().keys():
        pattern = util.scale_linetype_length(linetype.dxf.pattern)
        op = OpenCVOp(_draw_pl_op,
                      args=((vertices, S.SEQUENCE_MAPPING),),
                      kwargs={
                          'color': (color, S.NO_MAPPING),
                          'thickness': (thickness, S.CONSTANT_MAPPING),
                          'is_closed': (entity.is_closed, S.NO_MAPPING),
                          'draw_func': (pattern_line, S.NO_MAPPING),
                          'pattern': (pattern, S.SEQUENCE_MAPPING),
                          'dot_radius': (util.get_dot_radius(entity, drawing), S.CONSTANT_MAPPING)})
    else:
        op = OpenCVOp(_draw_pl_op,
                      args=((vertices, S.SEQUENCE_MAPPING),),
                      kwargs={
                          'color': (color, S.NO_MAPPING),
                          'thickness': (thickness, S.CONSTANT_MAPPING),
                          'is_closed': (entity.is_closed, S.NO_MAPPING),
                          'draw_func': (textured_line, S.NO_MAPPING),
                          'pattern_string': (entity.dxf.description, S.NO_MAPPING),
                          'pattern_length': (util.scale_linetype_length(entity.dxf.length), S.CONSTANT_MAPPING)})

    x_list = [v[0] for v in vertices]
    y_list = [v[1] for v in vertices]
    bbox = ((min(x_list), min(y_list)), (max(x_list), max(y_list)))
    return op, bbox


def draw_lwpolyline(
        entity: ezdxf.modern.lwpolyline.LWPolyline,
        drawing: ezdxf.drawing.Drawing) -> Optional[Tuple[OpenCVOp, BoundingBox]]:
    """軽量ポリラインを描画します"""

    color = util.get_color(entity, drawing)
    thickness = util.get_linewidth(entity, drawing)
    linetype = util.get_linetype(entity, drawing)
    vertices = [v[:2] for v in entity.vertices()]

    if linetype is None or linetype.dxf.length == 0:
        op = OpenCVOp(_draw_pl_op,
                      args=((vertices, S.SEQUENCE_MAPPING),),
                      kwargs={
                          'color': (color, S.NO_MAPPING),
                          'thickness': (thickness, S.CONSTANT_MAPPING),
                          'is_closed': (entity.closed, S.NO_MAPPING)})
    elif 'pattern' in linetype.dxfattribs().keys():
        pattern = util.scale_linetype_length(linetype.dxf.pattern)
        op = OpenCVOp(_draw_pl_op,
                      args=((vertices, S.SEQUENCE_MAPPING),),
                      kwargs={
                          'color': (color, S.NO_MAPPING),
                          'thickness': (thickness, S.CONSTANT_MAPPING),
                          'is_closed': (entity.closed, S.NO_MAPPING),
                          'draw_func': (pattern_line, S.NO_MAPPING),
                          'pattern': (pattern, S.SEQUENCE_MAPPING),
                          'dot_radius': (util.get_dot_radius(entity, drawing), S.CONSTANT_MAPPING)})
    else:
        op = OpenCVOp(_draw_pl_op,
                      args=((vertices, S.SEQUENCE_MAPPING),),
                      kwargs={
                          'color': (color, S.NO_MAPPING),
                          'thickness': (thickness, S.CONSTANT_MAPPING),
                          'is_closed': (entity.closed, S.NO_MAPPING),
                          'draw_func': (textured_line, S.NO_MAPPING),
                          'pattern_string': (linetype.dxf.description, S.NO_MAPPING),
                          'pattern_length': (util.scale_linetype_length(linetype.dxf.length), S.CONSTANT_MAPPING)})

    x_list = [v[0] for v in vertices]
    y_list = [v[1] for v in vertices]
    bbox = ((min(x_list), min(y_list)), (max(x_list), max(y_list)))
    return op, bbox


def _draw_pl_op(img, vertices, color, thickness, is_closed=False, draw_func=cv2.line, **kwargs):
    kwargs.update({'color': color, 'thickness': thickness})
    pt_start = None
    pt_prev = None
    for pt in vertices:
        if pt_prev is None:
            pt_start = pt
            pt_prev = pt
            continue

        draw_func(img, pt, pt_prev, **kwargs)
        pt_prev = pt

    if is_closed:
        draw_func(img, pt_start, pt_prev, **kwargs)
