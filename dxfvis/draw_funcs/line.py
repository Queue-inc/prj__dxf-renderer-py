#!/usr/bin/env python
# -*- coding:utf-8 -*-


from typing import Tuple

import cv2
import ezdxf
import numpy as np

from dxfvis import util
from dxfvis.types import OpenCVOp
from dxfvis.types import BoundingBox
from dxfvis.types import VariableStatus as S
from dxfvis.types import NPPoint


def draw_line(
        entity: ezdxf.legacy.graphics.Line,
        drawing: ezdxf.drawing.Drawing) -> Tuple[OpenCVOp, BoundingBox]:
    """実線を描画します"""

    linetype = util.get_linetype(entity, drawing)
    if linetype is None or linetype.dxf.length == 0:
        op = OpenCVOp(cv2.line,
                      args=((entity.dxf.start, S.POINT_MAPPING), (entity.dxf.end, S.POINT_MAPPING)),
                      kwargs={
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})
    elif 'pattern' in linetype.dxfattribs().keys():
        op = OpenCVOp(pattern_line,
                      args=((entity.dxf.start, S.POINT_MAPPING), (entity.dxf.end, S.POINT_MAPPING)),
                      kwargs={
                          'pattern': (linetype.dxf.pattern, S.SEQUENCE_MAPPING),
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING),
                          'dot_radius': (util.get_dot_radius(entity, drawing), S.CONSTANT_MAPPING)})
    else:
        pattern_length = 1 if 'length' not in entity.dxfattribs() else entity.dxf.length
        op = OpenCVOp(textured_line,
                      args=((entity.dxf.start, S.POINT_MAPPING), (entity.dxf.end, S.POINT_MAPPING)),
                      kwargs={
                          'pattern_string': (entity.dxf.description, S.NO_MAPPING),
                          'pattern_length': (entity.dxf.length, S.CONSTANT_MAPPING),
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})

    xmin = min(entity.dxf.start[0], entity.dxf.end[0])
    xmax = max(entity.dxf.start[0], entity.dxf.end[0])
    ymin = min(entity.dxf.start[1], entity.dxf.end[1])
    ymax = min(entity.dxf.start[1], entity.dxf.end[1])
    bbox = ((xmin, ymin), (xmax, ymax))

    return op, bbox


def pattern_line(
        img: np.ndarray,
        pt1: NPPoint,
        pt2: NPPoint,
        pattern: Tuple[float, ...],
        color=(255, 255, 255),
        thickness=10,
        dot_radius=4) -> None:
    """2点間の線状のパターンをDXF形式のline/dot/blankの組み合わせによって描画します"""

    total_line_length = np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
    drawn_length: float = 0
    # pt1とpt2がなす角を求める
    angle = util.get_angle_between(pt1, pt2)
    if angle is None:
        return

    x_coef = np.cos(angle)
    y_coef = np.sin(angle)

    start_pt = pt1
    end_pt = pt1
    while drawn_length <= total_line_length:
        for p in pattern:
            if p == 0:
                cv2.circle(img, end_pt, dot_radius, color, thickness=-1)
                continue

            p_abs = abs(p)
            drawn_length += p_abs
            if drawn_length > total_line_length:
                break

            start_pt = end_pt
            end_pt = (end_pt[0] + int(p_abs * x_coef), end_pt[1] + int(p_abs * y_coef))
            if p > 0:
                cv2.line(img, start_pt, end_pt, color, thickness)


def textured_line(
        img: np.ndarray,
        pt1: NPPoint,
        pt2: NPPoint,
        pattern_string: str,
        pattern_length: float,
        color=(255, 255, 255),
        font=cv2.FONT_HERSHEY_SIMPLEX) -> None:
    """2点間の線状のパターンを描画します"""

    text_size, baseline = cv2.getTextSize(pattern_string, font, fontScale=1., thickness=1)
    font_scale = pattern_length / text_size[0]
    total_line_length = np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
    # pt1とpt2がなす角を求める
    angle_rad = util.get_angle_between(pt1, pt2)
    if angle_rad is None:
        return

    angle = util.rad2degree(angle_rad)
    drawn_length: float = 0
    org = pt1
    while drawn_length <= total_line_length:
        util.putTextRotated(img, angle, pattern_string, org, font, font_scale, color)
        org = (org[0] + int(pattern_length * np.cos(angle_rad)), org[1] + int(pattern_length * np.sin(angle_rad)))
        drawn_length += pattern_length
