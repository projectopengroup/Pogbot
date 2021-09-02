import logging

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

# import index.py
# will need to take a list of permissioned servers for the slash commands
# probably stored int he same place as the token

from utils.databaseController import add_scores, add_user, add_team, reset_opp_flag, set_opponent, get_all_results, \
    check_admin, get_admins, get_user_info, get_stat_leaders, remove_user, get_team_ranks, get_team_players, \
    get_team_name, get_missing_scores
from utils.embed_creator import create_embed

log = logging.getLogger(__name__)


async def reset_opponents():
    print("Testing")
    await reset_opp_flag()


class slash_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        scheduler = AsyncIOScheduler()
        scheduler.add_job(reset_opponents, CronTrigger(hour=15, minute=50))
        scheduler.start()

    @cog_ext.cog_slash(name="Add_Player", description="Add a player to your team", guild_ids=lvlBot.permed_servers,
                       options=[
                           create_option(
                               name="name",
                               description="The players in game name",
                               option_type=3,
                               required=True),
                           create_option(
                               name="onbehalfof",
                               description="on behalf of another user (tag them)",
                               option_type=6,
                               required=False
                           )
                       ])
    async def addPlayer(self, ctx, name, onbehalfof: discord.member = None):
        if onbehalfof:
            if check_admin(ctx.author.id):
                userid = onbehalfof.id
            else:
                admins = get_admins(ctx.guild.id)
                embed = create_embed("Unable to add player", self.bot)
                embed.add_field(name="You do not have Admin privileges",
                                value="Adding a player on belhalf of another user requires Admin access, please speak contact:\n".format(
                                    "\n".join(admins)), inline=False)
                await ctx.send(embed=embed)
                return
        else:
            userid = ctx.author.id

        team_name = add_user(ctx.guild.id, userid, name)
        embed = create_embed("Added Player to the team", self.bot)
        embed.add_field(name="Added {} to {}".format(name, team_name),
                        value="Welcome {}, you have been added to the database, you can now add your scores and get data".format(
                            name), inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Remove_Player", description="Remove a player from your team",
                       guild_ids=lvlBot.permed_servers,
                       options=[create_option(
                           name="in_game_name",
                           description="In game name of the player to be removed",
                           option_type=3,
                           required=True)
                       ])
    async def remove_player(self, ctx, inGameName):
        embed = create_embed("Remove Player", self.bot)
        if check_admin(ctx.author.id):
            team = remove_user(server_id=ctx.guild.id, in_game_name=inGameName)
            if team:
                embed.add_field(name="**Player removed**", value="{} has been removed from {}".format(inGameName, team))
            else:
                embed.add_field(name="**Player not removed**",
                                value="No player with the name {} was found on {}".format(inGameName, team))
        else:
            admins = get_admins(ctx.guild.id)
            embed.add_field(name="**You do not have Admin privileges**",
                            value="Adding a score on belhalf of another user requires Admin access, please speak contact:\n".format(
                                "\n".join(admins)), inline=False)
        ctx.send(embed=embed)

    @cog_ext.cog_slash(name='Add_Score', guild_ids=lvlBot.permed_servers,
                       description="Get the price of a player",
                       options=[
                           create_option(
                               name="score",
                               description="Total points scored",
                               option_type=4,
                               required=True
                           ), create_option(
                               name="ints",
                               description="Number of ints thrown (excluding 2pt attempts)",
                               option_type=4,
                               required=True
                           ), create_option(
                               name="fumbles",
                               description="Numbers of fumbles lost (excluding 2pt attempts",
                               option_type=4,
                               required=True
                           ), create_option(
                               name="onbehalfof",
                               description="on behalf of another user (tag them)",
                               option_type=6,
                               required=False
                           )
                       ])
    async def add_scores(self, ctx, score: int, ints: int, fumbles: int, onbehalfof: discord.member = None):
        log.info(
            "Got score update from request from user: {0} on server {1}, id: {2}".format(str(ctx.author),
                                                                                         ctx.guild.name,
                                                                                         ctx.guild.id))

        # powerDiff = yourPower - theirPower
        # if powerDiff >= 0:
        #     isNeg = False
        # else:
        #     isNeg = True
        # powerDiff = abs(powerDiff)
        # if 0 <= powerDiff < 99:
        #     ratingDiff = 0
        # elif 100 <= powerDiff < 249:
        #     ratingDiff = 1
        # elif 250 <= powerDiff < 449:
        #     ratingDiff = 2
        # elif 450 <= powerDiff < 699:
        #     ratingDiff = 3
        # elif 700 <= powerDiff < 999:
        #     ratingDiff = 4
        # else:
        #     ratingDiff = 5
        # if isNeg:
        #     ratingDiff = -abs(ratingDiff)
        #
        # total_diff = yourOffence - theirDefence + ratingDiff
        if onbehalfof:
            if check_admin(ctx.author.id):
                userid = onbehalfof.id
            else:
                admins = get_admins(ctx.guild.id)
                embed = create_embed("Unable to add score", self.bot)
                embed.add_field(name="**You do not have Admin privileges**",
                                value="Adding a score on belhalf of another user requires Admin access, please speak contact:\n".format(
                                    "\n".join(admins)), inline=False)
                await ctx.send(embed)
                return
        else:
            userid = ctx.author.id
        in_game_name = add_scores(userid, score, ints, fumbles, ctx.guild.id)
        if in_game_name[0]:
            embed = create_embed("Added Scores to the database", self.bot)
            embed.add_field(name="**Added stats for user: {}**".format(in_game_name[1]),
                            value="Score: {}\nInterceptions: {}\nFumbles: {}".format(score, ints, fumbles),
                            inline=False)
        else:
            embed = create_embed("Unable to add scores", self.bot)
            embed.add_field(name="**Reason**", value=in_game_name[1], inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Add_Team", description="Add a team to the database", guild_ids=lvlBot.permed_servers,
                       options=[
                           create_option(
                               name="teamname",
                               description="The in game team name",
                               option_type=3,
                               required=True)
                       ])
    async def addTeam(self, ctx, teamname):
        success = add_team(teamname, ctx.guild.id)
        embed = create_embed("Add Team to the Database", self.bot)
        if success:
            embed.add_field(name="**Added {} to database**".format(teamname),
                            value="Welcome {}, you have been added to the database, you can now add your players".format(
                                teamname), inline=False)
        else:
            embed.add_field(name="**Unable to add Team to the database**",
                            value="This Discord server has already been assigned to a team",
                            inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Set_Opponent", description="Set today's Opponent", guild_ids=lvlBot.permed_servers,
                       options=[
                           create_option(
                               name="opponent_name",
                               description="The opponents in game team name",
                               option_type=3,
                               required=True),
                           create_option(
                               name="opponent_rank",
                               description="The opponents rank",
                               option_type=3,
                               required=True),
                           create_option(
                               name="team_rank",
                               description="Your teams current rank",
                               option_type=3,
                               required=True),
                       ])
    async def setOpponent(self, ctx, opponent_name, opponent_rank, team_rank):
        if not check_admin(ctx.author.id):
            admins = get_admins(ctx.guild.id)
            embed = create_embed("Unable to add player", self.bot)
            embed.add_field(name="You do not have Admin privileges",
                            value="Setting the opponent requires Admin access, please speak contact:\n".format(
                                "\n".join(admins)), inline=False)
            await ctx.send(embed=embed)
            return
        set_opponent(ctx.guild.id, opponent_name, opponent_rank, team_rank)

        embed = create_embed("Set Today's Opponent", self.bot)
        embed.add_field(name="Playing {} today".format(opponent_name),
                        value="Good luck against {}, they are ranked {}".format(
                            opponent_name, opponent_rank), inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Get_stat_leaders", description="Get stats about your performance",
                       guild_ids=lvlBot.permed_servers)
    async def get_set_leaders(self, ctx):
        results = get_stat_leaders(ctx.guild.id)
        embed = create_embed("All time performers", self.bot)
        ppd = results[0]
        embed.add_field(name="**Points Per Drive**",
                        value="1st: {} {} ppd\n2nd: {} {} ppd\n3rd: {} {} ppd".format(ppd[0][0], ppd[0][1],
                                                                                      ppd[1][0], ppd[1][1],
                                                                                      ppd[2][0], ppd[2][1]),
                        inline=False)
        total = results[1]
        embed.add_field(name="**Total Points Scored**",
                        value="1st: {} {} points\n2nd: {} {} points\n3rd: {} {} points".format(total[0][0], total[0][1],
                                                                                               total[1][0], total[1][1],
                                                                                               total[2][0],
                                                                                               total[2][1]),
                        inline=False)
        ints = results[2]
        embed.add_field(name="**Least Ints Thrown**",
                        value="1st: {} {} ints\n2nd: {} {} ints\n3rd: {} {} ints".format(ints[0][0], ints[0][1],
                                                                                         ints[1][0], ints[1][1],
                                                                                         ints[2][0], ints[2][1]),
                        inline=False)

        await ctx.send(embed=embed)
        # await ctx.send(message="test")

    @cog_ext.cog_slash(name="Get_All_Results", description="Get stats about your performance",
                       guild_ids=lvlBot.permed_servers, options=[
            create_option(
                name="onbehalfof",
                description="on behalf of another user (tag them)",
                option_type=6,
                required=False
            )
        ])
    async def get_all_results(self, ctx, onbehalfof: discord.member = None):
        if onbehalfof:
            userid = onbehalfof.id
        else:
            userid = ctx.author.id
        results = get_all_results(userid, ctx.guild.id)
        embed = create_embed("All results for {}".format(results[0]), self.bot)
        if len(results[0]):
            for result in results[1]:
                response = ["Score: {} points".format(result[0]), "Opponent Rank: {}".format(result[2]),
                            "Difference in Rating: {}".format(result[3]), "Fumbles Lost: {}".format(result[4]),
                            "Ints Thrown: {}".format(result[5])]
                embed.add_field(name="**Results against {}**".format(result[1]), value="\n".join(response),
                                inline=False)
        else:
            embed.add_field(name="No Results found", value="There were no results found in the database", inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Get_User_Info", description="Get stats about your performance",
                       guild_ids=lvlBot.permed_servers,
                       options=[
                           create_option(
                               name="onbehalfof",
                               description="on behalf of another user (tag them)",
                               option_type=6,
                               required=False
                           )
                       ])
    async def get_user_info(self, ctx, onbehalfof: discord.member = None):
        if onbehalfof:
            userid = onbehalfof.id
        else:
            userid = ctx.author.id
        results = get_user_info(user_id=userid, server_id=ctx.guild.id)
        if results:
            embed = create_embed("Info about {}".format(results[1]), self.bot)
            embed.add_field(name="Info:",
                            value="{} joined {} on {}\nThey are{} an admin".format(results[1], results[0], results[2],
                                                                                   "" if results[3] == 1 else " not"))
            await ctx.send(embed=embed)
        else:
            embed = create_embed("No results found", self.bot)
            embed.add_field(name="No matching results for that user on this team")
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Get_team_ranks", description="Get stats about your performance",
                       guild_ids=lvlBot.permed_servers)
    async def get_team_ranks(self, ctx):
        ranks = get_team_ranks(ctx.guild.id)
        embed = create_embed("Team Ranks", self.bot)
        embed.add_field(name="**Current Rank**", value=ranks[0][2], inline=False)
        formatted_rank = []
        for rank in ranks[1:]:
            formatted_rank.append(str(rank[2]))
        embed.add_field(name="**Previous Ranks in order**", value="\n".join(formatted_rank), inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Get_team_players", description="Get a list of all the players",
                       guild_ids=lvlBot.permed_servers)
    async def get_team_players(self, ctx):
        players = get_team_players(ctx.guild.id)
        team_name = get_team_name(ctx.guild.id)
        embed = create_embed("Players in {}".format(team_name), self.bot)
        embed.add_field(name="List of current players", value="\n".format(players), inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="Missing_scores", description="Get a list of all the players",
                       guild_ids=lvlBot.permed_servers)
    async def get_team_players(self, ctx):
        players = get_missing_scores(ctx.guild.id)
        embed = create_embed("Scores that are missing from today's match-up", self.bot)
        embed.add_field(name="Players with no scores added", value="\n".join(players), inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(slash_commands(bot))
