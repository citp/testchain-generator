from testchain.runner import Generator


class SetupChain(Generator):

    def setup(self):
        """
        Generate 110 blocks, so we have 10 coinbase transactions to spend from.
        """
        block_hashes = self.generate_block(110)
        self.log.info("Starting chain tip is {}".format(block_hashes[-1]))

    def run(self):
        self.setup()


class FinalizeChain(Generator):

    def finalize(self):
        """
        Mine one final block, in case another generator forgot to call generate_block()
        """
        block_hash = self.generate_block()
        self.log.info("Final chain tip is {}".format(block_hash))

    def run(self):
        self.finalize()
