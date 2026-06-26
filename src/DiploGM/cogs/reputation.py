"""Cog for managing user reputation."""

import logging

import discord
from discord.ext import commands

from DiploGM import config
from DiploGM.perms import is_moderator, mod_only
from DiploGM.services import reputation_service
from DiploGM.utils.send_message import send_message_and_file

logger = logging.getLogger(__name__)


class ReputationCog(commands.Cog):
    """Cog for managing user reputation."""

    def __init__(self, bot):
        self.bot = bot
        self.service = reputation_service

    @commands.group(name="rep")
    async def rep(self, ctx: commands.Context):
        """Base command for .rep without arguments."""
        await send_message_and_file(
            channel=ctx.channel,
            message="Valid commands are: *add*, *delete*, and *view*",
        )

    @rep.command(
        name="add",
        brief="Add a reputation delta",
        description="",
        help="Usage: .rep add <user> <hours> <reason>",
    )
    @mod_only("add a reputation delta")
    async def rep_add(
        self,
        ctx: commands.Context,
        user: discord.User,
        amount: int,
        *,
        reason: str = "unspecified",
    ):
        """Adds a reputation delta for a user."""
        delta = self.service.create_delta(user.id, amount, reason)

        out = f"ID: {delta.id}\nUser: {user.mention}\nChange: {amount}\n"
        await send_message_and_file(
            channel=ctx.channel, title="Reputation Logged!", message=out
        )

        current = self.service.get_user_value(user.id)
        if current > -10:
            return

        hub = self.bot.get_guild(config.HUB_SERVER_ID)
        if hub is None:
            await send_message_and_file(
                channel=ctx.channel,
                message=f"{user.name} is now below -10 reputation!",
                embed_colour=config.PARTIAL_ERROR_COLOUR,
            )
            return

        hub_member = hub.get_member(user.id)
        role = discord.utils.get(hub.roles, name="Under -10 Reputation")
        if hub_member is None or role is None:
            await send_message_and_file(
                channel=ctx.channel,
                message=f"{user.name} is now below -10 reputation!",
                embed_colour=config.PARTIAL_ERROR_COLOUR,
            )
            return

        hub_member.add_role(role)

    @rep.command(
        name="delete",
        brief="Delete a reputation delta",
        description="Provide a rep delta id to delete.",
        help="Usage: .rep delete <id>",
    )
    @mod_only("delete a reputation delta")
    async def rep_delete(self, ctx: commands.Context, delta_id: int):
        """Deletes a reputation delta by ID."""
        success = self.service.delete_delta(delta_id)

        if not success:
            await send_message_and_file(
                channel=ctx.channel,
                message=f"There is not a Delta with ID of {delta_id}",
                embed_colour=config.ERROR_COLOUR,
            )
            return
        await send_message_and_file(
            channel=ctx.channel,
            message=f"Deleted Reputation Delta with ID of {delta_id}",
        )

    @rep.command(
        name="view",
        brief="View a user's rep history",
        description="",
        help="Usage: .rep view <user> <history_check>\n"
        + "History check default = 'none', Moderators can use 'all' to fetch reasons",
    )
    async def rep_view(
        self, ctx: commands.Context, user: discord.User, history_check: str = "none"
    ):
        """Views a user's reputation history."""
        history = self.service.get_user_history(user.id)
        current = self.service.get_user_value(user.id)

        out = f"### Overall Value: {current}\n"
        for delta in history:
            out += f"({delta.id}): <t:{delta.created_at.timestamp()}:f>\n"
            out += f"- Change: {delta.delta}\n"
            if is_moderator(ctx.author) and history_check == "all":
                out += f"- Reason: {delta.reason}\n"

        await send_message_and_file(
            channel=ctx.channel, title=f"{user.name} reputation history", message=out
        )


async def setup(bot):
    """Setup function for the Reputation cog."""
    cog = ReputationCog(bot)
    await bot.add_cog(cog)
