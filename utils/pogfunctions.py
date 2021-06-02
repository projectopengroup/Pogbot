import io

import discord
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


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
                     color=discord.Colour.default(), footer=None, thumbnail=None, image=None, url=None, fields=None):
    if title is None and description is None:
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


def create_welcome_card(avatarRequest, user, server):
    avatarlayer = Image.open(io.BytesIO(avatarRequest)).convert("RGBA")

    welcomecardfolder = Path("img/card_welcomes/")
    welcomecardbase = welcomecardfolder / "baselayer.png"
    welcomecardtop = welcomecardfolder / "toplayer.png"
    welcomecardcircle = welcomecardfolder / "circlelayer.png"
    fontvegurbold = Path("fonts/") / "Vegur-Bold.otf"
    fontvegurlight = Path("fonts/") / "Vegur-Light.otf"

    toplayer = Image.open(welcomecardtop)
    baselayer = Image.open(welcomecardbase)
    circlelayer = Image.open(welcomecardcircle)
    avatarlayer = avatarlayer.resize((300, 300), Image.ANTIALIAS)

    compiled = baselayer.copy()

    #                               ,right(x)
    # baselayer.paste(avatarlayer, (0, 0))fd
    #                                   ^down(y)

    compiled.paste(avatarlayer, (46, 37), mask=avatarlayer)
    compiled.paste(toplayer, (0, 0), mask=toplayer)
    compiled.paste(circlelayer, (0, 0), mask=circlelayer)

    name_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 50)
    msg_font = ImageFont.truetype("fonts/Vegur-Light.otf", 30)
    id_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 25)
    member_num_font = ImageFont.truetype("fonts/Vegur-Light.otf", 20)

    draw = ImageDraw.Draw(compiled)
    draw.text((365, 120), str(user), (255, 255, 255), font=name_font)
    draw.text((365, 170), f"HAS JOINED THE SERVER", (255, 255, 255), font=msg_font)
    draw.text((365, 200), f"ID#{user.id}", (255, 255, 255), font=id_font)
    draw.text((365, 225), f"MEMBER#{server.member_count}", (255, 255, 255), font=member_num_font)

    arr = io.BytesIO()
    compiled.save(arr, format='PNG')
    arr.seek(0)
    file = discord.File(fp=arr, filename=f'WelcomeCard.png')
    return file
    # compiled.save(f'{welcomecardfolder / "compiled/welcomecard.png"}')



