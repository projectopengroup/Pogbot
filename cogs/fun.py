import aiohttp
import requests
import random
from discord.ext import commands
from utils.pogfunctions import send_embed


# https://github.com/public-apis/public-apis

class Fun(commands.Cog, name="Fun Stuff"):
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

    @commands.command(name='fox', aliases=['foxes'], brief='Responds with a picture of a fox.',
                      description="Responds with a picture of a random fox.")
    # Look for a command called cat
    async def fox(self, ctx):

        request = requests.get(url='https://randomfox.ca/floof/', headers={"Accept": "application/json"})
        fox = request.json()
        await send_embed(ctx, title="Foxes", description='Random fox picture', image=fox["image"],
                         color=0x08d5f7)

    @commands.command(name='joke', aliases=['jokes'], brief='Tells a joke.', description='Tells a random joke.')
    # Look for a command called joke
    async def joke(self, ctx, joke_type="Any"):
        # Chooses a random api. If the user specified a programming joke, then it only chooses randomly from the APIs
        # that have programming jokes (which are the first 2)
        if "pro" in joke_type:
            api_choice = random.randint(0, 1)
        else:
            api_choice = random.randint(0, 3)

        # Finds the chosen api, gets a random joke, and sends it.
        if api_choice == 0:
            if "pro" in joke_type:
                joke_type = "Programming"
            else:
                joke_type = "Any"
            request = requests.get(url=f'https://v2.jokeapi.dev/joke/{joke_type}?blacklistFlags=political,racist,sexist')
            joke = request.json()
            if "joke" in joke:
                await send_embed(ctx, description=str(joke["joke"]), color=0x08d5f7)
            else:
                await send_embed(ctx, title=str(joke["setup"]), description=str(joke["delivery"]), color=0x08d5f7)
        elif api_choice == 1:
            if "pro" in joke_type:
                request = requests.get(url='https://official-joke-api.appspot.com/jokes/programming/random')
                joke = request.json()
                await send_embed(ctx, title=str(joke[0]["setup"]), description=str(joke[0]["punchline"]), color=0x08d5f7)
            else:
                request = requests.get(url='https://official-joke-api.appspot.com/random_joke')
                joke = request.json()
                await send_embed(ctx, title=str(joke["setup"]), description=str(joke["punchline"]), color=0x08d5f7)
        elif api_choice == 2:
            request = requests.get(url='https://yomomma-api.herokuapp.com/jokes')
            joke = request.json()
            await send_embed(ctx, description=str(joke["joke"]), color=0x08d5f7)
        elif api_choice == 3:
            print("This one.")
            request = requests.get(url='https://icanhazdadjoke.com/', headers={"Accept": "application/json"})
            joke = request.json()
            await send_embed(ctx, description=str(joke["joke"]), color=0x08d5f7)

    @commands.command(name='idea', aliases=['bored', 'activity'], brief='Suggests an activity.',
                      description="Suggests an activity for you to do when you're bored.")
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

    @commands.command(name='spock', aliases=['sjoke', 'spockjoke', 'sjokes'], brief='Responds with a Spock Joke.',
                      description="Responds with a joke that pertains to Spock.")
    async def spock(self, ctx):
        spock = ["Spock had three ears: a left ear, a right ear, and a final front ear",
                 "What did Spock find in the toilet of the Enterprise? \n**The captain's log.**",
                 "What does Spock use as birth control? \n**Vulcanized Rubber.**",
                 "Why doesn't Spock give hand jobs? \n**Because his Vulcan grip will make you limp**",
                 "What do Captain Kirk and Mister Spock do to get their baggage up to their hotel room? \n**Tell a "
                 "porter.**",
                 "Why didn't Spock do a mind meld with Frodo? \n**Because he figured that would be a bad hobbit to "
                 "get in to.**",
                 "**Yo Mama's so fat, even Spock thought she outweighed the needs of the many!**",
                 "If the shocker don't rock her. \nSpock Her."]
        await send_embed(ctx, title=random.choice(spock), color=0x08d5f7)


def setup(bot):
    bot.add_cog(Fun(bot))
