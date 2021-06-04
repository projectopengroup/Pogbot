from discord.ext import commands


class Moderator(commands.Cog, name="Moderator"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Moderator(bot))
