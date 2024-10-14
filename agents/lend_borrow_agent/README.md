# AAVE agent

This agent provides lending and borrowing of cryptocurrencies from the AAVE pool. AAVE is a Decentralized Finance (DeFi) protocol that allows users to lend and borrow cryptocurrencies without the need for intermediaries. It operates on a peer-to-peer network, providing liquidity and earning interest for lenders while offering collateralized loans for borrowers.

## Environment Setup
You need to specify an `RPC_URL` and `PRIVATE_KEY`  in a _.env_ file in this directory.

Make a copy of the [.env.example](.env.example) file and rename it to _.env_.

The `RPC_URL` can come from an Infura key.

The `PRIVATE_KEY` is your digital wallet's private key. 

# Usage

Sample prompt:
> _Borrow 5 ETH from the AAVE lending pool, with a variable interest rate_

## Setup

Make sure the .env file file is created by doing the following: 

- Create a new file called .env
- Copy the contents of [.env.example](.env.example) into your new .env file

Then create a virtual Python environment:
```
$ python -m venv ./venv
```
- Activate the Python virtual env.
  - Windows:
    - In cmd.exe: `venv\Scripts\activate.bat`
    - In PowerShell: `venv\Scripts\Activate.ps1`
  - Unix: `source venv/bin/activate`
- Install dependencies.
```
$ pip install -r requirements.txt
```



### Testing

- Make sure you're in the `lend_borrow_agent` directory:
```sh
$ pytest test/test_lend_borrow.py
```
- Run the test suite:
```sh
$ pytest
```
- Run tests for a specific module:
```sh
$ pytest tests/path/to/test_module.py
```
- Run with verbose output:
```sh
$ pytest -v
```
- Run with a detailed output of each test (including print statements):
```sh
$ pytest -s
```

## Learn More

- [SwarmZero](https://swarmzero.ai)
- AAVE:
  - Website: https://aave.com/
  - AAVE documentation: https://docs.aave.com/hub
  - AAVE token: https://docs.aave.com/developers/v/1.0/developing-on-aave/the-protocol/aave-token
  - Smart contracts overview: https://docs.aave.com/developers/getting-started/contracts-overview
