import os
import shutil
from src.data.scraper import Scraper
import pandas as pd


# update raw data from vastaav repo, overwriting old data
def update_all_raw_data():
    os.chdir("../../data")
    if os.path.exists("raw"):
        shutil.rmtree("raw")
    print('Updating fpl data...')
    os.system("svn export https://github.com/vaastav/Fantasy-Premier-League/trunk/data")
    os.system("mv data raw")


# update raw data from specific season
def update_season_data():
    pass


# take players_raw.csv from specific season and update with the latest player data scraped directly from fpl
# can be used before season begins to get updated player club, position and price data before vastaav releases his
def manual_update_players_csv(season="2021-22"):
    base_data = pd.read_csv(f"../../data/raw/{season}/players_raw.csv")

    s = Scraper()
    updates = s.get_players()[['second_name', 'cost', 'position', 'points', 'team']]
    updates['position'] = updates['position'].map({'GKP': 1, 'DEF': 2, 'MID': 3, 'FWD': 4})
    updates['cost'] = updates['cost'].apply(lambda x: x*10)
    updates = updates.rename(columns={"team": "new_team"})

    # filter out players that aren't in the league anymore
    merged_df = base_data.merge(updates, left_on=['second_name', 'total_points'], right_on=['second_name', 'points'],
                                how='inner')

    # update data
    merged_df['element_type'] = merged_df.loc[merged_df['element_type'] != merged_df['position'], 'element_type'] = \
        merged_df['position']
    merged_df['now_cost'] = merged_df.loc[merged_df['now_cost'] != merged_df['cost'], 'now_cost'] = \
        merged_df['cost']
    merged_df['team'] = merged_df.loc[merged_df['team'] != merged_df['new_team'], 'team'] = \
        merged_df['new_team']

    # remove useless columns and return
    return merged_df.iloc[:, :-len(updates.columns)+1]


if __name__ == '__main__':
    update_all_raw_data()
    # players = manual_update_players_csv()
    # print(players)

