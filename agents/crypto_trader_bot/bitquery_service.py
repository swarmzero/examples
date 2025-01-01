import logging
from datetime import datetime, timedelta, timezone
from typing import Dict

import aiohttp

from config import get_chain_id

logger = logging.getLogger(__name__)


class BitQueryService:
    def __init__(self, oauth_token: str):
        if not oauth_token:
            raise ValueError("BitQuery OAuth token is required")

        logger.debug("Initializing BitQueryService")
        self.oauth_token = oauth_token
        self.url = "https://streaming.bitquery.io/graphql"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {oauth_token}",
        }

    def _get_base_trade_fields(self, address_field: str = "SmartContract") -> str:
        """Get common trade fields structure for all chains"""
        return f"""
            Block {{
                Number
                Time
            }}
            Transaction {{
                Hash
            }}
            Trade {{
                Buy {{
                    Amount
                    Currency {{
                        Name
                        Symbol
                        {address_field}
                    }}
                    Price
                }}
                Sell {{
                    Amount
                    Currency {{
                        Name
                        Symbol
                        {address_field}
                    }}
                    Price
                }}
                Dex {{
                    ProtocolName
                }}
            }}
        """

    def _get_chain_query(self, chain: str) -> tuple[str, str]:
        """Get chain-specific query structure and namespace"""
        if chain == "solana":
            return "Solana", "MintAddress"
        elif chain == "tron":
            return "Tron", "Address"
        elif chain == "ton":
            return "TON", "Address"
        else:  # EVM chains
            return "EVM", "SmartContract"

    async def get_chain_activity(self, chain: str, time_window: int = 60) -> Dict:
        """
        Fetch trading activity for specified chain
        time_window: minutes to look back
        """
        try:
            logger.debug(f"Fetching chain activity for {chain}, time window: {time_window}min")
            now = datetime.now(timezone.utc)
            time_ago = now - timedelta(minutes=time_window)

            # Normalize chain name
            chain = get_chain_id(chain)
            namespace, address_field = self._get_chain_query(chain)
            trade_fields = self._get_base_trade_fields(address_field)

            # Build query based on chain type
            if namespace == "EVM":
                # Query for EVM chains
                query = f"""
                query ($network: evm_network!, $since: DateTime) {{
                  {namespace}(network: $network) {{
                    DEXTrades(
                      orderBy: {{descending: Block_Time}}
                      where: {{Block: {{Time: {{since: $since}}}}}}
                    ) {{
                      {trade_fields}
                    }}
                  }}
                }}
                """
                variables = {"network": chain.lower(), "since": time_ago.isoformat()}
            else:
                # Query for non-EVM chains (Solana, Tron, TON)
                query = f"""
                query ($since: DateTime) {{
                  {namespace} {{
                    DEXTrades(
                      orderBy: {{descending: Block_Time}}
                      where: {{Block: {{Time: {{since: $since}}}}}}
                    ) {{
                      {trade_fields}
                    }}
                  }}
                }}
                """
                variables = {"since": time_ago.isoformat()}

            # Log the query and variables
            logger.debug(f"BitQuery request for {chain}:")
            logger.debug(f"Query: {query}")
            logger.debug(f"Variables: {variables}")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    headers=self.headers,
                    json={"query": query, "variables": variables},
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"BitQuery API error: Status {response.status}, Response: {error_text}")
                        raise aiohttp.ClientError(f"BitQuery API returned status {response.status}")

                    data = await response.json()

                    if "errors" in data:
                        logger.error(f"GraphQL errors: {data['errors']}")
                        raise ValueError(f"GraphQL query failed: {data['errors']}")

                    # Log the response data
                    trades = data.get("data", {}).get(namespace, {}).get("DEXTrades", [])
                    logger.info(f"Received {len(trades)} trades from BitQuery for {chain}")

                    # Log sample of trades for debugging
                    if trades:
                        logger.debug("Sample trade data (first trade):")
                        logger.debug(f"Block: {trades[0].get('Block', {})}")
                        logger.debug(f"Transaction: {trades[0].get('Transaction', {})}")
                        logger.debug(f"Trade details: {trades[0].get('Trade', {})}")

                    logger.debug(f"Successfully fetched data for {chain}")
                    return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching chain activity: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching chain activity for {chain}: {str(e)}")
            raise
