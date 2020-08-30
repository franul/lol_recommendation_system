import streamlit as st
import os
import json
from create_recommendations import create_recommendations

@st.cache
def load_champions():
    data_path = os.path.join(os.path.abspath(os.getcwd()), 'data')
    path = os.path.join(data_path, 'champion.json')
    with open(path, 'r') as f:
        champions = json.load(f)
    poss_champ_list = [item for item in champions['data'].keys()]
    return poss_champ_list
poss_champ_list = load_champions()
bans = st.multiselect("Choose bans (10 max):", poss_champ_list)
if len(bans) > 10:
    st.error("There are more than 10 bans.")
team100 = st.multiselect("Choose champions for team blue:", [item for item in poss_champ_list if item not in bans])
team200 = st.multiselect("Choose champions for team purple:", [item for item in poss_champ_list if item not in bans])

if len(team100) > 5:
    st.error("Team blue has more than 5 champions.")
    st.stop()

if len(team200) > 5:
    st.error("Team purple has more than 5 champions.")
    st.stop()
champion_list = dict(zip(team100 + team200, [100 for _ in team100] + [200 for _ in team200]))
rec_dict, pos_picks, prediction = create_recommendations(bans, champion_list)
# st.write(rec_dict[100])
# st.write(rec_dict[200])
if len(team200) == 5 and len(team100) == 5:
    st.write('### Prediction for current picks: ')
    st.write('Team blue: {}'.format(str(round(100 * prediction[1], 2))) + '%')
    st.write('Team purple: {}'.format(str(round(100 * prediction[0], 2))) + '%')

if pos_picks[100]:
    st.write('### Recommendations for team blue:')
    for item in pos_picks[100][:20]:
        percentage = round(100 * (item[1] - prediction[1]), 2)
        if percentage > 0:
            percentage = '+' + str(percentage) + '%'
        else:
            percentage = str(percentage) + '%'
        st.write('{}: {}'.format(item[0], percentage))
if pos_picks[200]:
    st.write('### Recommendations for team purple:')
    for item in pos_picks[200][:20]:
        percentage = round(100 * (item[1] - prediction[0]), 2)
        if percentage > 0:
            percentage = '+' + str(percentage) + '%'
        else:
            percentage = str(percentage) + '%'
        st.write('{}: {}'.format(item[0], percentage))
