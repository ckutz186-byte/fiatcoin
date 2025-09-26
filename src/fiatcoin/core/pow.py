import struct
from fiatcoin.core.hash import sha256d


def target_from_bits(difficulty_bits: int) -> int:
    return 1 << (256 - difficulty_bits)


def mine(
    header_without_nonce: bytes, 
    difficulty_bits: int, 
    start_nonce: int = 0, 
    max_nonce: int = 2**32 - 1
):
    target = target_from_bits(difficulty_bits)
    for nonce in range(start_nonce, max_nonce + 1):
        nonce_bytes = struct.pack("<I", nonce)
        h = sha256d(header_without_nonce + nonce_bytes)
        if int.from_bytes(h, "big") < target:
            return nonce, h
    raise RuntimeError("No valid nonce found")


def validate(header_without_nonce: bytes, nonce: int, difficulty_bits: int) -> bool:
    target = target_from_bits(difficulty_bits)
    nonce_bytes = struct.pack("<I", nonce)
    h = sha256d(header_without_nonce + nonce_bytes)
    return int.from_bytes(h, "big") < target