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

class DispatchServer(ConnectionServer):
    CONNECTION = Conection1

    def connect_event(self, con):
        pass

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
    c = dispatchServer("localhost", 2000)
    c.start()
