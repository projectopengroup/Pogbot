import os
import platform
import re
import urllib

import discord
import requests
import operator
import subprocess
import gc
import json
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from discord.ext import commands
from utils.pogfunctions import send_embed, create_welcome_card, create_level_card, create_profile_card, check_xp
from utils.pogesquelle import get_prefix, get_db_item, check_snipes, decodebase64, check_user, get_db_user_item, \
    check_global_user, get_global_currency, set_global_currency
# from rembg.bg import remove
from urllib.request import Request, urlopen
from pathlib import Path
import numpy as np
from discord.ext.commands.cooldowns import BucketType
import io
from PIL import Image, ImageFont, ImageDraw
from PIL import ImageFile
from math import floor, ceil

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Counter(discord.ui.View):
    @discord.ui.button(label='0', style=discord.ButtonStyle.red)
    async def counter(self, button: discord.ui.Button, interaction: discord.Interaction):
        number = int(button.label)
        button.label = str(number + 1)
        if number + 1 >= 5:
            button.style = discord.ButtonStyle.green

        await interaction.message.edit(view=self)


class Commands(commands.Cog, name="Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='prefix', brief='Responds with the prefix.',
                      description="Responds with Pogbot's command prefix.")
    async def prefix(self, ctx):
        justprefix = await get_prefix(self.bot, ctx.message)
        await send_embed(ctx.message.channel, send_option=0, description=f"**The current prefix is {justprefix[2]}**",
                         color=0x08d5f7)

    @commands.command(name='counter', brief='Posts a button counter',
                      description="Posts a button counter.")
    async def counter(self, ctx):
        view = Counter()
        # add_option_embed = await send_embed(ctx, send_option=2, description=f"**Count with me**", color=0x08d5f7)
        # await ctx.send(embed=add_option_embed, view=view)
        await ctx.send('**Count with me**', view=view)

    @commands.command(name='ping', aliases=['latency'], brief='Responds with latency.',
                      description="Responds with Pogbot's latency.")
    # Look for a command called ping.
    async def ping(self, ctx):
        # Responds with the bots latency in a embed.
        embedping = discord.Embed(
            description=f"<:Check:845178458426179605> **Pogbot's latency is {round(self.bot.latency * 100)}ms**",
            color=0x08d5f7)
        # Edit the original message
        await ctx.send(embed=embedping)

    @commands.command(name='github', brief="Responds with github link.",
                      description="Responds with the link to Pogbot's github.")
    # Look for a command called github.
    async def github(self, ctx):
        # Sends the link to the bot github page when the github command is used.
        await ctx.send("https://github.com/projectopengroup/Pogbot")

    @commands.command(name='codeck', aliases=['deck'], brief='Responds with codeck link.',
                      description="Responds with the link to Pogbot's codeck.")
    # Look for a command called codeck.
    async def codeck(self, ctx):
        # Sends the link to the bot codeck page when the codeck command is used.
        await ctx.send("https://open.codecks.io/pog")

    @commands.command(name='echo', brief='Responds with the text provided.',
                      description="Replies with the same text argument that's provided by the user.")
    # Look for a command called echo
    async def echo(self, ctx, *, text_to_echo):
        # Send an echo of the keyword-only argument.
        await ctx.send(text_to_echo)

    @commands.command(name='icon', brief="Responds with Pogbot's avatar.", description="Responds with Pogbot's avatar.")
    # Look for a command called icon.
    async def icon(self, ctx):
        # Send pogbot icon
        await ctx.send(self.bot.user.avatar.url)

    @commands.command(name='avatar', aliases=['av', 'pfp'], brief='Responds with an avatar.',
                      description="Responds with the avatar of a user provided, if none provided, responds with the "
                                  "avatar of the user that called the command.")
    # Look for a command called avatar and collects optional user parameter, so if no user given, user = None.
    async def avatar(self, ctx, *, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author
        # Defining pfp from user's avatar_url.
        pfp = user.avatar.url

        await send_embed(ctx, title=f'**{user}**', description='**Avatar**', color=0x08d5f7, image=pfp)

    @commands.command(name='userid', aliases=['id', 'uid'], brief='Responds with a users ID.',
                      description="Responds with the ID of a user provided, if none provided, responds with the"
                                  " ID of the user that called the command.")
    # Look for a command called userid and collects optional user parameter, so if no user given, user = None.
    async def userid(self, ctx, *, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author
        # Creates a discord embed with the elements: title (Which gets the user's tag),
        # description (Which gets the user's id), and color (which is the bot's color).
        await send_embed(ctx, author=f"{user}'s ID", author_pfp=user.avatar.url, description=f'**{user.id}**',
                         color=0x08d5f7)

    @commands.command(name='botinfo', aliases=['binfo'], brief='Responds with information about the bot.',
                      description="Responds with information about the bot and it's hosting environment.")
    async def botinfo(self, ctx):
        await send_embed(ctx, title=f"**Pogbot's Info**", thumbnail=self.bot.user.avatar.url,
                         fields=[(f'**Python Version:**', platform.python_version(), True),
                                 (f'**Operating System:**', platform.system(), True),
                                 (f'**OS Version:**', platform.release(), True),
                                 (f'**OS Details:**', platform.platform(), True),
                                 (f'**Created by:**',
                                  "[Project Open Group, a community project.](https://github.com/projectopengroup)",
                                  True),
                                 (f'**Pogbot is:**',
                                  "[Open Source](https://github.com/projectopengroup/pogbot)", True)],
                         color=0x08d5f7)

    @commands.command(name='serverinfo', aliases=['sinfo'], brief='Responds with information about the discord server.',
                      description="Responds with information about the discord server it's ran in.")
    async def serverinfo(self, ctx):
        server = ctx.message.guild
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        list_of_bots = [bot.mention for bot in server.members if bot.bot]

        await send_embed(ctx, title=f"**{server} Info**", thumbnail=server.icon.url,
                         fields=[(f'**Server Owner**', f"{server.owner}", True),
                                 (f'**Owner ID:**', server.owner.id, True),
                                 (f'**Server ID:**', server.id, True),
                                 (f'**Highest Role:**', server.roles[-2], True),
                                 (f'**Member Count:**', server.member_count, True),
                                 (f'**Channel Count:**', len(server.channels), True),
                                 (f'**Role Count**', len(server.roles), True),
                                 (f'**Bots**',
                                  str(list_of_bots).replace("'", "").replace(']', '').replace('[', ''), True),
                                 (f'**Region**', len(server.region), True),
                                 (f'**Verification Level**', len(server.verification_level), True),
                                 (f'**Bot Count**', len(list_of_bots), True),
                                 (f'**Created:**', time, True)],
                         color=0x08d5f7)

    @commands.command(name='whois', aliases=['userinfo', 'uinfo'], brief='Responds with information on a user.',
                      description="Responds with the information of a user provided, if none provided, responds "
                                  "with the information of the user that called the command.")
    # Look for a command called whois and collects optional user parameter, so if no user given, user = None.
    async def whois(self, ctx, *, user: discord.User = None):
        if user is None:
            user = ctx.author

        isMember = ctx.guild.get_member(user.id)
        if isMember is not None:
            user = ctx.guild.get_member(user.id)

        # Checks if the user is a bot and stores it in a variable
        isBot = "No"
        if user.bot:
            isBot = "Yes"

        # Checks if the user has a nickname set by taking the username, removing the # and numbers, and comparing it
        # with the display name.
        usernameFull = str(user)
        username, usertag = usernameFull.split("#")
        nickname = user.display_name
        if username == nickname:
            nickname = "None"
        try:
            # Get's user's status
            userStatus = str(user.status).title()
            if userStatus == "Dnd":
                userStatus = "Do not disturb"
        except AttributeError:
            userStatus = "None"

        # Gets user's roles, excludes the @everyone role, and puts it in a string
        foundRoles = []
        try:
            for role in user.roles:
                if role.name != "@everyone":
                    foundRoles.append(role.mention)
        except AttributeError:
            foundRoles.append("None")

        foundRoles.reverse()
        userRoles = " ".join(foundRoles)

        try:
            userJoined = str(user.joined_at.strftime("%b %d, %Y"))
        except AttributeError:
            userJoined = "Not in server."

        # Creates and sends an embed with various user info by adding them as fields. When getting dates, the format
        # as to be converted so that it is easier to read.
        await send_embed(ctx, author=f"{username}", author_pfp=user.avatar.url, thumbnail=user.avatar.url,
                         fields=[(f'**Username:**', usernameFull, True), (f'**Nickname:**', nickname, True),
                                 (f'**User ID:**', str(user.id), True),
                                 (f'**Registered:**', str(user.created_at.strftime("%b %d, %Y")), True),
                                 (f'**Joined Server:**', userJoined, True),
                                 (f'**Is Bot:**', isBot, True),
                                 (f'**Status:**', userStatus, True),
                                 (f'**Roles:**', userRoles, True)],
                         color=0x08d5f7)

    @commands.command(name='qr', brief='Responds with a QR code.',
                      description="Responds with a QR code of the data provided.")
    async def qr(self, ctx, *, text_or_url):
        # Send an echo of the keyword-only argument.
        request = requests.get(url=f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text_or_url}')
        await ctx.send(request.url)

    @commands.command(name='contributors', aliases=['contrib', 'contribs'],
                      brief='Responds with a list of contributors.',
                      description="Responds with a full list of project contributors.")
    async def contributors(self, ctx):
        contribs = "__**Leads**: Mag#7777, h3resjonny#0741, TheOneCheetah#3764, and Stu__\n \n" \
                   "**TG#5287** -> Graphics contributions. POG logo, Pogbot logo, welcome graphic. \n " \
                   "**Mag#7777** -> Developer. Foundational code contributions. \n **TheOneCheetah#3764** -> " \
                   "Developer. Foundational code contributions. \n **DJ DeHao#4627** -> Coder. Code contributions. (" \
                   "avatar command). \n **Panda Gummies#2155** -> Coder. Code contributions. (echo command). \n " \
                   "**ravenig#8429** -> Coder. Code contributions. (main check and run.sh). \n **Jaycon#4073** -> " \
                   "Coder. Code contributions. (icon command). "
        await send_embed(ctx, title="**Pogbot's Contributors**", description=contribs, color=0x08d5f7)

    @commands.command(name='covid', aliases=['coviddata', 'covid19', 'coronavirus', 'covid19data'],
                      brief='Responds with covid data.',
                      decription='Responds with covid data based on specified country.')
    async def covid(self, ctx, *, country=None):
        possible_us = ["us", "usa", "u.s", "u.s.", "u.s.a", "u.s.a.", "united states", "unitedstates", "united-states",
                       "united states of america", "unitedstatesofamerica", "united-states-of-america"]
        possible_uk = ["uk", "u.k", "u.k.", "united kingdom", "unitedkingdom", "united-kingdom"]
        possible_skorea = ["s. korea", "s.korea", "south korea", "southkorea"]

        if country is None:
            country = "World"
        elif country.lower() in possible_us:
            country = "usa"
        elif country.lower() in possible_uk:
            country = "uk"
        elif country.lower() in possible_skorea:
            country = "s. korea"

        request1 = requests.get(url=f'https://www.worldometers.info/coronavirus/#main_table')
        request2 = requests.get(url=f'https://www.worldometers.info/coronavirus/weekly-trends/#weekly_table')
        soup1 = BeautifulSoup(request1.text, 'html.parser')
        soup2 = BeautifulSoup(request2.text, 'html.parser')

        covid_data = soup1.find_all(id="main_table_countries_today")
        covid_change = soup2.find_all(id="main_table_countries_today")

        selected_country = None
        iter = 0
        for countries in covid_data[0].find_all('tr'):
            iter += 1
            if iter >= 9:
                data = countries.find_all('td')
                for value in range(0, len(data)):
                    data[value] = data[value].get_text()
                    if data[value] == '':
                        data[value] = 'N/A'
                if country.lower() == data[1].lower():
                    selected_country = {'Country': data[1], 'Total Cases': data[2], 'New Cases': data[3],
                                        'Total Deaths': data[4],
                                        'New Deaths': data[5], 'Total Recovered': data[6], 'Active Cases': data[8],
                                        'Critical Cases': data[9]}
                    break
        if selected_country is not None:
            iter = 0
            for countries in covid_change[0].find_all('tr'):
                iter += 1
                if iter >= 9:
                    data = countries.find_all('td')
                    if data[1].get_text() == selected_country['Country']:
                        selected_country['Case Change'] = data[4].get_text()
                        selected_country['Death Change'] = data[8].get_text()
            await send_embed(ctx, title=f"{selected_country['Country']} Covid-19 Statistics", color=0x08d5f7,
                             fields=[(f"**Total Cases:**", selected_country["Total Cases"], True),
                                     (f"**New Cases:**", selected_country["New Cases"], True),
                                     (f"**Weekly Change:**", selected_country["Case Change"], True),
                                     (f"**Total Recovered:**", selected_country["Total Recovered"], True),
                                     (f"**Active Cases:**", selected_country["Active Cases"], True),
                                     (f"**Critical Cases:**", selected_country["Critical Cases"], True),
                                     (f"**Total Deaths:**", selected_country["Total Deaths"], True),
                                     (f"**New Deaths:**", selected_country["New Deaths"], True),
                                     (f"**Weekly Change:**", selected_country["Death Change"], True)],
                             footer="Data via worldometers.info", thumbnail="https://i.imgur.com/kYANkld.jpg")
        else:
            await send_embed(ctx, description="<:Pogbot_X:850089728018874368> **Country Not Found**", color=0x08d5f7)

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        check_snipes(ctx.author.guild.id)
        Message = get_db_item(ctx.author.guild.id, "snipes", "Message")
        MessageID = get_db_item(ctx.author.guild.id, "snipes", "MessageID")
        Author = get_db_item(ctx.author.guild.id, "snipes", "Author")
        AuthorAvatar = get_db_item(ctx.author.guild.id, "snipes", "AuthorAvatar")
        TimeStamp = get_db_item(ctx.author.guild.id, "snipes", "Timestamp")

        Author = decodebase64(Author)
        Message = decodebase64(Message)

        if Message != "None":
            await send_embed(ctx, author=f"{Author}", author_pfp=AuthorAvatar,
                             description=Message,
                             color=0x08d5f7,
                             timestamp=datetime.strptime(TimeStamp, '%Y-%m-%d %H:%M:%S.%f'),
                             footer=f"Message ID: {MessageID}\nDeleted")

    @commands.command(name="createpoll", aliases=['newpoll', 'poll', 'makepoll'],
                      brief='Creates a poll.',
                      description="Creates a poll embed that members can vote on by reacting to the message.")
    async def createpoll(self, ctx):
        createpoll_desc_str = "React with the emotes to perform the desired actions.\n " \
                              "\n<:OptionA:854536640625508393>" \
                              " Edit Title\n<:OptionB:854536641519812618> Add Option (Max 10 options)\n" \
                              "<:OptionC:854536641867415572> Finish\n"

        cp_embed = await send_embed(ctx, send_option=1, title="<:PollIcon:854536641849589780> **Create Poll**",
                                    description=createpoll_desc_str,
                                    color=0x08d5f7)

        def reaction_check(reaction, user):
            return reaction.message.id == cp_embed.id and user.id == ctx.author.id

        def checkAuthor(message):
            return message.author.id == ctx.author.id and message.guild.id == ctx.guild.id

        await cp_embed.add_reaction('<:OptionA:854536640625508393>')
        await cp_embed.add_reaction('<:OptionB:854536641519812618>')
        await cp_embed.add_reaction('<:OptionC:854536641867415572>')

        poll_options = []
        poll_title = "No Title"

        while True:
            if len(poll_options) < 10:
                greaction, guser = await self.bot.wait_for('reaction_add', timeout=60, check=reaction_check)
                try:
                    await greaction.remove(guser)
                except discord.Forbidden:
                    print("[Error]: MissingPermissions: Unable to remove reaction")
                if str(greaction.emoji) == "<:OptionA:854536640625508393>":
                    add_option_embed = await send_embed(ctx, send_option=2,
                                                        title="<:PollIcon:854536641849589780> **Create Poll**",
                                                        description="**Edit poll title**\n"
                                                                    "Respond with the new poll title", color=0x08d5f7)
                    await cp_embed.edit(embed=add_option_embed)
                    new_title = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                    try:
                        await new_title.delete()
                    except discord.Forbidden:
                        print("[Error]: MissingPermissions: Unable to delete message")
                    poll_title = new_title.content
                elif str(greaction.emoji) == "<:OptionB:854536641519812618>":
                    add_option_embed = await send_embed(ctx, send_option=2,
                                                        title="<:PollIcon:854536641849589780> **Create Poll**",
                                                        description="**Add a new poll option**\n"
                                                                    "Respond with the option text", color=0x08d5f7)
                    await cp_embed.edit(embed=add_option_embed)
                    option = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                    try:
                        await option.delete()
                    except discord.Forbidden:
                        print("[Error]: MissingPermissions: Unable to delete message")
                    poll_options.append(option.content)
                elif str(greaction.emoji) == "<:OptionC:854536641867415572>":
                    break
                menu_embed = await send_embed(ctx, send_option=2,
                                              title="<:PollIcon:854536641849589780> **Create Poll**",
                                              description=createpoll_desc_str + f" \n`Added options: {len(poll_options)}`",
                                              color=0x08d5f7)
                await cp_embed.edit(embed=menu_embed)
            else:
                break

        option_emotes = ["<:OptionA:854536640625508393>", "<:OptionB:854536641519812618>",
                         "<:OptionC:854536641867415572>", "<:OptionD:854541014059581500>",
                         "<:OptionE:854541014240460820>", "<:OptionF:854541014668935188>",
                         "<:OptionG:854541014945234944>", "<:OptionH:854541017109233694>",
                         "<:OptionI:854541014580461570>", "<:OptionJ:854541014815735809>"]
        poll_string = ""
        for p_option in range(0, len(poll_options)):
            poll_string += option_emotes[p_option] + " " + poll_options[p_option] + "\n"

        await cp_embed.delete()
        poll_embed = await send_embed(ctx, send_option=1, title="<:PollIcon:854536641849589780> " + poll_title,
                                      description=poll_string, color=0x08d5f7)
        for p_option in range(0, len(poll_options)):
            await poll_embed.add_reaction(option_emotes[p_option])

    @commands.command(name="level", aliases=['rank'], brief='Displays level card.', description="Displays your level "
                                                                                                "card and rank.")
    async def level(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await check_xp(ctx)
        # Gets the user's xp in the server
        userxp = get_db_user_item(ctx.guild.id, user.id, "XP")

        # Gets the user's level in the server
        userlvl = get_db_user_item(ctx.guild.id, user.id, "Level")

        MemberList = []
        for member in ctx.guild.members:
            MemberList.append([member.id, get_db_user_item(ctx.guild.id, member.id, "Level"),
                               get_db_user_item(ctx.guild.id, member.id, "XP")])

        sorted_member_list = sorted(MemberList, key=operator.itemgetter(1, 2))
        sorted_member_list.reverse()
        x = 0
        for i in sorted_member_list:
            x = x + 1
            if i[0] == user.id:
                rank = x

        # Gets the time when the user can earn xp again (A person can only earn xp once a minute)
        xp_lvl_up = round(125 * (((int(userlvl) + 1) / 1.20) ** 1.20))
        avatarRequest = (requests.get(user.avatar.url)).content
        # Testing create welcome card on message send right now, until we get it done.
        await ctx.send(file=create_level_card(avatarRequest, user, ctx.guild, userxp, xp_lvl_up, userlvl, rank))

    @commands.command(name='olympics', aliases=['olympicgames', 'medals', 'medalcount'],
                      brief='Responds with the medal counts.',
                      decription='Responds with the medal counts for each country for the olympic games. ')
    async def olympics(self, ctx, page=1):
        request = requests.get(url=f'https://www.cbssports.com/olympics/news/medal-count-tokyo-2021-olympics/')
        soup = BeautifulSoup(request.text, 'html.parser')
        medal_table = soup.find_all('table')
        medal_data = medal_table[0].find_all('td')
        flag_emotes = {
            "united states": "<:unitedstates:868871032189108256>",
            "ukraine": "<:ukraine:868871032411402291>",
            "turkey": "<:turkey:868871032289783869>",
            "tunisia": "<:tunisia:868871032289779763>",
            "thailand": "<:thailand:868871032411402292>",
            "switzerland": "<:switzerland:868871032239452232>",
            "spain": "<:spain:868871032419790868>",
            "south korea": "<:southkorea:868871032172322857>",
            "slovenia": "<:slovenia:868871032176513026>",
            "serbia": "<:serbia:868871032373674006>",
            "russian olympic committee": "<:russianolympiccommittee:868871032184918079>",
            "romania": "<:romania:868871032193306645>",
            "puerto rico": "<:puertorico:868871032184930316>",
            "norway": "<:norway:868871032184930317>",
            "north korea": "<:northkorea:868871032130371627>",
            "nigeria": "<:nigeria:868871032218452000>",
            "new zealand": "<:newzealand:868871032407203890>",
            "netherlands": "<:netherlands:868871032201707592>",
            "mongolia": "<:mongolia:868871032373661746>",
            "mexico": "<:mexico:868871032239452231>",
            "kosovo": "<:kosovo:868871032046506087>",
            "kazakhstan": "<:kazakhstan:868871032474333256>",
            "japan": "<:japan:868871032474333255>",
            "jamaica": "<:jamaica:868871032319131698>",
            "italy": "<:italy:868871032176513025>",
            "israel": "<:israel:868871032147153007>",
            "ireland": "<:ireland:868871032130371625>",
            "iran": "<:iran:868871032159731732>",
            "indonesia": "<:indonesia:868871032046506085>",
            "india": "<:india:868871032184918077>",
            "hungary": "<:hungary:868871032130371624>",
            "greece": "<:greece:868871032189116467>",
            "great britain": "<:greatbritain:868871032147153006>",
            "germany": "<:germany:868871032134582292>",
            "georgia": "<:georgia:868871032189116466>",
            "france": "<:france:868871031874531340>",
            "finland": "<:finland:868871032289783868>",
            "estonia": "<:estonia:868871032239452230>",
            "ecuador": "<:ecuador:868871032218460190>",
            "denmark": "<:denmark:868871032172322856>",
            "chinese taipei": "<:chinesetaipei:868871032189108254>",
            "china": "<:china:868871032176513024>",
            "canada": "<:canada:868871032193306644>",
            "bulgaria": "<:bulgaria:868871032042291211>",
            "brazil": "<:brazil:868871032285589534>",
            "belgium": "<:belgium:868871032218451999>",
            "austria": "<:austria:868871032201707591>",
            "australia": "<:australia:868871032310726726>",
            "argentina": "<:argentina:868871032289779762>",
            "algeria": "<:algeria:868871032373674005>"
        }

        for i in range(0, len(medal_data)):
            medal_data[i] = medal_data[i].get_text()
            medal_data[i] = medal_data[i].replace("\t", "")
            medal_data[i] = "".join(medal_data[i].rstrip())

        medal_fields = []

        for i in range(1, int(len(medal_data) / 6)):
            medal_fields.append(
                (medal_data[i * 6 + 1], medal_data[i * 6 + 2], medal_data[i * 6 + 3], medal_data[i * 6 + 4],
                 medal_data[i * 6 + 5]))

        olymp_embed = discord.Embed(colour=0x08d5f7, title="**Olympic Games Medal Counts**")
        olymp_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/732409264907485185/868531514244202527"
                                      "/unknown.png")
        olymp_embed.set_footer(text="Ranked based on most golds")
        for i in range((page - 1) * 10, page * 10):
            if medal_fields[i][0].lower() in flag_emotes:
                olymp_embed.add_field(name=f"{flag_emotes[medal_fields[i][0].lower()]} **{medal_fields[i][0]}**",
                                      value=f":first_place: `{medal_fields[i][1]}` :second_place: `{medal_fields[i][2]}` "
                                            f":third_place: `{medal_fields[i][3]}`\nTotal: `{medal_fields[i][4]}`")
            else:
                olymp_embed.add_field(name=f"**{medal_fields[i][0]}**",
                                      value=f":first_place: `{medal_fields[i][1]}` :second_place: `{medal_fields[i][2]}` "
                                            f":third_place: `{medal_fields[i][3]}`\nTotal: `{medal_fields[i][4]}`")

        await ctx.send(embed=olymp_embed)

    @commands.command(name="profile", brief='Displays user profile.',
                      description="Displays the user information like level, coin balance, etc.")
    async def profile(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await check_xp(ctx)
        # Gets the user's xp in the server
        userxp = get_db_user_item(ctx.guild.id, user.id, "XP")

        # Gets the user's level in the server
        userlvl = get_db_user_item(ctx.guild.id, user.id, "Level")

        MemberList = []
        for member in ctx.guild.members:
            MemberList.append([member.id, get_db_user_item(ctx.guild.id, member.id, "Level"),
                               get_db_user_item(ctx.guild.id, member.id, "XP")])

        sorted_member_list = sorted(MemberList, key=operator.itemgetter(1, 2))
        sorted_member_list.reverse()
        x = 0
        for i in sorted_member_list:
            x = x + 1
            if i[0] == user.id:
                rank = x

        # Gets the time when the user can earn xp again (A person can only earn xp once a minute)
        xp_lvl_up = round(125 * (((int(userlvl) + 1) / 1.20) ** 1.20))
        avatarRequest = (requests.get(user.avatar.url)).content
        # Testing create welcome card on message send right now, until we get it done.
        await ctx.send(file=create_profile_card(avatarRequest, user, ctx.guild, userxp, xp_lvl_up, userlvl, rank))

    @commands.command(name="leaderboard", aliases=['lb', 'rankings'], brief="Displays the server's leaderboard.",
                      description="Displays the server's leaderboard which is ranked by level.")
    async def leaderboard(self, ctx, page=1):
        if page < 1:
            page = 1
        await check_xp(ctx)

        MemberList = []
        for member in ctx.guild.members:
            MemberList.append([member.id, get_db_user_item(ctx.guild.id, member.id, "Level"),
                               get_db_user_item(ctx.guild.id, member.id, "XP")])

        sorted_member_list = sorted(MemberList, key=operator.itemgetter(1, 2))
        sorted_member_list.reverse()

        x = 0
        user_rank = None
        user_xp = None
        user_level = None
        for i in sorted_member_list:
            x = x + 1
            if i[0] == ctx.author.id:
                user_rank = x
                user_level = i[1]
                user_xp = i[2]

        top_ten_list = []
        for int in range((page-1)*10, page*10):
            try:
                top_ten_list.append(sorted_member_list[int])
            except IndexError:
                pass


        welcomecardfolder = Path("img/card_welcomes/")

        base_layer = Image.open(welcomecardfolder / "leaderboard_baselayer.png")
        top_layer = Image.open(welcomecardfolder / "leaderboard_toplayer.png")

        compiled = base_layer.copy()
        guild_icon_layer = Image.open(io.BytesIO((requests.get(ctx.guild.icon)).content)).convert("RGBA")
        guild_icon_layer = guild_icon_layer.resize((85, 85), Image.ANTIALIAS)
        compiled.paste(guild_icon_layer, (49, 13), mask=guild_icon_layer)

        server_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 44)
        level_txt_font = ImageFont.truetype("fonts/Vegur-Light.otf", 18)
        level_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 24)
        rank_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 30)
        username_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 22)
        you_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 18)

        draw = ImageDraw.Draw(top_layer)
        draw.text((160, 11), f"{ctx.guild}", (255, 255, 255), font=server_font)

        iter = 0
        for user in top_ten_list:
            user_obj = await self.bot.fetch_user(user[0])
            user_avatar_layer = Image.open(io.BytesIO((requests.get(user_obj.avatar.url)).content)).convert("RGBA")
            user_avatar_layer = user_avatar_layer.resize((39, 39), Image.ANTIALIAS)
            compiled.paste(user_avatar_layer, (33, 115 + 58 * iter), mask=user_avatar_layer)

            if len(str(user_obj)) > 24:
                UserSplit = str(user_obj).upper()
                UserSplit = UserSplit.split('#')
                UserFormatted = UserSplit[0]
                UserFormatted = UserFormatted[0:19] + "...#" + UserSplit[1]
            else:
                UserFormatted = str(user_obj).upper()

            if (page-1)*10+1+iter == user_rank:
                draw.text((505, 123 + 58 * iter), f"(YOU)", (255, 255, 255), font=you_font)
            draw.text((80, 115 + 58 * iter), f"LEVEL", (255, 255, 255), font=level_txt_font)
            draw.text((80, 130 + 58 * iter), f"{user[1]}", (255, 255, 255), font=level_font)
            draw.text((143, 117 + 58 * iter), f"#{(page-1)*10+1+iter}", (255, 255, 255), font=rank_font)
            draw.text((228, 120 + 58 * iter), f"{UserFormatted}", (255, 255, 255), font=username_font)

            color = 98, 211, 245
            x = 226
            y = 151 + 58 * iter
            h = 3
            w = 318
            xp_lvl_up = round(125 * (((user[1] + 1) / 1.20) ** 1.20))
            progress = w * (float(user[2]) / float(xp_lvl_up))
            w = progress
            draw.ellipse((x + w, y, x + h + w, y + h), fill=color)
            draw.ellipse((x, y, x + h, y + h), fill=color)
            draw.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=color)

            iter += 1

        user_avatar_layer = Image.open(io.BytesIO((requests.get(ctx.author.avatar.url)).content)).convert("RGBA")
        user_avatar_layer = user_avatar_layer.resize((39, 39), Image.ANTIALIAS)
        compiled.paste(user_avatar_layer, (33, 115 + 58 * 11-1), mask=user_avatar_layer)

        if len(str(ctx.author)) > 24:
            UserSplit = str(ctx.author).upper()
            UserSplit = UserSplit.split('#')
            UserFormatted = UserSplit[0]
            UserFormatted = UserFormatted[0:19] + "...#" + UserSplit[1]
        else:
            UserFormatted = str(ctx.author).upper()

        draw.text((50, 81 + 58 * 11-1), f"YOUR RANK", (255, 255, 255), font=username_font)
        draw.text((80, 115 + 58 * 11-1), f"LEVEL", (255, 255, 255), font=level_txt_font)
        draw.text((80, 130 + 58 * 11-1), f"{user_level}", (255, 255, 255), font=level_font)
        draw.text((143, 117 + 58 * 11-1), f"#{user_rank}", (255, 255, 255), font=rank_font)
        draw.text((228, 120 + 58 * 11-1), f"{UserFormatted}", (255, 255, 255), font=username_font)

        color = 98, 211, 245
        x = 226
        y = 151 + 58 * 11 -1
        h = 3
        w = 318
        xp_lvl_up = round(125 * (((user_level + 1) / 1.20) ** 1.20))
        progress = w * (float(user_xp) / float(xp_lvl_up))
        w = progress
        draw.ellipse((x + w, y, x + h + w, y + h), fill=color)
        draw.ellipse((x, y, x + h, y + h), fill=color)
        draw.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=color)

        compiled.paste(top_layer, (0, 0), mask=top_layer)

        # set a var to arr that represents bytes.
        arr = io.BytesIO()
        # Save our compiled image in PNG format as bytes
        compiled.save(arr, format='PNG')
        # Set the byte stream position to 0.
        arr.seek(0)
        # Set a file var to a file discord understands, using our bytes, with a filename of "WelcomeCard.png"
        await ctx.send(file=discord.File(fp=arr, filename=f'Leaderboard.PNG'))

    @commands.command(name="pay", aliases=["give", "gift"], brief='Pays a user coins.',
                      description="Pays the specified user the specified amount of coins.")
    async def pay(self, ctx, user: discord.Member, amount):
        author_currency = get_global_currency(ctx.author.id)
        try:
            amount = int(amount)
        except ValueError:
            await send_embed(ctx, author="Invalid Amount", description="<:Pogbot_X:850089728018874368> "
                                                                       "That is not a valid amount.",
                             color=0x08d5f7)
            return
        if amount > author_currency:
            await send_embed(ctx, author="Insufficient Funds", description="<:Pogbot_X:850089728018874368> "
                                                                           "You do not have enough "
                                                                           "<:PogCoin:870094422233215007> Pog Coins to "
                                                                           "pay that amount.",
                             color=0x08d5f7)
            return
        set_global_currency(ctx.author.id, author_currency - amount)

        recipient_currency = get_global_currency(user.id)
        set_global_currency(user.id, recipient_currency + amount)

        await send_embed(ctx, author="Successful Payment",
                         description=f"{ctx.author.mention} paid {user.mention} <:PogCoin:870094422233215007> {amount} "
                                     f"Pog Coins.", color=0x08d5f7)

    @commands.command(name="schedule", brief="Displays the NFL schedule.",
                      description="Displays the NFL schedule for the current week.")
    async def schedule(self, ctx):
        rliveGameData = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard")
        liveGameData = json.loads(rliveGameData.text)

        teamDict = {"Minnesota Vikings": ["<:vikings:771799797769175080>", "Vikings", 32],
                    "Tennessee Titans": ["<:titans:771799797837463552>", "Titans", 31],
                    "Houston Texans": ["<:texans:771799797828026428>", "Texans", 30],
                    "Pittsburgh Steelers": ["<:steelers:771799797434548225>", "Steelers", 29],
                    "Seattle Seahawks": ["<:seahawks:771799797458796604>", "Seahawks", 28],
                    "New Orleans Saints": ["<:saints:771799797790408714>", "Saints", 27],
                    "Baltimore Ravens": ["<:ravens:771800517805735938>", "Ravens", 26],
                    "Los Angeles Rams": ["<:rams:771799797605859358>", "Rams", 25],
                    "Las Vegas Raiders": ["<:raiders:771799797858041877>", "Raiders", 24],
                    "New England Patriots": ["<:patriots:771799796725710880>", "Patriots", 23],
                    "Carolina Panthers": ["<:panthers:771799797480292412>", "Panthers", 22],
                    "Green Bay Packers": ["<:packers:771799797698920478>", "Packers", 21],
                    "Detroit Lions": ["<:lions:771799797757116418>", "Lions", 20],
                    "New York Jets": ["<:jets:771799797715566632>", "Jets", 19],
                    "Jacksonville Jaguars": ["<:jags:771799797501263914>", "Jaguars", 18],
                    "New York Giants": ["<:giants:771799797187084358>", "Giants", 17],
                    "Washington": ["<:footballteam:771799797094809662>", "Football Team", 16],
                    "Atlanta Falcons": ["<:falcons:771799797413183570>", "Falcons", 15],
                    "Philadelphia Eagles": ["<:eagles:771799797371633694>", "Eagles", 14],
                    "Miami Dolphins": ["<:dolphins:771799797353938954>", "Dolphins", 13],
                    "Dallas Cowboys": ["<:cowboys:771799797504933909>", "Cowboys", 12],
                    "Indianapolis Colts": ["<:colts:771799797702721536>", "Colts", 11],
                    "Kansas City Chiefs": ["<:chiefs:771799796712734751>", "Chiefs", 10],
                    "Los Angeles Chargers": ["<:chargers:771799796784562197>", "Chargers", 9],
                    "Arizona Cardinals": ["<:cardinals:771799796662534156>", "Cardinals", 8],
                    "Tampa Bay Buccaneers": ["<:buccaneers:771799796717060126>", "Buccaneers", 7],
                    "Cleveland Browns": ["<:browns:771799797001617428>", "Browns", 6],
                    "Denver Broncos": ["<:broncos:771799795999834113>", "Broncos", 5],
                    "Buffalo Bills": ["<:bills:771799794137169970>", "Bills", 4],
                    "Cincinnati Bengals": ["<:bengals:771799793915134012>", "Bengals", 3],
                    "Chicago Bears": ["<:bears:771799793726521415>", "Bears", 2],
                    "San Francisco 49ers": ["<:49ers:771799793553899521>", "49ers", 1]}

        welcomecardfolder = Path("img/card_welcomes/")

        compiled = Image.open(welcomecardfolder / "nflschedule_toplayer.png")
        side_bars = Image.open(welcomecardfolder / "game_sidebars.png")
        team_logos = Image.open(welcomecardfolder / "nflteamlogos.png")
        draw = ImageDraw.Draw(compiled)
        week_txt_font = ImageFont.truetype("fonts/gadugi-bold.ttf", 48)

        week_label = liveGameData["leagues"][0]["season"]["type"]["name"]
        week_num = liveGameData["week"]["number"]
        if week_label == "Preseason":
            draw.text((408, 147), f"PRESEASON", (255, 255, 255), font=week_txt_font)
            draw.text((325, 183), f"WEEK {week_num} SCHEDULE", (255, 255, 255), font=week_txt_font)
        else:
            draw.text((325, 152), f"WEEK {week_num} SCHEDULE", (255, 255, 255), font=week_txt_font)

        num_games = 0
        schedule_str = ""
        for game in liveGameData["events"]:
            at_txt_font = ImageFont.truetype("fonts/gadugi-bold.ttf", 31)
            date_txt_font = ImageFont.truetype("fonts/gadugi-bold.ttf", 20)
            odds_txt_font = ImageFont.truetype("fonts/gadugi-bold.ttf", 16)

            new_bars = side_bars.copy()
            compiled.paste(new_bars, (140 + 228 * (num_games % 4), 259 + 152 * floor(num_games / 4)), mask=new_bars)

            gameInfo = {"Status": game["status"]["type"]["detail"], "Start Date": game['competitions'][0]["startDate"],
                        "Home Team": game['competitions'][0]['competitors'][0]['team']['displayName'],
                        "Away Team": game['competitions'][0]['competitors'][1]['team']['displayName']}
            gameInfo["Matchup"] = f"{teamDict[gameInfo['Away Team']][0]} {teamDict[gameInfo['Away Team']][1]} @ " \
                                  f"{teamDict[gameInfo['Home Team']][1]} {teamDict[gameInfo['Home Team']][0]}"

            home_logo = team_logos.crop((((teamDict[gameInfo["Home Team"]][2]-1) % 8)*128, 
                                         floor((teamDict[gameInfo["Home Team"]][2]-1)/8)*128, 
                                         (teamDict[gameInfo["Home Team"]][2] - floor((teamDict[gameInfo["Home Team"]][2]-1) / 8)*8)*128,
                                         ceil(teamDict[gameInfo["Home Team"]][2]/8)*128))
            away_logo = team_logos.crop((((teamDict[gameInfo["Away Team"]][2]-1) % 8)*128, 
                                         floor((teamDict[gameInfo["Away Team"]][2]-1)/8)*128, 
                                         (teamDict[gameInfo["Away Team"]][2] - floor((teamDict[gameInfo["Away Team"]][2]-1) / 8)*8)*128,
                                         ceil(teamDict[gameInfo["Away Team"]][2]/8)*128))

            home_logo = home_logo.resize((60, 60), Image.ANTIALIAS)
            away_logo = away_logo.resize((60, 60), Image.ANTIALIAS)

            compiled.paste(home_logo, (258 + 228 * (num_games % 4), 278 + 152 * floor(num_games / 4)), mask=home_logo)
            compiled.paste(away_logo, (150 + 228 * (num_games % 4), 278 + 152 * floor(num_games / 4)), mask=away_logo)
            draw.text((220 + 228 * (num_games % 4), 285 + 152 * floor(num_games / 4)), f"@", (255, 255, 255),
                      font=at_txt_font)

            dt_object = datetime.strptime(gameInfo["Start Date"], "%Y-%m-%dT%H:%MZ") - timedelta(hours=4)
            draw.text((150 + 228 * (num_games % 4), 252 + 152 * floor(num_games / 4)),
                      f"{dt_object.month}/{dt_object.day}", (255, 255, 255), font=date_txt_font)

            if game["status"]["type"]["description"] == "Scheduled":
                gameInfo["Odds"] = game["competitions"][0]["odds"][0]["details"]

                if int(dt_object.hour) > 12:
                    draw.text((150 + 228 * (num_games % 4), 333 + 152 * floor(num_games / 4)),
                              f"{dt_object.hour-12}:{dt_object.minute:02} {dt_object:%p} EDT", (255, 255, 255),
                              font=date_txt_font)
                else:
                    draw.text((150 + 228 * (num_games % 4), 333 + 152 * floor(num_games / 4)),
                              f"{dt_object.hour}:{dt_object.minute:02} {dt_object:%p} EDT", (255, 255, 255),
                              font=date_txt_font)
                draw.text((173 + 228 * (num_games % 4), 357 + 152 * floor(num_games / 4)),
                          f"{gameInfo['Odds']} ", (255, 255, 255), font=odds_txt_font)
            elif game["status"]["type"]["description"] == "Final":
                gameInfo["Home Score"] = game["competitions"][0]["competitors"][0]["score"]
                gameInfo["Away Score"] = game["competitions"][0]["competitors"][1]["score"]
                gameInfo["Score Display"] = f'{gameInfo["Away Score"]} - {gameInfo["Home Score"]}'
                if game["competitions"][0]["competitors"][0]["winner"]:
                    gameInfo["Winner"] = "Home Team"
                else:
                    gameInfo["Winner"] = "Away Team"

                draw.text((150 + 228 * (num_games % 4), 333 + 152 * floor(num_games / 4)),
                          f"{gameInfo['Score Display']}", (255, 255, 255), font=date_txt_font)
                draw.text((150 + 228 * (num_games % 4), 357 + 152 * floor(num_games / 4)),
                          f"FINAL", (255, 255, 255), font=odds_txt_font)
            elif game["status"]["type"]["description"] == "In Progress":
                gameInfo["Home Score"] = game["competitions"][0]["competitors"][0]["score"]
                gameInfo["Away Score"] = game["competitions"][0]["competitors"][1]["score"]
                gameInfo["Score Display"] = f'{gameInfo["Away Score"]} - {gameInfo["Home Score"]}'

                draw.text((150 + 228 * (num_games % 4), 333 + 152 * floor(num_games / 4)),
                          f"{gameInfo['Status']}", (255, 255, 255), font=date_txt_font)
                draw.text((150 + 228 * (num_games % 4), 357 + 152 * floor(num_games / 4)),
                          f"{gameInfo['Score Display']}", (255, 255, 255), font=odds_txt_font)
            num_games += 1

        # set a var to arr that represents bytes.
        arr = io.BytesIO()
        # Save our compiled image in PNG format as bytes
        compiled.save(arr, format='PNG')
        # Set the byte stream position to 0.
        arr.seek(0)
        # Set a file var to a file discord understands, using our bytes, with a filename of "WelcomeCard.png"
        await ctx.send(file=discord.File(fp=arr, filename=f'NFLSchedule.PNG'))


def setup(bot):
    bot.add_cog(Commands(bot))
