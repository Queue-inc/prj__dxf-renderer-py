
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


def draw_arc(
        entity: ezdxf.legacy.graphics.Arc,
        drawing: ezdxf.drawing.Drawing) -> Optional[Tuple[OpenCVOp, BoundingBox]]:
    """弧を描画します"""

    pt_center = entity.dxf.center[:2]
    radius = int(entity.dxf.radius)
    if radius == 0:
        return None

    start_angle = int(entity.dxf.start_angle)
    end_angle = int(entity.dxf.end_angle)
    start_angle, end_angle = flip_angle(start_angle, end_angle)
    linetype = util.get_linetype(entity, drawing)
    if linetype is None or linetype.dxf.length == 0:
        op = OpenCVOp(cv2.ellipse,
                      args=(
                          (pt_center, S.POINT_MAPPING),
                          ((radius, radius), S.SEQUENCE_MAPPING),
                          (0, S.NO_MAPPING),
                          (start_angle, S.NO_MAPPING),
                          (end_angle, S.NO_MAPPING)),
                      kwargs={
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})
    elif 'pattern' in linetype.dxfattribs().keys():
        pattern = util.scale_linetype_length(linetype.dxf.pattern)
        op = OpenCVOp(pattern_arc,
                      args=(
                          (pt_center, S.POINT_MAPPING),
                          (radius, S.CONSTANT_MAPPING),
                          (pattern, S.SEQUENCE_MAPPING),
                          (start_angle, S.NO_MAPPING),
                          (end_angle, S.NO_MAPPING)),
                      kwargs={
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})
    else:
        pattern_length = 1 if 'length' not in linetype.dxfattribs() else util.scale_linetype_length(linetype.dxf.length)
        op = OpenCVOp(textured_arc_approx,
                      args=(
                          (pt_center, S.POINT_MAPPING),
                          (radius, S.CONSTANT_MAPPING),
                          (linetype.dxf.description, S.NO_MAPPING),
                          (pattern_length, S.CONSTANT_MAPPING),
                          (start_angle, S.NO_MAPPING),
                          (end_angle, S.NO_MAPPING)),
                      kwargs={
                          'color': (util.get_color(entity, drawing), S.NO_MAPPING),
                          'thickness': (util.get_linewidth(entity, drawing), S.CONSTANT_MAPPING)})

    bbox = ((pt_center[0] - radius, pt_center[1] - radius), (pt_center[0] + radius, pt_center[1] + radius))

    return op, bbox


def pattern_arc(
        img: np.ndarray,
        center: NPPoint,
        radius: int,
        pattern: Tuple[float, ...],
        start_angle: int,
        end_angle: int,
        color=(255, 255, 255),
        thickness=10,
        dot_radius=4) -> None:
    """弧のパターンをDXF形式のline/dot/blankの組み合わせによって描画します"""

    if radius == 0:
        return

    total_line_length = util.degree2rad(end_angle - start_angle) * radius
    total_angle_length = abs(end_angle - start_angle)
    direction = np.sign(end_angle - start_angle)
    drawn_length: float = 0
    angle_from = start_angle
    angle_to = start_angle
    is_exceeded = False
    while not is_exceeded:
        for p in pattern[1:]:
            if p == 0:
                target_pt = (center[0] + int(radius * np.cos(util.degree2rad(angle_to))), center[1] + int(radius * np.sin(util.degree2rad(angle_to))))
                cv2.circle(img, target_pt, dot_radius, color, thickness=-1)
                continue

            p_abs = abs(p)
            angle_abs = util.rad2degree(p_abs / radius)
            drawn_length += angle_abs
            if drawn_length > total_angle_length:
                angle_abs = total_angle_length - drawn_length + angle_abs
                is_exceeded = True

            angle_from = angle_to
            angle_to += direction * angle_abs
            if p > 0:
                cv2.ellipse(img, center, (radius, radius), 0, angle_from, angle_to, color, thickness)

            if is_exceeded:
                break


def textured_arc_approx(
        img: np.ndarray,
        center: NPPoint,
        radius: int,
        pattern_string: str,
        pattern_length: float,
        start_angle: int,
        end_angle: int,
        color=(255, 255, 255),
        thickness=4,
        dot_radius=4) -> None:
    """弧のパターンをDXF形式のline/dot/blankの組み合わせによって描画します"""
    pattern = util.approx_pattern_string(pattern_string, pattern_length)
    pattern_arc(img, center, radius, pattern, start_angle, end_angle, color, thickness, dot_radius)


def flip_angle(start_angle, end_angle):
    if start_angle < 0:
        start_angle = 360 + start_angle
    if end_angle < 0:
        end_angle = 360 + end_angle

    if start_angle < end_angle:
        if start_angle != 0:
            start_angle = 360 - start_angle
            end_angle = 360 - end_angle
        else:
            end_angle *= -1

        return start_angle, end_angle
    else:
        start_angle = 360 - start_angle
        end_angle *= -1

        return start_angle, end_angle
