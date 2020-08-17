#!/usr/bin/env python3
from datetime import date, timedelta, datetime

from crawler import Riot_Crawler

if __name__ == '__main__':
    load = True
    api_key = 'RGAPI-cc723756-6fec-410f-8283-ad41083471b4'
    queue = 'RANKED_SOLO_5x5'
    queue_id = 420
    region = 'NA1'
    riot_crawler = Riot_Crawler(api_key, queue, queue_id)

    if load:
        summoner_ids, accounts, account_ids = riot_crawler.load_acc_ids(r'C:\Users\Franul\Desktop\tp_projekt\NA1')
        match_ids = riot_crawler.load_match_ids(r'C:\Users\Franul\Desktop\tp_projekt\NA1')
        match_list, match_id_dones, account_ids_unseen = riot_crawler.load_match_info(r'C:\Users\Franul\Desktop\tp_projekt\NA1')
    else:
        begin_time = int((datetime.today() - timedelta(6)).timestamp()) * 1000
        end_time = int(datetime.today().timestamp()) * 1000
        league_dict = riot_crawler.fetch_league(region)
        summoner_ids, accounts, account_ids = riot_crawler.fetch_acc_ids(region, league_dict)
        match_ids, account_ids_done = riot_crawler.fetch_match_ids(region, account_ids[:2], begin_time, end_time)
        match_list, match_id_dones, account_ids_unseen = riot_crawler.fetch_match_info(region, match_ids[:20])
