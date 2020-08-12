#!/usr/bin/env python3

import numpy as np
from itertools import combinations

class recommendation_system:
    def __init__(self, model, synergy, counter, champ2num):
        self.model = model
        self.synergy = synergy
        self.counter = counter
        self.champ2num = champ2num
        self.num2champ = {v: k for k, v in champ2num.items()}
        self.champ_list = champ2num.keys()
        self.champ_list_nums = champ2num.values()
        self.num_champs = len(champ2num)

        self.bans_champs = []
        self.bans_champs_nums = []
        self.champs_t100 = []
        self.champs_t100_nums = []
        self.champs_t200 = []
        self.champs_t200_nums = []

    def add_ban(self, champ):
        if type(champ) == str:
            if champ in self.champ_list:
                if champ in self.bans_champs:
                    print('Champion ' + champ + ' is already in ban list!')
                else:
                    self.bans_champs.append(champ)
                    self.bans_champs_nums.append(champ2num[champ])
            else:
                print('There is no champion with name ' + champ + '!')
        elif type(champ) == int:
            if champ in self.champ_list_nums:
                if champ in self.bans_champs_nums:
                    print('Champion with id' + str(champ) + ' is already in ban list!')
                else:
                    self.bans_champs.append(num2champ(champ))
                    self.bans_champs_nums.append(champ)
            else:
                print('There is no champion with id ' + champ + '!')
        else:
            print('Invalid input type!')

    def add_champ(self, champ, team):
        if type(champ) == str:
            if champ in self.champ_list:
                if champ in self.bans_champs:
                    print('Champion ' + champ + ' was already banned!')
                elif champ in self.champs_t100:
                    print('Champion ' + champ + ' is already in team blue!')
                elif champ in self.champs_t200:
                    print('Champion ' + champ + ' is already in team purple!')
                else:
                    if team == 100 or team == 'blue':
                        self.champs_t100.append(champ)
                        self.champs_t100_nums.append(self.champ2num[champ])
                    elif team == 200 or team == 'purple':
                        self.champs_t200.append(champ)
                        self.champs_t200_nums.append(self.champ2num[champ])
                    else:
                        print('Invalid team name!')
            else:
                print('There is no champion with name ' + champ + '!')
        elif type(champ) == int:
            if champ in self.champ_list_nums:
                if champ in self.bans_champs_nums:
                    print('Champion with id ' + str(champ) + ' was already banned!')
                elif champ in self.champs_t100_nums:
                    print('Champion with id ' + str(champ) + ' is already in team blue!')
                elif champ in self.champs_t200_nums:
                    print('Champion with id ' + str(champ) + ' is already in team purple!')
                else:
                    if team == 100 or team == 'blue':
                        self.champs_t100.append(self.num2champ[champ])
                        self.champs_t100_nums.append(champ)
                    elif team == 200 or team == 'purple':
                        self.champs_t200.append(self.num2champ[champ])
                        self.champs_t200_nums.append(champ)
                    else:
                        print('Invalid team name!')
            else:
                print('There is no champion with id ' + champ + '!')
        else:
            print('Invalid champ input type!')

    def add_bans(self, champ_list):
        for champ in champ_list:
            self.add_ban(champ)

    def add_champs(self, champ_list, teams):
        for champ, team in zip(champ_list, teams):
            self.add_champ(champ, team)

    def recommend_champ(self, team_to_recommend=100):
        def create_feacture_vector(example_champs_nums_t100, example_champs_nums_t200):
            feature_vector = np.zeros((2 * self.num_champs + 2))
            for champion_num100 in example_champs_nums_t100:
                feature_vector[champion_num100] = 1
            for champion_num200 in example_champs_nums_t200:
                feature_vector[champion_num200 + self.num_champs] = 1

            synergy100 = 0
            synergy200 = 0
            for champion_num1, champion_num2 in combinations(example_champs_nums_t100, 2):
                synergy100 += self.synergy[champion_num1, champion_num2]
            for champion_num1, champion_num2 in combinations(example_champs_nums_t200, 2):
                synergy200 += self.synergy[champion_num1, champion_num2]
            if len(list(combinations(example_champs_nums_t100, 2))) > 0:
                synergy100 = synergy100 / len(list(combinations(example_champs_nums_t100, 2)))
            if len(list(combinations(example_champs_nums_t200, 2))) > 0:
                synergy200 = synergy200 / len(list(combinations(example_champs_nums_t200, 2)))
            synergy_value = synergy100 - synergy200

            counter_value = 0
            count_num = 0
            for champion_num100 in example_champs_nums_t100:
                for champion_num200 in example_champs_nums_t200:
                    count_num += 1
                    counter_value += self.counter[champion_num100, champion_num200]
            if count_num > 0:
                counter_value = 0.5 - (counter_value / count_num)
            feature_vector[2 * self.num_champs] = synergy_value
            feature_vector[2 * self.num_champs + 1] = counter_value
            return feature_vector

        if team_to_recommend == 100 or team_to_recommend == 'blue':
            if len(self.champs_t100_nums) == 5:
                print('Team blue has full party!')
            else:
                recommendation_dict = {}
                for champion_num in self.champ_list_nums:
                    if champion_num in self.bans_champs_nums:
                        continue
                    if champion_num in self.champs_t100_nums:
                        continue
                    if champion_num in self.champs_t200_nums:
                        continue
                    example_champs_nums_t100 = self.champs_t100_nums.copy()
                    example_champs_nums_t100.append(champion_num)
                    example_champs_nums_t200 = self.champs_t200_nums.copy()
                    feature_vector_recom = [create_feacture_vector(example_champs_nums_t100, example_champs_nums_t200)]
                    recommendation_dict[self.num2champ[champion_num]] = self.model.predict_proba(feature_vector_recom)[0][0]
        elif team_to_recommend == 200 or team_to_recommend == 'purple':
            if len(self.champs_t200_nums) == 5:
                print('Team purple has full party!')
            else:
                recommendation_dict = {}
                for champion_num in self.champ_list_nums:
                    if champion_num in self.bans_champs_nums:
                        continue
                    if champion_num in self.champs_t100_nums:
                        continue
                    if champion_num in self.champs_t200_nums:
                        continue
                    example_champs_nums_t200 = self.champs_t200_nums.copy()
                    example_champs_nums_t200.append(champion_num)
                    example_champs_nums_t100 = self.champs_t100_nums.copy()
                    feature_vector_recom = [create_feacture_vector(example_champs_nums_t100, example_champs_nums_t200)]
                    recommendation_dict[self.num2champ[champion_num]] = self.model.predict_proba(feature_vector_recom)[0][0]
        recommendation_dict = {k: v for k, v in sorted(recommendation_dict.items(), key=lambda item: item[1], reverse=True)}
        return recommendation_dict
