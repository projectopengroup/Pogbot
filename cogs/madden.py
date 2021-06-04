from discord.ext import commands


class Madden(commands.Cog, name="Madden"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Madden(bot))
