import hashlib
import json
import os
import time
from datetime import datetime


class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_data.encode()).hexdigest()

    def mine_block(self, difficulty=2):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self):
        return {
            "index"        : self.index,
            "timestamp"    : self.timestamp,
            "transactions" : self.transactions,
            "previous_hash": self.previous_hash,
            "nonce"        : self.nonce,
            "hash"         : self.hash
        }


class Blockchain:
    def __init__(self, difficulty=2):
        self.difficulty = difficulty
        self.chain      = []
        _HERE           = os.path.dirname(os.path.abspath(__file__))
        self.CHAIN_FILE = os.path.join(_HERE, "chain_data.json")
        self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(self.CHAIN_FILE):
            try:
                with open(self.CHAIN_FILE, "r") as f:
                    raw = json.load(f)
                for b in raw:
                    block               = Block.__new__(Block)
                    block.index         = b["index"]
                    block.timestamp     = b["timestamp"]
                    block.transactions  = b["transactions"]
                    block.previous_hash = b["previous_hash"]
                    block.nonce         = b["nonce"]
                    block.hash          = b["hash"]
                    self.chain.append(block)
                return
            except Exception:
                self.chain = []
        self._create_genesis_block()

    def _persist(self):
        os.makedirs(os.path.dirname(self.CHAIN_FILE), exist_ok=True)
        with open(self.CHAIN_FILE, "w") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

    def _create_genesis_block(self):
        genesis = Block(0, [{"message": "VaultSense Genesis Block"}], "0")
        genesis.mine_block(self.difficulty)
        self.chain.append(genesis)
        self._persist()

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction: dict):
        """Add a transaction record to the blockchain."""
        new_block = Block(
            index         = len(self.chain),
            transactions  = [transaction],
            previous_hash = self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self._persist()
        return new_block.hash

    def is_chain_valid(self):
        """Verify the entire blockchain is untampered."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                print(f"❌ Block #{i} has been tampered!")
                return False

            if current.previous_hash != previous.hash:
                print(f"❌ Block #{i} is disconnected from chain!")
                return False

        print("✅ Blockchain is valid and untampered.")
        return True

    def print_chain(self):
        """Display all blocks in the chain."""
        print("\n" + "="*60)
        print("        📦 VAULTSENSE BLOCKCHAIN LEDGER")
        print("="*60)
        for block in self.chain:
            print(f"\n🔷 Block #{block.index}")
            print(f"   Timestamp   : {block.timestamp}")
            print(f"   Transaction : {json.dumps(block.transactions, indent=14)}")
            print(f"   Hash        : {block.hash}")
            print(f"   Prev Hash   : {block.previous_hash}")
            print(f"   Nonce       : {block.nonce}")
            print("-"*60)


# ── Test the blockchain ──
if __name__ == "__main__":
    bc = Blockchain(difficulty=2)

    bc.add_transaction({
        "tx_id": "TXN-0001",
        "user": "USR-0042",
        "amount": 9999.00,
        "merchant": "Unknown Offshore",
        "risk_score": 94,
        "status": "FRAUD"
    })

    bc.add_transaction({
        "tx_id": "TXN-0002",
        "user": "USR-0071",
        "amount": 42.00,
        "merchant": "Starbucks",
        "risk_score": 5,
        "status": "SAFE"
    })

    bc.add_transaction({
        "tx_id": "TXN-0003",
        "user": "USR-0118",
        "amount": 4200.00,
        "merchant": "Crypto Exchange",
        "risk_score": 72,
        "status": "SUSPICIOUS"
    })

    bc.print_chain()
    bc.is_chain_valid()
