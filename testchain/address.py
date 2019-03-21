import hashlib

from bitcointx.core import Hash160
from bitcointx.core.script import CScript, OP_CHECKSIG, OP_0
from bitcointx.wallet import CBitcoinSecret, P2PKHBitcoinAddress, P2SHBitcoinAddress, P2WSHBitcoinAddress, \
    P2WPKHBitcoinAddress

COINBASE_ADDRESS = "mjTkW3DjgyZck4KbiRusZsqTgaYTxdSz6z"
COINBASE_KEY = "cVpF924EspNh8KjYsfhgY96mmxvT6DgdWiTYMtMjuM74hJaU5psW"
UNSPENDABLE_ADDRESS = "mt7L7Qh8R5xwGjpLPJMv7tbjbQPVPXjtKJ"


class UnsupportedAddressTypeError(Exception):
    """We do not support the address type"""


class Address(object):
    """
    Stores information related to addresses such as keys or the most recent output pointer.
    """
    def __init__(self, key: CBitcoinSecret, address_type: str = "p2pkh"):
        self.key_index = None
        self.type = address_type
        self.key = key
        if address_type == "p2pkh":
            self.address = P2PKHBitcoinAddress.from_pubkey(self.key.pub)
        elif address_type == "p2sh":
            self.address = P2SHBitcoinAddress.from_redeemScript(CScript([self.key.pub, OP_CHECKSIG]))
        elif address_type == "p2wpkh":
            key_hash = Hash160(self.key.pub)
            script_pub_key = CScript([OP_0, key_hash])
            self.address = P2WPKHBitcoinAddress.from_scriptPubKey(script_pub_key)
        elif address_type == "p2wsh":
            self.witness_program = CScript([self.key.pub, OP_CHECKSIG])
            script_hash = hashlib.sha256(self.witness_program).digest()
            script_pub_key = CScript([OP_0, script_hash])
            self.address = P2WSHBitcoinAddress.from_scriptPubKey(script_pub_key)
        else:
            raise UnsupportedAddressTypeError()
        self.value = 0
        self.txid = None
        self.vout = None

    @staticmethod
    def compute_key(key_index: int) -> CBitcoinSecret:
        """
        Deterministically generate a key from an index.
        """
        h = hashlib.sha256(bytes(key_index)).digest()
        return CBitcoinSecret.from_secret_bytes(h)

    @classmethod
    def from_key_index(cls, key_index, address_type: str = "p2pkh"):
        """
        Creates an address object based on a key index.
        """
        c = cls(cls.compute_key(key_index), address_type)
        c.key_index = key_index
        return c
