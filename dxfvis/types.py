#!/usr/bin/env python
# -*- coding:utf-8 -*-

from enum import Enum

from typing import Any
from typing import Callable
from typing import Dict
from typing import NamedTuple
from typing import Sequence
from typing import Tuple
from typing import TypeVar

import numpy as np


DXFPoint = Tuple[float, float]
BoundingBox = Tuple[DXFPoint, DXFPoint]
NPPoint = Tuple[int, int]
Size = Tuple[int, ...]
Scalar = TypeVar('Scalar', int, float)


class VariableStatus(Enum):
    NO_MAPPING = 1
    CONSTANT_MAPPING = 2
    POINT_MAPPING = 3
    SEQUENCE_MAPPING = 4


class OpenCVOp(object):
    """representing opencv operations about drawing"""

    func: Callable[..., Any]
    args: Sequence[Tuple[Any, VariableStatus]]
    kwargs: Dict[str, Tuple[Any, VariableStatus]]

    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, img: np.ndarray, op_space: Tuple[DXFPoint, DXFPoint]) -> None:
        """ call opencv function with the scale into consideration """
        # map args
        args = []
        for val, status in self.args:
            if status == VariableStatus.CONSTANT_MAPPING:
                args.append(self._map_constant(val, op_space[0], op_space[1], img.shape))
            elif status == VariableStatus.POINT_MAPPING:
                args.append(self._map_point(val, op_space[0], op_space[1], img.shape))
            elif status == VariableStatus.SEQUENCE_MAPPING:
                if hasattr(val[0], '__len__'):
                    val = tuple([self._map_point(v, op_space[0], op_space[1], img.shape) for v in val])
                else:
                    val = tuple([self._map_constant(v, op_space[0], op_space[1], img.shape) for v in val])
                args.append(val)
            else:
                args.append(val)

        kwargs = {}
        for key, (val, status) in self.kwargs.items():
            if status == VariableStatus.CONSTANT_MAPPING:
                kwargs[key] = self._map_constant(val, op_space[0], op_space[1], img.shape)
            elif status == VariableStatus.POINT_MAPPING:
                kwargs[key] = self._map_point(val, op_space[0], op_space[1], img.shape)
            elif status == VariableStatus.SEQUENCE_MAPPING:
                val = kwargs[key]
                if hasattr(val[0], '__len__'):
                    val = tuple([self._map_point(v, op_space[0], op_space[1], img.shape) for v in val])
                else:
                    val = tuple([self._map_constant(v, op_space[0], op_space[1], img.shape) for v in val])

                kwargs[key] = val
            else:
                kwargs[key] = val

        self.func(img, *args, **kwargs)

    @staticmethod
    def _map_point(pt: DXFPoint, extmin: DXFPoint, extmax: DXFPoint, canvas_shape: Size) -> NPPoint:
        """DXFファイル上の座標をキャンバスのものにmapします

        : param pt: DXFファイル上の座標
        : param extmin: DXFファイルの最小端
        : param extmax: DXFファイルの最大端
        : param canvas_shape: キャンバスの大きさ
        """
        x, y = pt[:2]
        new_x = int((x - extmin[0]) / (extmax[0] - extmin[0]) * canvas_shape[1])
        new_y = int((y - extmin[1]) / (extmax[1] - extmin[1]) * canvas_shape[0])
        new_y = canvas_shape[0] - new_y
        return (new_x, new_y)

    @staticmethod
    def _map_constant(const: Scalar, extmin: DXFPoint, extmax: DXFPoint, canvas_shape: Size) -> Scalar:
        """DXFファイル上の定数をキャンバスのものにmapします

        : param const: DXFファイル上の定数
        : param extmin: DXFファイルの最小端
        : param extmax: DXFファイルの最大端
        : param canvas_shape: キャンバスの大きさ
        """
        const_type = type(const)
        scale = canvas_shape[1] / (extmax[0] - extmin[0])
        const_ = const * scale
        return const_type(const_)
