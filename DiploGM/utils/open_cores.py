from typing import Optional

from discord.ext import commands

from DiploGM.models.board import Board
from DiploGM.models.player import Player, ViewOpenCoresTags
from DiploGM.models.province import Province
from DiploGM.utils.sanitise import find_discord_role


def get_open_cores(
    board: Board,
    player_restriction: Player | None,
) -> list[tuple[Player, tuple[Province, ...]]]:
    if player_restriction is None:
        players = board.players
    else: players = {player_restriction}

    response = []

    for player in sorted(players, key=lambda sort_player: sort_player.get_name()):
        if board.is_player_hidden(player):
            continue
        open_cores = []
        for center in player.centers:
            if center.core_data.core is player and center.unit is None:
                open_cores.append(center)
        if len(open_cores) > 0:
            response.append((player, tuple(open_cores)))
    
    return response

def get_open_core_text(
    ctx: commands.Context,
    board: Board,
    player_restriction: Player | None,
    tags: ViewOpenCoresTags,
) -> str:
    assert ctx.guild is not None

    response = []
    open_core_info_by_player = get_open_cores(board, player_restriction)
    for player, open_cores in open_core_info_by_player:

        if (player_role := find_discord_role(player, ctx.guild.roles)) is not None:
            player_name = player_role.mention
        else:
            player_name = player.get_name()

        response.append(f"{player_name} ({len(open_cores)})")
        if tags.blind:
            continue
        for open_core in open_cores:
            response.append(f"{open_core.name}")
    
    return "\n".join(response)
