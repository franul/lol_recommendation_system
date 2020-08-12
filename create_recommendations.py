#!/usr/bin/env python3

import csv
import json
import os
import numpy as np
import pickle

from recommendation_system import recommendation_system


def create_recommendations(bans_path, champion_path, output_path,
                           team_to_recommend):
    #loading champion info
    data_path = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), 'data')
    path = os.path.join(data_path, 'champion.json')
    with open(path, 'r') as f:
        champions = json.load(f)
    id2champ = {}
    champ2id = {}
    id2number = {}
    number2id = {}
    for i, key in enumerate(champions['data'].keys()):
        #champion name
        id_name = champions['data'][key]['id']
        #champion unique id
        id_num = int(champions['data'][key]['key'])
        id2champ[id_num] = id_name
        champ2id[id_name] = id_num
        id2number[id_num] = i
        number2id[i] = id_num
    #dictonarz matching champion name with its ordinal number
    champ2num = {k: id2number[v] for k, v in champ2id.items()}
    #loading synergy, counter matrices
    path = os.path.join(data_path, 'synergy.npy')
    with open(path, 'rb') as f:
        synergy = np.load(f)
    path = os.path.join(data_path, 'counter.npy')
    with open(path, 'rb') as f:
        counter = np.load(f)

    #loading model
    path = os.path.join(data_path, 'logistic_regression_model.sav')
    with open(path, 'rb') as f:
        model = pickle.load(f)
    recommendation_system = recommendation_system(model, synergy, counter,
                                                  champ2num)
    #loading champion bans and names
    bans = []
    with open(bans_path) as f:
        lines = f.readlines()
        for line in lines:
            ban = line.strip()
            try:
                ban = int(ban)
            except:
                pass
            bans.append()

    #loading champion bans and names
    champions = []
    teams = []
    with open(champion_path) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            words = line.split()
            champion = words[0]
            try:
                champion = int(champion)
            except:
                pass
            team = words[1]
            try:
                team = int(team)
            except:
                pass
            champions.append(champion)
            teams.append(team)

        #adding bans and champions to recommmendation object
        recommendation_system.add_bans(bans)
        recommendation_system.add_champs(champions, teams)
        rec_dict = recommendation_system.recommend_champ(team_to_recommend=team_to_recommend)
        pos_picks = [(k,v) for k, v in rec_dict.items()  if v >= 0.5]
        return rec_dict, pos_picks
