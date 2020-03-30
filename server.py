from socketHelpers.server import ConnectionServer
from socketHelpers.server import Connection as C
from socketHelpers.packet import Packet



class Conection(C):
    pass

class dispatchServer(ConnectionServer):
    CONNECTION = Conection

    def connect_event(self, conn):
        conn.send(Packet("execute_list", ""))
        conn.send(Packet("execute", "0"))

    def distribute_packet(self, packet):
        for i in self:
            self[i].send(packet)


c = dispatchServer("localhost", 2000)
c.start()
