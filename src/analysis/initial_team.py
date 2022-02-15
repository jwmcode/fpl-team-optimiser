import pulp
import pandas as pd
from dfply import *


# return optimal 15 player squad
# using https://statnamara.wordpress.com/2021/02/05/finding-the-best-lazy-fantasy-football-team-using-pulp-in-python/
def optimal_squad(dataset="2019-20", maximisation_objective="total_points"):

    # load in data to dataframe
    players_df = pd.read_csv(f"../../data/raw/{dataset}/players_raw.csv")
    players_df['name'] = players_df['first_name'].map(str) + ' ' + players_df['second_name'].map(str)
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
    print("\nFull Squad:")
    for i in range(0, len(players_trim)):
        if pulp.value(x[i]) == 1:
            print("{player}: {points} {objective}, {element_type}, {team}".format(
                player=players_trim["name"][i],
                points=players_trim[maximisation_objective][i],
                element_type=players_trim["element_type"][i],
                team=players_trim["team"][i],
                objective=maximisation_objective
            ))


if __name__ == '__main__':
    optimal_squad()
