import streamlit as st
import os
import json


data_path = os.path.join(os.path.abspath(os.getcwd()), 'data')
path = os.path.join(data_path, 'champion.json')
with open(path, 'r') as f:
    champions = json.load(f)
poss_champ_list = [item for item in champions['data'].keys()]
