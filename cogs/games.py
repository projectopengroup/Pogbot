from discord.ext import commands


class Games(commands.Cog, name="Games Commands"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Games(bot))
