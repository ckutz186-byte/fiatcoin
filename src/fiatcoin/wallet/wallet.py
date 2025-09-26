import json
import os
from typing import List, Optional, TextIO
from fiatcoin.core.transaction import Output, Transaction
from fiatcoin.wallet.util import Address, KeyPair


class Wallet:
    def __init__(self, keypair: Optional[KeyPair]):
        self.keypair = keypair
        self.spent_transaction_outputs: List[Output] = []
        
    @classmethod
    def empty(cls) -> "Wallet":
        return cls(None)
    
    def generate_keypair(self) -> None:
        self.keypair = KeyPair()
    
    @property
    def addr(self) -> Address:
        return self.keypair.address # type: ignore
    
    def dump(self, f: TextIO) -> None:
        assert self.keypair        
        json.dump(
            {
                "keypair": {
                    "public_key": self.keypair.public_key.hex(),
                    "private_key": self.keypair.private_key.hex(),
                }
            }, f, indent=4
        )
        
    def add_spent_transaction_output(self, output: Output) -> None:
        self.spent_transaction_outputs.append(output)
    
    
def save_wallet(w: Wallet) -> None:
    with open("wallet.json.new", "w") as f:
        w.dump(f)
        
    os.replace("wallet.json.new", "wallet.json")


def sign_transaction(wallet: Wallet, transaction: Transaction) -> tuple[bytes, bool]:
    assert wallet.keypair
    signature = wallet.keypair.sign(transaction.serialize())
    verified = wallet.keypair.verify(transaction.serialize(), signature)
    return signature, verified