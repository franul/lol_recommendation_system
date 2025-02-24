#!/usr/bin/env python3
from datetime import date, timedelta, datetime
from crawler import Riot_Crawler
import os

if __name__ == '__main__':
    load = True
    api_key = ''
    queue = 'RANKED_SOLO_5x5'
    queue_id = 420
    regions = ['EUN1', 'EUW1', 'NA1', 'KR', 'BR1']
    riot_crawler = Riot_Crawler(api_key, queue, queue_id)
    begin_time = int((datetime.today() - timedelta(6)).timestamp()) * 1000
    end_time = int(datetime.today().timestamp()) * 1000
    for region in regions:
        folder_path = os.path.join(os.getcwd(), region)
        league_dict = riot_crawler.fetch_league(region)
        summoner_ids, accounts, account_ids = riot_crawler.fetch_acc_ids(region, league_dict, save=True, destination_path=folder_path)
        match_ids, account_ids_done = riot_crawler.fetch_match_ids(region, account_ids, begin_time, end_time, save=True, destination_path=folder_path)
        match_list, match_id_dones, account_ids_unseen = riot_crawler.fetch_match_info(region, match_ids, save=True, destination_path=folder_path)
