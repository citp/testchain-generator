import atexit
import json
import logging
import os
import shutil
import subprocess
import tempfile
from time import sleep
from typing import List, Type

import bitcoin
import bitcoin.rpc
from bitcoin.core.key import use_libsecp256k1_for_signing
from testchain.generator import Generator
from testchain.address import COINBASE_KEY

LOG_LEVEL = logging.INFO
bitcoin.SelectParams('regtest')

use_libsecp256k1_for_signing(True)  # for deterministic coinbase transactions and signatures


class Runner(object):
    motif_generators: List[Generator]

    def __init__(self, output_dir, chain, exec):
        self.chain = chain
        self.exec = exec
        self.current_time = 1535760000
        self.prev_block = None
        self.motif_generators = []
        self.kv = {}
        self.output_dir = os.path.join(output_dir, '')
        self._setup_logger()
        self._setup_bitcoind()
        self.proxy = bitcoin.rpc.Proxy(btc_conf_file=self._conf_file())
        self.proxy.call("importprivkey", COINBASE_KEY)

    def _setup_logger(self):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(LOG_LEVEL)
        ch = logging.StreamHandler()
        ch.setLevel(LOG_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

    def _setup_bitcoind(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.log.info("bitcoind datadir: {}".format(self.tempdir.name))

        # copy conf file to temp dir
        shutil.copy("bitcoin.conf", self.tempdir.name)

        # launch bitcoind
        params = [self.exec, "-rpcport=18443", "-datadir={}".format(self.tempdir.name),
                  "-mocktime={}".format(self.current_time)]

        # Disable Bitcoin Cash specific address format (breaks Python library)
        # Enable CTOR
        if self.chain == "bch":
            params += ["-usecashaddr=0", "-magneticanomalyactivationtime=0"]
        self.proc = subprocess.Popen(params, stdout=subprocess.DEVNULL)

        # kill process when generator is done
        atexit.register(self._terminate)

        self.log.info("Waiting 5 seconds for bitcoind to start")
        sleep(5)

    def _conf_file(self):
        return "{}/bitcoin.conf".format(self.tempdir.name)

    def _terminate(self):
        """
        Kills the bitcoind process
        """
        self.proc.terminate()
        self.log.info("Waiting 5 seconds for bitcoind to quit")
        sleep(5)

    def next_timestamp(self):
        self.current_time += 600
        return self.current_time

    def export_address_counts(self):
        self._address_sanity_check()
        counts = {"p2pkh": 2, "p2wpkh": 0, "p2sh": 0, "p2wsh": 0}  # coinbase addresses
        for g in self.motif_generators:
            for addr in g.addresses:
                counts[addr.type] += 1
        self.kv["p2pkh_address_count"] = counts["p2pkh"]
        self.kv["p2wpkh_address_count"] = counts["p2wpkh"]
        self.kv["p2sh_address_count"] = counts["p2sh"]
        self.kv["p2wsh_address_count"] = counts["p2wsh"]

    def _address_sanity_check(self):
        total_addresses = 0
        unique_addresses = set()
        for g in self.motif_generators:
            key_indizes = [x.key_index for x in g.addresses]
            unique_addresses |= set(key_indizes)
            total_addresses += len(key_indizes)
        if len(unique_addresses) != total_addresses:
            self.log.warning("Addresses are not unique.")

    def copy_blk_file(self, truncate_file=True):
        """
        Copies the first blk file from the regtest directory to the output directory
        :param truncate_file: Whether the final block file should be truncated. Works with BlockSci, but may not work
        when using other parsers.
        """
        blk_destination = self.output_dir + self.chain + "/regtest/blocks/"
        self.log.info("Copying blk00000.dat to {}".format(blk_destination))
        if not os.path.exists(blk_destination):
            os.makedirs(blk_destination)
        source = "{}/regtest/blocks/blk00000.dat".format(self.tempdir.name)

        if truncate_file:
            with open(source, "rb") as f:
                with open(blk_destination + "blk00000.dat", "wb") as dest:
                    counter = 0
                    while True:
                        bts = f.read(16)
                        if not bts or counter == 16:
                            break
                        if bts == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                            counter += 1
                        else:
                            counter = 0
                        dest.write(bts)
        else:
            shutil.copy(source, blk_destination)

    def persist_hashes(self):
        """
        Dumps hashes into JSON file.
        """
        # kv = {}
        # for g in self.motif_generators:
        #     kv = {**kv, **g.stored_hashes}

        self.log.info("Writing hashes to file output.json")
        self.log.debug(self.kv)
        dest_dir = self.output_dir + self.chain + "/"
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
        with open(dest_dir + "output.json", "w") as f:
            json.dump(self.kv, f, indent=4)

    def add_generator(self, generator: Type[Generator]):
        gen = generator(self.proxy, self.chain, self.log, self.kv, (len(self.motif_generators) + 1) * 10000,
                        self.next_timestamp)
        self.log.debug("Magic No: {}".format(gen.offset))
        self.motif_generators.append(gen)

    def run(self):
        for g in self.motif_generators:
            g.run()
        self._address_sanity_check()
        self.copy_blk_file()
        self.persist_hashes()
