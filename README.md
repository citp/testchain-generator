[![Build Status](https://travis-ci.org/citp/testchain-generator.svg?branch=master)](https://travis-ci.org/citp/testchain-generator)

# Testchain Generator

This tools deterministically generates a synthetic blockchain using Bitcoin's regtest mode.
It was written to provide a lean blockchain to run functional and regression against and is used to test [BlockSci](https://github.com/citp/BlockSci).

## Install
- Install [secp256k1](https://github.com/bitcoin-core/secp256k1) (should already be installed when using BlockSci)
- Install Bitcoin Core
    - Mac: `brew install bitcoin`
    - Linux: [Install instructions](https://bitcoin.org/en/full-node#linux-instructions) (only install the daemon)
- Install Python3 requirements
    - `pip3 install -r requirements.txt`

## Running

If you are using this as a submodule for BlockSci, you can just run
```
python3 generate_chain.py
```
It will automatically update the `BlockSci/test/files/` directory with the new block and json files. 

If you're using this as a standalone tool, you'll probably want to change the output directory for the generated files
```
python3 generate_chain.py --output-dir=output
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
