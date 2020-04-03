from socketHelpers.server import ConnectionServer
from socketHelpers.server import Connection as C
from socketHelpers.packet import Packet



class Conection(C):
    pass

class DispatchServer(ConnectionServer):
    CONNECTION = Conection


if __name__ == '__main__':
    c = dispatchServer("localhost", 2000)
    c.start()
