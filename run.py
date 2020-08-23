#!/usr/bin/env python3

from pathlib import Path
from sys import argv, stderr
from create_recommendations import create_recommendations

if __name__ == '__main__':
    bans_path = Path(argv[1])
    champion_path = Path(argv[2])
    output_path = Path(argv[3])
    team_to_recommend = int(argv[4])


    if not bans_path.exists():
        print(f'{bans_path} does not exist!', file=stderr)
        exit(-1)
    if not champion_path.exists():
        print(f'{champion_path} does not exist!', file=stderr)
        exit(-1)

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    rec_dict, pos_picks = create_recommendations(bans_path, champion_path,
                                                 output_path)
    recom_path = output_path / 'recommendations.txt'
    with open(recom_path, 'w') as f:
        if pos_picks[100]:
            f.write('Picks for team blue')
            for item in pos_picks[100]:
                f.write('%s: %f\n' % (item[0], item[1]))
        if pos_picks[200]:
            f.write('Picks for team purple')
            for item in pos_picks[200]:
                f.write('%s: %f\n' % (item[0], item[1]))
#can be run with python run.py data/bans.txt data/champions.txt data 100
