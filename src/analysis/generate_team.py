import pulp
from dfply import *
from src.data.update import manual_update_players_csv


def optimal_squad_balanced(season="2022-23", maximisation_objective="total_points", pre_season_updates=False):
    """Return optimal 15 player squad

    Help from https://statnamara.wordpress.com/2021/02/05/finding-the-best-lazy-fantasy-football-team-using-pulp-in-python/
    """

    # load in data to dataframe and remove unnecessary columns
    players_df = pd.read_csv(f"../../data/raw/{season}/players_raw.csv")
    if pre_season_updates:
        players_df = manual_update_players_csv(season=season)
    players_df['name'] = players_df['first_name'].map(str) + ' ' + players_df['second_name'].map(str)
    players_df['form*points'] = players_df.form * players_df.total_points
    players_trim = players_df[["name", maximisation_objective, "now_cost", "element_type", "team"]]

    # Find 15 best players in budget
    x = pulp.LpVariable.dict("player", range(0, len(players_trim)), 0, 1, cat=pulp.LpInteger)
    prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)
    prob += pulp.lpSum(players_trim[maximisation_objective][i] * x[i] for i in range(0, len(players_trim)))
    prob += sum(x[i] for i in range(0, len(players_trim))) == 15
    prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 1) == 2
    prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 2) == 5
    prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 3) == 5
    prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 4) == 3
    prob += sum(x[i] * players_trim["now_cost"][i] for i in range(0, len(players_trim))) <= 1000
    for team_id in np.unique(players_trim["team"]):
        prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["team"][i] == team_id) <= 3
    prob.solve()

    # print squad
    print("Full Squad:")
    for i in range(0, len(players_trim)):
        if pulp.value(x[i]) == 1:
            print("{player}: {points} {objective}, position type {element_type}, team {team}".format(
                player=players_trim["name"][i],
                points=players_trim[maximisation_objective][i],
                element_type=players_trim["element_type"][i],
                team=players_trim["team"][i],
                objective=maximisation_objective
            ))


# todo:unfinished
# stars players get cost bias
def optimal_squad_stars(season="2021-22", maximisation_objective="total_points", pre_season_updates=False,
                        captain_ratio=0.13, vice_captain_ratio=0.1):

    # select two star players first within the star player budget
    # build optimised squad around the star players with max as remaining budget
    return -1


# todo: unfinished
# first 11 gets cost bias. tries team in each formation
def optimal_squad_subs(season="2022-23", maximisation_objective="form*points", pre_season_updates=False,
                       sub_ratio=0.235):

    # load in data to dataframe and remove unnecessary columns
    players_df = pd.read_csv(f"../../data/raw/{season}/players_raw.csv")
    if pre_season_updates:
        players_df = manual_update_players_csv(season=season)
    players_df['name'] = players_df['first_name'].map(str) + ' ' + players_df['second_name'].map(str)
    players_df['form*points'] = players_df.form * players_df.total_points
    players_trim = players_df[["name", maximisation_objective, "now_cost", "element_type", "team"]]

    formations = [[4, 4, 2], [4, 5, 1], [4, 3, 3], [5, 4, 1], [5, 3, 2], [5, 2, 3], [3, 4, 3], [3, 5, 2]]
    optimal_team = None

    for formation in formations:
        # Find 15 best players in budget
        x = pulp.LpVariable.dict("player", range(0, len(players_trim)), 0, 1, cat=pulp.LpInteger)
        prob = pulp.LpProblem("FantasyFootball", pulp.LpMaximize)
        prob += pulp.lpSum(players_trim[maximisation_objective][i] * x[i] for i in range(0, len(players_trim)))
        prob += sum(x[i] for i in range(0, len(players_trim))) == sum(formation, 1)
        prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 1) == 1
        prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 2) == formation[0]
        prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 3) == formation[1]
        prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["element_type"][i] == 4) == formation[2]
        prob += sum(x[i] * players_trim["now_cost"][i] for i in range(0, len(players_trim))) <= 1000 - (
                    1000 * sub_ratio)
        for team_id in np.unique(players_trim["team"]):
            prob += sum(x[i] for i in range(0, len(players_trim)) if players_trim["team"][i] == team_id) <= 3
        prob.solve()

        # print squad
        print("Full Squad:")
        for i in range(0, len(players_trim)):
            if pulp.value(x[i]) == 1:
                print("{player}: {points} {objective}, position type {element_type}, team {team}".format(
                    player=players_trim["name"][i],
                    points=players_trim[maximisation_objective][i],
                    element_type=players_trim["element_type"][i],
                    team=players_trim["team"][i],
                    objective=maximisation_objective
                ))


# todo: needs 3 club player limit
def random_squad(season="2021-22"):
    """ Returns random 25 player squad within constraints
    """

    players_df = pd.read_csv(f"../../data/raw/{season}/players_raw.csv")
    players_df['name'] = players_df['first_name'].map(str) + ' ' + players_df['second_name'].map(str)
    players_df = players_df[["name", "now_cost", "element_type", "team"]]
    players_df['in_squad'] = 0

    # iterate over each squad position
    for _ in range(0, 15):

        if len(players_df[(players_df['element_type'] == 1) & (players_df['in_squad'] == 1)]) < 2:
            rand_gkp_index = players_df.query("in_squad == 0 & element_type == 1").sample(n=1).index[0]
            players_df.loc[rand_gkp_index, "in_squad"] = 1

        elif len(players_df[(players_df['element_type'] == 2) & (players_df['in_squad'] == 1)]) < 5:
            rand_def_index = players_df.query("in_squad == 0 & element_type == 2").sample(n=1).index[0]
            players_df.loc[rand_def_index, "in_squad"] = 1

        elif len(players_df[(players_df['element_type'] == 3) & (players_df['in_squad'] == 1)]) < 5:
            rand_mid_index = players_df.query("in_squad == 0 & element_type == 3").sample(n=1).index[0]
            players_df.loc[rand_mid_index, "in_squad"] = 1

        elif len(players_df[(players_df['element_type'] == 4) & (players_df['in_squad'] == 1)]) < 3:
            rand_fwd_index = players_df.query("in_squad == 0 & element_type == 4").sample(n=1).index[0]
            players_df.loc[rand_fwd_index, "in_squad"] = 1

        # replace most expensive player with random player of same position whilst the total cost is more than 1000
        while players_df.loc[players_df['in_squad'] == 1, 'now_cost'].sum() > 1000:
            old_player_index = players_df.loc[players_df['in_squad'] == 1, 'now_cost'].idxmax()
            old_player_position = players_df.loc[old_player_index, 'element_type']
            players_df.loc[old_player_index, "in_squad"] = 0
            new_player_index = \
                players_df.query(f"in_squad == 0 & element_type == {old_player_position}").sample(n=1).index[0]
            players_df.loc[new_player_index, "in_squad"] = 1

    return players_df.query("in_squad == 1").sort_values(by=["element_type"])


if __name__ == '__main__':
    optimal_squad_balanced()
