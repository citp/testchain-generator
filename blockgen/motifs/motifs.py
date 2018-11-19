from blockgen.runner import Generator
from blockgen.address import Address
import random


class Motifs(Generator):

    def run(self):
        self.create_m_input_n_output_tx(2, 2)
        self.create_m_input_n_output_tx(2, 3)
        self.create_tx_chain()
        self.create_peeling_chain()
        self.create_fan()
        self.create_merge()

    def init_pattern(self, name: str, value: float):
        """
        Creates a transaction output to a fresh address
        :param name: name of the pattern
        :param value: value of the output being created
        """
        txid, _ = self.fund_address(self.next_address(), value)

        self.log_value("funding-tx-{}".format(name), txid)

        str_addr = str(self.current_address().address)
        self.log_value("addr-{}".format(name), str_addr)

        self.generate_block()

    def create_m_input_n_output_tx(self, m: int, n: int):
        """
        Creates a transaction with m inputs and n outputs.
        :param m: number of inputs
        :param n: number of outputs
        """
        random.seed(20180917)
        self.init_pattern("{}-in-{}-out".format(m, n), 42)

        # split
        sources = [self.current_address()]
        total_value = self.current_address().value - self.fee
        destinations = []
        for _ in range(m):
            d = self.next_address()
            d.value = round(total_value / m, 8)
            destinations.append(d)

        self.create_transaction(sources, destinations)
        self.generate_block()

        total_value = round(total_value / m, 8) * m - self.fee
        new_destinations = []
        for _ in range(n):
            d = self.next_address()
            d.value = round(total_value / n, 8)
            new_destinations.append(d)

        self.create_transaction(destinations, new_destinations)
        self.generate_block()

    def create_tx_chain(self, length: int = 10):
        """
        Create a chain of {length} 1-input/1-output transactions, each only losing FEE in value
        """
        random.seed(20180917)
        self.fund_address(self.next_address(), 10)  # 10 BTC

        for i in range(length):
            source = self.current_address()
            destination = self.next_address()
            destination.value = source.value - self.fee

            txid = self.create_transaction([source], [destination])
            self.log_value("tx-chain-{}-tx-{}".format(length, i), txid)
            self.generate_block()

    def create_peeling_chain(self):
        """
        Create a peeling chain of length 10.
        """
        random.seed(20180913)
        self.init_pattern("peeling-chain", 42)
        dead_ends = [Address.from_key_index(x) for x in range(20181013, 20181023)]

        for i in range(10):
            sources = [self.current_address()]
            total_value = self.current_address().value - self.fee

            self.next_address().value = total_value - round(i / 10, 8)
            dead_ends[i].value = round(i / 10, 8)

            change_position = random.randint(0, 1)
            if change_position:
                destinations = [dead_ends[i], self.current_address()]
            else:
                destinations = [self.current_address(), dead_ends[i]]

            txid = self.create_transaction(sources, destinations)
            self.log_value("peeling-chain-{}-tx".format(i), txid)
            self.log_value("peeling-chain-{}-position".format(i), change_position)

            if random.random() > 0.5:
                self.generate_block()

        self.generate_block()

    def create_fan(self, n: int = 8):
        random.seed(20180914)
        self.init_pattern("fan-{}".format(n), 42)

        start_address = self.current_address()
        total_value = start_address.value - self.fee
        recipients = [self.next_address() for _ in range(n)]
        for x in recipients:
            x.value = round(total_value / n, 8)

        txid = self.create_transaction([start_address], recipients)
        self.log_value("fan-{}-tx".format(n), txid)

        self.generate_block()

        final_destination = self.next_address()
        final_destination.value = round(total_value / n, 8) * n - self.fee

        txid = self.create_transaction(recipients, [final_destination])
        self.log_value("fan-{}-tx-collect".format(n), txid)

        self.generate_block()

    def create_merge(self):
        random.seed(20181001)
        self.init_pattern("merge-0", value=1)
        addr1 = self.current_address()
        self.init_pattern("merge-1", value=2)
        addr2 = self.current_address()
        self.init_pattern("merge-2", value=3)
        addr3 = self.current_address()

        addr1_1 = self.next_address()
        addr1_1.value = 1 - self.fee
        self.create_transaction([addr1], [addr1_1])

        addr2_1 = self.next_address()
        addr2_1.value = 2 - self.fee
        self.create_transaction([addr2], [addr2_1])

        addr3_1 = self.next_address()
        addr3_1.value = 3 - self.fee
        self.create_transaction([addr3], [addr3_1])

        self.generate_block()

        addr_dest = self.next_address()
        addr_dest.value = 6 - 4 * self.fee

        txid = self.create_transaction([addr1_1, addr2_1, addr3_1], [addr_dest])
        self.log_value("merge-final-tx", txid)
        self.log_value("merge-addr-1", str(addr1_1.address))
        self.log_value("merge-addr-2", str(addr2_1.address))
        self.log_value("merge-addr-3", str(addr3_1.address))
        self.generate_block()
