import logging
from lend_borrow_agent.main import lend_crypto, borrow_crypto


def test_lend_crypto():
    try:
        tx_hash = lend_crypto(0.00000001, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')  # ETH special address
    except Exception as e:
        logging.error(f"Error during lend_crypto test: {e}")

def test_borrow_crypto():
    try:
        tx_hash = borrow_crypto(0.00000001, '0x6b175474e89094c44da98b954eedeac495271d0f', 2)  #  DAI address
    except Exception as e:
        logging.error(f"Error during borrow_crypto test: {e}")

if __name__ == "__main__":
    test_lend_crypto()
    test_borrow_crypto()
