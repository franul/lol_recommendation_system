#!/usr/bin/env python3

from riotwatcher import LolWatcher, ApiError, RiotWatcher
from datetime import date, timedelta, datetime
from ratelimit import limits, sleep_and_retry
import csv
import json
import os

api_key = 'RGAPI-cc723756-6fec-410f-8283-ad41083471b4'
leagues = ['challenger', 'master']
regions = ['NA1', 'KR', 'BR1']
queue = "RANKED_SOLO_5x5"


class Riot_Crawler():
    def __init__(self, api_key, queue, queue_id, matchlist_page_limit=100):
        self.api_key = api_key
        self.queue = queue
        self.queue_id = queue_id
        self.matchlist_page_limit = matchlist_page_limit
        self.api = LolWatcher(api_key)

    def fetch_league(self, region, save=False, destination_path=None):
        league_dict = {}
        league_dict['challenger'] =  self.api.league.challenger_by_queue(region=region, queue=self.queue)
        league_dict['grandmaster'] = self.api.league.grandmaster_by_queue(region=region, queue=self.queue)
        league_dict['masters'] = self.api.league.masters_by_queue(region=region, queue=self.queue)
        return league_dict

    def fetch_acc_ids(self, region, league_dict, calls_num=10, period_num=12,
                      save=False, destination_path=None):
        summoner_ids = []
        accounts = []
        account_ids = []

        @sleep_and_retry
        @limits(calls=calls_num, period=period_num)
        def get_account(summonerid, region):
            account = self.api.summoner.by_id(region=region, encrypted_summoner_id=summonerid)
            return account

        for rank_list in league_dict.values():
            for entry in rank_list['entries']:
                summoner_ids.append(entry['summonerId'])
                try:
                    account = get_account(entry['summonerId'], region)
                    accounts.append(account)
                    account_ids.append(account['accountId'])
                except:
                    pass
        if save:
            if destination_path is None:
                print('No destination path was given')
            else:
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)
                path = os.path.join(destination_path, 'summoner_ids.txt')
                with open(path, 'w') as f:
                    for item in summoner_ids:
                        f.write("%s\n" % item)

                path = os.path.join(destination_path, 'accounts.json')
                with open(path, 'w') as f:
                    json.dump(accounts, f, indent=4)

                path = os.path.join(destination_path, 'account_ids.txt')
                with open(path, 'w') as f:
                    for item in account_ids:
                        f.write("%s\n" % item)
        return summoner_ids, accounts, account_ids

    #loading summoner_ids, accounts, account_ids from folder path
    def load_acc_ids(self, load_path):
        if not os.path.exists(load_path):
            print('Path does not exist.')
            return None, None
        path = os.path.join(load_path, 'summoner_ids.txt')
        summoner_ids = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    summoner_ids.append(line.strip())

        path = os.path.join(load_path, 'accounts.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                accounts = json.load(f)

        path = os.path.join(load_path, 'account_ids.txt')
        account_ids = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    account_ids.append(line.strip())
        return summoner_ids, accounts, account_ids

    def fetch_match_ids(self, region, account_ids, begin_time, end_time,
                        calls_num=10, period_num=12, save=False,
                        destination_path=None):
        @sleep_and_retry
        @limits(calls=calls_num, period=period_num)
        def get_matchlist(region, account_id, begin_time, end_time, queue_id,
                          begin_index, end_index):
            new_matchlist = self.api.match.matchlist_by_account(region=region,
                                                           encrypted_account_id=account_id,
                                                           begin_time=begin_time,
                                                           end_time=end_time,
                                                           queue=queue_id,
                                                           begin_index=begin_index,
                                                           end_index=end_index)
            return new_matchlist

        account_ids_done = []
        match_ids = []
        for account_id in account_ids:
            # Start with empty matchlist
            matchlist = {"matches": [], "totalGames": 0}
            begin_index = 0
            more_matches=True
            while more_matches:
                new_matchlist = {}
                try:
                    new_matchlist = get_matchlist(region=region,
                                                  account_id=account_id,
                                                  begin_time=begin_time,
                                                  end_time=end_time,
                                                  queue_id=self.queue_id,
                                                  begin_index=begin_index,
                                                  end_index=begin_index+self.matchlist_page_limit)
                except:
                    pass
                if "matches" in new_matchlist.keys():
                    matchlist["matches"] = matchlist["matches"] + new_matchlist["matches"]
                    matchlist["totalGames"] = matchlist["totalGames"] + new_matchlist["totalGames"]
                    if len(new_matchlist["matches"]) == self.matchlist_page_limit:
                        begin_index += self.matchlist_page_limit
                    else:
                        more_matches=False
                else:
                    more_matches=False
            account_ids_done.append(account_id)
            new_match_ids = list(set([x['gameId'] for x in matchlist['matches']]) - set(match_ids))
            match_ids.extend(new_match_ids)
        if save:
            if destination_path is None:
                print('No destination path was given')
            else:
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)
                path = os.path.join(destination_path, 'match_ids.txt')
                with open(path, 'w') as f:
                    for item in match_ids:
                        f.write("%s\n" % item)

                path = os.path.join(destination_path, 'account_ids_done.txt')
                with open(path, 'w') as f:
                    for item in account_ids_done:
                        f.write("%s\n" % item)
        return match_ids, account_ids_done

    def load_match_ids(self, load_path):
        if not os.path.exists(load_path):
            print('Path does not exist.')
            return None, None
        path = os.path.join(load_path, 'match_ids.txt')
        match_ids = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    match_ids.append(line.strip())
        path = os.path.join(load_path, 'account_ids_done.txt')
        account_ids_done = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    account_ids_done.append(line.strip())
        return match_ids, account_ids_done

    def fetch_match_info(self, region, match_ids, account_ids_done,
                         calls_num=10, period_num=12,
                         save=False, destination_path=None):
        @sleep_and_retry
        @limits(calls=10, period=12)
        def get_match_info(region, match_id):
            match = self.api.match.by_id(region=region, match_id=match_id)
            return match

        match_id_dones = []
        match_list = []
        account_ids_unseen = []
        for match_id in list(set(match_ids)):
            if match_id in match_id_dones:
                continue
            else:
                match_id_dones.append(match_id)
                try:
                    match = get_match_info(region, match_id)
                    match_list.append(match)
                    game_account_ids = [x['player']['currentAccountId'] for x in match['participantIdentities']]
                    new_account_ids = list(set(game_account_ids) - set(account_ids_done) - set(account_ids_unseen))
                    account_ids_unseen.extend(new_account_ids)
                except:
                    pass
        if save:
            if destination_path is None:
                print('No destination path was given')
            else:
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)
                path = os.path.join(destination_path, 'match_id_dones.txt')
                with open(path, 'w') as f:
                    for item in match_id_dones:
                        f.write("%s\n" % item)

                path = os.path.join(destination_path, 'match_list.json')
                with open(path, 'w') as f:
                    json.dump(match_list, f, indent=4)

                path = os.path.join(destination_path, 'account_ids_unseen.txt')
                with open(path, 'w') as f:
                    for item in account_ids_unseen:
                        f.write("%s\n" % item)
        return match_list, match_id_dones, account_ids_unseen

    def load_match_info(self, load_path):
        if not os.path.exists(load_path):
            print('Path does not exist.')
            return None, None, None
        path = os.path.join(load_path, 'match_id_dones.txt')
        match_id_dones = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    match_id_dones.append(line.strip())

        path = os.path.join(load_path, 'match_list.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                match_list = json.load(f)

        path = os.path.join(load_path, 'account_ids_unseen.txt')
        account_ids_unseen = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    account_ids_unseen.append(line.strip())
        return match_list, match_id_dones, account_ids_unseen

    def create_features(self, match_list, id2number):
        num_champions = len(id2number)
        synergy_matrix = np.zeros((num_champions, num_champions))
        synergy_matrix_num = np.zeros((num_champions, num_champions))
        counter_matrix = np.zeros((num_champions, num_champions))
        counter_matrix_num = np.zeros((num_champions, num_champions))
        winratio_matrix = np.zeros((num_champions, ))
        winratio_matrix_num = np.zeros((num_champions, ))

        for match in match_list:
            #removing matches that don't match constraints
            duration = match['gameDuration']
            if duration < 600:
                continue

            game_type = match['gameType']
            if game_type != 'MATCHED_GAME':
                continue

            season = match['seasonId']
            if season != 13:
                continue

            game_mode = match['gameMode']
            if game_mode != 'CLASSIC':
                continue
            #creating team dictonary
            teams = {}
            teams[100] = []
            teams[200] = []
            for team in match['teams']:
                if team['win'] == 'Win':
                    teams[str(team['teamId']) + 'score'] = 1
                else:
                    teams[str(team['teamId']) + 'score'] = 0
            for participant in match['participants']:
                win = participant['stats']['win']
                champion_id = participant['championId']
                teamId = participant['teamId']
                teams[teamId].append(champion_id)
            #winratio
            for champion_id1, champion_id2 in zip(teams[100], teams[200]):
                id1 = id2number[champion_id1]
                id2 = id2number[champion_id2]
                winratio_matrix[id1] += teams['100score']
                winratio_matrix_num[id1] += 1
                winratio_matrix[id2] += teams['200score']
                winratio_matrix_num[id2] += 1
            #winratio for synergy:
            for champion_id1, champion_id2 in combinations(teams[100], 2):
                id1 = id2number[champion_id1]
                id2 = id2number[champion_id2]
                synergy_matrix[id1, id2] += teams['100score']
                synergy_matrix_num[id1, id2] += 1
                synergy_matrix[id2, id1] += teams['100score']
                synergy_matrix_num[id2, id1] += 1
            for champion_id1, champion_id2 in combinations(teams[200], 2):
                id1 = id2number[champion_id1]
                id2 = id2number[champion_id2]
                synergy_matrix[id1, id2] += teams['200score']
                synergy_matrix_num[id1, id2] += 1
                synergy_matrix[id2, id1] += teams['200score']
                synergy_matrix_num[id2, id1] += 1
            #winartio for counterpick:
            for champion_id1 in teams[100]:
                id1 = id2number[champion_id1]
                for champion_id2 in teams[200]:
                    id2 = id2number[champion_id2]
                    counter_matrix[id1, id2] += teams['100score']
                    counter_matrix_num[id1, id2] += 1
                    counter_matrix[id2, id1] += teams['200score']
                    counter_matrix_num[id2, id1] += 1
        return synergy_matrix, synergy_matrix_num, counter_matrix,
    counter_matrix_num, winratio_matrix, winratio_matrix_num
