from testchain.address import Address


def test_p2pkh_address(regtest):
    addr = Address.from_key_index(0, address_type="p2pkh")
    assert 0 == addr.key_index
    assert "p2pkh" == addr.type
    assert 0 == addr.value

    address_regression(addr, regtest)


def test_p2sh_address(regtest):
    addr = Address.from_key_index(1, address_type="p2sh")
    assert 1 == addr.key_index
    assert "p2sh" == addr.type
    assert 0 == addr.value

    address_regression(addr, regtest)


def test_p2wpkh_address(regtest):
    addr = Address.from_key_index(2, address_type="p2wpkh")
    assert 2 == addr.key_index
    assert "p2wpkh" == addr.type
    assert 0 == addr.value

    address_regression(addr, regtest)


def test_p2wsh_address(regtest):
    addr = Address.from_key_index(3, address_type="p2wsh")
    assert 3 == addr.key_index
    assert "p2wsh" == addr.type
    assert 0 == addr.value

    address_regression(addr, regtest)


def address_regression(addr, regtest):
    print(addr.address, file=regtest)
    print(addr.key, file=regtest)
    print(type(addr.address), file=regtest)
