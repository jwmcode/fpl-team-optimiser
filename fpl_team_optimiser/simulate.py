import pandas as pd


# assume: no chips, no transfers, no captain bonus
# squad 2d list, one list for first 11, one for subs
# only works for 21-22 and 20-21 data because of player name format differences in earlier data
def simulate_season(squad, season="2020-21"):

    df_all = pd.read_csv(f"../data/{season}/gws/merged_gw.csv")
    merged_squad = squad[0] + squad[1]
    df_squad = df_all[df_all['name'].str.contains('|'.join(merged_squad))].reset_index(drop=True)

    total_points = 0
    for gw_num in range(1, df_squad['GW'].nunique() + 2):
        for player in squad[0]:
            player_gw_df = df_squad[(df_squad['name'] == player)].GW.reset_index(drop=True)
            if gw_num in player_gw_df.values:
                gw_points = df_squad[(df_squad['name'] == player) & (df_squad['GW'] == gw_num)]['total_points'].sum()
                total_points += gw_points

    print(f'\ntotal points: {total_points}')


if __name__ == '__main__':
    test_squad = [['Trent Alexander-Arnold'], ['Aaron Cresswell']]
    simulate_season(test_squad)
