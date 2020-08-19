from crawler import Riot_Crawler

def load_match_list(region):
    folder_name = region
    folder_path = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(folder_path):
        return None
    path = os.path.join(folder_path, 'match_list.json')
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        match_list = json.load(f)
        return match_list

if __name__ == '__main__':
    load = True
    api_key = ''
    queue = 'RANKED_SOLO_5x5'
    queue_id = 420
    regions = ['EUN1', 'EUW1', 'NA1', 'KR', 'BR1']
    #creating dictonaries for faster matching
    champion_path = '..\\data'
    path = os.path.join(champion_path, 'champion.json')
    with open(path, 'r') as f:
        champions = json.load(f)
    id2champ = {}
    champ2id = {}
    id2number = {}
    number2id = {}
    for i, key in enumerate(champions['data'].keys()):
        id_name = champions['data'][key]['id']
        id_num = int(champions['data'][key]['key'])
        id2champ[id_num] = id_name
        champ2id[id_name] = id_num
        id2number[id_num] = i
        number2id[i] = id_num

    #input your path with data after using crawler
    load_path = 'C:\\Users\\Franul\\Desktop\\tp_projekt'
    load_paths = []
    for region in regions:
        folder_path = os.path.join(load_path, region)
        if not os.path.exists(folder_path):
            return None
        path = os.path.join(folder_path, 'match_list.json')
        if not os.path.exists(path):
            return None
        load_paths.append(path)
    #create synergy, counter winartios and champion winartios
    riot_crawler = Riot_Crawler(api_key, queue, queue_id)
    num_champions = len(id2number)
    synergy_matrix = np.zeros((num_champions, num_champions))
    synergy_matrix_num = np.zeros((num_champions, num_champions))
    counter_matrix = np.zeros((num_champions, num_champions))
    counter_matrix_num = np.zeros((num_champions, num_champions))
    winratio_matrix = np.zeros((num_champions, ))
    winratio_matrix_num = np.zeros((num_champions, ))

    for path in load_paths:
        match_list = riot_crawler.load_match_ids(path)
        syn, syn_num, coun, coun_num, winr, winr_num = riot_crawler.create_features(match_list, id2number)
        synergy_matrix += syn
        synergy_matrix_num += syn_num
        counter_matrix += coun
        counter_matrix_num += coun_num
        winratio_matrix += winr
        winratio_matrix_num += winr_num

    synergy = np.zeros((num_champions, num_champions))
    counter = np.zeros((num_champions, num_champions))
    winratio = np.zeros((num_champions, ))
    for i in range(num_champions):
        if winratio_matrix_num[i] != 0:
            winratio[i] = winratio_matrix[i]/winratio_matrix_num[i]
        else:
            winratio[i] = 0.5
        for j in range(num_champions):
            if i == j:
                continue
            if synergy_matrix_num[i][j] >= 10:
                synergy[i][j] = synergy_matrix[i][j]/synergy_matrix_num[i][j]
            else:
                synergy[i][j] = 0.5
            if counter_matrix_num[i][j] >= 10:
                counter[i][j] = counter_matrix[i][j]/counter_matrix_num[i][j]
            else:
                counter[i][j] = 0.5
    #save matrices for later use
    with open('synergy.npy', 'wb') as f:
        np.save(f, synergy)
    with open('counter.npy', 'wb') as f:
        np.save(f, counter)
    with open('winratio.npy', 'wb') as f:
        np.save(f, winratio)
    #creating feature vectors and target

    feature_vectors = []
    target_vector = []
    for path in load_paths:
        match_list = riot_crawler.load_match_ids(path)
for region in regions:
    for match in matches_wins[region].values():
        feature_vector = np.zeros((2 * num_champions + 2))
        for champion_id1, champion_id2 in zip(match[100], match[200]):
            feature_vector[id2number[champion_id1]] = 1
            feature_vector[id2number[champion_id2] + num_champions] = 1
        synergy100 = 0
        synergy200 = 0
        for champion_id1, champion_id2 in combinations(match[100], 2):
            id1 = id2number[champion_id1]
            id2 = id2number[champion_id2]
            synergy100 += synergy[id1, id2]
        for champion_id1, champion_id2 in combinations(match[200], 2):
            id1 = id2number[champion_id1]
            id2 = id2number[champion_id2]
            synergy200 += synergy[id1, id2]
        synergy_value = (synergy100 - synergy200) / 20
        counter_value = 0
        for champion_id1 in match[100]:
            id1 = id2number[champion_id1]
            for champion_id2 in match[200]:
                id2 = id2number[champion_id2]
                counter_value += counter[id1, id2]
        counter_value = 0.5 - (counter_value / 25)
        feature_vector[2 * num_champions] = synergy_value
        feature_vector[2 * num_champions + 1] = counter_value
        feature_vectors.append(feature_vector)
        target_vector.append(match['100score'])

        feature_vector2 = np.zeros((2 * num_champions + 2))
        feature_vector2[:num_champions] = feature_vector[num_champions:2 * num_champions]
        feature_vector2[2 * num_champions] = -synergy_value
        feature_vector2[2 * num_champions + 1] = -counter_value
        feature_vectors.append(feature_vector2)
        target_vector.append(match['200score'])

feature_vectors = np.array(feature_vectors)
target_vector = np.array(target_vector)
with open('data.npy', 'wb') as f:
    np.save(f, feature_vectors)
with open('target.npy', 'wb') as f:
    np.save(f, target_vector)
