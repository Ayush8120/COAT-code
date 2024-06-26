import constants, utils
import pdb,time,json,sys,copy
import itertools ,argparse
from itertools import chain
import os
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

def give_ideal_material(mat_pref, obj, task, cat, binary = True):
    # top 1,2,3 material from human decided ordering
    # gt_2_mat : contains human intuitive ordering when more than 1 material available for an object
    material = mat_pref
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

def calculate_effort_penalty(config, ideal):
    return 0

def calculate_material_penalty(config, ideal, concept,task,mat_pref):
    material_penalty = 0
    flag = 0
    object_name = ideal['object_name']
    for resp in mat_pref['mat_gt']:
        if resp['concept'] == concept:
            for task_card in resp['tasks']:
                if task == task_card['task'] and object_name in task_card['items'].keys():
                    ideal = task_card['items'][object_name]
                    flag = 1
                    break
            if flag == 1:
                break
        if flag == 1:
                break

    if len(ideal['good']) <= 3:
        cutoff = 0
        top = -1
    elif len(ideal['good']) > 3 and len(ideal['good']) <=5:
        cutoff = 1
        top = -2
    elif len(ideal['good']) >5:
        cutoff = 2
        top = -3

    if type(ideal) == dict and len(ideal.keys()) == 2:
        if config['material'] in ideal['bad']:
            material_penalty += 500
        elif config['material'] in ideal['good'][:cutoff+1]:
            material_penalty +=  200
        else:
            if config['material'] in ideal['good'][top:]:
                material_penalty += 0
            else:
                material_penalty = 10* (len(ideal['good']) - ideal['good'].index(config["material"]))
  
    return material_penalty
def calculate_time_penalty(config, ideal):

    time_penalty = 0
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

def create_task_2_suboptimal_pouches(oracle, ideal_config, responses, all_config, mat_pref, root):
    pouch_suboptimal = copy.deepcopy(oracle)
    print(type(oracle))
    for concept in oracle:
        print(concept)
        for task in oracle[concept]:
            pouch_suboptimal[concept][task] = {'bad':[],
                                               'moderate':[]}
            for config in all_config:
                if config['object_name'] in oracle[concept][task]:
                    obj = config['object_name']
                    if len(responses[obj]["material"]) == 1:    
                        min_mat_penalty = 0
                        all_comb = itertools.product(responses[obj]["mass"], ideal_config[obj]["temperature"], responses[obj]["material"], ideal_config[obj]["already_in_use"], ideal_config[obj]["condition"])
                        for comb in all_comb:
                            ideal = {
                            "object_name": obj,
                            "mass": comb[0],
                            "temperature": comb[1],
                            "material": comb[2],
                            "already_in_use": comb[3],
                            "condition": comb[4]
                            }
                            min_time_penalty = min(2000, calculate_time_penalty(config,ideal))
                        if min_time_penalty >= 500:
                            pouch_suboptimal[concept][task]['bad'].append({**config, "time_penalty": min_time_penalty, "material_penalty": min_mat_penalty})
                        elif calculate_time_penalty(config, ideal) == 0:
                            pass
                        else:
                            pouch_suboptimal[concept][task]['moderate'].append({**config, "time_penalty": min_time_penalty, "material_penalty": min_mat_penalty})
                    else:
                        all_comb = itertools.product(responses[obj]["mass"], ideal_config[obj]["temperature"], give_ideal_material(mat_pref, obj,task,concept), ideal_config[obj]["already_in_use"], ideal_config[obj]["condition"])
                        for comb in all_comb:
                            ideal = {
                            "object_name": obj,
                            "mass": comb[0],
                            "temperature": comb[1],
                            "material": comb[2],
                            "already_in_use": comb[3],
                            "condition": comb[4]
                            }
                            min_time_penalty = min(2000, calculate_time_penalty(config,ideal))
                            min_mat_penalty = min(2000,calculate_material_penalty(config,ideal,concept,task,mat_pref))
                        if min_time_penalty >= 500 or min_mat_penalty >= 500:
                            pouch_suboptimal[concept][task]['bad'].append({**config, "time_penalty": min_time_penalty, "material_penalty": min_mat_penalty})

                        elif min_time_penalty == 0 or min_mat_penalty == 0:
                            pass
                        else:
                            pouch_suboptimal[concept][task]['moderate'].append({**config, "time_penalty": min_time_penalty, "material_penalty": min_mat_penalty})
            '''
            arrange the 
            '''
    with open(root + '/data/task_2_results/Exp_1/GT_used/pouch_suboptimal.json', 'w') as var_file:
        json.dump(pouch_suboptimal, var_file, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--objects", type=str, default='/home2/raghav.prabhakar/ayush/concept-bot/thortils/data/task_0_results/Exp_1/GT_used/objects.json')
    # parser.add_argument("--tasks", type=str, default='/home2/raghav.prabhakar/ayush/concept-bot/thortils/data/task_0_results/Exp_1/GT_used/tasks.json')
    parser.add_argument('--responses',type=str, default='data/task_1_results/Exp_1/GT_used/ayush_var_responses.json')
    parser.add_argument('--oracle', type=str, default='data/task_0_results/Exp_1/GT_used/oracle.json' )
    parser.add_argument('--root', type=str, default='/home2/raghav.arora/RaghavP/concept-bot/thortils/')
    parser.add_argument('--mat_pref', type=str,default='')
    parser.add_argument('--mat_pref_file', type=str, default='data/task_1_results/Exp_1/GT_used/ayush_material_preference.json')
    parser.add_argument('--ideal_config', type=str,default='data/task_1_results/Exp_1/GT_used/3_var_ideal_config.json')
    parser.add_argument('--all_config', type=str, default='/data/task_1_results/Exp_1/GT_used/possible_configurations_v1.json')

    args = parser.parse_args()
    responses = utils.load_dataset(os.path.join(args.root,args.responses))
    oracle = utils.load_dataset(os.path.join(args.root, args.oracle))
    mat_pref = utils.load_dataset(os.path.join(args.root,args.mat_pref_file))
    ideal_config = utils.load_dataset(os.path.join(args.root,args.ideal_config))
    all_config = utils.load_dataset(os.path.join(args.root,args.all_config))
    create_task_2_suboptimal_pouches(oracle,ideal_config, responses, all_config, mat_pref, args.root)