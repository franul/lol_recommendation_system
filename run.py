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
                                                 output_path, team_to_recommend)
    recom_path = output_path / 'recommendations.txt'
    with open(recom_path, 'w') as f:
        for item in pos_picks:
            f.write('%s: %f\n' % (item[0], item[1]))
