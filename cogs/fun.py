import aiohttp
import requests
from discord.ext import commands
from utils.pogfunctions import send_embed


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cat', aliases=['cats'], brief='Responds with a picture of a cat.',
                      description="Responds with a picture of a random cat.")
    # Look for a command called cat
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://thecatapi.com/api/images/get')
            url = request.url
        await send_embed(ctx, title="Cats", description='Random cat picture', image=f'{url}',
                         color=0x08d5f7)

    @commands.command(name='dog', aliases=['dogs'], brief='Responds with a picture of a dog.',
                      description="Responds with a picture of a random dog.")
    # Look for a command called cat
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://thedogapi.com/api/images/get')
            url = request.url
        await send_embed(ctx, title="Dogs", description='Random dog picture', image=f'{url}',
                         color=0x08d5f7)

    @commands.command(name='joke', aliases=['jokes'], brief='Tells a joke.', description='Tells a random joke.')
    # Look for a command called joke
    async def joke(self, ctx, joke_type="Any"):
        if "pro" in joke_type:
            joke_type = "Programming"
        else:
            joke_type = "Any"
        request = requests.get(url=f'https://v2.jokeapi.dev/joke/{joke_type}?blacklistFlags=political')
        joke = request.json()
        if "joke" in joke:
            await send_embed(ctx, title=str(joke["joke"]), color=0x08d5f7)
        else:
            await send_embed(ctx, title=str(joke["setup"]), description=str(joke["delivery"]), color=0x08d5f7)

    @commands.command(name='idea', aliases=['bored', 'activity'], brief='Suggests and activity.',
                      description="Suggests and activity for you to do when you're bored.")
    # Look for a command called activity
    async def idea(self, ctx):
        request = requests.get(url=f'https://www.boredapi.com/api/activity')
        activity = request.json()
        link = activity['link']
        if not link:
            print(activity['link'])
            await send_embed(ctx, title=str(activity['activity']),
                             color=0x08d5f7)
        else:
            print(activity['link'])
            await send_embed(ctx, title=str(activity['activity']), url=link,
                             color=0x08d5f7)


def setup(bot):
    bot.add_cog(Fun(bot))
