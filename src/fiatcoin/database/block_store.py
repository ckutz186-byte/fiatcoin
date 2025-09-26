from fiatcoin.core.block import Block
from fiatcoin.database.db import Database


class BlockStore(Database):
    def __init__(self, path: str) -> None:
        super().__init__(path=path)
        self.path = path
        
    def write_block(self, hash: bytes, block: Block) -> None:
        self.put(hash.hex(), block.serialize())
        
    def read_block(self, hash: bytes) -> Block | None:
        block_bytes = self.get(hash.hex())
        if not block_bytes:
            raise ValueError("Not found")
        return Block.deserialize(block_bytes)  
    
    def remove_block(self, hash: bytes) -> None:
        self.delete(hash.hex())  
        
    def wipe(self) -> None:
        self.clear()