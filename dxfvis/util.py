#!/usr/bin/env python
# -*- coding:utf-8 -*-

import cv2
import numpy as np


def get_color(entity, drawing):
    """get color of an entity"""
    color = (255, 255, 255)  # default
    if hasattr(entity.dxf, 'color'):
        color = entity.dxf.color

    if color == 0:  # BYBLOCK
        color = (255, 255, 255)
    elif color == 256:  # BYLAYER
        layer = drawing.layers.get(entity.dxf.layer)
        color = layer.dxf.color

    if isinstance(color, int):
        color = _acadcolor2rgb(color)

    return color


def get_linewidth(entity, drawing):
    """(!deprecated) get line width of an entity"""
    return 3


def get_linetype(entity, drawing):
    """get line type of an entity"""

    ent_params = entity.dxfattribs()
    if drawing.layers.has_entry(entity.dxf.layer):
        layer_params = drawing.layers.get(entity.dxf.layer).dxfattribs()
    else:
        layer_params = {}

    if 'linetype' in ent_params.keys():
        linetype_repr = ent_params['linetype']
        if linetype_repr == 'BYBLOCK':
            linetype = None
        elif linetype_repr == 'BYLAYER':
            linetype_repr_ = layer_params.get('linetype')
            if linetype_repr_ is None:
                linetype = None
            else:
                linetype = drawing.linetypes.get(linetype_repr_)
        else:
            linetype = drawing.linetypes.get(linetype_repr)
    elif 'linetype' in layer_params.keys():
        linetype = drawing.linetypes.get(layer_params['linetype'])
    else:
        linetype = None

    return linetype


def get_dot_radius(entity, drawing):
    """(!deprecated) get dot radius inside an entity"""
    return 4


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
    prev_sign = None  # 0: blank, 1: line
    run_length = 0
    for idx, char in enumerate(pattern_string):
        if char == ' ':
            this_sign = -1
        else:
            this_sign = 1

        if idx == 0:
            prev_sign = this_sign
            run_length += 1
            continue

        if prev_sign == this_sign:
            run_length += 1
        else:
            patterns.append(prev_sign * run_length * char_size)
            prev_sign = this_sign
            run_length = 1

        if idx == len(pattern_string) - 1 and run_length > 0:
            patterns.append(prev_sign * run_length * char_size)

    return tuple(patterns)


def scale_linetype_length(values):
    if hasattr(values, '__len__'):
        total_length = values[0]
    else:
        total_length = values

    if total_length >= 300 or total_length == 0:
        return values

    scale = 300 / total_length
    if hasattr(values, '__len__'):
        return [v * scale for v in values]

    return values * scale


def _acadcolor2rgb(acadcolor):
    assert acadcolor > 0 and acadcolor < 250
    color_index = {
        1: (255, 0, 0),
        2: (255, 255, 0),
        3: (0, 255, 0),
        4: (0, 255, 255),
        5: (0, 0, 255),
        6: (255, 0, 255),
        7: (255, 255, 255),
        8: (128, 128, 128),
        9: (192, 192, 192),
        10: (255, 0, 0),
        20: (255, 63, 0),
        30: (255, 127, 0),
        40: (255, 191, 0),
        50: (255, 255, 0),
        60: (191, 255, 0),
        70: (127, 255, 0),
        80: (63, 255, 0),
        90: (0, 255, 0),
        100: (0, 255, 63),
        110: (0, 255, 127),
        120: (0, 255, 191),
        130: (0, 255, 255),
        140: (0, 191, 255),
        150: (0, 127, 255),
        160: (0, 63, 255),
        170: (0, 0, 255),
        180: (63, 0, 255),
        190: (127, 0, 255),
        200: (191, 0, 255),
        210: (255, 0, 255),
        220: (255, 0, 191),
        230: (255, 0, 127),
        240: (255, 0, 63),
        11: (255, 127, 127),
        21: (255, 159, 127),
        31: (255, 191, 127),
        41: (255, 223, 127),
        51: (255, 255, 127),
        61: (223, 255, 127),
        71: (191, 255, 127),
        81: (159, 255, 127),
        91: (127, 255, 127),
        101: (127, 255, 159),
        111: (127, 255, 191),
        121: (127, 255, 223),
        131: (127, 255, 255),
        141: (127, 223, 255),
        151: (127, 191, 255),
        161: (127, 159, 255),
        171: (127, 127, 255),
        181: (159, 127, 255),
        191: (191, 127, 255),
        201: (223, 127, 255),
        211: (255, 127, 255),
        221: (255, 127, 223),
        231: (255, 127, 191),
        241: (255, 127, 159),
        12: (204, 0, 0),
        22: (204, 51, 0),
        32: (204, 102, 0),
        42: (204, 153, 0),
        52: (204, 204, 0),
        62: (153, 204, 0),
        72: (102, 204, 0),
        82: (51, 204, 0),
        92: (0, 204, 0),
        102: (0, 204, 51),
        112: (0, 204, 102),
        122: (0, 204, 153),
        132: (0, 204, 204),
        142: (0, 153, 204),
        152: (0, 102, 204),
        162: (0, 51, 204),
        172: (0, 0, 204),
        182: (51, 0, 204),
        192: (102, 0, 204),
        202: (153, 0, 204),
        212: (204, 0, 204),
        222: (204, 0, 153),
        232: (204, 0, 102),
        242: (204, 0, 51),
        13: (204, 102, 102),
        23: (204, 127, 102),
        33: (204, 153, 102),
        43: (204, 178, 102),
        53: (204, 204, 102),
        63: (178, 204, 102),
        73: (153, 204, 102),
        83: (127, 204, 102),
        93: (102, 204, 102),
        103: (102, 204, 127),
        113: (102, 204, 153),
        123: (102, 204, 178),
        143: (102, 204, 204),
        133: (102, 178, 204),
        153: (102, 153, 204),
        163: (102, 127, 204),
        173: (102, 102, 204),
        183: (127, 102, 204),
        193: (153, 102, 204),
        203: (178, 102, 204),
        213: (204, 102, 204),
        223: (204, 102, 178),
        233: (204, 102, 153),
        243: (204, 102, 127),
        14: (152, 0, 0),
        24: (152, 38, 0),
        34: (152, 76, 0),
        44: (152, 114, 0),
        54: (152, 152, 0),
        64: (114, 152, 0),
        74: (76, 152, 0),
        84: (38, 152, 0),
        94: (0, 152, 0),
        104: (0, 152, 38),
        114: (0, 152, 76),
        124: (0, 152, 114),
        134: (0, 152, 152),
        144: (0, 114, 152),
        154: (0, 76, 152),
        164: (0, 38, 152),
        174: (0, 0, 152),
        184: (38, 0, 152),
        194: (76, 0, 152),
        204: (114, 0, 152),
        214: (152, 0, 152),
        224: (152, 0, 114),
        234: (152, 0, 76),
        244: (152, 0, 38),
        15: (152, 76, 76),
        25: (152, 95, 76),
        35: (152, 114, 76),
        45: (152, 133, 76),
        55: (152, 152, 76),
        65: (133, 152, 76),
        75: (114, 152, 76),
        85: (95, 152, 76),
        95: (76, 152, 76),
        105: (76, 152, 95),
        115: (76, 152, 114),
        125: (76, 152, 133),
        135: (76, 152, 152),
        145: (76, 133, 152),
        155: (76, 114, 152),
        165: (76, 95, 152),
        175: (76, 76, 152),
        185: (95, 76, 152),
        195: (114, 76, 152),
        205: (133, 76, 152),
        215: (152, 76, 152),
        225: (152, 76, 133),
        235: (152, 76, 114),
        245: (152, 76, 95),
        16: (127, 0, 0),
        26: (127, 31, 0),
        36: (127, 63, 0),
        46: (127, 95, 0),
        56: (127, 127, 0),
        66: (95, 127, 0),
        76: (63, 127, 0),
        86: (31, 127, 0),
        96: (0, 127, 0),
        106: (0, 127, 31),
        116: (0, 127, 63),
        126: (0, 127, 95),
        136: (0, 127, 127),
        146: (0, 95, 127),
        156: (0, 63, 127),
        166: (0, 31, 127),
        176: (0, 0, 127),
        186: (31, 0, 127),
        196: (63, 0, 127),
        206: (95, 0, 127),
        216: (127, 0, 127),
        226: (127, 0, 95),
        236: (127, 0, 61),
        246: (127, 0, 31),
        17: (127, 63, 63),
        27: (127, 79, 63),
        37: (127, 95, 63),
        47: (127, 111, 63),
        57: (127, 127, 63),
        67: (111, 127, 63),
        77: (95, 127, 63),
        87: (79, 127, 63),
        97: (63, 127, 63),
        107: (63, 127, 79),
        117: (63, 127, 95),
        127: (63, 127, 111),
        137: (63, 127, 127),
        147: (63, 111, 127),
        157: (63, 95, 127),
        167: (63, 79, 127),
        177: (63, 63, 127),
        187: (79, 63, 127),
        197: (95, 63, 127),
        207: (111, 63, 127),
        217: (127, 63, 127),
        227: (127, 63, 111),
        237: (127, 63, 95),
        247: (127, 63, 79),
        18: (76, 0, 0),
        28: (76, 19, 0),
        38: (76, 38, 0),
        48: (76, 57, 0),
        58: (76, 76, 0),
        68: (57, 76, 0),
        78: (38, 76, 0),
        88: (19, 76, 0),
        98: (0, 76, 0),
        108: (0, 76, 19),
        118: (0, 76, 38),
        128: (0, 76, 57),
        138: (0, 76, 76),
        148: (0, 57, 76),
        158: (0, 38, 76),
        168: (0, 19, 76),
        178: (0, 0, 76),
        188: (19, 0, 76),
        198: (38, 0, 76),
        208: (57, 0, 76),
        218: (76, 0, 76),
        228: (76, 0, 57),
        238: (76, 0, 38),
        248: (76, 0, 19),
        19: (76, 38, 38),
        29: (76, 47, 38),
        39: (76, 57, 38),
        49: (76, 66, 38),
        59: (76, 76, 38),
        69: (66, 76, 38),
        79: (57, 76, 38),
        89: (47, 76, 38),
        99: (38, 76, 38),
        109: (38, 76, 47),
        119: (38, 76, 57),
        129: (38, 76, 66),
        139: (38, 76, 76),
        149: (38, 66, 76),
        159: (38, 57, 76),
        169: (38, 47, 76),
        179: (38, 38, 76),
        189: (47, 38, 76),
        199: (57, 38, 76),
        209: (66, 38, 76),
        219: (76, 38, 76),
        229: (76, 38, 66),
        239: (76, 38, 57),
        249: (76, 38, 47),
    }
    return color_index[acadcolor]
