from data import constants, utils
import pdb,time,json,sys,copy
import itertools, argparse
from itertools import chain

# Temp Constants
constants.Natural_Heating_Cooling_Penalty 
constants.Cooling_Penalty_High_Room
constants.Cooling_Penalty_Room_Low

constants.Heating_Penalty_Low_High 
constants.Heating_Penalty_Low_Room 
constants.Heating_Penalty_Room_High 

#Cleaning constants
constants.Cleaning_Time 
constants.Cleaning_Effort

#use
constants.Rev_to_free_time
'''
Aim : to append to the dataset 
     1. | rough effort penalty 
     2. | time penalty 
     3. | operations required 
    
'''
def calculate_effort_penalty(config, ideal):
    return 0

def calculate_material_penalty(config, ideal):
    if config["material"] not in ideal["material"]: 
        for concept_card in material_ranks["mat_gt"]:
            if config["material"]["category"] == concept_card["Concept"]:
                reverse_rank = 1/(concept_card["Items"][config["object"]].index(config["material"]) + 1)
                return 50*reverse_rank
    else:
        return 0

def calculate_time_penalty(config, ideal):

    if config["condition"] == 'dirty':
        time_penalty =+ constants.Cleaning_Time
    elif config["condition"] == "broken":
        time_penalty += constants.Bad_Choice
    
    if config["already_in_use"] == "reversible-using":
        time_penalty += constants.Rev_to_free_time
    elif config["already_in_use"] == "irreversible-using":
        time_penalty += constants.Bad_Choice
    
    ideal_temp = ideal['temperature']

    if config["temperature"] == "Hot":
        if ideal_temp == "RoomTemp":
            time_penalty+= constants.Natural_Heating_Cooling_Penalty
        elif ideal_temp == "Cold":
            time_penalty += constants.Cooling_Penalty_High_Low

    elif config["temperature"] == "Cold":
        if ideal_temp == "RoomTemp":
            time_penalty+= constants.Natural_Heating_Cooling_Penalty
        elif ideal_temp == "Hot":
            time_penalty += constants.Heating_Penalty_Low_High

    elif config["temperature"] == "RoomTemp":
        if ideal_temp == "Cold":
            time_penalty+= constants.Cooling_Penalty_Room_Low
        elif ideal_temp == "Hot":
            time_penalty += constants.Heating_Penalty_Room_High
    
    return time_penalty


def create_task_1_ideal_config(oracle):

    # responses : human choice collection of whats physically possible config
    # ideal_config : only 3 variable data again taken by human : {temp, condition, already_in_use}
    # gt_2_mat : contains human intuitive ordering when more than 1 material available for an object
    mat_pref_file = './data/task_1_results/Exp_1/GT_used/ayush_material_preference.json'
    responses = utils.load_dataset('./data/task_1_results/Exp_1/GT_used/ayush_var_responses.json')
    ideal_config = utils.load_dataset('./data/task_1_results/Exp_1/GT_used/3_var_ideal_config.json')
    pouch_oracle = copy.deepcopy(oracle)
    for concept in oracle:
        for task in oracle[concept]:
            pouch_oracle[concept][task] = list(pouch_oracle[concept][task])
            oracle[concept][task] = list(oracle[concept][task])
            pouch_oracle[concept][task] = []
            for i,obj in enumerate(oracle[concept][task]):
                if len(responses[obj]["material"]) == 1:
                    oracle[concept][task][i] = {
                        "object_name": obj,
                        "mass": responses[obj]["mass"],
                        "temperature": ideal_config[obj]["temperature"],
                        "material": responses[obj]["material"],
                        "already_in_use": ideal_config[obj]["already_in_use"],
                        "condition": ideal_config[obj]["condition"]
                    }
                    all_comb = itertools.product(responses[obj]["mass"], ideal_config[obj]["temperature"], responses[obj]["material"], ideal_config[obj]["already_in_use"], ideal_config[obj]["condition"])
                    pouch_oracle[concept][task].append([{"object_name" : obj, "mass":comb[0], "temperature": comb[1], "material": comb[2], "already_in_use":comb[3], "condition": comb[4]} for comb in all_comb])
                else:
                    oracle[concept][task][i] = {
                        "object_name":obj,
                        "mass": responses[obj]["mass"],
                        "temperature": ideal_config[obj]["temperature"],
                        "material": give_ideal_material(mat_pref_file, obj,task,concept),
                        "already_in_use": ideal_config[obj]["already_in_use"],
                        "condition": ideal_config[obj]["condition"]
                    }
                    #beware of material
                    all_comb = itertools.product(responses[obj]["mass"], ideal_config[obj]["temperature"], give_ideal_material(mat_pref_file, obj,task,concept), ideal_config[obj]["already_in_use"], ideal_config[obj]["condition"])
                    pouch_oracle[concept][task].append([{"object_name" : obj, "mass":comb[0], "temperature": comb[1], "material": comb[2], "already_in_use":comb[3], "condition": comb[4]} for comb in all_comb])
                    
            # print(pouch_oracle)
            pouch_oracle[concept][task] = list(chain(*pouch_oracle[concept][task]))
    
    with open('./data/task_1_results/Exp_1/GT_used/choice_config_oracle.json', 'w') as var_file:
        json.dump(oracle, var_file, indent=4)
    with open('./data/task_1_results/Exp_1/GT_used/pouch_config_oracle.json', 'w') as var_file:
        json.dump(pouch_oracle, var_file, indent=4)
                             
def create_ranked_material_ideal_commonsense(oracle):
    "ranking all materials of an object; ascending order"
    mat_gt = {
        "mat_gt": []
    }
    # count = 0
    responses = utils.load_dataset('./data/task_1_results/Exp_1/GT_used/ayush_var_responses.json')
    for concept in oracle:
        concept_data = {
            "concept": concept,
            "tasks":[]
        }
        for task in oracle[concept]:
            task_data = {
                "task": task,
                "items": {}
            }
            for _, obj in enumerate(oracle[concept][task]):
                options_dict = {i+1 : option for i, option in enumerate(responses[obj]['material'])}
                if len(responses[obj]["material"]) > 1:
                    count += 1
                    print(f"Task: {task} \n\n Concept: {concept} \n\n Object:{obj} \n\n {options_dict}")
                    order = input("Insert ascending order of appropriateness:")
                    while True:
                        try:
                            assert len(order) == len(responses[obj]['material'])
                            task_data["items"][obj] = [responses[obj]['material'][int(char)-1] for char in order]
                            break
                        except:
                            print('You messed up!')
                            order = input("Insert ascending order of appropriatenss [no spaces, no symbols, just the numbering] -> ") 
            concept_data['tasks'].append(task_data)
        mat_gt["mat_gt"].append(concept_data)
    # print(count)
    with open('./data/task_1_results/Exp_1/GT_used/ayush_material_preference.json', 'w') as var_file:
        json.dump(mat_gt, var_file, indent=4)    

def create_binary_ranked_material_ideal_commonsense(oracle):
    '''
    divide the material list into good and bad;
    ranking all good materials of an object; ascending order
    '''
    mat_gt = {
        "mat_gt": []
    }
    # count = 0
    responses = utils.load_dataset('./data/task_1_results/Exp_1/GT_used/ayush_var_responses.json')
    for concept in oracle:
        concept_data = {
            "concept": concept,
            "tasks":[]
        }
        for task in oracle[concept]:
            task_data = {
                "task": task,
                "items": {}
            }
            for _, obj in enumerate(oracle[concept][task]):
                options_dict = {i+1 : option for i, option in enumerate(responses[obj]['material'])}
                task_data["items"][obj] = {}
                if len(responses[obj]["material"]) > 1:
                    # count += 1
                    print(f"Task: {task} \n\n Concept: {concept} \n\n Object:{obj} \n\n {options_dict}")
                    bad = input("Insert index that are very bad choices: ")
                    order = input("Insert ascending order of appropriateness of remaining options:")
                    while True:
                        try:
                            task_data["items"][obj]['good'] = [responses[obj]['material'][int(char)-1] for char in order]
                            assert len(order) == len(responses[obj]['material']) - len(bad)
                            task_data["items"][obj]['bad'] = [responses[obj]['material'][int(char)-1] for char in bad]
                            break
                        except Exception as e:
                            print(f'You messed up! \n\n Error:{e}')
                            bad = input("Insert index that are very bad choices: ")
                            order = input("Insert ascending order of appropriateness of remaining options [no spaces, no symbols, just the numbering] -> ") 
                elif len(responses[obj]["material"]) == 1:
                    task_data["items"][obj] = {}
                    task_data["items"][obj]['good'] = responses[obj]['material']
                    task_data["items"][obj]['bad'] = []

            concept_data['tasks'].append(task_data)
        mat_gt["mat_gt"].append(concept_data)
        with open('./data/task_1_results/Exp_1/GT_used/ayush_material_preference.json', 'w') as var2_file:
            json.dump(mat_gt, var2_file, indent=4)

    # print(count)
    with open('./data/task_1_results/Exp_1/GT_used/ayush_material_preference.json', 'w') as var_file:
        json.dump(mat_gt, var_file, indent=4)    

def check_mat_pref_has_all_entries():
    mat_pref = utils.load_dataset('./data/task_1_results/Exp_1/GT_used/ayush_material_preference.json')
    for data in mat_pref['mat_gt']:
        for task in data["tasks"]:
            if list(task['items'].keys()) != oracle[data["concept"]][task["task"]]:
                print(f'your file has : {task["items"].keys()} \n but oracle has {oracle[data["concept"]][task["task"]]}')

def give_ideal_material(mat_pref_file, obj, task, cat, binary = True):
    # top 1,2,3 material from human decided ordering
    # gt_2_mat : contains human intuitive ordering when more than 1 material available for an object
    material = utils.load_dataset(mat_pref_file)
    for concept_cat_card in material["mat_gt"]:
        if concept_cat_card["concept"].lower() == cat.lower():
            for task_card in concept_cat_card["tasks"]:
                if task_card["task"].lower() == task.lower():
                    for o, mat in task_card["items"].items():
                        if o.lower() == obj.lower():
                            if binary == True:
                                mat = mat['good']
                            if len(mat) <=3:
                                return [mat[-1]]
                            elif len(mat) > 3 and len(mat) <=5:
                                # print(mat[-2:])
                                return mat[-2:]
                            elif len(mat) > 5:
                                # print(mat[-3:])
                                return mat[-3:]
                            else:
                                print("idk man")
                        
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--objects", type=str, default='/home2/raghav.prabhakar/ayush/concept-bot/thortils/data/task_1_results/Exp_1/GT_used/objects.json')
    parser.add_argument("--tasks", type=str, default='/home2/raghav.prabhakar/ayush/concept-bot/thortils/data/task_1_results/Exp_1/GT_used/tasks.json')
    parser.add_argument("--oracle", type=str, default='/home2/raghav.prabhakar/ayush/concept-bot/thortils/data/task_1_results/Exp_1/GT_used/oracle.json' )
    args = parser.parse_args()
    
    objects = utils.load_dataset(args.objects)
    tasks = utils.load_dataset(args.tasks)
    oracle = utils.load_dataset(args.oracle)
    # create_binary_ranked_material_ideal_commonsense(oracle)
    # run multi_object.py and get ideal values for 3 variables
    create_task_1_ideal_config(oracle)

    