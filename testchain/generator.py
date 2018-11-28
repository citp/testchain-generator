from typing import List, Callable, Dict

from logging import Logger
import bitcoin.rpc
from bitcoin.core import CMutableTxIn, CMutableTxOut, CMutableTransaction, COutPoint, CTxInWitness, CTxWitness, b2lx
from bitcoin.core.script import CScript, CScriptWitness, OP_CHECKSIG, SignatureHash, SIGHASH_ALL, SIGVERSION_WITNESS_V0
from bitcoin.wallet import CBitcoinSecret

from testchain.address import Address, UnsupportedAddressTypeError, COINBASE_KEY, COINBASE_ADDRESS, UNSPENDABLE_ADDRESS
from testchain.util import Coin


class NoAddressError(Exception):
    """Raised when requesting an address, but none has been created yet."""


class Generator(object):
    addresses: List[Address]

    def run(self):
        raise NotImplementedError

    def __init__(self, proxy: bitcoin.rpc.Proxy, chain, log: Logger, stored_hashes: Dict, offset: int,
                 next_timestamp: Callable[[], int]):
        self.proxy = proxy
        self.chain = chain
        self.log = log
        self.addresses = []
        self.offset = offset
        self.address_cursor = -1
        self.stored_hashes = stored_hashes
        self.fee = 0.0001
        self._next_timestamp = next_timestamp
        self.segwit = self.chain == "btc"

    def log_value(self, k, v):
        self.stored_hashes[k] = v

    def current_block_reward(self):
        """
        Returns the current reward the miner gets for each block.
        In regtest mode, the reward is halved after the first 150 blocks.
        """
        return 50 if self.proxy.getblockcount() < 150 else 25

    def _advance_time(self):
        """
        Advance time by increasing the mocktime of the Bitcoin node
        """
        timestamp = self._next_timestamp()
        self.proxy.call("setmocktime", timestamp)
        self.log.debug("Set time to {}".format(timestamp))

    def generate_block(self, n: int = 1, spendable_coinbase=True):
        self._advance_time()

        if spendable_coinbase:
            address = COINBASE_ADDRESS
        else:
            address = UNSPENDABLE_ADDRESS

        block_hashes = self.proxy.call("generatetoaddress", n, address)
        if len(block_hashes) == 1:
            self.log.debug("Mined block: {}".format([x for x in block_hashes][0]))
        else:
            self.log.debug("Mined blocks: {}".format([x for x in block_hashes]))
        return block_hashes

    def next_address(self, address_type="p2pkh") -> Address:
        self.address_cursor += 1
        self.addresses.append(Address.from_key_index(self.address_cursor + self.offset, address_type))
        return self.addresses[self.address_cursor]

    def current_address(self) -> Address:
        if self.address_cursor < 0:
            raise NoAddressError("No addresses exist yet. Create one using `next_address()`")
        return self.addresses[self.address_cursor]

    def fund_address(self, address: Address, value: float):
        """
        Sends money to an address using a UTXO of the mining address
        :param address: the address that will receive the coins
        :param value: the value that the address will receive
        :return: the transaction id and
        """
        key = CBitcoinSecret(COINBASE_KEY)
        coinbase_addr = Address(key)

        unspents = self.proxy.listunspent(minconf=100, addrs=[coinbase_addr.address])
        unspents.sort(key=lambda x: x['confirmations'], reverse=True)
        oldest_utxo = next(x for x in unspents if Coin.from_satoshi(x['amount']).bitcoin() >= value + self.fee)

        coinbase_addr.txid = oldest_utxo['outpoint'].hash
        coinbase_addr.vout = oldest_utxo['outpoint'].n

        coinbase_addr.value = Coin.from_satoshi(oldest_utxo['amount']).bitcoin()
        address.value = value

        # change address is always the second output
        txid = self.create_transaction([coinbase_addr], [address, coinbase_addr],
                                       values=[value, coinbase_addr.value - self.fee - value])

        self.log.debug("Address: {}".format(address.address))
        self.log.debug("Tx: {}".format(txid))

        return txid, address.vout

    def create_transaction(self, sources: List[Address], recipients: List[Address], values=[], n_locktime=0,
                           n_sequence=0xffffffff):
        """
        Creates a transaction using `sources` as inputs and `recipients` as outputs.
        :param sources: list of addresses to spend from
        :param recipients: list of addresses to send to
        :param n_locktime: locktime value of the transaction
        :param n_sequence: sequence no for inputs
        :return: the TXID of the transaction as returned by the proxy
        """
        tx = self._create_transaction(sources, recipients, values, n_locktime=n_locktime, n_sequence=n_sequence)
        return self._send_transaction(tx, recipients)

    def _create_transaction(self, sources: List[Address], recipients: List[Address], values, n_locktime, n_sequence):
        if not values:
            values = [recipient.value for recipient in recipients]
        tx_ins = [CMutableTxIn(COutPoint(source.txid, source.vout), nSequence=n_sequence) for source in sources]
        tx_outs = []

        cnt = 0
        for recipient, value in zip(recipients, values):
            if recipient.value == 0:
                self.log.warning("Creating output with 0 BTC")
            recipient.vout = cnt

            tx_outs.append(CMutableTxOut(Coin(value).satoshi(), recipient.address.to_scriptPubKey()))
            cnt += 1

        tx = CMutableTransaction(tx_ins, tx_outs, nLockTime=n_locktime)

        in_idx = 0
        witnesses = []
        for txin, source in zip(tx_ins, sources):
            key = source.key

            if source.type == 'p2pkh':
                script = source.address.to_redeemScript()
            elif source.type == 'p2sh':
                script = CScript([key.pub, OP_CHECKSIG])
            elif source.type == 'p2wpkh':
                script = source.address.to_redeemScript()
            elif source.type == 'p2wsh':
                script = source.witness_program
            else:
                raise UnsupportedAddressTypeError()

            # Create signature
            amount = Coin(source.value).satoshi()
            sig = self._sign(script, tx, in_idx, amount, key, source.type)

            # Add signature to input or witness
            if source.type == 'p2pkh':
                txin.scriptSig = CScript([sig, key.pub])
                witnesses.append(CTxInWitness())
            elif source.type == 'p2sh':
                txin.scriptSig = CScript([sig, script])
                witnesses.append(CTxInWitness())
            elif source.type == 'p2wpkh':
                txin.scriptSig = CScript()
                witnesses.append(CTxInWitness(CScriptWitness([sig, key.pub])))
            elif source.type == 'p2wsh':
                txin.scriptSig = CScript()
                witnesses.append(CTxInWitness(CScriptWitness([sig, script])))
            in_idx += 1

        tx.wit = CTxWitness(witnesses)
        return tx

    def _send_transaction(self, tx: CMutableTransaction, recipients: List[Address]):
        txid = self.proxy.sendrawtransaction(tx)
        for rec in recipients:
            rec.txid = txid
        return b2lx(txid)

    def _sign(self, script, tx, in_idx, amount, key, script_type="p2pkh"):
        if self.chain == "bch":
            sighash = SignatureHash(script, tx, in_idx, SIGHASH_ALL | 0x40, amount=amount,
                                    sigversion=SIGVERSION_WITNESS_V0)
            sig = key.sign(sighash) + bytes([SIGHASH_ALL | 0x40])
        else:
            if script_type == 'p2wpkh' or script_type == 'p2wsh':
                sighash = SignatureHash(script, tx, in_idx, SIGHASH_ALL, amount=amount,
                                        sigversion=SIGVERSION_WITNESS_V0)
            else:
                sighash = SignatureHash(script, tx, in_idx, SIGHASH_ALL)
            sig = key.sign(sighash) + bytes([SIGHASH_ALL])
        return sig
