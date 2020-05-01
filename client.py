import time

from connectionclient import Client
from sockethelpers.packet import Packet
from customthreading import KillableThread
from torpy.torpy.http.requests import tor_requests_session


LOOP_DELAY = 0.5
PING_DELAY = 3 * 60
HOST = "localhost"
PORT = 2000


class MainLoop(KillableThread):
    kill = lambda self: super().kill() if self.onClose() else None

    def __init__(self, loopdelay=LOOP_DELAY):
        super().__init__()

        self.count = 0
        self.loopdelay = loopdelay
        self.pingdelay = 0


    def onStart(self):
        self.client = Client(HOST, PORT)
        self.client.start()

    def connect(self):
        self.pingdelay = time.time() + PING_DELAY
        if not self.client.send(Packet("ping")):
            print("No connect, retrying.")
            self.client = Client(HOST, PORT)
            self.client.start()
            return False
        return True


    def onLoop(self):
        if time.time() > self.pingdelay:
            return self.connect()
        return None


    def onClose(self):
        self.client.kill()
        return True


    def run(self):
        self.onStart()
        while True:
            self.onLoop()
            time.sleep(self.loopdelay)
            self.count += 1



if __name__ == '__main__':
    m = MainLoop()
    m.start()
