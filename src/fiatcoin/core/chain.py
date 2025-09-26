from typing import List, Optional
from fiatcoin.core.hash import sha256d
from fiatcoin.database.block_store import BlockStore
from fiatcoin.core.block import Block
from fiatcoin.util.genesis import genesis_block_data, just_believe_in_me


class MemoryFlushError(Exception):
    pass


class Chain:
    def __init__(
        self,
        chain_id: bytes,
        chain_uid: str,
        genesis_block: Optional[Block],
        target_block_time: int,
        disk: BlockStore,
        current_height: int
    ):
        self.chain_id = chain_id
        self.chain_uid = chain_uid
        self.genesis_block = genesis_block
        self.target_block_time = target_block_time
        self.disk = disk
        self.current_height = current_height
        
        self.blocks_memory: List[Block] = []
        
        if len(self.blocks_memory) == 0 and self.genesis_block == None:        
            self._insert_block_to_memory(
                Block.deserialize(genesis_block_data)
            )
            self.flush_chain_memory_to_disk()
        
    def _insert_block_to_memory(self, block: Block) -> None:
        self.blocks_memory.append(block)

    def insert_chain_to_memory(self, blocks: List[Block]) -> None:
        for block in blocks:
            self._insert_block_to_memory(block)
    
    def flush_chain_memory_to_disk(self) -> None:
        if len(self.blocks_memory) == 0:
            raise MemoryFlushError("Could not flush blocks memory to disk without genesis.")
        
        for block in self.blocks_memory:
            self.disk.put(block.hash().hex(), block.serialize())
        
        self.blocks_memory.clear()
        
    def generate_chain_id(self) -> bytes:
        return sha256d(just_believe_in_me)
    
    def get_current_height(self) -> int:
        return len(self.disk.items())
        
    def print_chain_state(self) -> None:
        print("\n")
        print(self)
        print("\n")
            
    def __repr__(self) -> str:
        return "Chain %s on '%s' with %s blocks" % (self.chain_id.hex(), self.chain_uid, len(self.disk.items()))  
            
        