import asyncio
import logging


from discord import Intents

# Importing config for the first time initialises it.
from DiploGM.bot import DiploGM
from DiploGM.config import (
	ConfigException,
	LOGGING_LEVEL,
	DISCORD_TOKEN,
	COMMAND_PREFIX,
	output_config_logs,
)
from DiploGM.utils.logging import setup_logging

match LOGGING_LEVEL:
	case "CRITICAL":
		log_level = logging.CRITICAL
	case "ERROR":
		log_level = logging.ERROR
	case "WARN" | "WARNING":
		log_level = logging.WARNING
	case "INFO":
		log_level = logging.INFO
	case "DEBUG":
		log_level = logging.DEBUG
	case _:
		raise ConfigException("bot.log_level is set to an invalid value")


logger = logging.getLogger(__name__)

# config is run before logging is setup. Output logs now.
output_config_logs()


async def main():
	token = DISCORD_TOKEN
	if not token:
		raise RuntimeError("The DISCORD_TOKEN environment variable is not set")

	intents = Intents.default()
	intents.message_content = True
	intents.members = True
	bot = DiploGM(command_prefix=COMMAND_PREFIX, intents=intents)

	async with bot:
		try:
			await bot.start(token)
		except (asyncio.CancelledError, KeyboardInterrupt):
			logger.warning("Interrupt detected, attempting close...")
		finally:
			if not bot.is_closed():
				await bot.close()

			logger.info("Bot has shut down :)")


def cli():
	setup_logging(LOGGING_LEVEL)
	asyncio.run(main())


if __name__ == "__main__":
	setup_logging(LOGGING_LEVEL)
	asyncio.run(main())
