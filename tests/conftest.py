import bitcoin
from bitcoin.core.key import use_libsecp256k1_for_signing

bitcoin.SelectParams('regtest')

use_libsecp256k1_for_signing(True)  # for deterministic coinbase transactions and signatures
