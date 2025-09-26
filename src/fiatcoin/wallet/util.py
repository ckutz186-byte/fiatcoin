import hashlib
from dataclasses import dataclass
from coincurve import PrivateKey, PublicKey


ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


@dataclass
class Address:
    data: bytes
    

class KeyPair:
    def __init__(self, private_key: bytes | None = None):
        self._priv = PrivateKey(private_key) if private_key else PrivateKey()
        self._pub = self._priv.public_key.format(compressed=True)
        self._addr = self._make_address(self._pub)

    @property
    def private_key(self) -> bytes:
        return self._priv.secret

    @property
    def public_key(self) -> bytes:
        return self._pub

    @property
    def address(self) -> Address:
        return self._addr
    
    def sign(self, msg: bytes) -> bytes:
        digest = hashlib.sha256(msg).digest()
        return self._priv.sign(digest) # type: ignore
    
    def verify(self, msg: bytes, signature: bytes) -> bool:
        digest = hashlib.sha256(msg).digest()
        pubkey = PublicKey(self._pub)
        return pubkey.verify(signature, digest)

    def _b58encode(self, b: bytes) -> str:
        n = int.from_bytes(b, "big")
        res = bytearray()
        while n > 0:
            n, r = divmod(n, 58)
            res.append(ALPHABET[r])
        res.reverse()
        prefix = 0
        for byte in b:
            if byte == 0:
                prefix += 1
            else:
                break
        return (ALPHABET[0:1] * prefix + res).decode("ascii")

    def _hash160(self, data: bytes) -> bytes:
        sha = hashlib.sha256(data).digest()
        rip = hashlib.new("ripemd160", sha).digest()
        return rip

    def _make_address(self, public_key: bytes, version: bytes = b"\x00") -> Address:
        h160 = self._hash160(public_key)
        payload = version + h160
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        full = payload + checksum
        return Address(data=self._b58encode(full).encode())
