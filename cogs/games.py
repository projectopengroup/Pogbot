import asyncio
import random

import discord
from discord.ext import commands

from utils.gamelogic import Connect4Game
from utils.pogesquelle import get_prefix
from utils.pogfunctions import send_embed


# CONNECT4 CODE © 2017 Benjamin Mintz <bmintz@protonmail.com> MIT Licensed

# CONNECT4 CODE is licensed under the MIT License,
# and uses code from SourSpoon, also MIT Licensed.
# The code from SourSpoon is Copyright © 2017 SourSpoon.

# MIT License

# Copyright (c) 2017–2018 bmintz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class Games(commands.Cog, name="Games"):
    CANCEL_GAME_EMOJI = '🚫'
    DIGITS = [str(digit) + '\N{combining enclosing keycap}' for digit in range(1, 8)] + ['🚫']
    VALID_REACTIONS = [CANCEL_GAME_EMOJI] + DIGITS
    GAME_TIMEOUT_THRESHOLD = 60

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def connect4(self, ctx, *, player2: discord.Member):
        """
        Play connect4 with another player
        """
        player1 = ctx.message.author

        game = Connect4Game(
            player1.display_name,
            player2.display_name
        )

        message = await ctx.send(str(game))

        for digit in self.DIGITS:
            await message.add_reaction(digit)

        def check(reaction, user):
            return (
                    user == (player1, player2)[game.whomst_turn() - 1]
                    and str(reaction) in self.VALID_REACTIONS
                    and reaction.message.id == message.id
            )

        while game.whomst_won() == game.NO_WINNER:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check=check,
                    timeout=self.GAME_TIMEOUT_THRESHOLD
                )
            except asyncio.TimeoutError:
                game.forfeit()
                break

            await asyncio.sleep(0.2)
            try:
                await message.remove_reaction(reaction, user)
            except discord.errors.Forbidden:
                pass

            if str(reaction) == self.CANCEL_GAME_EMOJI:
                game.forfeit()
                break

            try:
                # convert the reaction to a 0-indexed int and move in that column
                game.move(self.DIGITS.index(str(reaction)))
            except ValueError:
                pass  # the column may be full

            await message.edit(content=str(game))

        await self.end_game(game, message)

    @classmethod
    async def end_game(cls, game, message):
        await message.edit(content=str(game))
        await cls.clear_reactions(message)

    @staticmethod
    async def clear_reactions(message):
        try:
            await message.clear_reactions()
        except discord.HTTPException:
            pass

    @commands.command(name='blackjack', aliases=['bj'],
                      brief='Play blackjack.',
                      decription='Play a game of blackjack against the computer.')
    async def blackjack(self, ctx):
        deck = ['♠ A', '♠ 2', '♠ 3', '♠ 4', '♠ 5', '♠ 6', '♠ 7', '♠ 8', '♠ 9', '♠ 10', '♠ J', '♠ Q', '♠ K',
                '♦ A', '♦ 2', '♦ 3', '♦ 4', '♦ 5', '♦ 6', '♦ 7', '♦ 8', '♦ 9', '♦ 10', '♦ J', '♦ Q', '♦ K',
                '♣ A', '♣ 2', '♣ 3', '♣ 4', '♣ 5', '♣ 6', '♣ 7', '♣ 8', '♣ 9', '♣ 10', '♣ J', '♣ Q', '♣ K',
                '♥ A', '♥ 2', '♥ 3', '♥ 4', '♥ 5', '♥ 6', '♥ 7', '♥ 8', '♥ 9', '♥ 10', '♥ J', '♥ Q', '♥ K']

        def get_total(cards):
            total = 0
            values = []
            aces = []
            for pcard in cards:
                suit, value = pcard.split(" ")
                if value != "A":
                    values.append(value)
                elif value == "A":
                    aces.append(value)
            for value in values:
                if value == "K" or value == "Q" or value == "J":
                    total += 10
                else:
                    total += int(value)
            for value in aces:
                if value == "A" and total <= 10:
                    total += 11
                elif value == "A" and total > 10:
                    total += 1
            return total

        def get_cards(hand):
            card_list_string = ""
            for card in range(0, len(hand)):
                if card >= (len(hand)-1):
                    card_list_string += f"`{hand[card]}`"
                else:
                    card_list_string += f"`{hand[card]}`, "
            return card_list_string

        async def end_game(result):
            embed_color = None
            if result == "Win":
                embed_color = discord.Colour.green()
            elif result == "Lose":
                embed_color = discord.Colour.red()
            elif result == "Tied":
                embed_color = 0x08d5f7

            new_embed = await send_embed(ctx, send_option=2, title=f"You {result}", author="Blackjack Game",
                                         author_pfp=ctx.author.avatar_url,
                                         description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                     f"{get_cards(user_hand)}\nTotal: "
                                                     f"`{get_total(user_hand)}`\n"
                                                     f"**Dealer's Hand**\nCards: "
                                                     f"{get_cards(dealer_hand)}\nTotal: "
                                                     f"`{get_total(dealer_hand)}`",
                                         color=embed_color)
            await game_embed.edit(embed=new_embed)
            return

        def checkAuthor(message):
            return message.author.id == ctx.author.id and message.guild.id == ctx.guild.id

        user_hand = []
        dealer_hand = []
        u_initial_cards = random.sample(deck, 2)
        for card in u_initial_cards:
            user_hand.append(card)
            deck.remove(card)
        d_initial_cards = random.sample(deck, 2)
        for card in d_initial_cards:
            dealer_hand.append(card)
            deck.remove(card)

        game_embed = await send_embed(ctx, send_option=1, author="Blackjack Game", author_pfp=ctx.author.avatar_url,
                                      description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                  f"{get_cards(user_hand)}\nTotal: "
                                                  f"`{get_total(user_hand)}`\n"
                                                  f"**Dealer's Hand**\nCards: "
                                                  f"`{dealer_hand[0]}`, `?`\nTotal: "
                                                  f"`?`",
                                      color=0x08d5f7, footer="Reply with **hit** or **stand**")

        if get_total(user_hand) == 21:
            await end_game("Win")
            return

        while True:
            try:
                user_move = await self.bot.wait_for('message', timeout=30, check=checkAuthor)
                if user_move.content.lower() == "h" or user_move.content.lower() == "hit":
                    drawn_card = random.choice(deck)
                    user_hand.append(drawn_card)
                    deck.remove(drawn_card)
                    if get_total(user_hand) > 21:
                        await end_game("Lose")
                        return
                    elif get_total(user_hand) == 21:
                        await end_game("Win")
                        return

                elif user_move.content.lower() == "s" or user_move.content.lower() == "stand":
                    while True:
                        if get_total(dealer_hand) >= 17:
                            if get_total(dealer_hand) == 17 and ("♠ A" in dealer_hand or "♦ A" in dealer_hand or "♣ A" in dealer_hand or "♥ A" in dealer_hand):
                                drawn_card = random.choice(deck)
                                dealer_hand.append(drawn_card)
                                deck.remove(drawn_card)
                                if get_total(dealer_hand) > 21:
                                    await end_game("Win")
                                    return
                            else:
                                if get_total(dealer_hand) > get_total(user_hand):
                                    await end_game("Lose")
                                    return
                                elif get_total(dealer_hand) < get_total(user_hand):
                                    await end_game("Win")
                                    return
                                elif get_total(dealer_hand) == get_total(user_hand):
                                    await end_game("Tied")
                                    return
                        else:
                            drawn_card = random.choice(deck)
                            dealer_hand.append(drawn_card)
                            deck.remove(drawn_card)
                            if get_total(dealer_hand) > 21:
                                await end_game("Win")
                                return

                new_embed = await send_embed(ctx, send_option=2, author="Blackjack Game", author_pfp=ctx.author.avatar_url,
                                             description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                         f"{get_cards(user_hand)}\nTotal: "
                                                         f"`{get_total(user_hand)}`\n"
                                                         f"**Dealer's Hand**\nCards: "
                                                         f"`{dealer_hand[0]}`, `?`\nTotal: "
                                                         f"`?`",
                                             color=0x08d5f7, footer="Reply with hit or stand")
                await game_embed.edit(embed=new_embed)
            except asyncio.TimeoutError:
                new_embed = await send_embed(ctx, send_option=2, title=f"You Timed Out", author="Blackjack Game",
                                             author_pfp=ctx.author.avatar_url,
                                             description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                         f"{get_cards(user_hand)}\nTotal: "
                                                         f"`{get_total(user_hand)}`\n"
                                                         f"**Dealer's Hand**\nCards: "
                                                         f"{get_cards(dealer_hand)}\nTotal: "
                                                         f"`{get_total(dealer_hand)}`",
                                             color=discord.Colour.red())
                await game_embed.edit(embed=new_embed)
                return


def setup(bot):
    bot.add_cog(Games(bot))
