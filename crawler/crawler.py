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
    def __init__(self, api_key, queue, matchlist_page_limit=100):
        self.api_key = api_key
        self.queue = queue
        self.matchlist_page_limit = matchlist_page_limit
        self.api = LolWatcher(api_key)

    def fetch_league(self, region, queue, save=False, destination_path=None):
        league_dict = {}
        league_dict['challenger'] =  self.api.league.challenger_by_queue(region=region, queue=queue)
        league_dict['grandmaster'] = self.api.league.grandmaster_by_queue(region=region, queue=queue)
        league_dict['masters'] = self.api.league.masters_by_queue(region=region, queue=queue)
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
        path = os.path.join(load_path, 'summoner_ids.txt')
        summoner_ids = []
        with open(path) as f:
            for line in f:
                summoner_ids.append(line.strip())

        path = os.path.join(load_path, 'accounts.json')
        with open(path, 'r') as f:
            accounts = json.load(f)

        path = os.path.join(load_path, 'account_ids.txt')
        account_ids = []
        with open(path) as f:
            for line in f:
                account_ids.append(line.strip())
        return summoner_ids, accounts, account_ids

    def fetch_match_ids(self, region, account_ids, begin_time, end_time,
                        calls_num=10, period_num=12, save=False,
                        destination_path=None):
        @sleep_and_retry
        @limits(calls=calls_num, period=period_num)
        def get_matchlist(region, account_id, begin_time, end_time, queue,
                          begin_index, end_index):
            new_matchlist = api.match.matchlist_by_account(region=region,
                                                           encrypted_account_id=account_id,
                                                           begin_time=begin_time,
                                                           end_time=end_time,
                                                           queue=queue,
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
                                                  queue=self.queue,
                                                  begin_index=begin_index,
                                                  end_index=begin_index+self.matchlist_page_limit)
                except:
                    pass
                if "matches" in new_matchlist.keys():
                    matchlist["matches"] = matchlist["matches"] + new_matchlist["matches"]
                    matchlist["totalGames"] = matchlist["totalGames"] + new_matchlist["totalGames"]
                    if len(new_matchlist["matches"]) == MATCHLIST_PAGE_LIMIT:
                        begin_index += MATCHLIST_PAGE_LIMIT
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
        return match_ids, account_ids_done

    def load_match_ids(self, load_path):
        path = os.path.join(load_path, 'match_ids.txt')
        match_ids = []
        with open(path) as f:
            for line in f:
                match_ids.append(line.strip())
        return match_ids

    def fetch_match_info(self, region, match_ids, calls_num=10, period_num=12,
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

    def load_match_ids(self, load_path):
        path = os.path.join(folder_path, 'match_id_dones.txt')
        match_id_dones = []
        with open(path) as f:
            for line in f:
                match_id_dones.append(line.strip())

        path = os.path.join(folder_path, 'match_list.json')
        with open(path, 'r') as f:
            match_list = json.load(f)

        path = os.path.join(folder_path, 'account_ids_unseen.txt')
        account_ids_unseen = []
        with open(path) as f:
            for line in f:
                account_ids_unseen.append(line.strip())
        return match_list, match_id_dones, account_ids_unseen
