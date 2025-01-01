# Crypto Trader Telegram Bot

An AI-powered cryptocurrency trading bot that leverages BitQuery for market data and provides trading insights through a Telegram interface.

Inspired by [How to build your own Add Liquidity Signal Telegram Bot for Solana DEX Pools | Bitquery API Tutorial
](https://youtu.be/s5GTjKhUmEo?si=DI61viBplqKIYwXG).

## Features

- Real-time cryptocurrency market data monitoring via BitQuery
- Telegram bot interface for user interaction
- Configurable logging levels
- AI-powered trading analysis and recommendations

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Telegram Bot Token (from BotFather)
- BitQuery OAuth Token
- OpenAI API Key (for AI features)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/swarmzero/examples.git
cd examples/agents/crypto_trader_bot
```

2. Install dependencies using Poetry:
```bash
poetry install --no-root
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the required tokens and API keys:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `BOTFATHER_API_TOKEN`: Your Telegram bot token
     - `BITQUERY_OAUTH_TOKEN`: Your BitQuery OAuth token
     - `LOG_LEVEL`: Desired logging level (DEBUG, INFO, WARNING, ERROR)

## Usage

1. Activate the Poetry environment:
```bash
poetry shell
```

2. Run the bot:
```bash
poetry run python main.py
```

The bot will start and listen for commands through Telegram.

## Project Structure

- `main.py`: Entry point and bot initialization
- `bitquery_service.py`: BitQuery API integration
- `dex_agent.py`: Trading logic and analysis
- `dex_rabbit_bot.py`: Telegram bot implementation
- `config.py`: Configuration management
