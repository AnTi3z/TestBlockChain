from __future__ import annotations
import json
import time
from hashlib import sha256

from typing import List


class Transaction:
    _index = 1

    def __init__(self):
        self.index = Transaction._index
        Transaction._index += 1

    def __repr__(self):
        return f"<Transaction: {self.__dict__}>"


class TransactionJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Transaction):
            return obj.__dict__
        else:
            return super().default(obj)


class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Transaction], prev_hash: str):
        self.index: int = index
        self.timestamp: float = timestamp
        self.transactions: List[Transaction] = transactions
        self.prev_hash: str = prev_hash
        self.nonce: int = 0

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True, cls=TransactionJSONEncoder)
        return sha256(block_string.encode()).hexdigest()

    def is_valid_chain(self, prev_block: Block):
        return self.index > prev_block.index and \
               prev_block.timestamp <= self.timestamp <= time.time() and \
               self.prev_hash == prev_block.compute_hash()

    def __repr__(self):
        return f"<Block: {self.__dict__}>"


class BlockChain:
    difficulty = 4

    def __init__(self):
        self.unconfirmed_transactions: List[Transaction] = []
        self.chain: List[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis_block = Block(1, time.time(), [], "0")
        self.chain.append(genesis_block)

    @property
    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block: Block):
        # check proof of work difficulty
        if not block.compute_hash().startswith('0' * self.difficulty):
            return False

        # check block chain validity
        if not block.is_valid_chain(self.get_last_block):
            return False

        # check if transactions is still unconfirmed
        for transaction in block.transactions:
            if transaction not in self.unconfirmed_transactions:
                return False

        # mutex needed
        self.chain.append(block)
        for transaction in block.transactions:
            self.unconfirmed_transactions.remove(transaction)
        return True

    def add_transaction(self, transaction: Transaction):
        if transaction not in self.unconfirmed_transactions:
            self.unconfirmed_transactions.append(transaction)

    def __repr__(self):
        return f"<BlockChain: {self.__dict__}>"


def mine(chain: BlockChain):
    if not chain.unconfirmed_transactions:
        return None

    # 5 transactions in one block
    transactions = chain.unconfirmed_transactions[:5]

    last_block = chain.get_last_block
    new_block = Block(last_block.index + 1,
                      time.time(),
                      transactions,
                      last_block.compute_hash()
                      )

    while not new_block.compute_hash().startswith('0' * chain.difficulty):
        new_block.nonce += 1

    return new_block


if __name__ == "__main__":
    test_chain = BlockChain()
    test_chain.add_transaction(Transaction())
    test_chain.add_transaction(Transaction())
    print(test_chain)
    new_block = mine(test_chain)
    test_chain.add_block(new_block)
    print(test_chain)
