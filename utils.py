import sim
import json
import os
import shutil
import numpy as np
import centrality as cen

ROUNDS = 50

def round_specs(filename):
    info = filename.split('.')
    round_type = info[0].split('\\')[-1]     # RR or J
    num_seeds = info[1]
    graph_id = info[2]
    return round_type, num_seeds, graph_id

def parse_JSON(filename):
    adjacency_dict = {}
    # print(filename)
    with open(filename, 'r') as f:
        round_type, num_seeds, graph_id = round_specs(filename)
        adjacency_dict = json.loads(f.read())
    return adjacency_dict, num_seeds, round_type, graph_id

def filenames(path):
    if not os.path.exists(path):
        os.mkdir(path)
    files = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            _, ext = os.path.splitext(path + f)
            # Find graph
            if ext == '.json':
                files.append(path + f)
    return files

def convert_to_JSON(nodes, round_type, num_seeds, graph_id):
    file = {}
    file["Pathogen_Zero"] = []
    for i in range(ROUNDS):
        file["Pathogen_Zero"].append(nodes)
    # filename = f'{round_type}.{num_seeds}.{graph_id}-Pathogen_Zero.json'
    # f = open(filename, "a")
    # f.write(json.dumps(file))
    # f.close()
    return file

def compare_nodes(filename, node, opponent):
    adj_list, num_seeds, _, _ = parse_JSON(filename)
    num_seeds = int(num_seeds)
    node_mappings = {}
    node_mappings['Pathogen_Zero'] = [node]
    node_mappings['opponent'] = [opponent]
    result = sim.run(adj_list, node_mappings)
    return result['Pathogen_Zero'] >= result['opponent']

def generate_txt_files(output_path, round_type, num_seeds, graph_id, seeds):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.mkdir(output_path)
    file_id = 'Pathogen_Zero'
    write_filename = f'{output_path}{round_type}.{num_seeds}.{graph_id}-{file_id}.txt'
    f = open(write_filename, "a")
    for round in range(ROUNDS):
        for seed in seeds:
            f.writelines(str(seed) + "\n")
    f.close()
    print(f'Generated file: {write_filename}')

# Download the txt files in the output directory
def download_files(output_dir, seeds, round_type, num_seeds, graph_id):
    for name in os.listdir(output_dir):
        file = convert_to_JSON(np.array(seeds).tolist(), round_type, num_seeds, graph_id)
        file_id = 'Pathogen_Zero'
        write_filename = f'{output_dir}{round_type}.{num_seeds}.{graph_id}-{file_id}.json'
        with open(write_filename, "a") as f:
            json.dump(file, f, indent=4)

        print(f'Downloaded file: {write_filename}')

# Compares two Round-Robin strategies and determines the winner
def compare_strategies_RR(filename, seed_file, opponent_seed_file):
  adj_list, num_seeds, _, _ = parse_JSON(filename)
  node_mappings = {}
  
  with open(seed_file, 'r') as f:
    seed = json.loads(f.read())
    print(seed)
    node_mappings['Pathogen_Zero'] = seed['Pathogen_Zero'][0]

  with open(opponent_seed_file, 'r') as f:
    seed = json.loads(f.read())
    key = list(seed.keys())[0]
    node_mappings[key] = seed[key][0]
  return sim.run(adj_list, node_mappings)

# Compares Jungle strategies amonst all participants and determines the winner
def compare_strategies_J(filename, seed_file, opponent_seed_folder):
  opponent_seed_files = filenames(opponent_seed_folder)
  adj_list, num_seeds, _, _ = parse_JSON(filename)
  node_mappings = {}

  with open(seed_file, 'r') as f:
    seed = json.loads(f.read())
    node_mappings['Pathogen_Zero'] = seed[next(iter(seed))][0]

  for i, opponent_seed_file in enumerate(opponent_seed_files):
    with open(opponent_seed_file, 'r') as f:
      seed = json.loads(f.read())
      opponent_name = opponent_seed_file.split('-')[1].split('.')[0]
      node_mappings[opponent_name] = seed[next(iter(seed))][0]
  return sim.run(adj_list, node_mappings)

###################################
#        Initial Attempt          #
###################################

def random_choice(num_seeds, seeds, ratio=1.5):
    num_nodes = int(num_seeds * ratio)
    idxs = list(range(num_nodes))
    
    final_nodes = []
    for i in range(ROUNDS):
        shuffled_idxs = np.random.permutation(idxs)
        for j in range(num_seeds):
            idx = shuffled_idxs[j]
            final_nodes.append(seeds[idx])
    return final_nodes

def closeness(graph, num_seeds, ratio=1.5):
    num_nodes = int(num_seeds * ratio)
    seeds = cen.closeness(graph, num_nodes)
    return random_choice(num_seeds, ratio, seeds)
 
def degree(graph, num_seeds, ratio=1.5):
    num_nodes = int(num_seeds * ratio)
    seeds = cen.degree(graph, num_nodes)
    return random_choice(num_seeds, ratio, seeds)

def betweenness(graph, num_seeds, ratio=1.5):
    num_nodes = int(num_seeds * ratio)
    seeds = cen.betweenness(graph, num_nodes)
    return random_choice(num_seeds, ratio, seeds)

def all(graph, num_seeds, ratio=1.5):
    num_nodes = int(num_seeds * ratio)
    c_nodes = cen.closeness(graph, num_nodes)
    d_nodes = cen.degree(graph, num_nodes)
    b_nodes = cen.betweenness(graph, num_nodes)
    
    all_nodes = list(set(c_nodes + d_nodes + b_nodes))
    
    # randomly choose between those
    idxs = list(range(len(all_nodes)))
    chosen_nodes = []
    for i in range(ROUNDS):
        shuffled_idxs = np.random.permutation(idxs)
        for j in range(num_seeds):
            idx = shuffled_idxs[j]
            chosen_nodes.append(all_nodes[idx])
    return chosen_nodes