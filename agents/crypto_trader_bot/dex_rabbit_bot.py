import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config import SUPPORTED_CHAINS
from dex_agent import DexAgent

logger = logging.getLogger(__name__)


class DexRabbitBot:
    def __init__(self, token: str, agent: DexAgent):
        """Initialize the bot with Telegram token and DexAgent"""
        self.token = token
        self.agent = agent
        self.app = Application.builder().token(token).build()

    def setup_handlers(self):
        """Setup message and command handlers"""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self._start_command))
        self.app.add_handler(CommandHandler("help", self._help_command))
        self.app.add_handler(CommandHandler("chains", self._chains_command))

        # Message handler for chat
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

        # Error handler
        self.app.add_error_handler(self._error_handler)

        logger.info("Bot handlers configured successfully")

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "👋 Welcome to DexRabbit Trading Bot!\n\n"
            "I'm an AI assistant that can help you analyze and trade crypto across multiple blockchains.\n\n"
            "You can:\n"
            "• Ask me about market activity on any chain\n"
            "• Get trading suggestions\n"
            "• Check supported blockchains with /chains\n"
            "• Get help anytime with /help\n\n"
            "Try asking something like:\n"
            "- 'How's the Ethereum market looking?'\n"
            "- 'What trades do you suggest on BSC?'\n"
            "- 'Show me market activity on Solana'"
        )
        await update.message.reply_text(welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🤖 DexRabbit Bot Help\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/chains - List supported blockchains\n\n"
            "You can chat with me naturally! Try asking:\n"
            "• 'Analyze the ETH market'\n"
            "• 'What trades look good on BSC?'\n"
            "• 'Show me Solana trading activity'\n"
            "• 'Which chains do you support?'"
        )
        await update.message.reply_text(help_message)

    async def _chains_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chains command"""
        chains_list = "\n".join(
            f"• {config.name} ({chain_id.upper()}) - Native token: {config.native_token}"
            for chain_id, config in SUPPORTED_CHAINS.items()
        )
        message = f"🌐 Supported Blockchains:\n\n{chains_list}"
        await update.message.reply_text(message)

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming chat messages"""
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

            # Get response from AI agent
            response = await self.agent.chat(update.message.text)

            # Send response
            await update.message.reply_text(response, parse_mode="HTML", disable_web_page_preview=True)

        except ValueError as e:
            # Handle validation errors (like unsupported chains)
            logger.error(f"Validation error: {str(e)}")
            chains_list = ", ".join(SUPPORTED_CHAINS.keys())
            await update.message.reply_text(
                f"❌ {str(e)}\n\nSupported chains are: {chains_list}\n" "Try asking about one of these chains!"
            )
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await update.message.reply_text(
                "Sorry, I encountered an error while processing your request. "
                "This might be due to API rate limits or temporary service issues. "
                "Please try again in a moment."
            )

    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, something went wrong. Please try again later.",
            )

    def run(self):
        """Start the bot"""
        self.setup_handlers()
        logger.info("Bot started successfully")
        self.app.run_polling()
