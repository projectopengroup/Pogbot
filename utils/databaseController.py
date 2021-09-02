import sqlite3
from datetime import datetime

global db

# score table variables
PLAYED_AGAINST_KEY = "PLAYED_AGAINST_KEY"
USER_ID = "USER_ID"
SCORE = "SCORE"
RATING_DIFF = "RATING_DIFF"
FUMBLES = "FUMBLES"
INTERCEPTIONS = "INTS"

# team table variable
SERVER_ID = "SERVER_ID"
TEAM_NAME = "TEAM_NAME"
IS_OPP_SET = "IS_OPP_SET"
TEAM_RANK = "TEAM_RANK"

# opponents table variables
TEAM_KEY = "TEAM_KEY"
NAME = "NAME"
RANK = "RANK"

# players table variables
IN_GAME_NAME = "IN_GAME_NAME"
JOIN_DATE = "JOIN_DATE"
ADMIN = "ADMIN"
SET_SCORE = "SET_SCORE"


# This is called from main to take a command line arg for the db, could be hard coded.
def setdb(database_name):
    global db
    db = sqlite3.connect('{}.db'.format(database_name), check_same_thread=False)


def add_team(team_name, serverid):
    if db.execute("select * from TEAMS where {}=?".format(SERVER_ID), (serverid,)).fetchone():
        return False
    else:
        db.execute("insert into TEAMS({}, {}, {}) values(?, ?, ?)".format(TEAM_NAME, SERVER_ID, IS_OPP_SET),
                   (team_name, serverid, 0))
        db.commit()
        return True


def add_user(server_id, user_id, in_game_name):
    team_key = db.execute("select * from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()

    if db.execute("select * from PLAYERS where {}=? AND {}=?".format(TEAM_KEY, USER_ID),
                  (team_key[0], user_id)).fetchone():
        return
    db.execute(
        "insert into PLAYERS({}, {}, {}, {}, {}) values (?,?,?,?,?)".format(TEAM_KEY, IN_GAME_NAME, USER_ID, JOIN_DATE,
                                                                            SET_SCORE),
        (team_key[0], in_game_name, user_id, datetime.today().strftime(
            '%m/%d/%Y'), 0))
    db.commit()
    return team_key[1]


def remove_user(server_id, in_game_name):
    team_key = db.execute("select * from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()
    if not db.execute("select * from PLAYERS where {}=? AND {}=?".format(TEAM_KEY, IN_GAME_NAME),
                  (team_key[0], in_game_name)).fetchone():
        return
    db.execute("DELETE from PLAYERS where {}=? and {}=?".format(TEAM_KEY, IN_GAME_NAME), (team_key[0], in_game_name))
    db.commit()
    return team_key[1]


async def reset_opp_flag():
    db.execute("update TEAMS set {}=0".format(IS_OPP_SET))
    db.execute("update PLAYERS set {}=0".format(SET_SCORE))
    db.commit()


def set_opponent(serverId, opp_name, opp_rank, team_rank):
    team_key = db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (serverId,)).fetchone()[0]
    db.execute("insert into OPPONENTS({}, {}, {}) values(?, ?, ?)".format(TEAM_KEY, NAME, RANK),
               (team_key, opp_name, opp_rank))
    db.execute("update TEAMS set {}=? where {}=?".format(IS_OPP_SET, SERVER_ID), (1, serverId,))
    db.execute("insert into RANKS({}, {}) values(?,?)".format(TEAM_KEY, RANK), (team_key, team_rank))
    db.commit()


def add_scores(user_id, score, interceptions, fumbles_lost, serverid):
    team = db.execute("select * from TEAMS where {}=?".format(SERVER_ID), (serverid,)).fetchone()
    if team[3] == 1:
        player = db.execute("select * from PLAYERS where {}=? AND {}=?".format(TEAM_KEY, USER_ID),
                            (team[0], user_id)).fetchone()
        if player:
            if player[6] == 0:
                opp_id =b.execute("SELECT ID FROM OPPONENTS WHERE {}=? ORDER BY ID DESC".format(TEAM_KEY),
                                    (team[0],)).fetchone()
                db.execute("update PLAYERS set {}=1 where {}=?".format(SET_SCORE, USER_ID), (user_id,))
                db.execute(
                    "insert into SCORES({}, {}, {}, {}, {}, {}) values(?, ?, ?, ?, ?, ?)".format(PLAYED_AGAINST_KEY,
                                                                                                 TEAM_KEY, USER_ID,
                                                                                                 SCORE, FUMBLES,
                                                                                                 INTERCEPTIONS),
                    (opp_id[0], team[0], user_id, score, fumbles_lost, interceptions))
                db.commit()
                return [True, player[2]]
            return [False, "Your score has already been submitted"]
        return [False, "This player is not in the team"]
    return [False, "Please add today's opponent using the /set_opponent command"]


def get_userid_from_username(username):
    name = db.execute("select USER_ID from PLAYERS where {}=?".format(IN_GAME_NAME), (username,)).fetchone()
    if name:
        return name
    return "No player by the name of {} found".format(name)


def get_all_results(user_id, server_id):
    results = []
    team_key = db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()[0]
    scores = db.execute("select * from SCORES where {}=? and {}=?".format(TEAM_KEY, USER_ID),
                        (team_key, user_id)).fetchall()
    player_name = db.execute("select IN_GAME_NAME from PLAYERS where {}=?".format(USER_ID), (user_id,)).fetchone()
    if scores:
        for score in scores:
            opp = db.execute("select * from OPPONENTS where ID=?", (score[1],)).fetchone()
            result = [score[4], opp[2], opp[3], score[5], score[6], score[7]]
            results.append(result)

    return [player_name[0], results]


def get_user_info(user_id, server_id):
    team_info = db.execute("select * from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()
    if not team_info:
        return
    team_name = team_info[1]
    player_info = db.execute("select * from PLAYERS where {}=? AND {}=?".format(TEAM_KEY, USER_ID),
                             (team_info[0], user_id)).fetchone()
    if player_info:
        return [team_name, player_info[2], player_info[4], player_info[5]]
    return


def check_admin(user_id):
    is_admin = db.execute("select ADMIN from PLAYERS where {}=?".format(USER_ID), (user_id,)).fetchone()[0]
    if is_admin == 1:
        return True
    return False


def get_admins(server_id):
    team_key = db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()[0]
    return db.execute("select {} from PLAYERS where {}=? AND {}=?".format(IN_GAME_NAME, TEAM_KEY, ADMIN),
                      (team_key, server_id)).fetchall()


def find_highest_total(scores_map):
    total_per_user = []
    for user, score in scores_map.items():
        total = sum(i[1] for i in score)
        total_per_user.append([score[0][0], total])
    sorted_total = sorted(total_per_user, key=lambda x: x[1], reverse=True)
    return sorted_total[:3]


def find_least_ints(scores_map):
    ints_per_user = []
    for user, score in scores_map.items():
        ints = sum(i[4] for i in score)
        ints_per_user.append([score[0][0], ints])
    sorted_total = sorted(ints_per_user, key=lambda x: x[1], reverse=False)
    return sorted_total[:3]


def get_stat_leaders(server_id):
    team_key = db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()[0]
    players = db.execute("select * from PLAYERS where {}=?".format(TEAM_KEY), (team_key,)).fetchall()
    scores_map = {}
    for player in players:
        scores = db.execute("select * from SCORES where {}=? AND {}=?".format(TEAM_KEY, USER_ID),
                            (team_key, player[3])).fetchall()
        for score in scores:
            scores_map.setdefault(score[3], []).append([player[2], score[4], score[5], score[6], score[7]])
    ppd = find_highest_ppd(scores_map)
    hightest_total = find_highest_total(scores_map)
    least_ints = find_least_ints(scores_map)
    return [ppd, hightest_total, least_ints]


def find_highest_ppd(scores_map):
    ppd_per_user = []
    for user, score in scores_map.items():
        ppd = round(sum(i[1] / 3 for i in score) / len(score), 2)
        ppd_per_user.append([score[0][0], ppd])
    sorted_ppd = sorted(ppd_per_user, key=lambda x: x[1], reverse=True)

    return sorted_ppd[:3]


def get_team_ranks(server_id):
    team_key = db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()[0]
    ranks = db.execute("select * from RANKS where {}=?".format(TEAM_KEY), (team_key,)).fetchall()
    ranks = sorted(ranks, key=lambda x: x[0], reverse=True)
    return ranks


def get_team_players(server_id):
    team_key = db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()[0]
    players = db.execute("select * from PLAYERS where {}=?".format(TEAM_KEY), (team_key,)).fetchall()
    in_game_names = [list[2] for list in players]
    # in_game_names = [item[3] for sublist in players for item in sublist]
    return in_game_names


def get_team_name(server_id):
    return db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()[1]


def get_missing_scores(server_id):
    team_key = db.execute("select ID from TEAMS where {}=?".format(SERVER_ID), (server_id,)).fetchone()[0]
    players = db.execute("select * from PLAYERS where {}=? AND {}=0".format(TEAM_KEY, SET_SCORE),
                         (team_key,)).fetchall()
    in_game_names = [list[2] for list in players]
    return in_game_names
