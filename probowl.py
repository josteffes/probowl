import streamlit as st
import pandas as pd
from sleeper_wrapper import League, Players

# --- Constants ---
LEAGUE_ID = '1048276012670267392'  # Replace with your league ID
league = League(LEAGUE_ID)
players_data = Players().get_all_players()

# --- User Inputs ---
week = 18

# --- Helper Functions ---
def get_matchup_points(league, week):
    """Fetch matchups and calculate player points."""
    matchups = league.get_matchups(week)
    all_pts = {}
    all_players = []

    for team in matchups:
        points = team['players_points']
        players = team['players']
        all_pts.update(points)
        all_players += players

    df_points = pd.DataFrame.from_dict(all_pts, orient='index').reset_index()
    df_points.columns = ['PlayerID', 'Pts']
    return df_points, all_players

def fetch_player_names(all_players, players_data):
    """Fetch player names and IDs."""
    allnames, allids = [], []
    for player_id in all_players:
        try:
            player_info = players_data[player_id]
            allnames.append(player_info['full_name'])
            allids.append(player_id)
        except KeyError:
            # Handle missing players
            allnames.append(player_id)
            allids.append(player_id)

    return pd.DataFrame({'player_name': allnames, 'id': allids})

def create_roster_dataframe(df_points, df_final, roster_ids, positions):
    """Create a roster dataframe with total points."""
    boolean_series = df_final.id.isin(roster_ids)
    df_roster = df_final[boolean_series][['player_name', 'id']].copy()
    df_roster['pts'] = df_roster['id'].map(df_points.set_index('PlayerID')['Pts'])
    df_roster['pos'] = positions
    df_roster['pos'] = pd.Categorical(df_roster['pos'], ['QB', 'RB', 'WR', 'TE', 'Flex', 'Def', 'NA'])
    df_roster = df_roster.sort_values('pos').reset_index(drop=True)
    total_points = df_roster['pts'].sum()
    df_roster = pd.concat([df_roster, pd.DataFrame({'pos': ['Total'], 'player_name': ['Total'], 'pts': [total_points]})])
    return df_roster[['pos', 'player_name', 'pts']]

# --- Data Processing ---
df_points, all_players = get_matchup_points(league, week)
df_final = fetch_player_names(all_players, players_data)

# Define team rosters and positions
league_name = "Champs"
team1_ids = ['4984', '4046', '4663', '4018', '5859', '4034', '3321', '4950', '2133', '4066']
pos1 = ['QB', 'RB', 'WR', 'WR', 'TE', 'QB', 'RB', 'Flex', 'WR', 'Flex']
team2_ids = ['6770', '7523', '3198', '1466', '4199', '6794', '6786', '2449', '4217', '7547']
pos2 = ['Flex', 'Flex', 'WR', 'WR', 'RB', 'TE', 'WR', 'QB', 'QB', 'RB']
team_names = ['Team Chad', 'Team AJ']

# Create roster dataframes
team1_df = create_roster_dataframe(df_points, df_final, team1_ids, pos1)
team2_df = create_roster_dataframe(df_points, df_final, team2_ids, pos2)

team1_df = team1_df.set_index('pos')
team2_df = team2_df.set_index('pos')

# --- Display Results ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(team_names[0])
    st.table(team1_df)

with col2:
    st.subheader(team_names[1])
    st.table(team2_df)
