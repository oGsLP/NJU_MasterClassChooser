#!usr/bin/env python
# -*- coding:utf-8 -*-
""" PyCharm
@author: oGsLP
@file: des_encrypt.py
@time: 2020/12/24 21:10
@function: 
"""
import execjs


def strEncSimple(passwd):
    js_code = ""
    with open("util/des.js", "r") as f:
        js_code = "".join(f.readlines())
    DES = execjs.compile(js_code)
    return DES.call("strEncSimple", passwd)
