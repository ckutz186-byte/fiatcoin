from typing import Optional
import immutables
from fiatcoin.core.block import Block
from fiatcoin.core.transaction import Input, OutputReference, Transaction, Output, make_transaction
from fiatcoin.wallet.wallet import Wallet, sign_transaction


class VerificationFailedError(Exception):
    pass


def create_coinbase_transaction(wallet: Wallet, value: int = 100) -> Transaction:
    assert wallet.keypair
    
    coinbase_output = Output(
        value=value,
        public_key=wallet.keypair.public_key
    )
    
    coinbase = Transaction(inputs=[], outputs=[coinbase_output])
    coinbase.cached_hash = coinbase.hash()
    
    return coinbase


def create_spend_transaction(
    wallet: Wallet, 
    previous_transaction: Transaction, 
    output_index: int, 
    value: int
) -> Transaction:
    assert wallet.keypair
    
    previous_hash = previous_transaction.hash()
    utxo_reference = OutputReference(previous_hash, output_index)
    
    spend_output = Output(value=value, public_key=wallet.keypair.public_key)
    temp_tx = Transaction(inputs=[], outputs=[spend_output])
    signature, valid = sign_transaction(wallet, temp_tx)
    
    if not valid:
        raise VerificationFailedError("Signature verification failed in create_spend_transaction")
    
    spend_input = Input(utxo_reference, signature)
    
    spend_transaction = make_transaction(
        inputs=[spend_input],
        outputs=[spend_output]
    )
    
    wallet.add_spent_transaction_output(spend_output)
    
    return spend_transaction


class CoinState:
    def __init__(
        self,
        block_by_hash: immutables.Map[bytes, Block],
        unspent_transaction_outs_by_hash: immutables.Map[
            bytes, immutables.Map[OutputReference, Output]
        ],
        heads: immutables.Map[bytes, Block],
        current_chain_hash: Optional[bytes]
    ):
        self.block_by_hash = block_by_hash
        self.unspent_transaction_outs_by_hash = unspent_transaction_outs_by_hash
        self.heads = heads
        self.current_chain_hash = current_chain_hash
        