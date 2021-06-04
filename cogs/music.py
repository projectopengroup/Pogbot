from discord.ext import commands


class Music(commands.Cog, name="Music Commands"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Music(bot))
