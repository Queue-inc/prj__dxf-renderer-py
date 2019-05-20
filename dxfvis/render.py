#!/usr/bin/env python
# -*- coding:utf-8 -*-

import warnings

from typing import List
from typing import Union
from typing import Optional
from typing import Tuple
from typing import TypeVar

import cv2
import ezdxf
import numpy as np
from ezdxf.drawing import Drawing
from ezdxf.legacy.graphics import GraphicEntity
from ezdxf.legacy.tableentries import Layer

from dxfvis.draw_funcs import draw_arc
from dxfvis.draw_funcs import draw_circle
from dxfvis.draw_funcs import draw_line
from dxfvis.draw_funcs import draw_polyline
from dxfvis.draw_funcs import draw_lwpolyline
from dxfvis.draw_funcs import draw_text
from dxfvis.draw_funcs import draw_point
from dxfvis.draw_funcs import draw_insert
from dxfvis.draw_funcs import draw_mtext
from dxfvis.draw_funcs import draw_ellipse

from dxfvis.types import OpenCVOp
from dxfvis.types import DXFPoint
from dxfvis.types import NPPoint
from dxfvis.types import Size
from dxfvis.types import Scalar
from dxfvis.types import BoundingBox


ACCEPTED_DXFTYPES = ['LINE', 'CIRCLE', 'ARC', 'POLYLINE', 'LWPOLYLINE']


def render_dxf(
        drawing: Union[str, Drawing],
        image_size: int,
        is_plain: bool = False) -> np.ndarray:
    """render a dxf file and return as numpy array

    :param drawing: path or object for a DXF file
    :param image_size: maximum edge length of the image to return. original scales are applied in default.
    :param is_plain: limit the use of advansed properties. better speed & less possibility to encounter unknown errors, instead of less quality.
    """

    if isinstance(drawing, str):
        drawing = ezdxf.readfile(drawing)

    ops: List[OpenCVOp] = []
    drawing_xmin = np.inf
    drawing_xmax = -np.inf
    drawing_ymin = np.inf
    drawing_ymax = -np.inf
    msp = drawing.modelspace()
    for entity in msp:
        if entity.dxftype() == 'DIMENSION':
            if 'geometry' not in entity.dxfattribs():
                warnings.warn('No block for DIMENSION ENTITY')
                continue

            block = drawing.blocks.get(entity.dxf.geometry)
            for entity_ in block:
                entity_rep = draw_entity(entity_, drawing)
                if entity_rep is None:
                    continue

                op, bb = entity_rep
                ops.append(op)
                drawing_xmin = min(drawing_xmin, bb[0][0])
                drawing_xmax = min(drawing_xmax, bb[1][0])
                drawing_ymin = min(drawing_ymin, bb[0][1])
                drawing_ymax = min(drawing_ymax, bb[1][1])

        else:
            entity_rep = draw_entity(entity, drawing)
            if entity_rep is None:
                continue

            op, bb = entity_rep
            ops.append(op)
            drawing_xmin = min(drawing_xmin, bb[0][0])
            drawing_xmax = min(drawing_xmax, bb[1][0])
            drawing_ymin = min(drawing_ymin, bb[0][1])
            drawing_ymax = min(drawing_ymax, bb[1][1])

    # render dxf as an image
    dxf_space = ((drawing_xmin, drawing_ymin), (drawing_ymin, drawing_ymax))
    aspect_ratio = (drawing_ymax - drawing_ymin) / (drawing_xmax - drawing_xmin)
    scale = image_size / max((drawing_ymax - drawing_ymin), (drawing_xmax - drawing_xmin))
    if aspect_ratio > 1:
        image_shape = (image_size, int(image_size / aspect_ratio))
    else:
        image_shape = (int(image_size * aspect_ratio), image_size)

    canvas = np.zeros(image_shape)
    # actual drawing
    for op in ops:
        if op is None:
            continue

        op(canvas, dxf_space)

    return canvas


def draw_entity(
        obj: GraphicEntity,
        drawing: Drawing) -> Optional[Tuple[OpenCVOp, BoundingBox]]:
    """DXFファイル上のEntityをキャンバスに描画します

    :param obj: 描画対象のエンティティ
    :param drawing: DXFファイル

    :returns エンティティの描画メソッド、エンティティのbb

    .. Note::
        * 対応していないdxftypeが存在します。
        * DXFファイル上でエンティティが非表示の場合・フォーマットが非対応の場合には描画を行いません。
    """

    if drawing.layers.has_entry(obj.dxf.layer):
        layer: Layer = drawing.layers.get(obj.dxf.layer)
        if not layer.is_on():
            return None

        layer_params = layer.dxfattribs()
    else:
        layer_params = {}

    dxftype = obj.dxftype()
    if dxftype not in ACCEPTED_DXFTYPES:
        return None

    if dxftype == 'ARC':
        return draw_arc(obj, drawing)
    elif dxftype == 'CIRCLE':
        return draw_circle(obj, drawing)
    elif dxftype == 'LINE':
        return draw_line(obj, drawing)
    elif dxftype == 'POLYLINE':
        return draw_polyline(obj, drawing)
    elif dxftype == 'LWPOLYLINE':
        return draw_lwpolyline(obj, drawing)
    elif dxftype == 'TEXT':
        return draw_text(obj, drawing)
    elif dxftype == 'POINT':
        return draw_point(obj, drawing)
    elif dxftype == 'INSERT':
        return draw_insert(obj, drawing)
    elif dxftype == 'MTEXT':
        return draw_mtext(obj, drawing)
    elif dxftype == 'ELLIPSE':
        return draw_ellipse(obj, drawing)
    else:
        return None
