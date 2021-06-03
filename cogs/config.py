import sqlite3
import discord
import asyncio
import requests
from discord.ext import commands
from utils.pogfunctions import send_embed, create_welcome_card
from utils.pogesquelle import get_prefix, set_welcome_message, \
    set_welcome_dm_message, set_welcome_role, set_welcome_card, set_welcome_channel, reset_welcome_message

current_users = set()

def setup_in_progress(ctx):
    if ctx.guild.id not in current_users:
        current_users.add(ctx.guild.id)
        return True
    return False


class Config(commands.Cog, name="config"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='devcard', brief='displays some things in development')
    async def devcard(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        avatarRequest = (requests.get(user.avatar_url)).content
        # Testing create welcome card on message send right now, until we get it done.
        await ctx.send(file=create_welcome_card(avatarRequest, user, ctx.guild))

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

    @commands.command(name='prefix', brief='Responds with the prefix.',
                      description="Responds with Pogbot's command prefix.")
    async def prefix(self, ctx):
        justprefix = await get_prefix(self.bot, ctx.message)
        await send_embed(ctx.message.channel, send_option=0, description=f"**The current prefix is {justprefix[2]}**",
                         color=0x08d5f7)

    @commands.command(name='setup', brief='Walks you through setup.',
                      description='Walks you through, and lists setup options for Pogbot.')
    @commands.check(setup_in_progress)
    # Look for a command called setup
    async def setup(self, ctx):
        inwelcomesetup = False
        bothsetup = False
        textsetup = False
        # Check if the user using the setup command has administrator:
        if ctx.author.guild_permissions.administrator:
            # Sending a message embed that says running setup.
            embedorg = discord.Embed(description='<:Check:845178458426179605> **Running Setup...**',
                                     color=0x08d5f7)
            # Collecting the message ID into our global setup id var.
            pogsetupid = await ctx.send(embed=embedorg)
            # Sleep the thread for a little bit so we can edit the message.
            await asyncio.sleep(0.4)
            # Form the embed that we want to use for our edit.
            embededit = await send_embed(ctx, send_option=2, title=f"**Pogbot Setup**", color=0x08d5f7,
                                         thumbnail='https://i.imgur.com/rYKYpDw.png',
                                         description="Respond with any menu option to proceed.",
                                         fields=[('Settings', 'Basic server settings.', True),
                                                 ('Moderator', "Moderator settings.", True),
                                                 ('Reactions', "Setup role reactions.", True),
                                                 ('Commands', "Configure custom commands.", True),
                                                 ('Logs', "Enable event logs.", True),
                                                 ('Switcher', "Turn on/off commands.", True)])
            # Setting our global pogsetup var to true.
            # pogsetup = True

            # orginchannel = ctx.message.channel
            # Editing our original message into our new embed.
            await pogsetupid.edit(embed=embededit)
            # Delete the orignal message.
            await ctx.message.delete()
            trueprefix = await get_prefix(self.bot, ctx)

            def checkAuthor(message):
                return message.author.id == ctx.author.id and message.guild.id == ctx.guild.id and f"{trueprefix[2]}setup" not in message.content

            while True:
                await pogsetupid.edit(embed=embededit)
                try:
                    reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                    if "set" in str(reply.content.lower()):
                        # If it's found then form our embed.
                        embededit = await send_embed(ctx, send_option=2, title=f"**Basic Settings**",
                                                     thumbnail='https://i.imgur.com/rYKYpDw.png', color=0x08d5f7,
                                                     description="Respond with any menu option to proceed.",
                                                     fields=[('Prefix', "Set the bots prefix.", True),
                                                             ('Welcomes', "Setup a channel for welcome messages.",
                                                              True)])
                        # Edit the original message.
                        await pogsetupid.edit(embed=embededit)
                        # Delete the message.
                        await reply.delete()
                        reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                    # Look for wel in lowercase message.
                    if "wel" in str(reply.content.lower()):
                        print("Found")
                        # If found, then form the embed.
                        embededit = await send_embed(ctx, send_option=2, title=f"**Welcome Message Setup**",
                                                     description="Select the type of welcome message or action you'd "
                                                                 "like to edit.", color=0x08d5f7,
                                                     thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                     fields=[('Respond with',
                                                              "**channel**, **dm**, **role** or **back**", True)])
                        # Edit the message.
                        await pogsetupid.edit(embed=embededit)
                        await reply.delete()
                        reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                        inwelcomesetup = True

                        if "channel" in str(reply.content.lower()):
                            # If found, then form the embed.
                            embededit = await send_embed(ctx, send_option=2, title=f"**Channel Welcome Setup**",
                                                         description=f"**{ctx.message.channel}** will be set to the "
                                                                     f"welcome message channel. \n\n **Choose a type of"
                                                                     f" welcome message to continue.**",
                                                         color=0x08d5f7,
                                                         thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                         fields=[('Respond with', "**image**, **text**, **both**, "
                                                                                  "or **disable**",
                                                                  True)])
                            # Edit the message.
                            await pogsetupid.edit(embed=embededit)
                            await reply.delete()
                            reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                            if "disable" in str(reply.content.lower()):
                                # If found, then form the embed.
                                set_welcome_card(0, reply.guild.id)
                                set_welcome_channel(0, reply.guild.id)
                                reset_welcome_message(reply.guild.id)
                                embededit = discord.Embed(
                                    description=f'<:Check:845178458426179605> **Reset welcome '
                                                f'messages for channels and disabled them.**',
                                    color=0x08d5f7)
                                # Edit the message.
                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()
                                break

                            elif "image" in str(reply.content.lower()):
                                set_welcome_card(1, reply.guild.id)
                                set_welcome_channel(reply.channel.id, reply.guild.id)
                                embededit = discord.Embed(
                                    description=f'<:Check:845178458426179605> **{ctx.message.channel} set'
                                                f' to welcome message channel.**',
                                    color=0x08d5f7)

                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()
                                inwelcomesetup = False
                                break
                            elif "text" in str(reply.content.lower()):
                                embededit = await send_embed(ctx, send_option=2, title=f"**Welcome Message Setup**",
                                                             description=f"**Respond with the text you'd like to use"
                                                                         f" for the welcome message.**",
                                                             color=0x08d5f7,
                                                             thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                             fields=[('Wildcards:', "%USER%, %SERVER%", True),
                                                                     ('Example:',
                                                                      "Hey %USER%, glad you're here, welcome to"
                                                                      " %SERVER%!", True)])
                                # Edit the message.
                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()
                                textreply = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                                textsetup = True
                                inwelcomesetup = False
                                if textreply:
                                    set_welcome_channel(textreply.channel.id, textreply.guild.id)
                                    set_welcome_message(str(textreply.content), textreply.guild.id)
                                    embededit = await send_embed(ctx, send_option=2,
                                                                 title=f"**{textreply.guild}'s welcome message has "
                                                                       f"been set.**",
                                                                 description=f"Channel: {textreply.channel} \n"
                                                                             f"Message:{textreply.content}",
                                                                 color=0x08d5f7)
                                    await pogsetupid.edit(embed=embededit)
                                    set_welcome_card(0, reply.guild.id)
                                    await textreply.delete()
                                    await self.bot.wait_for('message', timeout=5, check=checkAuthor)
                                    textsetup = False
                                    break
                            elif "both" in str(reply.content.lower()):
                                embededit = await send_embed(ctx, send_option=2, title=f"**Welcome Message Setup**",
                                                             description=f"**Respond with the text you'd like to use for "
                                                                         f"the welcome message.**", color=0x08d5f7,
                                                             thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                             fields=[('Wildcards:', "%USER%, %SERVER%", True),
                                                                     ('Example:',
                                                                      "Hey %USER%, glad you're here, welcome to"
                                                                      " %SERVER%!", True)])
                                # Edit the message.
                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()
                                bothsetup = True
                                bothreply = await self.bot.wait_for('message', timeout=60, check=checkAuthor)
                                inwelcomesetup = False
                                if bothreply:
                                    set_welcome_message(str(bothreply.content), bothreply.guild.id)
                                    set_welcome_card(1, bothreply.guild.id)
                                    set_welcome_channel(bothreply.channel.id, bothreply.guild.id)
                                    embededit = await send_embed(ctx, send_option=2,
                                                                 title=f"**{bothreply.guild}'s welcome message has "
                                                                       f"been set.**",
                                                                 description=f"Channel: {bothreply.channel} \n"
                                                                             f"Message:{bothreply.content}",
                                                                 color=0x08d5f7)
                                    await pogsetupid.edit(embed=embededit)
                                    await bothreply.delete()
                                    await self.bot.wait_for('message', timeout=5, check=checkAuthor)
                                    bothsetup = False
                                    break
                            else:
                                embededit = await send_embed(ctx, send_option=2, title=f"**Pogbot Setup**",
                                                             color=0x08d5f7,
                                                             thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                             description="Respond with any menu option to proceed.",
                                                             fields=[('Settings', 'Basic server settings.', True),
                                                                     ('Moderator', "Moderator settings.", True),
                                                                     ('Reactions', "Setup role reactions.", True),
                                                                     ('Commands', "Configure custom commands.",
                                                                      True),
                                                                     ('Logs', "Enable event logs.", True),
                                                                     ('Switcher', "Turn on/off commands.", True)
                                                                     ])
                                await pogsetupid.edit(embed=embededit)
                                await reply.delete()
                                inwelcomesetup = False
                        elif "role" in str(reply.content.lower()):
                            # If found, then form the embed.
                            embededit = await send_embed(ctx, send_option=2, title=f"**Role Handout Setup**",
                                                         description=f"**Respond with the Role ID you'd like to hand "
                                                                     f"out to users when they join the server.**",
                                                         color=0x08d5f7,
                                                         thumbnail='https://i.imgur.com/rYKYpDw.png')
                            # Edit the message.
                            await pogsetupid.edit(embed=embededit)
                            await reply.delete()
                            reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                        elif "dm" in str(reply.content.lower()):
                            embededit = await send_embed(ctx, send_option=2,
                                                         title=f"**Direct Message Welcome Setup**",
                                                         description=f"**Respond with the text you'd like to use for "
                                                                     f"the welcome message.**", color=0x08d5f7,
                                                         thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                         fields=[
                                                             ('Wildcards:', "%USER%, %SERVER%, %CHANNEL%", True),
                                                             ('Example:', "Hey %USER%, glad you're here, welcome to"
                                                                          " %SERVER%! Come join us in %CHANNEL%.",
                                                              True)])
                            # Edit the message.
                            await pogsetupid.edit(embed=embededit)
                            await reply.delete()
                            reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)
                        else:
                            embededit = await send_embed(ctx, send_option=2, title=f"**Pogbot Setup**",
                                                         color=0x08d5f7,
                                                         thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                         description="Respond with any menu option to proceed.",
                                                         fields=[('Settings', 'Basic server settings.', True),
                                                                 ('Moderator', "Moderator settings.", True),
                                                                 ('Reactions', "Setup role reactions.", True),
                                                                 ('Commands', "Configure custom commands.", True),
                                                                 ('Logs', "Enable event logs.", True),
                                                                 ('Switcher', "Turn on/off commands.", True)
                                                                 ])
                            await pogsetupid.edit(embed=embededit)
                            await reply.delete()
                            inwelcomesetup = False

                    # Look for pre in lowercase message
                    if "pre" in str(reply.content.lower()):
                        # If it's found then form the embed.
                        trueprefix = await get_prefix(self.bot, ctx)
                        embededit = await send_embed(ctx, send_option=2, title=f"**Prefix Setting**",
                                                     description="Respond with a new prefix for the bot.",
                                                     color=0x08d5f7, thumbnail='https://i.imgur.com/rYKYpDw.png',
                                                     fields=[('Current Prefix', f"{trueprefix[2]}", True)])
                        # Edit the message.
                        await pogsetupid.edit(embed=embededit)
                        # Delete the user message.
                        await reply.delete()
                        # Set setup to false.
                        pogsetup = False
                        # Set prefix setup to true.
                        prefixsetup = True
                        reply = await self.bot.wait_for('message', timeout=20, check=checkAuthor)

                        # Set the prefix var to the message.
                        prefix = reply.content
                        # connect to db.
                        conn = sqlite3.connect('prefs.db')
                        # Str for connection type.
                        conn.text_factory = str
                        # Define cursor.
                        cur = conn.cursor()
                        # Update the servers table, set prefix to new prefix where the server ID matches this one.
                        cur.execute(f"UPDATE servers SET Prefix = '{prefix}' WHERE ServerID = '{ctx.guild.id}'")
                        # Commit the changes.
                        conn.commit()
                        # Close the database.
                        conn.close()
                        # Setup the embed.
                        embededit = discord.Embed(color=0x08d5f7,
                                                  description=f'<:Check:845178458426179605> **Bot prefix changed to {prefix}**')
                        # Edit the original message
                        await pogsetupid.edit(embed=embededit)
                        # Turn off Prefix setup.
                        prefixsetup = False
                        # Delete the message sent by user.
                        await reply.delete()
                        break
                except asyncio.TimeoutError:
                    embedexpire = discord.Embed(description='<:Check:845178458426179605> **Exiting setup...**',
                                                color=0x08d5f7)
                    # Edit the Original Message.
                    await pogsetupid.edit(embed=embedexpire)
                    await asyncio.sleep(0.4)
                    await pogsetupid.delete()
                    inwelcomesetup = False
                    break
        else:
            # Sending a message saying the user has to be admin to run the command, keeping the message ID as a var.
            denymessage = await send_embed(ctx,
                                           description=f'<:Check:845178458426179605> **You must have ADMINISTRATOR '
                                                       f'to run setup.**',
                                           color=0x08d5f7)
        current_users.remove(ctx.guild.id)


def setup(bot):
    bot.add_cog(Config(bot))
