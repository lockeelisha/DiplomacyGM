"""Custom HelpCommand that provides dynamic, variant-aware help text."""
from __future__ import annotations

import logging
import tomllib
from typing import TYPE_CHECKING
from discord.ext import commands
from DiploGM.errors import NoGameError
from DiploGM.manager import Manager
if TYPE_CHECKING:
    from DiploGM.models.board import Board

logger = logging.getLogger(__name__)
manager = Manager()

with open("assets/help_texts.toml", "rb") as file:
    HELP_TEXTS: dict[str, dict[str, str]] = tomllib.load(file)

def _add_color_options(guild_id: int) -> str:
    try:
        board = manager.get_board(guild_id)
    except NoGameError:
        return ""
    color_options: list[str] = board.data.get("svg config", {}).get("color_options", ["standard"])
    description = " The following color modes are supported:"
    for color in [*color_options, "custom"]:
        credit = board.data.get("svg config", {}).get("color_credits", {}).get(color)
        suffix = f" (by {credit})" if credit else ""
        description += f"\n      {color}{suffix}"
    return description

class HelpCommand(commands.DefaultHelpCommand):
    async def send_command_help(self, command: commands.Command) -> None:
        ctx = self.context
        if not ctx or not ctx.guild:
            await super().send_command_help(command)
            return
        if command.qualified_name in HELP_TEXTS:
            data = HELP_TEXTS[command.qualified_name]
            if "usage" in data:
                self.paginator.add_line(command.qualified_name + " " + data["usage"])
                self.paginator.add_line("")
            self.paginator.add_line(data["description"].strip())
            params = {k: v for k, v in data.items() if k not in {"description", "usage"}}
            if params:
                self.paginator.add_line("\nArguments:")
                for param, description in params.items():
                    if param == "color":
                        description += _add_color_options(ctx.guild.id)
                    self.paginator.add_line(f"  '{param}': {description}")
            if command.aliases:
                self.paginator.add_line(f"\nAliases: {', '.join(command.aliases)}")
            await self.send_pages()
            return
        await super().send_command_help(command)
