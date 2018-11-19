from blockgen.motifs.setup import SetupChain, FinalizeChain
from blockgen.motifs.change import Change
from blockgen.motifs.motifs import Motifs
from blockgen.motifs.addresses import Addresses
from blockgen.motifs.special import SpecialCases
from blockgen.motifs.taint import Taint
from blockgen.motifs.heuristics import Heuristics
from blockgen.runner import Runner

generator = Runner()

generator.add_generator(SetupChain)
generator.add_generator(Addresses)
generator.add_generator(Motifs)
generator.add_generator(Change)
generator.add_generator(SpecialCases)
generator.add_generator(Taint)
generator.add_generator(Heuristics)
generator.add_generator(FinalizeChain)

generator.run()
