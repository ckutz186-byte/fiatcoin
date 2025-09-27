from fiatcoin.wallet import Wallet, sign_transaction
from fiatcoin.transaction import Input, OutputReference, Transaction, Output, make_transaction


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


class UnspentTransactionOutSet:
    def __init__(self):
        self.unspent_transaction_outs: dict[tuple[bytes, int], Output] = {}

    def add_transaction(self, transaction: Transaction) -> None:
        tx_hash = transaction.hash()
        for index, output in enumerate(transaction.outputs):
            self.unspent_transaction_outs[(tx_hash, index)] = output

    def spend_output(self, reference: OutputReference) -> None:
        key = (reference.tx_hash, reference.index)
        if key not in self.unspent_transaction_outs:
            raise ValueError("Attempt to spend nonexistent UTXO")
        del self.unspent_transaction_outs[key]

    def is_unspent_transaction_out(self, reference: OutputReference) -> bool:
        return (reference.tx_hash, reference.index) in self.unspent_transaction_outs

    def get_unspent_transaction_outs(self, reference: OutputReference) -> Output:
        return self.unspent_transaction_outs[(reference.tx_hash, reference.index)]

    def all_unspent_transaction_outs(self) -> dict[tuple[bytes, int], Output]:
        return self.unspent_transaction_outs.copy()


class CoinState:
    def __init__(self):
        self.utxos = UnspentTransactionOutSet()

    def utxo_apply_transaction(self, transaction: Transaction) -> None:
        for inp in transaction.inputs:
            self.utxos.spend_output(inp.output_reference)

        self.utxos.add_transaction(transaction)

    def has_utxo(self, reference: OutputReference) -> bool:
        return self.utxos.is_unspent_transaction_out(reference)

    def snapshot(self) -> dict[str, int]:
        balances = {}
        for (_, _), output in self.utxos.all_unspent_transaction_outs().items():
            pk = output.public_key.hex()
            balances[pk] = balances.get(pk, 0) + output.value
        return balances