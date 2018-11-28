from testchain.runner import Generator


class Addresses(Generator):

    def create_address(self, addr_type):
        """
        Sends money to a certain address type i times, for i in range(3)
        :param addr_type: address type, currently "p2pkh", "p2sh", "p2wpkh" and "p2wsh"
        :return:
        """
        for i in range(3):
            address = self.next_address(address_type=addr_type)
            txid, _ = self.fund_address(address, 1)

            self._log_create_addresses(addr_type, i, address, txid)

            for j in range(1, i + 1):
                if j > 1:
                    self.fund_address(address, j)
                dest = self.next_address()
                dest.value = j - self.fee
                self.create_transaction([address], [dest])
            self.generate_block()

    def _log_create_addresses(self, addr_type, idx, address, txid):
        self.log_value("address-{}-spend-{}".format(addr_type, idx), str(address.address))
        self.log_value("address-{}-spend-{}-value".format(addr_type, idx), 1)
        self.log_value("address-{}-spend-{}-tx".format(addr_type, idx), txid)
        self.log_value("address-{}-spend-{}-height".format(addr_type, idx), self.proxy.getblockcount() + 1)

    def run(self):
        self.create_address("p2pkh")
        self.create_address("p2sh")
        if self.segwit:
            self.create_address("p2wpkh")
            self.create_address("p2wsh")
