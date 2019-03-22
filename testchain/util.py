from bitcointx.core import CBlock, x, COIN, CoreChainParams


class Coin(object):
    COIN = 1e8

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_satoshi(cls, value):
        return cls(value / cls.COIN)

    def satoshi(self):
        return int(round(self.val * self.COIN, 0))

    def bitcoin(self):
        return round(self.val, 8)

    def __eq__(self, other):
        if type(other) == Coin:
            return self.satoshi() == other.satoshi()
        else:
            return self.satoshi() == other

    def __ne__(self, other):
        if type(other) == Coin:
            return self.satoshi() != other.satoshi()
        else:
            return self.satoshi() != other

    def __le__(self, other):
        if type(other) == Coin:
            return self.satoshi() <= other.satoshi()
        else:
            return self.satoshi() <= other

    def __ge__(self, other):
        if type(other) == Coin:
            return self.satoshi() >= other.satoshi()
        else:
            return self.satoshi() >= other

    def __lt__(self, other):
        if type(other) == Coin:
            return self.satoshi() < other.satoshi()
        else:
            return self.satoshi() < other

    def __gt__(self, other):
        if type(other) == Coin:
            return self.satoshi() > other.satoshi()
        else:
            return self.satoshi() > other

    def __add__(self, other):
        if type(other) == Coin:
            return self.satoshi() + other.satoshi()
        else:
            return self.satoshi() + other

    def __sub__(self, other):
        if type(other) == Coin:
            return self.satoshi() - other.satoshi()
        else:
            return self.satoshi() - other

    def __mul__(self, other):
        if type(other) == Coin:
            return self.satoshi() * other.satoshi()
        else:
            return self.satoshi() * other

    def __div__(self, other):
        if type(other) == Coin:
            return self.satoshi() / other.satoshi()
        else:
            return self.satoshi() / other

    def __str__(self):
        return "Coin[{}]".format(self.satoshi())

    def __repr__(self):
        return "Coin[{}]".format(self.satoshi())


class CoreLitecoinParams(CoreChainParams):
    NAME = 'litecoin-mainnet'
    GENESIS_BLOCK = CBlock.deserialize(x(
        '0100000000000000000000000000000000000000000000000000000000000000'
        '00000000d9ced4ed1130f7b7faad9be25323ffafa33232a17c3edf6cfd97bee6'
        'bafbdd97b9aa8e4ef0ff0f1ecd513f7c01010000000100000000000000000000'
        '00000000000000000000000000000000000000000000ffffffff4804ffff001d'
        '0104404e592054696d65732030352f4f63742f32303131205374657665204a6f'
        '62732c204170706c65e280997320566973696f6e6172792c2044696573206174'
        '203536ffffffff0100f2052a010000004341040184710fa689ad5023690c80f3'
        'a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f47'
        '0216fe1b51850b4acf21b179c45070ac7b03a9ac00000000'))
    SUBSIDY_HALVING_INTERVAL = 840000
    PROOF_OF_WORK_LIMIT = 2 ** 256 - 1 >> 20
    MAX_MONEY = 84000000 * COIN


class RegtestLitecoinParams(CoreLitecoinParams):
    RPC_PORT = 18443
    BASE58_PREFIXES = {'PUBKEY_ADDR': 111,
                       'SCRIPT_ADDR': 58,
                       'SECRET_KEY': 239,
                       'EXTENDED_PUBKEY': b'\x04\x35\x87\xCF',
                       'EXTENDED_PRIVKEY': b'\x04\x35\x83\x94'}
    BECH32_HRP = 'rltc'
    BASE58_PREFIX_ALIAS = {5: 50}
