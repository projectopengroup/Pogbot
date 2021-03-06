import asyncio
import random

import discord
from discord.ext import commands
import requests

from utils.gamelogic import Connect4Game
from utils.pogesquelle import get_prefix, get_global_currency, set_global_currency
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

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                assert isinstance(child, discord.ui.Button)  # just to shut up the linter
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class Games(commands.Cog, name="Games"):
    CANCEL_GAME_EMOJI = '🚫'
    DIGITS = [str(digit) + '\N{combining enclosing keycap}' for digit in range(1, 8)] + ['🚫']
    VALID_REACTIONS = [CANCEL_GAME_EMOJI] + DIGITS
    GAME_TIMEOUT_THRESHOLD = 60

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tictactoe", aliases=['ttt'], brief="Tic Tac Toe",
                      description="Starts a game of tic tac toe.")
    async def tictactoe(self, ctx):
        await ctx.send('TicTacToe, X goes first!', view=TicTacToe())

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
    async def blackjack(self, ctx, bet=0):
        deck = ['♠ A', '♠ 2', '♠ 3', '♠ 4', '♠ 5', '♠ 6', '♠ 7', '♠ 8', '♠ 9', '♠ 10', '♠ J', '♠ Q', '♠ K',
                '♦ A', '♦ 2', '♦ 3', '♦ 4', '♦ 5', '♦ 6', '♦ 7', '♦ 8', '♦ 9', '♦ 10', '♦ J', '♦ Q', '♦ K',
                '♣ A', '♣ 2', '♣ 3', '♣ 4', '♣ 5', '♣ 6', '♣ 7', '♣ 8', '♣ 9', '♣ 10', '♣ J', '♣ Q', '♣ K',
                '♥ A', '♥ 2', '♥ 3', '♥ 4', '♥ 5', '♥ 6', '♥ 7', '♥ 8', '♥ 9', '♥ 10', '♥ J', '♥ Q', '♥ K']
        currency = get_global_currency(ctx.author.id)

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
                if card >= (len(hand) - 1):
                    card_list_string += f"`{hand[card]}`"
                else:
                    card_list_string += f"`{hand[card]}`, "
            return card_list_string

        async def end_game(result):
            embed_color = None
            footer_str = ""
            if result == "Win":
                currency = get_global_currency(ctx.author.id)
                set_global_currency(ctx.author.id, currency + bet)
                footer_str = f"You won {bet} coins"
                embed_color = discord.Colour.green()
            elif result == "Lose":
                currency = get_global_currency(ctx.author.id)
                set_global_currency(ctx.author.id, currency - bet)
                footer_str = f"You lost {bet} coins"
                embed_color = discord.Colour.red()
            elif result == "Tied":
                embed_color = 0x08d5f7
                footer_str = f"You got your bet of {bet} coins back"


            new_embed = await send_embed(ctx, send_option=2, title=f"You {result}", author="Blackjack Game",
                                         author_pfp=ctx.author.avatar.url,
                                         description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                     f"{get_cards(user_hand)}\nTotal: "
                                                     f"`{get_total(user_hand)}`\n"
                                                     f"**Dealer's Hand**\nCards: "
                                                     f"{get_cards(dealer_hand)}\nTotal: "
                                                     f"`{get_total(dealer_hand)}`", footer=footer_str,
                                         color=embed_color)
            await game_embed.edit(embed=new_embed)
            return

        def checkAuthor(message):
            return message.author.id == ctx.author.id and message.guild.id == ctx.guild.id

        if bet > currency:
            await send_embed(ctx, author="Insufficient Funds", description="<:Pogbot_X:850089728018874368> "
                                         "You do not have enough Pog Coins to make that bet.", color=0x08d5f7)
            return

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

        game_embed = await send_embed(ctx, send_option=1, author="Blackjack Game", author_pfp=ctx.author.avatar.url,
                                      description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                  f"{get_cards(user_hand)}\nTotal: "
                                                  f"`{get_total(user_hand)}`\n"
                                                  f"**Dealer's Hand**\nCards: "
                                                  f"`{dealer_hand[0]}`, `?`\nTotal: "
                                                  f"`?`",
                                      color=0x08d5f7, footer="Reply with hit or stand")

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
                            if get_total(dealer_hand) == 17 and (
                                    "♠ A" in dealer_hand or "♦ A" in dealer_hand or "♣ A" in dealer_hand or "♥ A" in dealer_hand):
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

                new_embed = await send_embed(ctx, send_option=2, author="Blackjack Game",
                                             author_pfp=ctx.author.avatar.url,
                                             description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                         f"{get_cards(user_hand)}\nTotal: "
                                                         f"`{get_total(user_hand)}`\n"
                                                         f"**Dealer's Hand**\nCards: "
                                                         f"`{dealer_hand[0]}`, `?`\nTotal: "
                                                         f"`?`",
                                             color=0x08d5f7, footer="Reply with hit or stand")
                await game_embed.edit(embed=new_embed)
            except asyncio.TimeoutError:
                currency = get_global_currency(ctx.author.id)
                set_global_currency(ctx.author.id, currency - bet)
                new_embed = await send_embed(ctx, send_option=2, title=f"You Timed Out", author="Blackjack Game",
                                             author_pfp=ctx.author.avatar.url,
                                             description=f"**{ctx.author.display_name}'s Hand**\nCards: "
                                                         f"{get_cards(user_hand)}\nTotal: "
                                                         f"`{get_total(user_hand)}`\n"
                                                         f"**Dealer's Hand**\nCards: "
                                                         f"{get_cards(dealer_hand)}\nTotal: "
                                                         f"`{get_total(dealer_hand)}`", footer=f"You lost {bet} coins",
                                             color=discord.Colour.red())
                await game_embed.edit(embed=new_embed)
                return
            
    
    @commands.command()
    async def trivia(self, ctx, *, category="Default"):
        request = None
        if category.lower() == "sports":
            request = requests.get(url="https://opentdb.com/api.php?amount=5&category=21").json()
        else:
            request = requests.get(url="https://opentdb.com/api.php?amount=5").json()
        question_num = 0
        leaderboard = {'leaderboard': []}
        for question in request["results"]:
            question['question'] = question['question'].replace('&quot;', '"')
            question['question'] = question['question'].replace("&#039;", "'")
            question['question'] = question['question'].replace("&amp;", "&")
            if question["type"] == "boolean":
                correct_answer_option = 0
                if "False" == question["correct_answer"]:
                    correct_answer_option = 1

                q_embed = await send_embed(ctx, send_option=1, title=f"**Question {question_num+1}**",
                                           description=f"Q: {question['question']}\n<:OptionA:854536640625508393> True\n"
                                                       f"<:OptionB:854536641519812618> False\n \nCategory: "
                                                       f"{question['category']}\nDifficulty: {question['difficulty']}",
                                           color=0x08d5f7)
                await q_embed.add_reaction("<:OptionA:854536640625508393>")
                await q_embed.add_reaction("<:OptionB:854536641519812618>")
                await asyncio.sleep(15)

                getmsg = await ctx.channel.fetch_message(q_embed.id)
                users = await getmsg.reactions[correct_answer_option].users().flatten()
                for i in range(0, 2):
                    if i == correct_answer_option:
                        pass
                    else:
                        temp_users = await getmsg.reactions[i].users().flatten()
                        for user in temp_users:
                            if user in users:
                                users.remove(user)
                correct_users = "The following users answered correctly: \n \n"
                for user in users:
                    found_user = False
                    for users in leaderboard["leaderboard"]:
                        if user.name == users["name"]:
                            users["score"] = users["score"] + 1
                            found_user = True
                    if not found_user:
                        leaderboard["leaderboard"].append({"name": user.name, "score": 1})
                    correct_users += user.name + "\n"
                if correct_users == "The following users answered correctly: \n \n":
                    correct_users = "No one answered that question correctly."
                await send_embed(ctx, title="Correct Users",
                                 description=correct_users,
                                 color=0x08d5f7)

                a_embed = await send_embed(ctx, send_option=2, title=f"**Question {question_num + 1}**",
                                           description=f"Q: {question['question']}\n<:OptionA:854536640625508393> True\n"
                                                       f"<:OptionB:854536641519812618> False\n \nCategory: "
                                                       f"{question['category']}\nDifficulty: {question['difficulty']}",
                                           footer=f"Correct Answer: {question['correct_answer']}", color=0x08d5f7)
                await q_embed.edit(embed=a_embed)
            else:
                question['correct_answer'] = question['correct_answer'].replace('&quot;', '"')
                question['correct_answer'] = question['correct_answer'].replace("&#039;", "'")
                question['correct_answer'] = question['correct_answer'].replace("&amp;", "&")
                for i in range(0, 3):
                    question['incorrect_answers'][i] = question['incorrect_answers'][i].replace('&quot;', '"')
                    question['incorrect_answers'][i] = question['incorrect_answers'][i].replace("&#039;", "'")
                    question['incorrect_answers'][i] = question['incorrect_answers'][i].replace("&amp;", "&")
                options = [question["correct_answer"], question["incorrect_answers"][0],
                           question["incorrect_answers"][1], question["incorrect_answers"][2]]
                random.shuffle(options)

                correct_answer_option = 0
                for option in range(0, 4):
                    if options[option] == question["correct_answer"]:
                        correct_answer_option = option

                q_embed = await send_embed(ctx, send_option=1, title=f"**Question {question_num + 1}**",
                                           description=f"Q: {question['question']}\n<:OptionA:854536640625508393> "
                                                       f"{options[0]}\n<:OptionB:854536641519812618> {options[1]}\n"
                                                       f"<:OptionC:854536641867415572> {options[2]}\n"
                                                       f"<:OptionD:854541014059581500> {options[3]}\n \n"
                                                       f"Category: {question['category']}\n"
                                                       f"Difficulty: {question['difficulty']}",
                                           color=0x08d5f7)
                await q_embed.add_reaction("<:OptionA:854536640625508393>")
                await q_embed.add_reaction("<:OptionB:854536641519812618>")
                await q_embed.add_reaction("<:OptionC:854536641867415572>")
                await q_embed.add_reaction("<:OptionD:854541014059581500>")
                await asyncio.sleep(15)

                getmsg = await ctx.channel.fetch_message(q_embed.id)
                users = await getmsg.reactions[correct_answer_option].users().flatten()
                for i in range(0, 4):
                    if i == correct_answer_option:
                        pass
                    else:
                        temp_users = await getmsg.reactions[i].users().flatten()
                        for user in temp_users:
                            if user in users:
                                users.remove(user)
                correct_users = "The following users answered correctly: \n \n"
                for user in users:
                    found_user = False
                    for users in leaderboard["leaderboard"]:
                        if user.name == users["name"]:
                            users["score"] = users["score"] + 1
                            found_user = True
                    if not found_user:
                        leaderboard["leaderboard"].append({"name": user.name, "score": 1})
                    correct_users += user.name + "\n"
                if correct_users == "The following users answered correctly: \n \n":
                    correct_users = "No one answered that question correctly."
                await send_embed(ctx, title="Correct Users",
                                 description=correct_users,
                                 color=0x08d5f7)

                a_embed = await send_embed(ctx, send_option=2, title=f"**Question {question_num + 1}**",
                                           description=f"Q: {question['question']}\n<:OptionA:854536640625508393> "
                                                       f"{options[0]}\n<:OptionB:854536641519812618> {options[1]}\n"
                                                       f"<:OptionC:854536641867415572> {options[2]}\n"
                                                       f"<:OptionD:854541014059581500> {options[3]}\n \n"
                                                       f"Category: {question['category']}\n"
                                                       f"Difficulty: {question['difficulty']}",
                                           footer=f"Correct Answer: {question['correct_answer']}", color=0x08d5f7)
                await q_embed.edit(embed=a_embed)
            await asyncio.sleep(4)
            question_num += 1
        leaderboard = sorted(leaderboard["leaderboard"], key=lambda x: x["score"], reverse=True)
        previous_score = 0
        current_place = 1
        standings_str = ""
        for user in range(0, len(leaderboard)):
            if leaderboard[user]["score"] == previous_score:
                pass
            else:
                current_place = user + 1
            standings_str += f"{current_place}. {leaderboard[user]['name']} - {leaderboard[user]['score']}\n"
            previous_score = leaderboard[user]["score"]

        await send_embed(ctx, title="Final Standings", description=standings_str, color=0x08d5f7)


def setup(bot):
    bot.add_cog(Games(bot))
