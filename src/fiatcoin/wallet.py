import json
import os
from typing import List, Optional, TextIO

from fiatcoin.coinstate import VerificationFailedError
from fiatcoin.transaction import Output, Transaction, Input, make_transaction, OutputReference
from fiatcoin.util import Address, KeyPair


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

    
def save_wallet(w: Wallet) -> None:
    with open("wallet.json.new", "w") as f:
        w.dump(f)
        
    os.replace("wallet.json.new", "wallet.json")


def sign_transaction(wallet: Wallet, transaction: Transaction) -> tuple[bytes, bool]:
    assert wallet.keypair
    signature = wallet.keypair.sign(transaction.serialize())
    verified = wallet.keypair.verify(transaction.serialize(), signature)
    return signature, verified


def create_spend_transaction(
    wallet: Wallet,
    previous_transaction: Transaction,
    output_index: int,
    value: int,
    recipient_public_key: bytes
) -> Transaction:
    assert wallet.keypair, "Wallet must have keypair generated to create a spend transaction"

    prev_hash = previous_transaction.hash()
    utxo_reference = OutputReference(prev_hash, output_index)

    input_value = previous_transaction.outputs[output_index].value
    if value > input_value:
        raise ValueError("Spend value exceeds available balance")

    recipient_output = Output(value=value, public_key=recipient_public_key)

    change_value = input_value - value
    outputs = [recipient_output]
    if change_value > 0:
        change_output = Output(value=change_value, public_key=wallet.keypair.public_key)
        outputs.append(change_output)

    unsigned_transaction = Transaction(inputs=[], outputs=outputs)
    signature, valid = sign_transaction(wallet, unsigned_transaction)
    if not valid:
        raise VerificationFailedError("Signature verification failed")

    spend_input = Input(utxo_reference, signature)

    spend_transaction = make_transaction(inputs=[spend_input], outputs=outputs)

    return spend_transaction