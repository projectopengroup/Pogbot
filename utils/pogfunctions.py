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

    fontvegurbold = Path("fonts/") / "Vegur-Bold.otf"
    fontvegurlight = Path("fonts/") / "Vegur-Light.otf"

    # Open our images by their paths.
    toplayer = Image.open(welcomecardtop)
    baselayer = Image.open(welcomecardbase)
    circlelayer = Image.open(welcomecardcircle)

    # resize the avatarlayer
    avatarlayer = avatarlayer.resize((300, 300), Image.ANTIALIAS)

    # Make a new var called compiled by taking our welcome card base image and copying it
    compiled = baselayer.copy()
    # This is to help people understand x and y axis and which direction they move in from their orgin state.
    #               ,right(x)
    # paste(image, (0, 0))
    #                  ^down(y)
    # In the new compiled image, paste the avatar layer at x46, y37 and set a mask.
    compiled.paste(avatarlayer, (46, 37), mask=avatarlayer)
    # In the compiled image, paste the toplayer and set a mask.
    compiled.paste(toplayer, (0, 0), mask=toplayer)
    # Going to leave the circle off for now, I think it looks better without it? Maybe I'm wrong. Lol.
    # compiled.paste(circlelayer, (0, 0), mask=circlelayer)

    # Name and set our fonts.
    name_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 50)
    msg_font = ImageFont.truetype("fonts/Vegur-Light.otf", 30)
    id_font = ImageFont.truetype("fonts/Vegur-Bold.otf", 25)
    member_num_font = ImageFont.truetype("fonts/Vegur-Light.otf", 20)

    # Draw our compiled image as a base.
    draw = ImageDraw.Draw(compiled)

    # Set all of our text at specific positions, colors, and with certain fonts.
    draw.text((365, 120), str(user).upper(), (255, 255, 255), font=name_font)
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
    file = discord.File(fp=arr, filename=f'WelcomeCard.png')
    # Send the file back.
    return file
