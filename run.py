#!/usr/bin/env python3

from pathlib import Path
from sys import argv, stderr
from create_recommendations import create_recommendations

if __name__ == '__main__':
    bans_path = Path(argv[1])
    champion_path = Path(argv[2])
    output_path = Path(argv[3])


    if not bans_path.exists():
        print(f'{bans_path} does not exist!', file=stderr)
        exit(-1)
    if not champion_path.exists():
        print(f'{champion_path} does not exist!', file=stderr)
        exit(-1)

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

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
            bans.append(ban)

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
    champion_dict = dict(zip(champions, teams))

    rec_dict, pos_picks, _ = create_recommendations(bans, champion_dict)
    recom_path = output_path / 'recommendations.txt'
    with open(recom_path, 'w') as f:
        if pos_picks[100]:
            f.write('Picks for team blue: \n')
            for item in pos_picks[100][:20]:
                f.write('%s: %f\n' % (item[0], item[1]))
        f.write('\n')
        if pos_picks[200]:
            f.write('Picks for team purple: \n')
            for item in pos_picks[200][:20]:
                f.write('%s: %f\n' % (item[0], item[1]))
