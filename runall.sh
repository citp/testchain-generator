#!/bin/sh
python3 generate_chain.py --output-dir=output --chain=btc --exec=./bin/bitcoind
python3 generate_chain.py --output-dir=output --chain=bch --exec=./bin/bitcoin-cash
python3 generate_chain.py --output-dir=output --chain=ltc --exec=./bin/litecoind
