"""Game management commands related to grace."""
import logging
from typing import Optional
import discord
from discord.ext import commands
from DiploGM.config import ERROR_COLOUR
from DiploGM.utils import send_message_and_file
from DiploGM.services.extension import extension_service
from DiploGM.manager import Manager

logger = logging.getLogger(__name__)
manager = Manager()

async def grace_log(ctx: commands.Context, user: discord.User, hours: float, reason: str = "Unspecified") -> None:
    """Store a record of grace in a game"""
    assert ctx.guild is not None

    if user.bot:
        await send_message_and_file(channel=ctx.channel,
                                    message="Can't log grace for a bot",
                                    embed_colour=ERROR_COLOUR)
        return

    
    grace_id = extension_service.record_extension(user.id, ctx.guild.id, hours, reason)
    await send_message_and_file(channel=ctx.channel,
                                title=f"Grace (No. {grace_id}) logged!",
                                message=f"Logged under: {user.mention}\nHours: {hours}")

async def grace_delete(ctx: commands.Context, grace_id: int) -> None:
    """Delete a record of grace from the database"""
    extension_service.delete_extension(grace_id)
    await send_message_and_file(channel=ctx.channel,
                                message=f"If a grace with ID {grace_id} existed, it exists no longer :fire:")

async def grace_view_user(ctx: commands.Context, user: discord.User) -> None:
    """View the grace record for a specific user

    Usage: 
        `.grace view user <user>`

    Note: 
        Groups by server graces are logged in
        Records sorted by server_id (newer servers?) then creation datetime

    Args:
        user (discord.User): User to check
    """

    extensions = extension_service.view_user_extensions(user.id)

    out = ""
    if len(extensions) == 0:
        out = "No graces caused by this user!"
        await send_message_and_file(channel=ctx.channel, title=f"Graces caused by {user.name}", message=out)
        return

    for server_id, events in extensions.items():
        server = ctx.bot.get_guild(server_id)
        out += f"### For: {server.name or server_id}\n"

        for e in sorted(events, key=lambda e: e.created_at, reverse=True):
            out += (
                f"ID({e.id}):  {user.mention}\n"
                f"- Hours: {e.hours}\n"
                f"- Reason: {e.reason}\n"
                f"- Time: {e.created_at}\n"
            )

    await send_message_and_file(channel=ctx.channel, title=f"Graces caused by {user.name}", message=out)

async def grace_view_server(ctx: commands.Context, server_id: Optional[int] = None) -> None:
    """View the grace record for the current server"""
    assert ctx.guild is not None

    gid = ctx.guild.id
    gname = ctx.guild.name
    if server_id is not None:
        gid = server_id
        gname = ctx.bot.get_guild(server_id).name or gid

    extensions = extension_service.view_server_extensions(gid)

    out = ""
    if len(extensions) == 0:
        out = "No graces caused by this server!"
        await send_message_and_file(channel=ctx.channel, title=f"Graces caused by {gname}", message=out)
        return

    sorted_events = sorted(
        extensions.items(),
        key=lambda p: max(e.created_at for e in p[1]),
        reverse=True 
    )
    for user_id, events in sorted_events:
        user = ctx.bot.get_user(user_id)
        out += f"### For: {user.name}\n"

        for e in sorted(events, key=lambda e: e.created_at, reverse=True):
            out += (
                f"ID({e.id}) for {e.hours} hours\n"
                f"- Reason: {e.reason}\n"
                f"- Time: {e.created_at}\n"
            )
    
    await send_message_and_file(channel=ctx.channel, title=f"Graces caused by {gname}", message=out)
