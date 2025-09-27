import struct
from typing import BinaryIO, List

from fiatcoin.hash import sha256d
from fiatcoin.serialize import Serializable, safe_read, stream_deserialize_list, stream_deserialize_vlq, stream_serialize_list, stream_serialize_vlq # type: ignore
from fiatcoin.transaction import Transaction


class BlockSummary(Serializable):
    def __init__(
        self,
        time: int,
        height: int,
        previous_hash: bytes,
        nonce: int,
        block_hash: bytes,
        merkle_root_hash: bytes,
    ) -> None:
        self.time = time
        self.height = height
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.block_hash = block_hash
        self.merkle_root_hash = merkle_root_hash
        
    def hash(self) -> bytes:
        return sha256d(self.serialize())

    def stream_serialize(self, f: BinaryIO) -> None:
        f.write(struct.pack(b">I", self.time))
        stream_serialize_vlq(f, self.height)
        f.write(self.previous_hash)
        f.write(struct.pack(b">I", self.nonce))
        f.write(self.block_hash)
        f.write(self.merkle_root_hash)
        
    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "BlockSummary":
        (time,) = struct.unpack(b">I", safe_read(f, 4))
        height = stream_deserialize_vlq(f)
        previous_hash = safe_read(f, 32)
        (nonce,) = struct.unpack(b">I", safe_read(f, 4))
        block_hash = safe_read(f, 32)
        merkle_root = safe_read(f, 32)
        
        return cls(time, height, previous_hash, nonce, block_hash, merkle_root)
        

class Block(Serializable):
    def __init__(self, summary: BlockSummary, transactions: List[Transaction], hash: bytes) -> None:
        self.summary = summary
        self.transactions = transactions
    
    def stream_serialize(self, f: BinaryIO) -> None:
        self.summary.stream_serialize(f)
        stream_serialize_list(f, self.transactions)
        
    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "Serializable":
        start_position = f.tell()
        summary = BlockSummary.stream_deserialize(f)
        end_position = f.tell()
        f.seek(start_position)
        hash = sha256d(f.read(end_position - start_position))
        transactions = stream_deserialize_list(f, Transaction)
        return cls(summary, transactions, hash) 

    def hash(self) -> bytes:
        return self.summary.hash()