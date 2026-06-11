import asyncio
import logging
from typing import Callable

from discord import TextChannel
from discord.ext import commands

from DiploGM import config
from DiploGM import perms
from DiploGM.utils import (
    get_filtered_orders,
    send_message_and_file,
)
from DiploGM.manager import Manager
from DiploGM.models.player import Player
from DiploGM.utils.sanitise import remove_prefix
from DiploGM.utils.send_message import ErrorMessage, send_error

logger = logging.getLogger(__name__)
manager = Manager()

# if possible save one svg slot for others
fow_export_limit = asyncio.Semaphore(
    max(int(config.SIMULATRANEOUS_SVG_EXPORT_LIMIT) - 1, 1)
)

class FogOfWarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # for fog of war
    async def publish_fow_current(self, ctx: commands.Context):
        await publish_map(
            ctx, manager, "starting map", lambda m, s, p: m.draw_map(s, False, p, fow_player=p)
        )

    @commands.command(
        brief="Sends fog of war maps",
    )
    @perms.gm_only("publish fow moves")
    async def publish_fow_moves(self, ctx: commands.Context):
        assert ctx.guild is not None
        board = manager.get_board(ctx.guild.id)

        if board.data.get("fow", "disabled") != "enabled":
            await send_error(ctx.channel, ErrorMessage.FOW_DISABLED)
            return

        player_category = next((c for c in ctx.guild.categories if config.is_player_category(c)), None)
        if not player_category:
            await send_error(ctx.channel, ErrorMessage.NO_PLAYER_CATEGORY)
            return

        dpi = board.data["svg config"].get("dpi", 200)
        prev_turn = board.turn.get_previous_turn()

        for channel in player_category.channels:
            if not isinstance(channel, TextChannel):
                continue
            if not (player := perms.get_player_by_channel(board, channel)):
                continue
            if (len(player.units) + len(player.centers) == 0) or not player.is_active:
                continue

            file, file_name = manager.draw_map(server_id=ctx.guild.id,
                                            draw_moves=True,
                                            player=None,
                                            turn=prev_turn,
                                            fow_player=player)
            await send_message_and_file(channel=channel,
                                        title=f"{prev_turn} Orders Map",
                                        message=f"Here is the {prev_turn} orders map for {player.name}",
                                        file=file,
                                        file_name=file_name,
                                        convert_svg=True,
                                        file_in_embed=False,
                                        dpi=dpi)
            await asyncio.sleep(0)

            file, file_name = manager.draw_map(server_id=ctx.guild.id,
                                            draw_moves=False,
                                            player=None,
                                            turn=board.turn,
                                            fow_player=player)
            await send_message_and_file(channel=channel,
                                        title=f"{prev_turn} Results Map",
                                        message=f"Here is the {prev_turn} results map for {player.name}",
                                        file=file,
                                        file_name=file_name,
                                        convert_svg=True,
                                        file_in_embed=False,
                                        dpi=dpi)
            await asyncio.sleep(0)

    @commands.command(
        brief="Sends fog of war orders",
    )
    @perms.gm_only("send fow order logs")
    async def publish_fow_order_logs(self, ctx: commands.Context):
        assert ctx.guild is not None
        player_category = None

        guild = ctx.guild
        guild_id = guild.id
        board = manager.get_board(guild_id)

        if board.data.get("fow", "disabled") != "enabled":
            raise ValueError("This is not a fog of war game")

        filter_player = board.get_player(remove_prefix(ctx))

        for category in guild.categories:
            if config.is_player_category(category):
                player_category = category
                break

        if not player_category:
            return "No player category found"

        name_to_player: dict[str, Player] = {}
        for player in board.get_players():
            name_to_player[player.name.lower()] = player

        for channel in player_category.channels:
            if not isinstance(channel, TextChannel):
                continue
            player = perms.get_player_by_channel(board, channel)

            if not player or (filter_player and player != filter_player):
                continue

            message = get_filtered_orders(board, player)

            await send_message_and_file(channel=channel, message=message)

        return "Successful"


async def setup(bot):
    cog = FogOfWarCog(bot)
    await bot.add_cog(cog)


# FIXME add a decorator / helper method for iterating over all player order channels
async def publish_map(
    ctx: commands.Context,
    manager: Manager,
    name: str,
    map_caller: Callable[[Manager, int, Player], tuple[bytes, str]],
    filter_player=None,
):
    assert ctx.guild is not None
    player_category = None

    guild = ctx.guild
    guild_id = guild.id
    board = manager.get_board(guild_id)

    for category in guild.categories:
        if config.is_player_category(category):
            player_category = category
            break

    if not player_category:
        # FIXME this shouldn't be an Error/this should propagate
        raise RuntimeError("No player category found")

    name_to_player: dict[str, Player] = {}
    for player in board.get_players():
        name_to_player[player.name.lower()] = player

    tasks = []

    for channel in player_category.channels:
        if not isinstance(channel, TextChannel):
            continue
        player = perms.get_player_by_channel(board, channel)

        if not player or (filter_player and player != filter_player):
            continue

        message = f"Here is the {name} for {board.turn}"
        # capture local of player
        tasks.append(
            map_publish_task(
                lambda player=player: map_caller(manager, guild_id, player),
                channel,
                message,
                dpi=board.data["svg config"].get("dpi", 200),
            )
        )

    await asyncio.gather(*tasks)


async def map_publish_task(map_maker, channel, message, dpi: int = 200):
    async with fow_export_limit:
        file, file_name = map_maker()
        await send_message_and_file(
            channel=channel,
            message=message,
            file=file,
            file_name=file_name,
            file_in_embed=False,
            convert_svg=True,
            dpi=dpi
        )
