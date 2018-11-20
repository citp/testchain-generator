from testchain.runner import Generator


class Taint(Generator):

    def run(self):
        self.create_simple_pattern()
        self.create_two_tx_for_mapping_test()

    def create_simple_pattern(self):
        start_1 = self.next_address()
        start_2 = self.next_address()
        txid, _ = self.fund_address(start_1, 7)
        self.log_value("taint-fund-tx-1", txid)
        txid, _ = self.fund_address(start_2, 8)
        self.log_value("taint-fund-tx-2", txid)
        self.generate_block(spendable_coinbase=False)

        addr_1 = self.next_address()
        addr_1.value = 1 - self.fee
        addr_2 = self.next_address()
        addr_2.value = 2 - self.fee
        addr_3 = self.next_address()
        addr_3.value = 4 - self.fee
        txid = self.create_transaction([start_1], [addr_1, addr_2, addr_3])
        self.log_value("taint-split-tx-1", txid)
        self.generate_block(spendable_coinbase=False)

        addr_4 = self.next_address()
        addr_4.value = 3 - 3 * self.fee
        txid = self.create_transaction([addr_1, addr_2], [addr_4])
        self.log_value("taint-merge-tx-1", txid)

        addr_5 = self.next_address()
        addr_5.value = 12 - 2 * self.fee
        txid = self.create_transaction([addr_3, start_2], [addr_5])
        self.log_value("taint-merge-tx-2", txid)

        self.generate_block(spendable_coinbase=False)

        addr_6 = self.next_address()
        addr_6.value = 15 - 6 * self.fee
        txid = self.create_transaction([addr_4, addr_5], [addr_6])
        self.log_value("taint-merge-tx-3", txid)
        self.generate_block(spendable_coinbase=False)
        self.log_value("taint-max-height", self.proxy.getblockcount())

    def create_two_tx_for_mapping_test(self):
        in_1 = self.next_address()
        txid, _ = self.fund_address(in_1, 4)
        self.log_value("taint-mapping-fund-tx-1", txid)
        in_2 = self.next_address()
        txid, _ = self.fund_address(in_2, 4)
        self.log_value("taint-mapping-fund-tx-2", txid)
        in_3 = self.next_address()
        txid, _ = self.fund_address(in_3, 2)
        self.log_value("taint-mapping-fund-tx-3", txid)

        self.generate_block(spendable_coinbase=False)

        out_1 = self.next_address()
        out_1.value = 3.3333
        out_2 = self.next_address()
        out_2.value = 3.3333
        out_3 = self.next_address()
        out_3.value = 3.3333

        txid = self.create_transaction([in_1, in_2, in_3], [out_1, out_2, out_3])
        self.log_value("taint-mapping-tx", txid)

        self.generate_block(spendable_coinbase=False)

        next_outs = []
        for i in range(6):
            next_out = self.next_address()
            next_out.value = 1.6666
            next_outs.append(next_out)

        txid = self.create_transaction([out_1, out_2, out_3], next_outs)
        self.log_value("taint-check-tx", txid)

        self.generate_block(spendable_coinbase=False)
