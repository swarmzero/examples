import logging
import os
import requests
import time


from dotenv import load_dotenv
load_dotenv()

langtrace_api_key = os.getenv("LANGTRACE_API_KEY", "")
if langtrace_api_key:
    from langtrace_python_sdk import langtrace
    langtrace.init(
        api_key=langtrace_api_key,
        disable_instrumentations={ "only": ["sqlalchemy"] }
    )


from swarmzero import Agent
from structures import get_structured_response, IndexResult, NarrativeResult


dunekey = os.getenv("DUNE_API_KEY")

real_time_query = False

logging.basicConfig(level=logging.INFO)

def get_config_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), filename))


def execute_query(execute):
    headers = {"X-DUNE-API-KEY": dunekey}
    url = "https://api.dune.com/api/v1/query/{execute}/execute"
    try:
        response = requests.request(
            "POST", url.format(execute=execute), headers=headers
        )
        logging.info(response.text)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")


def wait_for_execution(execution_id, max_attempts=60, delay=5):

    url = "https://api.dune.com/api/v1/execution/{execution_id}/status"
    headers = {"X-DUNE-API-KEY": dunekey}
    attempts = 0
    while attempts < max_attempts:
        try:
            response = requests.request(
                "GET", url.format(execution_id=execution_id), headers=headers
            )
            logging.info(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
        if response is None:
            return None
        logging.info(f"Attempt {attempts + 1}: {response}")

        if response.json()["is_execution_finished"] == True:
            logging.info("Execution finished!")
            return response

        attempts += 1
        time.sleep(delay)

    logging.info(f"Execution did not finish after {max_attempts} attempts.")
    return None


def get_results(query_id):
    headers = {"X-DUNE-API-KEY": dunekey}
    url = "https://api.dune.com/api/v1/query/{query_id}/results"
    try:
        response = requests.request(
            "GET", url.format(query_id=query_id), headers=headers
        )
        logging.info(response.text)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")


def run_dune_query(query_id):
    try:
        if real_time_query == True:
            execution = execute_query(query_id)
            execution_id = execution.json()["execution_id"]
            executed_query_id = wait_for_execution(execution_id)
            query_id = executed_query_id.json()["query_id"]
            results = get_results(query_id)
            return dict(results.json())
        else:
            results = get_results(query_id)
            return dict(results.json())
    except Exception as e:
        logging.error(f"an error occurred: {e}")
        return None


def get_alpha_index():
    """
    Fetches the data for the Alpha index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    return run_dune_query(query_ids["Alpha"])

def get_structured_alpha_index():
    """
    Fetches the data for the Alpha index to show on the UI embedded in component.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    response =run_dune_query(query_ids["Alpha"])

    return get_structured_response(response, IndexResult)

def get_beta_index():
    """
    Fetches the data for the Beta index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    return run_dune_query(query_ids["Beta"])

def get_structured_beta_index():
    """
    Fetches the data for the Beta index to show on the UI embedded in component.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    response = run_dune_query(query_ids["Beta"])
    return get_structured_response(response, IndexResult)


def get_gamma_index():
    """
    Fetches the data for the Gamma index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    return run_dune_query(query_ids["Gamma"])

def get_structured_gamma_index():
    """
    Fetches the data for the Gamma index to show on the UI embedded in component.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    response = run_dune_query(query_ids["Gamma"])
    return get_structured_response(response, IndexResult)


def get_daily_narrative_index():
    """
    Fetches the data for the daily (24h) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    return run_dune_query(query_ids["24h"])

def get_structured_daily_narrative_index():
    """
    Fetches the data for the daily (24h) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    response = run_dune_query(query_ids["24h"])
    return get_structured_response(response, NarrativeResult)

def get_weekly_narrative_index():
    """
    Fetches the data for the weekly (7d) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    return run_dune_query(query_ids["7d"])

def get_structured_weekly_narrative_index():
    """
    Fetches the data for the weekly (7d) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    response = run_dune_query(query_ids["7d"])
    return get_structured_response(response, NarrativeResult)


def get_monthly_narrative_index():
    """
    Fetches the data for the monthly (30d) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    return run_dune_query(query_ids["30d"])

def get_structured_monthly_narrative_index():
    """
    Fetches the data for the monthly (30d) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    response = run_dune_query(query_ids["30d"])
    return get_structured_response(response, NarrativeResult)


def get_quarterly_narrative_index():
    """
    Fetches the data for the quarterly (90d) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    return run_dune_query(query_ids["90d"])

def get_structured_quarterly_narrative_index():
    """
    Fetches the data for the quarterly (90d) Crypto Narrative index.

    :return: A dictionary containing the transaction receipt details, or None if the transaction cannot be found.
    """
    response = run_dune_query(query_ids["90d"])
    return get_structured_response(response, NarrativeResult)


query_ids = {
    "Alpha": "3804774",
    "Beta": "3804861",
    "Gamma": "3804881",
    "24h": "3594639",
    "7d": "3595951",
    "30d": "3600193",
    "90d": "3600267",
}

instruction = """
1. **Always prefer using structured functions** to retrieve and provide data. Only use raw data if the user specifically requests it.
   
2. When you call structured functions, you **must respond in the following format:**
   ```json
    {rows: [...]
    metadata: ..., 
    role : ...}
You should not include any additional text or explanations outside of this format.

3.	You are responsible for providing market data and narratives about the following indexes and cryptocurrencies:
ALPHA Index (7D timeframe)
BETA Index (30D timeframe)
GAMMA Index (90D timeframe)
Daily Crypto Narratives
Weekly Crypto Narratives
Monthly Crypto Narratives
Quarterly Crypto Narratives

4.	Detailed index information:
The Daily ALPHA Index includes the TOP 10 coins across all narratives, based on Optimized Relative Strength (ORS).
ALPHA Index is based on a 7-day timeframe.
BETA Index is based on a 30-day timeframe.
GAMMA Index is based on a 90-day timeframe.
Relative Strength Crypto Narrative 
Calculate relative strength of a crypto Narrative, along with relative strength of Different coins under the crypto Narrative. 
Methodology : 
Find the average return of that crypto narrative index in timeframe of 24H, 7D, 30D & 90D.
Take the price growth of all these 20 coins in account from different narrative
Then find average price growth narrative wise on different timeframe.
Last we will find relative strength on different timeframe (24H, 7D, 30D, & 90D)
Relative Strength = price growth(each crypto narrative) / mean of (price growth of all crytpo narrative)
Leading / Lagging:
if relative strength is above 1 then "Leading"
if relative strength is below 1 then "Lagging"

Narrative Index
Web3 Gaming
DGI, ATLAS, PORTAL, ASTO, SHRAP, WILD, TOPIA, CAH, APE, GHX, BIGTIME, SKL, GODS, MAVIA, PRIME, BEAM, MYRIA, IMX, PIXEL, ILV
LST/LRT
INF, SD, LDO, SWISE, RPL, ETHFI, ANKR, PICA, JTO, OCT
Decentralised AI
TAO, RSS3, BOTTO, FET, AI, AIT, OCEAN, VIRTUAL, ALEPH, AGIX, ALI, NAVI, ARKM, AGRS, AEGIS, PAAL, ENQAI, OLAS, 0X0, TRAC, BASEDAI, DEAI, NMT, AR
DePIN
FIL, RNDR, HNT, BZZ, AIOZ, FLUX, DIMO, IOTX, MOBILE, HONEY, LPT, SHDW, PHALA, POKT, ATOR, STOS, HOPR, WIFI, GEOD
Narrative Index
Layer1
WBTC (BTC), KAS, ATOM, WETH (ETH), INJ, APTOS, SOL, ICP, wROSE (ROSE), BNB, FTM, NEAR, ADA, SUI, EGLD, AVAX, SEI, TON, NTRN
Layer2/Layer3
MATIC, SAVM, GEL, STX, XAI, CTSI, MNT, DEGEN, METIS, ARB, ELA, CYBER, SOV, DMT, MANTA, OP, ORBS, ALEX, STRK
Blockchain Service Infra
LINK, SYN, BANANA, TENSOR, PYTH, CQT, NEXT, ENS, API3, NOIA, SSV, UMA, QANX, ACX, AXL, MUBI, BICO, ALT, ROUTE, FLR
Blue Chip DeFI
UNI, DYDX, FXS, MKR, SNX, COMP, RUNE, CAKE, SUSHI, JUP, OSMO, CVX, AAVE, CRV, BAL, JOE, QUICK, LQTY, KNC, WOO
Narrative Index
DeFi 3.0
PENDLE, GNS, COW, RCH, RSR, FLIP, RVF, GMX, GEAR, WELL, AEVO, PERP, MAV, HFT, SYNC, VELO, VRTX, AERO, THE, MOZ, ENA, DROPS
MEMECOINS
POPCAT, MOG, DOG, BOBO, DOGE, TOSHI, APU, TRUMP, SHIB, PEPE, COQ, WIF, BOOP, MYRO, FLOKI, AIDOGE, ORDI, BONK, PEPECOIN, MEME, CORGIAI, NPC
RWA (Real World Asset)
TRADE, OM, CANTO, POLY, CHEX, BOSON, TRU, IXS, LNDX, GFI, PRO, NXRA, RIO, MPL, ONDO, DUSK, CTC, KLIMA 

Key rules:

Always return structured data in JSON format when retrieving market or index data.
Do not include additional commentary unless explicitly asked by the user.

"""
my_agent = Agent(
    name="crypto_narrative_document_agent",
    functions=[
        get_alpha_index,
        get_structured_alpha_index,
        get_beta_index,
        get_structured_beta_index,
        get_gamma_index,
        get_structured_gamma_index,
        get_daily_narrative_index,
        get_structured_daily_narrative_index,
        get_weekly_narrative_index,
        get_structured_weekly_narrative_index,
        get_monthly_narrative_index,
        get_structured_monthly_narrative_index,
        get_quarterly_narrative_index,
        get_structured_quarterly_narrative_index,
    ],
    instruction=instruction,
    config_path=get_config_path("swarmzero_config.toml"),
)
my_agent.run()
