#!/usr/bin/env python3

import json
import os
import numpy as np
import pickle
from itertools import combinations

from recommendation_system import Recommendation_System


def create_recommendations(bans, champion_dict):
    #loading champion info
    # data_path = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), 'data')
    data_path = os.path.join(os.path.abspath(os.getcwd()), 'data')
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
    #dictonary matching champion name with its ordinal number
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
    recom_system = Recommendation_System(model, synergy, counter,
                                                  champ2num)
    champions = list(champion_dict.keys())
    teams = list(champion_dict.values())
    #adding bans and champions to recommmendation object
    recom_system.add_bans(bans)
    recom_system.add_champs(champions, teams)
    rec_dict100 = recom_system.recommend_champ(team_to_recommend=100)
    rec_dict200 = recom_system.recommend_champ(team_to_recommend=200)
    pos_picks100 = [(k,v) for k, v in rec_dict100.items()]
    pos_picks200 = [(k,v) for k, v in rec_dict200.items()]

    rec_dict = dict()
    rec_dict[100] = rec_dict100
    rec_dict[200] = rec_dict200

    pos_picks = dict()
    pos_picks[100] = pos_picks100
    pos_picks[200] = pos_picks200

    #create prediction, can be part of class in the future
    num_champions = len(id2number)
    match = {}
    match[100] = []
    match[200] = []
    for champ, team in champion_dict.items():
        if team == 100:
            match[100].append(champ2num[champ])
        if team == 200:
            match[200].append(champ2num[champ])
    feature_vector = np.zeros((2 * num_champions + 2))
    for champion_id1 in match[100]:
        feature_vector[champion_id1] = 1
    for champion_id2 in match[200]:
        feature_vector[champion_id2 + num_champions] = 1
    synergy100 = 0
    synergy200 = 0
    for champion_id1, champion_id2 in combinations(match[100], 2):
        synergy100 += synergy[champion_id1, champion_id2]
    for champion_id1, champion_id2 in combinations(match[200], 2):
        synergy200 += synergy[champion_id1, champion_id2]

    len_t100 = len(list(combinations(match[100], 2)))
    len_t200 = len(list(combinations(match[200], 2)))
    if len_t100 == len_t200:
        if len_t100 > 0:
            synergy100 /= len_t100
            synergy200 /= len_t200
    elif len_t100 > len_t200:
        synergy100 /= len_t100
        synergy200 += (len_t100 - len_t200) * 0.5
        synergy200 /= len_t100
    else:
        synergy200 /= len_t200
        synergy100 += (len_t200 - len_t100) * 0.5
        synergy100 /= len_t200
    synergy_value = synergy100 - synergy200

    counter_value = 0
    count_num = 0
    for champion_id1 in match[100]:
        for champion_id2 in match[200]:
            count_num += 1
            counter_value += counter[champion_id1, champion_id2]
    if count_num > 0:
        counter_value = (counter_value / count_num) - 0.5
    feature_vector[2 * num_champions] = synergy_value
    feature_vector[2 * num_champions + 1] = counter_value
    prediction = model.predict_proba(np.expand_dims(feature_vector, axis=0))[0]


    return rec_dict, pos_picks, prediction
