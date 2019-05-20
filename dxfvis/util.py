#!/usr/bin/env python
# -*- coding:utf-8 -*-

import numpy as np


def get_color(entity, drawing):
    pass


def get_linewidth(entity, drawing):
    pass


def get_linetype(entity, drawing):
    pass


def get_dot_radius(entity, drawing):
    pass


def degree2rad(deg):
    """角度->ラジアンの変換"""
    return deg / 180 * np.pi


def rad2degree(rad):
    """ラジアン->角度の変換"""
    return rad / np.pi * 180


def putTextRotated(img, angle, text, org, fontFace, fontScale, color, thickness=1):
    """textを回転させて配置します"""

    height, width = img.shape[:2]
    img_canvas = np.zeros_like(img)
    cv2.putText(img_canvas, text, org, fontFace, fontScale, color, thickness)
    # rotate text
    angle = 360 - angle
    trans = cv2.getRotationMatrix2D(org, angle, 1)
    img_text = cv2.warpAffine(img_canvas, trans, (width, height))
    img[:] = np.maximum(img, img_text)


def get_angle_between(pt1, pt2):
    """pt1を原点とした時のpt2の位相を求めます.
    値域は0 ~ 2pi.
    例外としてpt1とpt2が同一である場合Noneを返します"""

    if pt1 == pt2:
        return None

    x_diff = pt2[0] - pt1[0]
    y_diff = pt2[1] - pt1[1]
    if x_diff == 0:
        angle = np.pi / 2 if y_diff > 0 else np.pi * 1.5
    elif y_diff == 0:
        angle = 0 if x_diff > 0 else np.pi
    else:
        angle = np.arctan(y_diff / x_diff)

    # limit to 0 ~ 2 pi
    if angle * y_diff < 0:
        angle = np.pi + angle

    return angle


def approx_pattern_string(pattern_string, pattern_length):
    """pattern stringを近似します"""

    char_num = len(pattern_string)
    char_size = pattern_length / char_num
    idx = 0
    patterns = [pattern_length]
    for char in pattern_string:
        if char == ' ':
            patterns.append(-1 * char_size)
        else:
            patterns.append(char_size)

    return tuple(patterns)
