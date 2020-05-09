from Crypto import Random
from Crypto.PublicKey import RSA



private_key = RSA.generate(1024, Random.new().read)

with open("pubkey.pem", "wb") as f:
    f.write(private_key.publickey().exportKey())

with open("privkey.pem", "wb") as f:
    f.write(private_key.exportKey('PEM', input("password: "), pkcs=1))
