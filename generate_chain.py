import argparse

from testchain.motifs.setup import SetupChain, FinalizeChain
from testchain.motifs.change import Change
from testchain.motifs.motifs import Motifs
from testchain.motifs.addresses import Addresses
from testchain.motifs.special import SpecialCases
from testchain.motifs.taint import Taint
from testchain.motifs.heuristics import Heuristics
from testchain.runner import Runner

parser = argparse.ArgumentParser(description='Generate a synthetic blockchain.')
parser.add_argument('--output-dir', dest='output_dir', default="../files/", help='Output directory')
args = parser.parse_args()
generator = Runner(args.output_dir)

generator.add_generator(SetupChain)
generator.add_generator(Addresses)
generator.add_generator(Motifs)
generator.add_generator(Change)
generator.add_generator(SpecialCases)
generator.add_generator(Taint)
generator.add_generator(Heuristics)
generator.add_generator(FinalizeChain)

generator.run()
