import discord
import traceback
import sys
from discord.ext import commands

from utils.pogfunctions import send_embed


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            errorsend = await send_embed(ctx, send_option=2,
                                         description=f"<:Pogbot_X:850089728018874368> "
                                                     f"{ctx.command} has been disabled.",
                                         color=0x08d5f7)
            await ctx.send(embed=errorsend)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                errorsend = await send_embed(ctx, send_option=2,
                                             description=f"<:Pogbot_X:850089728018874368> "
                                                         f"{ctx.command} can not be used in Direct Messages.",
                                             color=0x08d5f7)
                await ctx.author.send(embed=errorsend)
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                errorsend = await send_embed(ctx, send_option=2,
                                             description=f"<:Pogbot_X:850089728018874368> "
                                                         f"that member cannot be found. Try again.",
                                             color=0x08d5f7)
                await ctx.send(embed=errorsend)

        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
