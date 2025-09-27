import struct
from fiatcoin.hash import sha256d


def target_from_bits(difficulty_bits: int) -> int:
    if not 0 <= difficulty_bits <= 256:
        raise ValueError("difficulty_bits must be between 0 and 256 inclusive")
    return 1 << (256 - difficulty_bits)


def mine(
    header_without_nonce: bytes, 
    difficulty_bits: int, 
    start_nonce: int = 0, 
    max_nonce: int = 2**32 - 1
):
    target = target_from_bits(difficulty_bits)
    if not (0 <= start_nonce <= 0xFFFFFFFF):
       raise ValueError("start_nonce must be between 0 and 2**32 - 1")
    if not (0 <= max_nonce <= 0xFFFFFFFF):
        raise ValueError("max_nonce must be between 0 and 2**32 - 1")
    if start_nonce > max_nonce:
        raise ValueError("start_nonce must not exceed max_nonce")
    for nonce in range(start_nonce, max_nonce + 1):
        nonce_bytes = struct.pack("<I", nonce)
        h = sha256d(header_without_nonce + nonce_bytes)
        if int.from_bytes(h, "big") < target:
            return nonce, h
    raise RuntimeError("No valid nonce found")


def validate(header_without_nonce: bytes, nonce: int, difficulty_bits: int) -> bool:
    target = target_from_bits(difficulty_bits)
    if not (0 <= nonce <= 0xFFFFFFFF):
        raise ValueError("nonce must be between 0 and 2**32 - 1")
    nonce_bytes = struct.pack("<I", nonce)
    h = sha256d(header_without_nonce + nonce_bytes)
    return int.from_bytes(h, "big") < target