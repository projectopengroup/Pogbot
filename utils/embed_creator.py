import discord


def create_embed(title, bot):
    embed_message = discord.Embed(
        title="**{}**".format(title),
        color=0x002244)

    embed_message.set_author(name="lvlBot",
                             icon_url=bot.user.avatar_url)

    return embed_message
