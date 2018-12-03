import random
from testchain.runner import Generator


class Change(Generator):

    def create_power_of_ten_change(self):
        random.seed(20180919)
        full_value = 2.11111111
        spend_value = 1.23456789
        for i in range(6):
            start_address = self.next_address()
            self.fund_address(start_address, full_value)
            self.generate_block()

            spend = self.next_address()
            spend.value = float(str(spend_value)[:2 + i])
            change = self.next_address()
            change.value = full_value - spend.value - self.fee

            # randomize change output position
            change_position = random.randint(0, 1)
            if change_position:
                destinations = [spend, change]
            else:
                destinations = [change, spend]
            self.log_value("change-ten-{}-position".format(i), change_position)

            txid = self.create_transaction([start_address], destinations)
            self.log_value("change-ten-{}-tx".format(i), txid)
            self.generate_block()

    def create_optimal_change(self):
        for pos in range(2):
            in1 = self.next_address()
            in2 = self.next_address()
            self.fund_address(in1, 1)
            self.fund_address(in2, 2)

            spend = self.next_address()
            spend.value = 2.9

            change = self.next_address()
            change.value = 0.1 - self.fee

            if pos:
                dest = [spend, change]
            else:
                dest = [change, spend]

            txid = self.create_transaction([in1, in2], dest)
            self.log_value("change-optimal-{}-tx".format(pos), txid)
            self.log_value("change-optimal-{}-position".format(pos), pos)
            self.generate_block()

    def create_address_type_change(self):
        for pos in range(3):
            in1 = self.next_address("p2pkh")
            self.fund_address(in1, 3 + self.fee)
            change = self.next_address("p2pkh")
            change.value = 1
            spend1 = self.next_address("p2sh")
            spend1.value = 1
            spend2 = self.next_address("p2sh")
            spend2.value = 1

            dest = [spend1, spend2]
            dest.insert(pos, change)

            txid = self.create_transaction([in1], dest)
            self.generate_block()

            self.log_value("change-address-type-tx-{}".format(pos), txid)
            self.log_value("change-address-type-position-{}".format(pos), pos)
            self.generate_block()

    def create_locktime_change(self):
        for pos in range(3):
            start = self.next_address()
            self.fund_address(start, 3 + self.fee)
            change = self.next_address()
            change.value = 1
            spend1 = self.next_address()
            spend1.value = 1
            spend2 = self.next_address()
            spend2.value = 1

            dest = [spend1, spend2]
            dest.insert(pos, change)

            txid = self.create_transaction([start], dest, n_locktime=110)
            self.generate_block()

            self.log_value("change-locktime-tx-{}".format(pos), txid)
            self.log_value("change-locktime-position-{}".format(pos), pos)

            for x in [spend1, spend2]:
                dummy = self.next_address()
                dummy.value = 1 - self.fee
                self.create_transaction([x], [dummy])

            dummy_change = self.next_address()
            dummy_change.value = 1 - self.fee

            self.create_transaction([change], [dummy_change], n_locktime=111)
            self.generate_block()

    def create_address_reuse_change(self):
        for pos in range(3):
            change = self.next_address()
            self.fund_address(change, 3 + self.fee)

            spend1 = self.next_address()
            spend1.value = 1

            spend2 = self.next_address()
            spend2.value = 1

            dest = [spend1, spend2]
            dest.insert(pos, change)
            txid = self.create_transaction([change], dest, values=[1, 1, 1])

            self.log_value("change-reuse-tx-{}".format(pos), txid)
            self.log_value("change-reuse-position-{}".format(pos), pos)
            self.generate_block()

    def create_client_behavior_change(self):
        # this does NOT implement the typical client behavior
        for pos in range(3):
            change = self.next_address()
            self.fund_address(change, 3 + self.fee)

            spend1 = self.next_address()
            self.fund_address(spend1, 1)
            spend1.value = 1

            spend2 = self.next_address()
            self.fund_address(spend2, 1)
            spend2.value = 1

            dest = [spend1, spend2]
            dest.insert(pos, change)
            self.create_transaction([change], dest, values=[1, 1, 1])

            self.generate_block()

    def run(self):
        self.create_power_of_ten_change()
        self.create_optimal_change()
        self.create_address_type_change()
        self.create_locktime_change()
        self.create_address_reuse_change()
        self.create_client_behavior_change()
