import json,pdb
from tqdm import tqdm
import constants
import google.generativeai as palm
import os
from pprint import pprint

# palm.configure(api_key=os.getenv("AYUSH_PALM_API_KEY"))
palm.configure(api_key=os.getenv("RAGHAV_PALM_API_KEY"))

def check_repeat(options, unique_options, task, num_options):
    if options == [] or options == [-1]:
        return 1    
    assert len(options) == num_options, 'You messed up in sampling!'
    combination = []
    for config in options:
        if task in ['fi','fm',1,2]:
            combination.append(config['id'])
        elif task in [0,'u']:
            combination.append(config)
    combination = sorted(combination)
    
    assert len(combination) == len(set(combination)), "Ouch..!! Sampled same object more than once!"
    # if unique_options == None:
    #     return 1
    # print(f'unique opt : {unique_options} \n combination : {combination}')
    # pdb.set_trace()
    if tuple(combination) in unique_options and len(unique_options) and len(combination):
        print("oops! Repetitive Options Sampled!")
        # print(combination)
        # pdb.set_trace()
        return 0       
    else:
        return 1

def check_dataset(dataset, task):
    '''
    - to check if all the questions have 5 options
    - to check no question has same 5 options for a task and concept
    '''
    dataset = load_dataset(dataset)
    unique_options = list()
    for ques_card in dataset:
        combination = list()
        # pdb.set_trace()
        for config in ques_card['options'].values():
            if task in ['fi','fm',1,2]:
                combination.append(config['id'])
            elif task == 0 or task == 'u':
                combination.append(config)
        combination = sorted(combination)
        if task in ['fi','fm',1,2]:
            combination.append(ques_card['context'])
        else:
            combination.append(ques_card['concept'])
        combination.append(ques_card['question'])
        if tuple(combination) in unique_options:
            print("Repetitive Options Sampled!")       
        else:
            unique_options.append((combination))
    return len(unique_options)
    
def load_dataset(filename):
    dataset = None
    try:
        with open(filename, "r") as file:
            dataset = json.load(file)
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    
    return dataset
