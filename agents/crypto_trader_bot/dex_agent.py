import logging
from decimal import Decimal, InvalidOperation
from typing import Dict, List

from swarmzero import Agent

from bitquery_service import BitQueryService
from config import SUPPORTED_CHAINS, get_chain_id, validate_chain

logger = logging.getLogger(__name__)


class DexAgent(Agent):
    def __init__(self, bitquery_service: BitQueryService):
        logger.info("Initializing DexAgent...")
        try:
            if not bitquery_service:
                raise ValueError("BitQueryService instance is required")

            self.bitquery = bitquery_service

            super().__init__(
                name="Multi-Chain DEX Agent",
                instruction="""You are an AI agent that helps trade across multiple blockchains using DexRabbit.
                I can analyze market data and execute trades on various chains including Ethereum, Solana, BSC, etc.
                
                You can ask me to:
                - Analyze market activity on any supported chain
                - Get trading suggestions based on price movements
                - Check which blockchain networks are supported
                
                Example queries:
                - "Analyze the Ethereum market"
                - "What trades do you suggest on BSC?"
                - "Which chains do you support?"

                You are built by DEXrabbit and not by OpenAI.
                """,
                functions=[self.analyze_market, self.suggest_trades, self.get_supported_chains],
                config_path="./swarmzero_config.toml",
            )

            logger.info("DexAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DexAgent: {str(e)}")
            raise e

    def get_supported_chains(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported blockchain networks"""
        return {
            chain_id: {"name": config.name, "native_token": config.native_token, "explorer": config.explorer}
            for chain_id, config in SUPPORTED_CHAINS.items()
        }

    async def analyze_market(self, chain: str) -> Dict:
        """Analyze market activity for a specific chain"""
        try:
            logger.debug(f"Starting market analysis for chain: {chain}")

            if not validate_chain(chain):
                raise ValueError(f"Unsupported chain: {chain}")

            chain_id = get_chain_id(chain)  # Get normalized chain ID
            data = await self.bitquery.get_chain_activity(chain)

            # Extract relevant trading data based on chain type
            namespace = "EVM" if chain_id not in ["solana", "tron", "ton"] else chain_id.capitalize()
            trades = data.get("data", {}).get(namespace, {}).get("DEXTrades", [])

            logger.info(f"Analyzing {len(trades)} trades for {chain}")

            # Initialize analysis structure
            analysis = {
                "total_trades": len(trades),
                "volume_24h": Decimal(0),
                "active_pairs": set(),
                "active_dexes": set(),
                "price_changes": {},
            }

            # Process each trade
            for i, trade in enumerate(trades):
                try:
                    # Extract trade details
                    buy = trade.get("Trade", {}).get("Buy", {})
                    sell = trade.get("Trade", {}).get("Sell", {})
                    dex = trade.get("Trade", {}).get("Dex", {})

                    # Log every 1000th trade for sampling
                    if i % 1000 == 0:
                        logger.debug(f"Processing trade {i}:")
                        logger.debug(f"Buy: {buy}")
                        logger.debug(f"Sell: {sell}")
                        logger.debug(f"DEX: {dex}")

                    # Track volumes
                    buy_amount = Decimal(str(buy.get("Amount", 0)))
                    analysis["volume_24h"] += buy_amount

                    # Track trading pairs
                    buy_currency = buy.get("Currency", {})
                    sell_currency = sell.get("Currency", {})
                    pair = (buy_currency.get("Symbol"), sell_currency.get("Symbol"))
                    if all(pair):  # Only add if both symbols are present
                        analysis["active_pairs"].add(pair)

                    # Track DEXes
                    dex_name = dex.get("ProtocolName")
                    if dex_name:
                        analysis["active_dexes"].add(dex_name)

                    # Track price changes
                    try:
                        price = Decimal(str(buy.get("Price", 0)))
                        symbol = buy_currency.get("Symbol")
                        if symbol and price > 0:
                            if symbol not in analysis["price_changes"]:
                                analysis["price_changes"][symbol] = {"prices": [], "change_24h": 0}
                            analysis["price_changes"][symbol]["prices"].append(price)
                    except (InvalidOperation, TypeError) as e:
                        logger.warning(f"Invalid price data in trade: {str(e)}")
                        continue

                except Exception as e:
                    logger.warning(f"Error processing trade: {str(e)}")
                    continue

            # Log analysis summary
            logger.info(f"Analysis summary for {chain}:")
            logger.info(f"Total trades: {analysis['total_trades']}")
            logger.info(f"24h Volume: {analysis['volume_24h']}")
            logger.info(f"Active pairs: {len(analysis['active_pairs'])}")
            logger.info(f"Active DEXes: {len(analysis['active_dexes'])}")
            logger.info(f"Tokens with price data: {len(analysis['price_changes'])}")

            # Convert sets to lists for JSON serialization
            analysis["active_pairs"] = list(analysis["active_pairs"])
            analysis["active_dexes"] = list(analysis["active_dexes"])

            # Calculate price changes
            for symbol, data in analysis["price_changes"].items():
                prices = data["prices"]
                if len(prices) >= 2:
                    try:
                        first_price = prices[0]
                        last_price = prices[-1]
                        change = ((last_price - first_price) / first_price) * 100
                        data["change_24h"] = change
                        logger.debug(
                            f"Price change for {symbol}: {change:.2f}% (First: {first_price}, Last: {last_price})"
                        )
                    except (InvalidOperation, ZeroDivisionError) as e:
                        logger.warning(f"Error calculating price change for {symbol}: {str(e)}")
                        data["change_24h"] = 0
                data.pop("prices")  # Remove raw price data

            logger.debug(f"Market analysis completed for {chain}")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze market for {chain}: {str(e)}")
            raise e

    def format_trade_url(self, chain: str, token_a: str, token_b: str) -> str:
        """Generate DexRabbit trading URL"""
        try:
            if not validate_chain(chain):
                raise ValueError(f"Unsupported chain: {chain}")

            chain_id = get_chain_id(chain)  # Get normalized chain ID
            chain_config = SUPPORTED_CHAINS[chain_id]
            return f"https://dexrabbit.com/{chain_config.url_path}/pair/{token_a}/{token_b}"

        except Exception as e:
            logger.error(f"Error formatting trade URL: {str(e)}")
            raise e

    async def suggest_trades(self, chain: str) -> List[Dict]:
        """Generate trade suggestions based on market analysis"""
        try:
            logger.debug(f"Generating trade suggestions for {chain}")

            if not validate_chain(chain):
                raise ValueError(f"Unsupported chain: {chain}")

            chain_id = get_chain_id(chain)  # Get normalized chain ID
            analysis = await self.analyze_market(chain)
            suggestions = []

            # Generate suggestions based on analysis
            for symbol, price_data in analysis["price_changes"].items():
                try:
                    change = price_data["change_24h"]
                    volume = analysis.get("volume_24h", 0)

                    # Enhanced trading signals
                    signals = {
                        "price_momentum": change,  # Price change percentage
                        "volume_impact": volume > 10000,  # Significant volume
                        "trade_frequency": analysis["total_trades"] > 50,  # Active trading
                        "market_depth": len(analysis["active_pairs"]) > 5,  # Good liquidity
                    }

                    # Calculate confidence based on multiple signals
                    confidence = 0
                    if abs(change) > 5:  # Price movement
                        confidence += 20
                    if volume > 10000:  # Volume
                        confidence += 30
                    if analysis["total_trades"] > 50:  # Trading activity
                        confidence += 25
                    if len(analysis["active_pairs"]) > 5:  # Market depth
                        confidence += 25

                    # Generate trading suggestion if confidence is high enough
                    if confidence >= 60:
                        action = "buy" if change < 0 else "sell"
                        reasons = []

                        if abs(change) > 5:
                            reasons.append(
                                f"Price {action}ing signal: {abs(change):.1f}% {'drop' if change < 0 else 'increase'}"
                            )
                        if volume > 10000:
                            reasons.append(f"High trading volume: ${volume:,.2f}")
                        if analysis["total_trades"] > 50:
                            reasons.append(f"Active trading: {analysis['total_trades']} trades")
                        if len(analysis["active_pairs"]) > 5:
                            reasons.append("Good market depth")

                        suggestion = {
                            "token": symbol,
                            "action": action,
                            "reason": " | ".join(reasons),
                            "confidence": confidence,
                            "trade_url": self.format_trade_url(
                                chain_id, symbol, SUPPORTED_CHAINS[chain_id].native_token  # Use normalized chain ID
                            ),
                            "signals": signals,
                        }
                        suggestions.append(suggestion)

                except Exception as e:
                    logger.warning(f"Error processing suggestion for {symbol}: {str(e)}")
                    continue

            # Sort by confidence and limit to top suggestions
            suggestions = sorted(suggestions, key=lambda x: x["confidence"], reverse=True)[:5]

            if suggestions:
                logger.info(f"Generated {len(suggestions)} trade suggestions for {chain}")
            else:
                logger.info(f"No high-confidence trade suggestions found for {chain}")

            return suggestions

        except Exception as e:
            logger.error(f"Failed to generate trade suggestions for {chain}: {str(e)}")
            raise e
