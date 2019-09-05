#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="dxfvis",
    version="0.1",
    description="Python visualization toll for dxf files",
    author="Queue-inc.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["ezdxf==0.9.0"],
)
