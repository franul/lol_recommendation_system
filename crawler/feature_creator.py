

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
