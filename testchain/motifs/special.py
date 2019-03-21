from bitcointx.core import CBlock, CMutableTransaction, CMutableTxIn, CMutableTxOut, COutPoint, COIN, lx, x
from bitcointx.core.script import CScript, OP_RETURN, OP_0, OP_2, OP_3, OP_CHECKMULTISIG

from testchain.runner import Generator
from testchain.util import Coin


class SpecialCases(Generator):
    """
    Creates transactions or blocks that differ from "normal" behavior.
    Useful to check for parser bugs and for cornercase behavior of algorithms.
    """

    def create_custom_block(self, reward):
        txid, _ = self.fund_address(self.next_address(), 10)
        tx2 = self.proxy.getrawtransaction(lx(txid))

        coinbase = CMutableTransaction()
        coinbase.vin.append(CMutableTxIn(COutPoint(), CScript([self.proxy.getblockcount() + 1])))
        coinbase.vout.append(CMutableTxOut(reward * COIN, self.next_address().address.to_scriptPubKey()))

        prev_block_hash = self.proxy.getblockhash(self.proxy.getblockcount())

        ts = self._next_timestamp()
        self.proxy.call("setmocktime", ts)

        for nonce in range(1000):
            block = CBlock(nBits=0x207fffff, vtx=[coinbase, tx2], hashPrevBlock=prev_block_hash, nTime=ts, nNonce=nonce)
            result = self.proxy.submitblock(block)
            if not result:
                self.log.debug("Chosen nonce: {}".format(nonce))
                break

    def coinbase_does_not_claim_fees(self):
        reward = self.current_block_reward()
        self.create_custom_block(reward)
        self.log_value("block-fee-unclaimed-height", self.proxy.getblockcount())

    def coinbase_does_not_claim_full_reward(self):
        reward = self.current_block_reward() - 10
        self.create_custom_block(reward)
        self.log_value("block-partial-reward-height", self.proxy.getblockcount())

    def non_max_nsequence_no(self):
        source = self.next_address()
        self.fund_address(source, 1)
        destination = self.next_address()
        destination.value = 1 - self.fee
        txid = self.create_transaction([source], [destination], n_sequence=0xfffffffe)
        self.log_value("nsequence-fffffffe-tx", txid)

    def op_return(self):
        source = self.next_address("p2pkh")
        self.fund_address(source, 2 * self.fee)

        tx_ins = [CMutableTxIn(COutPoint(source.txid, source.vout))]
        tx_outs = [CMutableTxOut(Coin(self.fee).satoshi(), CScript([OP_RETURN, x("4c6f726420566f6c64656d6f7274")]))]
        tx = CMutableTransaction(tx_ins, tx_outs)

        key = source.key
        script = source.address.to_scriptPubKey()

        sig = self._sign(script, tx, 0, Coin(source.value).satoshi(), key)
        tx_ins[0].scriptSig = CScript([sig, key.pub])

        txid = self._send_transaction(tx, [])
        self.log_value("op-return-tx", txid)

    def raw_multisig(self):
        source = self.next_address()
        self.fund_address(source, 0.1)

        # construct transaction manually
        tx_ins = [CMutableTxIn(COutPoint(source.txid, source.vout))]

        keys = [self.next_address().key for _ in range(3)]
        redeem_script = CScript([OP_2, keys[0].pub, keys[1].pub, keys[2].pub, OP_3, OP_CHECKMULTISIG])
        tx_outs = [
            CMutableTxOut(Coin(0.1 - self.fee).satoshi(), redeem_script)]

        tx = CMutableTransaction(tx_ins, tx_outs)

        # sign and submit
        key = source.key
        script = source.address.to_scriptPubKey()

        sig = self._sign(script, tx, 0, Coin(source.value).satoshi(), key)
        tx_ins[0].scriptSig = CScript([sig, key.pub])

        txid = self._send_transaction(tx, [])
        self.log_value("raw-multisig-tx", txid)

        # Redeem Transaction
        tx_ins = [CMutableTxIn(COutPoint(lx(txid), 0))]
        destination = self.next_address()
        tx_outs = [CMutableTxOut(Coin(0.1 - 2 * self.fee).satoshi(), destination.address.to_scriptPubKey())]
        tx = CMutableTransaction(tx_ins, tx_outs)

        # Sign with 2 out of three keys
        sig1 = self._sign(redeem_script, tx, 0, Coin(0.1 - self.fee).satoshi(), keys[0])
        sig3 = self._sign(redeem_script, tx, 0, Coin(0.1 - self.fee).satoshi(), keys[2])

        tx_ins[0].scriptSig = CScript([OP_0, sig1, sig3])

        txid = self._send_transaction(tx, [])
        self.log_value("raw-multisig-redeem-tx", txid)
        self.generate_block()

    def p2sh_multisig(self):
        source = self.next_address()
        self.fund_address(source, 0.1)

        # construct transaction manually
        tx_ins = [CMutableTxIn(COutPoint(source.txid, source.vout))]

        keys = [self.next_address().key for _ in range(3)]
        redeem_script = CScript([OP_2, keys[0].pub, keys[1].pub, keys[2].pub, OP_3, OP_CHECKMULTISIG])
        tx_outs = [
            CMutableTxOut(Coin(0.1 - self.fee).satoshi(), redeem_script.to_p2sh_scriptPubKey())]

        tx = CMutableTransaction(tx_ins, tx_outs)

        # sign and submit
        key = source.key
        script = source.address.to_scriptPubKey()
        sig = self._sign(script, tx, 0, Coin(source.value).satoshi(), key)
        tx_ins[0].scriptSig = CScript([sig, key.pub])

        txid = self._send_transaction(tx, [])
        self.log_value("p2sh-multisig-tx", txid)

        # Redeem Transaction
        tx_ins = [CMutableTxIn(COutPoint(lx(txid), 0))]
        destination = self.next_address()
        tx_outs = [CMutableTxOut(Coin(0.1 - 2 * self.fee).satoshi(), destination.address.to_scriptPubKey())]
        tx = CMutableTransaction(tx_ins, tx_outs)

        # Sign with 2 out of three keys
        sig1 = self._sign(redeem_script, tx, 0, Coin(0.1 - self.fee).satoshi(), keys[0], "p2sh")
        sig3 = self._sign(redeem_script, tx, 0, Coin(0.1 - self.fee).satoshi(), keys[2], "p2sh")

        tx_ins[0].scriptSig = CScript([OP_0, sig1, sig3, redeem_script])

        txid = self._send_transaction(tx, [])
        self.log_value("p2sh-multisig-redeem-tx", txid)
        self.generate_block()

    def run(self):
        self.coinbase_does_not_claim_fees()
        self.coinbase_does_not_claim_full_reward()
        self.non_max_nsequence_no()
        self.op_return()
        self.raw_multisig()
        self.p2sh_multisig()
