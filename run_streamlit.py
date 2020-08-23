import streamlit as st
import os
import json


data_path = os.path.join(os.path.abspath(os.getcwd()), 'data')
path = os.path.join(data_path, 'champion.json')
with open(path, 'r') as f:
    champions = json.load(f)
poss_champ_list = [item for item in champions['data'].keys()]

bans = st.multiselect("Choose bans (10 max):", poss_champ_list)
if len(bans) > 10:
    st.error("There are more than 10 bans.")
team100 = st.multiselect("Choose champions for team blue:", [item for item in poss_champ_list if item not in bans])
team200 = st.multiselect("Choose champions for team purple:", [item for item in poss_champ_list if item not in bans])

if not team100 and not team100:
    st.error("Please select at least one champion.")

if len(team100) > 5:
    st.error("Team blue has more than 5 champions.")

if len(team200) > 5:
    st.error("Team purple has more than 5 champions.")
