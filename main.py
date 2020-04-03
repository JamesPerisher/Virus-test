from consoleInterpreter import *
from server import DispatchServer

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


@cc.command(["execute"],
    Arg(object, "target device"),
    Arg(int, "Payload index.", optional=True))
def cexecute(x):
    pass


ds.start()
while True:
    print(c.handleExecute(input(": ")))


print(c)
