# Testchain Generator

[![Build Status](https://travis-ci.org/citp/testchain-generator.svg?branch=master)](https://travis-ci.org/citp/testchain-generator)

This tools deterministically generates a synthetic blockchain using Bitcoin's regtest mode.
It was written to provide a lean blockchain to run functional and regression against and is used to test [BlockSci](https://github.com/citp/BlockSci).

## Requirements
- Requires Python >=3.6
- Install Bitcoin Core (`bitcoind`)
    - Mac: `brew install bitcoin`
    - Linux: [Install instructions](https://bitcoin.org/en/full-node#linux-instructions) (only install the daemon)
- Install [secp256k1](https://github.com/bitcoin-core/secp256k1)
- Install Python3 requirements
    - `pip3 install -r requirements.txt`

## Running

The `generate_chain.py` script takes three arguments:

- `--output-dir=` specifies where the output should be stored (default: `../files/`)
- `--chain=` specifies whether a Bitcoin or a Bitcoin Cash chain should be generated (options: `btc` or `bch`, default: `btc`)
- `--exec=` expects a path to the node daemon (default: `bitcoind`)

If you are using this as a submodule for BlockSci and want to update the Bitcoin (BTC) chain, you would run
```
python3 generate_chain.py
```
It will automatically update the `BlockSci/test/files/btc/` directory with the new block and json files. 

To update the Bitcoin Cash output, you'll need to select `bch` and provide a path to the Bitcoin ABC daemon executable.
```
python3 generate_chain.py --chain=bch --exec=<path/to/bitcoincashdaemon>
```

If you're using this as a standalone tool, you'll probably want to change the output directory for the generated files, e.g.
```
python3 generate_chain.py --output-dir=.output
```

## Extending the blockchain

New motifs can be created by adding a new class in `blockgen/motifs/` that inherits from `Generator`.
Then, add this new class to `generate_chain.py`.
The `Generator` class provides a number of utility functions, such as:

- `next_address()`: returns a new `Address`
- `current_address()`: returns the current address (the one returned by the last `next_address()` call)
- `fund_address(addr, value)`: sends `value` BTC to the address `addr`
- `create_transaction([sources], [recipients])`: creates a new transaction using a list of addresses as inputs (`[sources]`) and another list of addresses as outputs (`[recipients]`)
- `generate_block()`: creates a new block that includes all transactions created since it was last called

