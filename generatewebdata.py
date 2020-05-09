from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from base64 import urlsafe_b64encode
from base64 import urlsafe_b64decode
from Crypto.Signature import PKCS1_v1_5


def load_key(filename, password=""):
    with open(filename, 'rb') as f:
        data = f.read()
    key = RSA.importKey(data, password)
    return key


key = load_key("data/privkey.pem", input("password: "))
host = input("host and port: ")

data = host.encode()

digest = SHA256.new()
digest.update(data)
signer = PKCS1_v1_5.new(key)

sig = signer.sign(digest)
data = "%s.%s"%(urlsafe_b64encode(data).decode(), urlsafe_b64encode(sig).decode())
print(data)


og,sig = urlsafe_b64decode(data.split(".")[0]), urlsafe_b64decode(data.split(".")[1])
digest = SHA256.new()
digest.update(og)
print("manual verify data:", og.decode())

verifier = PKCS1_v1_5.new(load_key("data/pubkey.pem"))
if verifier.verify(digest, sig):
    print('Successfully verified message')
else:
    print('Signature verification failed')
