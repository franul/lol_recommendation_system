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
    def __init__(self, api_key, regions, queue):
        self.api_key = api_key
        self.regions = regions
        self.queue = queue
        self.api = LolWatcher(api_key)

    def fetch_league(self, region, queue, save=False, destination_path=None):
        league_dict = {}
        league_dict['challenger'] =  self.api.league.challenger_by_queue(region=region, queue=queue)
        league_dict['grandmaster'] = self.api.league.grandmaster_by_queue(region=region, queue=queue)
        league_dict['masters'] = self.api.league.masters_by_queue(region=region, queue=queue)
        return league_dict

    def fetch_acc_ids(self, calls_num=10, period_num=12, region, league_dict,
                      save=False, destination_path=None)
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



if save:
    if destination_path is None:
        print('No destination path was given')
    else:
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        path = os.path.join(destination_path, 'league.txt')
