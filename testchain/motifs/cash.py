from testchain.generator import Generator


class BitcoinCash(Generator):
    def run(self):
        self.create_block_with_dependencies(20)

    def create_block_with_dependencies(self, length: int):
        """
        Create a chain of {length} 1-input/1-output transactions, each only losing FEE in value
        """
        self.fund_address(self.next_address(), 10)  # 10 BTC

        for i in range(length):
            source = self.current_address()
            destination = self.next_address()
            destination.value = source.value - self.fee

            txid = self.create_transaction([source], [destination])
            self.log_value("tx-chain-{}-tx-{}".format(length, i), txid)
        block_hash = self.generate_block()
        self.log_value("bitcoin-cash-test-block", block_hash[0])
