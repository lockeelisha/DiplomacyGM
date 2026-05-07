"""Custom HelpCommand that provides dynamic, variant-aware help text."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from discord.ext import commands
from DiploGM.manager import Manager
if TYPE_CHECKING:
    from DiploGM.models.board import Board

logger = logging.getLogger(__name__)
manager = Manager()

def _view_map(command: commands.Command, board: Board) -> list[str]:
    show_moves = command.qualified_name == "view_map"
    color_options: list[str] = board.data.get("svg config", {}).get("color_options", ["standard"])
    color_options.append("custom")

    lines = [f"Draws and outputs a map of the board{' with submitted orders' if show_moves else ''}."]
    lines.append("")
    lines.append("Arguments:")
    lines.append("  Year and/or season: Used to view older maps.")
    lines.append("  svg: Return the map as an SVG file. (Available to GMs only)")
    lines.append("  Color options: The following color modes are supported:")
    for color in color_options:
        credit = board.data.get("svg config", {}).get("color_credits", {}).get(color)
        suffix = f" (by {credit})" if credit else ""
        lines.append(f"    {color}{suffix}")
    lines.append("")
    lines.append("Examples:")
    lines.append(f"  .view_map {board.data.get('start_year', 1901)} fm")
    lines.append("  .vc custom")
    lines.append("")
    lines.append(f"Aliases: {', '.join(f'{a}' for a in command.aliases)}")
    return lines

class HelpCommand(commands.DefaultHelpCommand):
    async def send_command_help(self, command: commands.Command) -> None:
        ctx = self.context
        if not ctx or not ctx.guild:
            await super().send_command_help(command)
            return
        if command.qualified_name in {"view_map", "view_current"}:
            try:
                board = manager.get_board(ctx.guild.id)
                for line in _view_map(command, board):
                    self.paginator.add_line(line)
                await self.send_pages()
                return
            except Exception:
                pass
        await super().send_command_help(command)
