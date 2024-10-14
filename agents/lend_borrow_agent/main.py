
import os
import logging
from typing import Union
import json

from web3 import Web3
from swarmzero import Agent
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
rpc_url = os.getenv("RPC_URL")
private_key = os.getenv("PRIVATE_KEY")
aave_lending_pool_address = os.getenv("AAVE_LENDING_POOL_ADDRESS")

# Initialize Web3 connection
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Load AAVE Lending Pool ABI
with open('./aave_lending_pool_abi.json', 'r') as abi_file:
    aave_lending_pool_abi = json.load(abi_file)

def lend_crypto(amount: float, asset_address: str) -> Union[str, None]:
    """
    Lend cryptocurrency to the AAVE lending pool.

    Parameters:
    amount (float): The amount of cryptocurrency to lend.
    asset_address (str): The address of the asset to lend.

    Returns:
    Union[str, None]: The transaction hash if successful, None otherwise.
    """
    if not web3.is_connected():
        logging.error("Unable to connect to Ethereum")
        return None

    try:
        lending_pool = web3.eth.contract(address=aave_lending_pool_address, abi=aave_lending_pool_abi)
        account = web3.eth.account.from_key(private_key)
        nonce = web3.eth.get_transaction_count(account.address) + 1 # increment nonce by 1 to avoid nonce collision
        logging.info(f"Lending from this address: {account.address}")

        amount_in_wei = int(web3.from_wei(amount, 'ether'))

        tx = lending_pool.functions.deposit(asset_address, web3.from_wei(amount_in_wei, 'ether'), account.address, 0).build_transaction({
            'chainId': 11155111,
            'gas': 700000,
            'gasPrice': web3.eth.gas_price * 2, 
            'nonce': nonce,
        })

        logging.info(f"Transaction before estimation: {tx}")

        tx['gas'] = web3.eth.estimate_gas(tx)
        logging.info(f"Estimated gas: {tx['gas']}")

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logging.info(f"Lending Transaction Hash: {tx_hash.hex()}")
        return web3.to_hex(tx_hash)
    except Exception as e:
        logging.error(f"An error occurred during lending: {e}")
        return None

def borrow_crypto(amount: float, asset_address: str, interest_rate_mode: int) -> Union[str, None]:
    """
    Borrow cryptocurrency from the AAVE lending pool.

    Parameters:
    amount (float): The amount of cryptocurrency to borrow.
    asset_address (str): The address of the asset to borrow.
    interest_rate_mode (int): The interest rate mode (1 for stable, 2 for variable).

    Returns:
    Union[str, None]: The transaction hash if successful, None otherwise.
    """
    if not web3.is_connected():
        logging.error("Unable to connect to Ethereum")
        return None

    try:
        lending_pool = web3.eth.contract(address=aave_lending_pool_address, abi=aave_lending_pool_abi)
        account = web3.eth.account.from_key(private_key)
        nonce = web3.eth.get_transaction_count(account.address)
        logging.info(f"Borrowing from this address: {account.address}")

        amount_in_wei = int(web3.from_wei(amount, 'ether'))

        # Convert addresses to checksum format
        checksum_asset_address = web3.to_checksum_address(asset_address)
        checksum_account_address = web3.to_checksum_address(account.address)

        tx = lending_pool.functions.borrow(checksum_asset_address, web3.from_wei(amount_in_wei, 'ether'), interest_rate_mode, 0, checksum_account_address).build_transaction({
            'chainId': 11155111,
            'gas': 700000,
            'gasPrice': web3.eth.gas_price * 2,
            'nonce': nonce,
        })
        logging.info(f"Transaction before estimation: {tx}")

        tx['gas'] = web3.eth.estimate_gas(tx)
        logging.info(f"Estimated gas: {tx['gas']}")

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logging.info(f"Borrowing Transaction Hash: {tx_hash.hex()}")
        return tx_hash.hex()
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    my_agent = Agent(
        name="AAVE_agent",
        functions=[lend_crypto, borrow_crypto],
        config_path='./swarmzero_config.toml'
    )

    my_agent.run()
