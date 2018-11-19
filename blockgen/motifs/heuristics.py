from blockgen.runner import Generator


class Heuristics(Generator):

    def run(self):
        self.create_simple_coinjoin()

    def create_simple_coinjoin(self):
        in_1 = self.next_address()
        self.fund_address(in_1, 1)
        in_2 = self.next_address()
        self.fund_address(in_2, 2)
        in_3 = self.next_address()
        self.fund_address(in_3, 3)

        self.generate_block(1)

        out_addresses = [self.next_address() for _ in range(6)]
        values = [0.5, 1.5 - self.fee, 0.5, 0.5 - self.fee, 2.5 - self.fee, 0.5]
        for address, value in zip(out_addresses, values):
            address.value = value

        txid = self.create_transaction([in_1, in_2, in_3], out_addresses)

        self.log_value("simple-coinjoin-tx", txid)
        self.log_value("simple-coinjoin-spends", [0, 2, 5])
        self.log_value("simple-coinjoin-change", [1, 3, 4])
