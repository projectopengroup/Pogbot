import io
import random
from datetime import datetime, timedelta
import PIL
import discord
import requests
import re
from PIL import Image, ImageDraw, ImageFont, ImageColor
from pathlib import Path
from colorthief import ColorThief
from math import sqrt
from utils.pogesquelle import get_global_welcomeimg, get_global_bannercolor, get_global_bgcolor, get_global_currency, \
    check_global_user, check_user, get_db_user_item, set_db_user_item, set_global_currency
from discord.ext import commands


# Function to create one line embeds. So far it takes most of the possible arguments that you can set to an embed. Not
# all args need to be filled out, but a title or description is required. One of them has to be filled
# out to create an embed, or both. To create an embed, just type ' await send_embed(ctx, send_option=option, arg=value)'
# with the arg being one of the args that it takes and the appropriate value. Any image, thumbnail, pfp, etc. takes a
# url in the form of a string. The fields argument takes an array of tuples. So for example:
#                                                           [(name1, value1, inline1), (name2, value2, inline2)]

# send_option = 0 means create then send the embed
# send_option = 1 means create and send the embed, but also return the embed so that it can be stored in a variable and
# the sent embed can be edited later
# send_option = 2 create the embed, but only return the embed, not send it, so the embed object is stored in a variable
# that can be used later.
async def send_embed(ctx, send_option=0, title=None, description=None, author=None, author_pfp=None,
                     color=discord.Colour.default(), timestamp=None, footer=None, thumbnail=None, image=None, url=None,
                     fields=None):
    if title is None and description is None and author is None:
        print("[Error]: Error creating embed. No title or description specified.")
    else:
        # Initializes new_embed variable
        new_embed = discord.Embed(colour=color)

        # Checks if title, description, and url are 'None'. If None, that element isn't added to the embed
        if title is not None:
            new_embed.title = title
        if description is not None:
            new_embed.description = description
        if url is not None:
            new_embed.url = url

        # Checks if each argument is 'None'. If None, the argument is ignored. But if not None, then the element is
        # added to the embed.
        if image is not None:
            new_embed.set_image(url=image)
        if timestamp is not None:
            new_embed.timestamp = timestamp
        if footer is not None:
            new_embed.set_footer(text=footer)
        if thumbnail is not None:
            new_embed.set_thumbnail(url=thumbnail)
        if author is not None and author_pfp is not None:
            new_embed.set_author(name=author, icon_url=author_pfp)
        elif author is not None and author_pfp is None:
            new_embed.set_author(name=author)

        if fields is not None:
            for field in fields:
                new_embed.add_field(name=field[0], value=field[1], inline=field[2])

        if send_option == 0:
            await ctx.send(embed=new_embed)
        elif send_option == 1:
            return await ctx.send(embed=new_embed)
        elif send_option == 2:
            return new_embed


# Card creation for welcome messages
def create_welcome_card(avatarRequest, user, server):
    # Set a var to the image that was passed into the function and convert it to RGBA.
    avatarlayer = Image.open(io.BytesIO(avatarRequest)).convert("RGBA")
    # Define our folder.
    welcomecardfolder = Path("img/card_welcomes/")
    # Set our other image variables paths.
    welcomecardbase = welcomecardfolder / "baselayer.png"
    welcomecardtop = welcomecardfolder / "toplayer.png"
    welcomecardcircle = welcomecardfolder / "circlelayer.png"
    welcomecardbanner = welcomecardfolder / "bannerlayer.png"
    welcomecardeffect = welcomecardfolder / "effectlayer.png"

    fontvegurbold = Path("fonts/") / "Vegur-Bold.otf"
    fontvegurlight = Path("fonts/") / "Vegur-Light.otf"

    # Open our images by their paths.
    toplayer = Image.open(welcomecardtop)
    baselayer = Image.open(welcomecardbase)
    circlelayer = Image.open(welcomecardcircle)
    bannerlayer = Image.open(welcomecardbanner)
    effectlayer = Image.open(welcomecardeffect)

    # resize the avatarlayer
    avatarlayer = avatarlayer.resize((250, 250), Image.ANTIALIAS)

    compiled = baselayer.copy()

    getcolorfrom = ColorThief(io.BytesIO(avatarRequest))
    swatch = getcolorfrom.get_palette(color_count=25)
    domcolor = getcolorfrom.get_color(quality=1)

    custombgcolor = get_global_bgcolor(user.id)
    if custombgcolor != "None":
        Lightcolor = ImageColor.getrgb(custombgcolor)
        print(Lightcolor)
    else:
        Lightcolor = closest_color((8, 213, 247), swatch)
        print(Lightcolor)

    custombannercolor = get_global_bannercolor(user.id)
    if custombannercolor != "None":
        if custombannercolor == "#FFFFFF":
            custombannercolor = "#000000"
        Darkcolor = ImageColor.getrgb(custombannercolor)
        print(Darkcolor)
    else:
        Darkcolor = closest_color((15, 15, 15), swatch)
        print(Darkcolor)

    custombg = get_global_welcomeimg(user.id)
    if custombg != "None":
        try:
            custombgimg = requests.get(custombg).content
            alpha = toplayer.getchannel('A')
            newlayer = Image.open(io.BytesIO(custombgimg)).convert("RGBA")
            newlayer = newlayer.resize((int(toplayer.size[0]), int(toplayer.size[1])), 0)
            # baselayer = baselayer.resize((int(baselayer.size[0]),int(baselayer.size[1])), 0)
            print(baselayer.getbands())
            print(newlayer.getbands())
            print(baselayer.size)
            print(newlayer.size)
            newlayer.putalpha(alpha)
            toplayer = newlayer.copy()
            effectlayer = Image.new('RGBA', effectlayer.size, (255, 0, 0, 0))
        except PIL.UnidentifiedImageError as exception:
            alpha = toplayer.getchannel('A')
            toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
            toplayer.putalpha(alpha)
            alpha = effectlayer.getchannel('A')
            effectlayer = Image.new('RGBA', effectlayer.size, color=Darkcolor)
            effectlayer.putalpha(alpha)
        except requests.ConnectionError as exception:
            alpha = toplayer.getchannel('A')
            toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
            toplayer.putalpha(alpha)
            alpha = effectlayer.getchannel('A')
            effectlayer = Image.new('RGBA', effectlayer.size, color=Darkcolor)
            effectlayer.putalpha(alpha)
    else:
        alpha = toplayer.getchannel('A')
        toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
        toplayer.putalpha(alpha)

    alpha = bannerlayer.getchannel('A')
    bannerlayer = Image.new('RGBA', bannerlayer.size, color=Darkcolor)
    bannerlayer.putalpha(alpha)
    # This is to help people understand x and y axis and which direction they move in from their orgin state.
    #               ,right(x)
    # paste(image, (0, 0))
    #                  ^down(y)
    # In the compiled image, paste the toplayer and set a mask.
    compiled.paste(avatarlayer, (75, 60), mask=avatarlayer)
    compiled.paste(toplayer, (0, 0), mask=toplayer)
    compiled.paste(bannerlayer, (0, 0), mask=bannerlayer)
    compiled.paste(effectlayer, (0, 0), mask=effectlayer)
    # Going to leave the circle off for now, I think it looks better without it? Maybe I'm wrong. Lol.
    # compiled.paste(circlelayer, (0, 0), mask=circlelayer)

    # Name and set our fonts.
    name_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 50)
    msg_font = ImageFont.truetype("fonts/Vegur-Light.otf", 30)
    id_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 25)
    member_num_font = ImageFont.truetype("fonts/Vegur-Light.otf", 20)

    # Draw our compiled image as a base.
    draw = ImageDraw.Draw(compiled)

    if len(str(user)) > 18:
        UserSplit = str(user).upper()
        UserSplit = UserSplit.split('#')
        UserFormatted = UserSplit[0]
        UserFormatted = UserFormatted[0:13] + "...#" + UserSplit[1]
    else:
        UserFormatted = str(user).upper()

    # Set all of our text at specific positions, colors, and with certain fonts.
    draw.text((365, 120), UserFormatted, (255, 255, 255), font=name_font)
    draw.text((365, 170), f"HAS JOINED THE SERVER", (255, 255, 255), font=msg_font)
    draw.text((365, 200), f"ID#{user.id}", (255, 255, 255), font=id_font)
    draw.text((365, 225), f"MEMBER#{server.member_count}", (255, 255, 255), font=member_num_font)

    # set a var to arr that represents bytes.
    arr = io.BytesIO()
    # Save our compiled image in PNG format as bytes
    compiled.save(arr, format='PNG')
    # Set the byte stream position to 0.
    arr.seek(0)
    # Set a file var to a file discord understands, using our bytes, with a filename of "WelcomeCard.png"
    file = discord.File(fp=arr, filename=f'WelcomeCard.PNG')
    # Send the file back.
    return file


# Card creation for level
def create_level_card(avatarRequest, user, server, userxp, xp_lvl_up, userlvl, rank):
    # Set a var to the image that was passed into the function and convert it to RGBA.
    avatarlayer = Image.open(io.BytesIO(avatarRequest)).convert("RGBA")
    # Define our folder.
    welcomecardfolder = Path("img/card_welcomes/")
    # Set our other image variables paths.
    welcomecardbase = welcomecardfolder / "baselayer.png"
    welcomecardtop = welcomecardfolder / "toplayer.png"
    welcomecardcircle = welcomecardfolder / "circlelayer.png"
    welcomecardbanner = welcomecardfolder / "bannerlayer.png"
    welcomecardeffect = welcomecardfolder / "effectlayer.png"
    levelstatusbar = welcomecardfolder / "statusbar.png"

    fontvegurbold = Path("fonts/") / "Vegur-Bold.otf"
    fontvegurlight = Path("fonts/") / "Vegur-Light.otf"

    # Open our images by their paths.
    toplayer = Image.open(welcomecardtop)
    baselayer = Image.open(welcomecardbase)
    circlelayer = Image.open(welcomecardcircle)
    bannerlayer = Image.open(welcomecardbanner)
    effectlayer = Image.open(welcomecardeffect)

    statusbar = Image.open(levelstatusbar)

    # resize the avatarlayer
    avatarlayer = avatarlayer.resize((250, 250), Image.ANTIALIAS)

    compiled = baselayer.copy()

    getcolorfrom = ColorThief(io.BytesIO(avatarRequest))
    swatch = getcolorfrom.get_palette(color_count=25)
    domcolor = getcolorfrom.get_color(quality=1)

    custombgcolor = get_global_bgcolor(user.id)
    if custombgcolor != "None":
        Lightcolor = ImageColor.getrgb(custombgcolor)
        print(Lightcolor)
    else:
        Lightcolor = closest_color((8, 213, 247), swatch)
        print(Lightcolor)

    custombannercolor = get_global_bannercolor(user.id)
    if custombannercolor != "None":
        if custombannercolor == "#FFFFFF":
            custombannercolor = "#000000"
        Darkcolor = ImageColor.getrgb(custombannercolor)
        print(Darkcolor)
    else:
        Darkcolor = closest_color((15, 15, 15), swatch)
        print(Darkcolor)

    custombg = get_global_welcomeimg(user.id)
    if custombg != "None":
        try:
            custombgimg = requests.get(custombg).content
            alpha = toplayer.getchannel('A')
            newlayer = Image.open(io.BytesIO(custombgimg)).convert("RGBA")
            newlayer = newlayer.resize((int(toplayer.size[0]), int(toplayer.size[1])), 0)
            # baselayer = baselayer.resize((int(baselayer.size[0]),int(baselayer.size[1])), 0)
            print(baselayer.getbands())
            print(newlayer.getbands())
            print(baselayer.size)
            print(newlayer.size)
            newlayer.putalpha(alpha)
            toplayer = newlayer.copy()
            effectlayer = Image.new('RGBA', effectlayer.size, (255, 0, 0, 0))
        except PIL.UnidentifiedImageError as exception:
            alpha = toplayer.getchannel('A')
            toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
            toplayer.putalpha(alpha)
            alpha = effectlayer.getchannel('A')
            effectlayer = Image.new('RGBA', effectlayer.size, color=Darkcolor)
            effectlayer.putalpha(alpha)
        except requests.ConnectionError as exception:
            alpha = toplayer.getchannel('A')
            toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
            toplayer.putalpha(alpha)
            alpha = effectlayer.getchannel('A')
            effectlayer = Image.new('RGBA', effectlayer.size, color=Darkcolor)
            effectlayer.putalpha(alpha)
    else:
        alpha = toplayer.getchannel('A')
        toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
        toplayer.putalpha(alpha)

    alpha = bannerlayer.getchannel('A')
    bannerlayer = Image.new('RGBA', bannerlayer.size, color=Darkcolor)
    bannerlayer.putalpha(alpha)
    # This is to help people understand x and y axis and which direction they move in from their orgin state.
    #               ,right(x)
    # paste(image, (0, 0))
    #                  ^down(y)
    # In the compiled image, paste the toplayer and set a mask.
    compiled.paste(avatarlayer, (75, 60), mask=avatarlayer)
    compiled.paste(toplayer, (0, 0), mask=toplayer)
    compiled.paste(bannerlayer, (0, 0), mask=bannerlayer)
    compiled.paste(effectlayer, (0, 0), mask=effectlayer)


    # Going to leave the circle off for now, I think it looks better without it? Maybe I'm wrong. Lol.
    # compiled.paste(circlelayer, (0, 0), mask=circlelayer)

    # Name and set our fonts.
    name_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 50)
    msg_font = ImageFont.truetype("fonts/Vegur-Light.otf", 35)
    xp_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 25)
    member_num_font = ImageFont.truetype("fonts/Vegur-Light.otf", 20)

    # Draw our compiled image as a base.
    draw = ImageDraw.Draw(compiled)

    if len(str(user)) > 18:
        UserSplit = str(user).upper()
        UserSplit = UserSplit.split('#')
        UserFormatted = UserSplit[0]
        UserFormatted = UserFormatted[0:13] + "...#" + UserSplit[1]
    else:
        UserFormatted = str(user).upper()

    # Set all of our text at specific positions, colors, and with certain fonts.
    draw.text((355, 120), UserFormatted, (255, 255, 255), font=name_font)
    draw.text((355, 170), f"LEVEL {userlvl} RANK {rank}", (255, 255, 255), font=msg_font)
    draw.text((820, 185), f"XP {userxp} / {xp_lvl_up}", (255, 255, 255), font=xp_font)

    drawObject = ImageDraw.Draw(compiled)

    color = 98, 211, 245

    x = 350
    y = 222
    h = 25
    w = 590
    progress = w * float(userxp) / float(xp_lvl_up)

    w = progress
    drawObject.ellipse((x + w, y, x + h + w, y + h), fill=color)
    drawObject.ellipse((x, y, x + h, y + h), fill=color)
    drawObject.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=color)

    compiled.paste(statusbar, (0, 0), mask=statusbar)

    # set a var to arr that represents bytes.
    arr = io.BytesIO()
    # Save our compiled image in PNG format as bytes
    compiled.save(arr, format='PNG')
    # Set the byte stream position to 0.
    arr.seek(0)
    # Set a file var to a file discord understands, using our bytes, with a filename of "WelcomeCard.png"
    file = discord.File(fp=arr, filename=f'LevelCard.PNG')
    # Send the file back.
    return file


def create_profile_card(avatarRequest, user, server, userxp, xp_lvl_up, userlvl, rank):
    # Set a var to the image that was passed into the function and convert it to RGBA.
    avatarlayer = Image.open(io.BytesIO(avatarRequest)).convert("RGBA")
    # Define our folder.
    welcomecardfolder = Path("img/card_welcomes/")
    # Set our other image variables paths.
    welcomecardbase = welcomecardfolder / "baselayer.png"
    welcomecardtop = welcomecardfolder / "toplayer_profile.png"
    welcomecardcircle = welcomecardfolder / "circlelayer.png"
    welcomecardbanner = welcomecardfolder / "bannerlayer_profile.png"
    welcomecardeffect = welcomecardfolder / "effectlayer.png"
    levelstatusbar = welcomecardfolder / "statusbar_profile.png"
    pogcoinlayer = welcomecardfolder / "pogcoinlayer.png"

    fontvegurbold = Path("fonts/") / "Vegur-Bold.otf"
    fontvegurlight = Path("fonts/") / "Vegur-Light.otf"

    # Open our images by their paths.
    toplayer = Image.open(welcomecardtop)
    baselayer = Image.open(welcomecardbase)
    circlelayer = Image.open(welcomecardcircle)
    bannerlayer = Image.open(welcomecardbanner)
    effectlayer = Image.open(welcomecardeffect)

    statusbar = Image.open(levelstatusbar)
    pogcoin = Image.open(pogcoinlayer)

    # resize the avatarlayer
    avatarlayer = avatarlayer.resize((105, 105), Image.ANTIALIAS)

    compiled = baselayer.copy()

    getcolorfrom = ColorThief(io.BytesIO(avatarRequest))
    swatch = getcolorfrom.get_palette(color_count=25)
    domcolor = getcolorfrom.get_color(quality=1)

    custombgcolor = get_global_bgcolor(user.id)
    if custombgcolor != "None":
        Lightcolor = ImageColor.getrgb(custombgcolor)
        print(Lightcolor)
    else:
        Lightcolor = closest_color((8, 213, 247), swatch)
        print(Lightcolor)

    custombannercolor = get_global_bannercolor(user.id)
    if custombannercolor != "None":
        if custombannercolor == "#FFFFFF":
            custombannercolor = "#000000"
        Darkcolor = ImageColor.getrgb(custombannercolor)
        print(Darkcolor)
    else:
        Darkcolor = closest_color((15, 15, 15), swatch)
        print(Darkcolor)

    custombg = get_global_welcomeimg(user.id)
    if custombg != "None":
        try:
            custombgimg = requests.get(custombg).content
            alpha = toplayer.getchannel('A')
            newlayer = Image.open(io.BytesIO(custombgimg)).convert("RGBA")
            newlayer = newlayer.resize((int(toplayer.size[0]), int(toplayer.size[1])), 0)
            # baselayer = baselayer.resize((int(baselayer.size[0]),int(baselayer.size[1])), 0)
            print(baselayer.getbands())
            print(newlayer.getbands())
            print(baselayer.size)
            print(newlayer.size)
            newlayer.putalpha(alpha)
            toplayer = newlayer.copy()
            effectlayer = Image.new('RGBA', effectlayer.size, (255, 0, 0, 0))
        except PIL.UnidentifiedImageError as exception:
            alpha = toplayer.getchannel('A')
            toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
            toplayer.putalpha(alpha)
            alpha = effectlayer.getchannel('A')
            effectlayer = Image.new('RGBA', effectlayer.size, color=Darkcolor)
            effectlayer.putalpha(alpha)
        except requests.ConnectionError as exception:
            alpha = toplayer.getchannel('A')
            toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
            toplayer.putalpha(alpha)
            alpha = effectlayer.getchannel('A')
            effectlayer = Image.new('RGBA', effectlayer.size, color=Darkcolor)
            effectlayer.putalpha(alpha)
    else:
        alpha = toplayer.getchannel('A')
        toplayer = Image.new('RGBA', toplayer.size, color=Lightcolor)
        toplayer.putalpha(alpha)

    alpha = bannerlayer.getchannel('A')
    bannerlayer = Image.new('RGBA', bannerlayer.size, color=Darkcolor)
    bannerlayer.putalpha(alpha)
    # This is to help people understand x and y axis and which direction they move in from their orgin state.
    #               ,right(x)
    # paste(image, (0, 0))
    #                  ^down(y)
    # In the compiled image, paste the toplayer and set a mask.
    compiled.paste(avatarlayer, (18, 67), mask=avatarlayer)
    compiled.paste(toplayer, (0, 0), mask=toplayer)
    compiled.paste(bannerlayer, (0, 0), mask=bannerlayer)
    compiled.paste(effectlayer, (0, 0), mask=effectlayer)


    # Going to leave the circle off for now, I think it looks better without it? Maybe I'm wrong. Lol.
    # compiled.paste(circlelayer, (0, 0), mask=circlelayer)

    # Name and set our fonts.
    name_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 32)
    pog_coin_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 30)
    coins_font = ImageFont.truetype("fonts/Vegur-Light.otf", 28)
    msg_font = ImageFont.truetype("fonts/Vegur-Light.otf", 30)
    xp_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 20)
    member_num_font = ImageFont.truetype("fonts/Vegur-Light.otf", 20)

    # Draw our compiled image as a base.
    draw = ImageDraw.Draw(compiled)

    if len(str(user)) > 18:
        UserSplit = str(user).upper()
        UserSplit = UserSplit.split('#')
        UserFormatted = UserSplit[0]
        UserFormatted = UserFormatted[0:13] + "...#" + UserSplit[1]
    else:
        UserFormatted = str(user).upper()

    currency = get_global_currency(user.id)

    # Set all of our text at specific positions, colors, and with certain fonts.
    draw.text((132, 108), UserFormatted, (255, 255, 255), font=name_font)
    draw.text((22, 177), f"LEVEL {userlvl} RANK {rank}", (255, 255, 255), font=msg_font)
    draw.text((390, 188), f"XP {userxp} / {xp_lvl_up}", (255, 255, 255), font=xp_font)
    draw.text((599, 108), f"POG COINS", (255, 255, 255), font=pog_coin_font)
    draw.text((599, 141), str(currency), (255, 255, 255), font=coins_font)

    drawObject = ImageDraw.Draw(compiled)

    color = 98, 211, 245

    x = 20
    y = 221
    h = 20
    w = 450
    progress = w * (float(userxp) / float(xp_lvl_up))

    w = progress
    drawObject.ellipse((x + w, y, x + h + w, y + h), fill=color)
    drawObject.ellipse((x, y, x + h, y + h), fill=color)
    drawObject.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=color)

    compiled.paste(statusbar, (0, 0), mask=statusbar)
    compiled.paste(pogcoin, (0, 0), mask=pogcoin)

    # set a var to arr that represents bytes.
    arr = io.BytesIO()
    # Save our compiled image in PNG format as bytes
    compiled.save(arr, format='PNG')
    # Set the byte stream position to 0.
    arr.seek(0)
    # Set a file var to a file discord understands, using our bytes, with a filename of "WelcomeCard.png"
    file = discord.File(fp=arr, filename=f'LevelCard.PNG')
    # Send the file back.
    return file


async def check_xp(ctx):
    check_global_user(ctx.author.id)
    # Check if user is in user table unique to each server. If not, then creates an entry for that user.
    check_user(ctx.guild.id, ctx.author.id)
    # Gets the user's xp in the server
    userxp = get_db_user_item(ctx.guild.id, ctx.author.id, "XP")
    # Gets the user's level in the server
    userlvl = get_db_user_item(ctx.guild.id, ctx.author.id, "Level")
    # Gets the time when the user can earn xp again (A person can only earn xp once a minute)
    xplock = get_db_user_item(ctx.guild.id, ctx.author.id, "XPLockedUntil")

    # Checks if the user is able to earn xp again. If yes, the xp lock is set to 1 minute from now and a random
    # amount of xp between the range 11 and 18 is given to the user.
    if xplock == "0" or datetime.strptime(xplock, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
        set_db_user_item(ctx.guild.id, ctx.author.id, "XPLockedUntil", datetime.now() + timedelta(minutes=1))
        set_db_user_item(ctx.guild.id, ctx.author.id, "XP", int(userxp) + random.randint(15, 25))
        currency = get_global_currency(ctx.author.id)
        set_global_currency(ctx.author.id, currency + 10)

        # The formula calculates how much xp is needed to reach the next level, and it is unique to each level.
        # The higher the level the user is at, the more xp that is needed to reach the next level.
        xp_lvl_up = round(125 * (((int(userlvl) + 1) / 1.20) ** 1.20))
        # Gets the users new xp total
        userxp = get_db_user_item(ctx.guild.id, ctx.author.id, "XP")

        # Checks to see if the user has enough xp to level up. If yes, the users xp amount is set to the amount
        # the user went over the required xp to level up. Ex. The user has 100 xp, but only needed 96 xp to
        # level up, the users xp will be set to 4. The users level is then updated in the db
        if userxp >= xp_lvl_up:
            await send_embed(ctx.channel, author="Level Up!", author_pfp=ctx.author.avatar.url,
                             description=f"Keep up the activeness {ctx.author.mention}! "
                                         f"You have leveled up to level {userlvl + 1} and you have earned "
                                         f"<:PogCoin:870094422233215007> {(userlvl + 1) * 100} Pog Coins!",
                             color=0x08d5f7)
            overflow_xp = userxp - xp_lvl_up
            set_db_user_item(ctx.guild.id, ctx.author.id, "XP", overflow_xp)
            set_db_user_item(ctx.guild.id, ctx.author.id, "Level", userlvl + 1)
            currency = get_global_currency(ctx.author.id)
            set_global_currency(ctx.author.id, currency + ((userlvl + 1) * 100))


def closest_color(rgb, colors):
    r, g, b = rgb
    color_diffs = []
    for color in colors:
        cr, cg, cb = color
        color_diff = sqrt(abs(r - cr) ** 2 + abs(g - cg) ** 2 + abs(b - cb) ** 2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


def diff_lists(before, after):
    b, a = set(before), set(after)
    return list(a - b), list(b - a), list(a & b)


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time
