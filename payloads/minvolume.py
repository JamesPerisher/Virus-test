import random,os,shutil,time,ctypes,webbrowser
from os.path import expanduser
from pathlib import Path
from itertools import chain

RETURNS = False

SendInput=ctypes.windll.user32.SendInput
PUL=ctypes.POINTER(ctypes.c_ulong)

class ca(ctypes.Structure):
    _fields_=[("wVk",ctypes.c_ushort),("wScan",ctypes.c_ushort),("dwFlags",ctypes.c_ulong),("time",ctypes.c_ulong),("dwExtraInfo",PUL)]

class cb(ctypes.Structure):
    _fields_=[("uMsg",ctypes.c_ulong),("wParamL",ctypes.c_short),("wParamH",ctypes.c_ushort)]

class cc(ctypes.Structure):
    _fields_=[("dx",ctypes.c_long),("dy",ctypes.c_long),("mouseData",ctypes.c_ulong),("dwFlags",ctypes.c_ulong),("time",ctypes.c_ulong),("dwExtraInfo",PUL)]

class cd(ctypes.Union):
    _fields_=[("ki",ca),("mi",cc),("hi",cb)]

class ce(ctypes.Structure):
    _fields_=[("type", ctypes.c_ulong),("ii",cd)]

VK_VOLUME_UP=0xAE

def fa(va):
    extra=ctypes.c_ulong(0)
    ii_=cd()
    ii_.ki=ca(va,0x48,0,0,ctypes.pointer(extra))
    x=ce(ctypes.c_ulong(1),ii_ )
    SendInput(1,ctypes.pointer(x),ctypes.sizeof(x))

def fb(va):
    extra=ctypes.c_ulong(0)
    ii_=cd()
    ii_.ki=ca(va,0x48,0x0002,0,ctypes.pointer(extra))
    x=ce(ctypes.c_ulong(1),ii_)
    SendInput(1,ctypes.pointer(x),ctypes.sizeof(x))

def fc(va,length=0):
    fa(va)
    time.sleep(length)
    fb(va)

def execute(caller):
    while caller.running:
        fa(VK_VOLUME_UP)
        fb(VK_VOLUME_UP)
        time.sleep(0.02)
