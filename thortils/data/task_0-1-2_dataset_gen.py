import numpy as np
import json,random, argparse
import os, pdb, sys
import constants
import utils
from collections import OrderedDict
import copy,pdb,math
from pprint import pprint
from tqdm import tqdm

random.seed(constants.DATA_GEN_SEED)
'''
This file generates the JSON containing question and question_answer JSON for task-0,1,2
'''

#concept = utility , used interchangeably in comments
def max_comb_count(cat,ques,pouch_subop,task_number,op_type, objects = None):
    '''to avoid generating questions with same options
        cat: concept of question
        ques: a string specifying (concept, task) combination
        pouch_subop: json containing mappings between (concept,task,'moderate') -> object_configuration and (concept,task,'bad') -> object_configuration
        task_num: int(0,1,2), task number 
        op_type: int, option sampling strategy
        objects: objects.json containing concepts-> objects mapping
    '''
    if task_number == 2:    
        # if op_type == 1: # similar score allowed as long as there is a winner
        #     mod = 5
        #     bad = 0
        if op_type == 2: # similar score allowed as long as there is a winner
            mod = 3
            bad = 2
        elif op_type == 3: # similar score allowed as long as there is a winner
            mod = 2
            bad = 3
        elif op_type == 4: # similar score allowed as long as there is a winner
            mod = 4
            bad = 1
        elif op_type == 5: # similar score allowed as long as there is a winner
            mod = 1
            bad = 4
        elif op_type == 6: # similar score allowed as long as there is a winner
            mod = 5
            bad = 0
        elif op_type == 7: # similar score allowed as long as there is a winner
            mod = 2
            bad = 0
        elif op_type == 8:
            mod = 1
            bad = 1
        elif op_type == 9: # similar score allowed as long as there is a winner
            mod = 2
            bad = 1
        elif op_type == 10:
            mod = 1
            bad = 2
        elif op_type == 11: # similar score allowed as long as there is a winner
            mod = 3
            bad = 0
        elif op_type == 12: # similar score allowed as long as there is a winner
            mod = 3
            bad = 1
        elif op_type == 13:
            mod = 1
            bad = 3
        elif op_type == 14: # similar score allowed as long as there is a winner
            mod = 2
            bad = 2
        elif op_type == 15: # similar score allowed as long as there is a winner
            mod = 4
            bad = 0
        count_mod = len(pouch_subop[cat][ques]['moderate'])
        count_bad = len(pouch_subop[cat][ques]['bad'])
        # pdb.set_trace()
        if count_mod >= mod and count_bad >= bad:
            return math.comb(count_mod, mod)* math.comb(count_bad, bad)
        else:
            return 10000
    elif task_number == 1:
        return 1000000
    elif task_number == 0:
        num_options = op_type
        count = len(objects[cat]) - len(oracle[cat][ques])
        if count >= num_options - 1:
            return math.comb(count, num_options - 1)
        else:
            return 10000
        
    
def task_0_create_object_level_qna(objects, tasks, oracle, root, num_options):
    '''main func for generating task-0 dataset
       
       objects: json containing object names
       tasks : json containing tasks
       oracle: json containing Ground Truth (concept,task) -> object mappings
       root : path to root dir
       num_options: int for choosing count of options which is sampling strategy for this dataset
    '''
    task_0_qa_database= []
    task_0_q_database = []
    q_number =0
    def sample_objects(correct_category, ques, num_options, unique_options):
        '''sample options'''
        options = []
        resample_count = 0
        #adding correct option    
        correct_answer = random.sample(oracle[correct_category][ques],1)
        options.extend(correct_answer)
        rem_cat_objects = set(objects[correct_category]) - set(oracle[correct_category][ques])
        while True:
            try:
                if len(rem_cat_objects) >= num_options -1:
                    options.extend(random.sample(rem_cat_objects,num_options -1))
                elif len(rem_cat_objects) < num_options -1:
                    options.extend(random.sample(rem_cat_objects,len(rem_cat_objects)))

                #randomly sampling the remaining options
                # Create a list of all objects
                objects_copy = objects.copy()
                # del objects_copy[correct_category]
                all_objects = [obj for obj_list in objects_copy.values() for obj in obj_list]
                all_objects = list(set(all_objects))
                curr_len = len(options)
                
                for ob in objects[correct_category]:
                    if ob in all_objects:
                        all_objects.remove(ob)
                
                # Randomly sample 2 objects from the entire list
                options.extend(random.sample(all_objects, num_options - curr_len))
                if not utils.check_repeat(options,unique_options,0,num_options) and resample_count <= 100:
                    # print('here, repeat!')
                    resample_count += 1
                    raise Exception("Repetition in object sampling!")
                elif resample_count > 100:
                    return -1,-1, unique_options
                    
            except Exception as error:
                # print(f'oops! {error}')
                # print(ques)
                # print(correct_category)
                # pdb.set_trace()
                options = []
                continue
        
            unique_options.append(sorted([option for option in options]))
            random.shuffle(options)
            options_dict = {chr(65 + i): option for i, option in enumerate(options)}    
            correct_answer = next((key for key, value in options_dict.items() if value == correct_answer[0]), None)
            
            return options_dict, correct_answer, unique_options

    obj_len_list =  [len(value) for _,value in objects.items()]
    total_obj = sum(obj_len_list)

    fragments = dict.fromkeys(objects.keys())
    for i,length in enumerate(obj_len_list):
        fragment = (length / total_obj) * constants.TASK_0_NUM_QUESTIONS
        fragments[list(objects.keys())[i]] = int(fragment)

    # Handle rounding errors by adjusting the last fragment
    fragments[list(objects.keys())[-1]] += constants.TASK_0_NUM_QUESTIONS - sum(fragments.values())
   
    # List of questions
    for cat,task_list in tqdm(tasks.items(),desc='Categories'):
        for ques in tqdm(task_list,desc='Tasks'):
            unique_options = list()
            if ques == task_list[-1]:
                task_q_count = fragments[cat] - (fragments[cat]//len(task_list))*(len(task_list)-1)
            else:
                task_q_count = fragments[cat]//len(task_list)
            task_q_count = min(task_q_count,max_comb_count(cat, ques, oracle , 0, num_options, objects))
            for n in range(task_q_count):

                q_number +=1
                question = f"Which of the following objects would be best suited for the purpose of \"{cat}\" when tasked to \"{ques}\"?"
                options, correct_answer,unique_options = sample_objects(cat, ques,num_options,unique_options)
                if options in [0,-1]:
                    break
                # Create the JSON structure
                qa_database = {
                    "question_id": q_number,
                    "concept": cat,
                    "question": question,
                    "options": options,
                    "correct_answer": correct_answer
                }

                q_database = {
                    "question_id": q_number,
                    "concept": cat,
                    "question": question,
                    "options": options,
                    "correct_answer": {}
                }
                task_0_qa_database.append(qa_database)
                task_0_q_database.append(q_database)
    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_0/Variation_{num_options}/GT/question_database.json"), "w") as json_file:
        json.dump(task_0_q_database, json_file,indent=4)

    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_0/Variation_{num_options}/GT/question_answer_database.json"), "w") as json_file:
        json.dump(task_0_qa_database, json_file,indent=4)
    print(utils.check_dataset(os.path.join(root,f"data/task_0/Variation_{num_options}/GT/question_database.json"),0))

def calculate_fragments_task_1():
    '''how many questions per (concept,household task) combination'''
    total_count = 0
    task_count = 0
    count_dict = {key: {task: None} for key,task_list in tasks.items() for task in task_list}
    for cat,task_list in tasks.items():
        for ques in task_list:
            config_len_list =  [len(pouch_subop[cat][ques]['moderate'])] + [len(pouch_subop[cat][ques]['bad'])] #+ [len(pouch_oracle[cat][ques])]
            count_dict[cat][ques] = sum(config_len_list)
            total_count += count_dict[cat][ques]
            task_count += 1 
    total_good_config = total_count #without correction - just sum of all oracle, moderate configs of all concepts,tasks

    scaled_total = 0
    for con,dic in count_dict.items():
        for task,coun in dic.items():
            fragment = (coun / total_good_config) * constants.TASK_1_NUM_QUESTIONS
            dic[task] = int(fragment)
            scaled_total += dic[task] #scaled total ; near the max number of questions but has a remainder; need to distribute it

            scaled_total_after_correction = 0
            if con == list(count_dict.keys())[-1] and task == list(count_dict[con].keys())[-1]:
                # Handle rounding errors by distributing evenly to every task; and then 1 at a time to all tasks
                increase_per_task = (constants.TASK_1_NUM_QUESTIONS - scaled_total)//task_count
                rem = (constants.TASK_1_NUM_QUESTIONS - scaled_total)%task_count
                for con,t_list in count_dict.items():
                    for task,_ in t_list.items():
                        if rem > 0:
                            count_dict[con][task] += increase_per_task + 1
                            rem -= 1
                        else:
                            count_dict[con][task] += increase_per_task
                        scaled_total_after_correction += count_dict[con][task]

    assert scaled_total_after_correction == constants.TASK_1_NUM_QUESTIONS
    return count_dict

    
def task_1_ideal_config_qna(tasks, oracle, pouch_oracle, all_config,root, op_type):
    '''main func for generating task-1 dataset
       
       tasks : json containing tasks
       oracle: json containing Ground Truth (concept,task) -> object mappings
       pouch_oracle : json containing (concept,task) -> ideal_object_configuration mappings
       all_config : json containing all commonly occurring physical configurations of objects
       root : path to root dir
       op_type: int for choosing option sampling strategy
    '''
    random.seed(constants.DATA_GEN_SEED)
    task_1_qa_database= []
    task_1_q_database = []
    q_number =0
    def task_1_sample_config(correct_category, ques, unique_options, op_type):
        '''sampling the options for the ques'''
        resample_count = 0
        options = []
        wrong_options = []
        wrong_options_diff = []
        wrong_options_same = []
        #adding correct option    
        ideal_correct_answer = random.sample(pouch_oracle[correct_category][ques],1)
        #to add the 'id' in correct option as when generating correct options we don't have that.
        index = None
        for c, config in enumerate(all_config):
            if all(config.get(key) == value for key, value in ideal_correct_answer[0].items()):
                index = config['id']
                assert config['id'] == c+1
                break
        final_answer = OrderedDict([('id', index)] + list(ideal_correct_answer[0].items()))
        options.extend([final_answer])
            
        if op_type in [1,4,8,11]:
            '''Same ideal Obj suboptimal configs:
            Fails if less than 4 config of that object ; also might be repeating options if less possible config'''
            for config in all_config:
                if config["object_name"] == ideal_correct_answer[0]['object_name'] and not any(all(config.get(key) == value for key, value in prob_answer.items()) for prob_answer in pouch_oracle[correct_category][ques]):
                    wrong_options.append(config)
           
        elif op_type in [2,5,9,12]:
            '''Different Oracle Obj's suboptimal configs
            Fails if only 1 oracle object'''
            for config in all_config:
                if config["object_name"] in oracle[correct_category][ques] and config["object_name"] != ideal_correct_answer[0]['object_name'] and not any(all(config.get(key) == value for key, value in prob_answer.items()) for prob_answer in pouch_oracle[correct_category][ques]):
                    wrong_options.append(config)
           
        elif op_type in [3,6,7,10]:
            '''
            2 same oracle obj suboptimal config
            2 diff oracle obj suboptimal config [fail if no other oracle obj for that concept]
            '''
            for config in all_config:
                if config["object_name"] in oracle[correct_category][ques] and config["object_name"] != ideal_correct_answer[0]['object_name'] and not any(all(config.get(key) == value for key, value in prob_answer.items()) for prob_answer in pouch_oracle[correct_category][ques]):
                    wrong_options_diff.append(config)
                elif config["object_name"] == ideal_correct_answer[0]['object_name'] and not any(all(config.get(key) == value for key, value in prob_answer.items()) for prob_answer in pouch_oracle[correct_category][ques]):
                    wrong_options_same.append(config)
            
        while True:
            try:
                #5 options
                if op_type in [1,2] and len(wrong_options) >= 4:
                    options.extend(random.sample(wrong_options,4))
                    opt_count = 5    
                elif op_type == 3 and len(wrong_options_diff) >=2 and len(wrong_options_same) >= 2:
                    options.extend(random.sample(wrong_options_diff,2))
                    options.extend(random.sample(wrong_options_same,2))
                    opt_count = 5
                #4 options
                elif op_type in [4,5] and len(wrong_options) >= 3:
                    options.extend(random.sample(wrong_options,3))
                    opt_count = 4
                elif op_type == 6 and len(wrong_options_diff) >=2 and len(wrong_options_same) >= 1:
                    options.extend(random.sample(wrong_options_diff,2))
                    options.extend(random.sample(wrong_options_same,1))
                    opt_count = 4
                elif op_type == 7 and len(wrong_options_diff) >=1 and len(wrong_options_same) >= 2:
                    options.extend(random.sample(wrong_options_diff,1))
                    options.extend(random.sample(wrong_options_same,2))
                    opt_count = 4
                #3 options
                elif op_type in [8,9] and len(wrong_options) >= 2:
                    options.extend(random.sample(wrong_options,2))
                    opt_count = 3
                elif op_type == 10 and len(wrong_options_diff) >=1 and len(wrong_options_same) >= 1:
                    options.extend(random.sample(wrong_options_diff,1))
                    options.extend(random.sample(wrong_options_same,1))
                    opt_count = 3
                #2 options
                elif op_type in [11,12] and len(wrong_options) >= 1:
                    options.extend(random.sample(wrong_options,1))
                    opt_count = 2
                else:
                    return 0,0,unique_options
                
                if not utils.check_repeat(options,unique_options,1,opt_count) and resample_count <= 100:
                    resample_count += 100
                    raise Exception("Repetition in object sampling!")
                
                elif resample_count > 1:
                    return -1,-1,unique_options
                
            except Exception as error:
                options = []
            
            if len(options): 
                unique_options.append(sorted([option['id'] for option in options]))     
            random.shuffle(options)
            options_dict = {chr(65 + i): option for i, option in enumerate(options)}
            # print(options_dict)
            correct_answer = next((key for key, value in options_dict.items() if value == final_answer), None)
            return options_dict, correct_answer,unique_options
    
    # List of questions
    for cat,task_list in tqdm(tasks.items(),desc='Categories'):
        for ques in tqdm(task_list,desc='Tasks'):
            
            count_dict = calculate_fragments_task_1()
            task_q_count = count_dict[cat][ques]
            unique_options = list()
            for n in range(task_q_count):
                
                question = f"Which of the following objects would be best suited for the purpose of \"{cat}\" when tasked to \"{ques}\"?"
                options, correct_answer,unique_options = task_1_sample_config(cat,ques,unique_options,op_type)
                if options in [-1,0]:
                    break
                q_number+=1
                # Create the JSON structure
                qa_database = {
                    "question_id": q_number,
                    "question": question,
                    "context":cat,
                    "options": options,
                    "correct_answer": correct_answer
                }

                q_database = {
                    "question_id": q_number,
                    "question": question,
                    "context":cat,
                    "options": options,
                    "correct_answer": {}
                }
                task_1_qa_database.append(qa_database)
                task_1_q_database.append(q_database)
    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_1/Variation_{op_type}/GT/question_answer_database.json"), "w") as json_file:
        json.dump(task_1_qa_database, json_file,indent=4)
    
    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_1/Variation_{op_type}/GT/question_database.json"), "w") as json_file:
        json.dump(task_1_q_database, json_file,indent=4)

    print(utils.check_dataset(os.path.join(root,f"data/task_1/Variation_{op_type}/GT/question_database.json"),1))

def calculate_fragments_task_2():
    '''how many questions per (concept,household task) combination'''
    total_count = 0
    task_count = 0
    count_dict = {key: {task: None} for key,task_list in tasks.items() for task in task_list}
    for cat,task_list in tasks.items():
        for ques in task_list:
            config_len_list =  [len(value) for _,value in pouch_subop[cat][ques].items()]
            count_dict[cat][ques] = sum(config_len_list)
            total_count += count_dict[cat][ques]
            task_count += 1 
    total_not_good_config = total_count #without correction - just sum of all bad, moderate configs of all concepts,tasks

    scaled_total = 0
    for con,dic in count_dict.items():
        for task,coun in dic.items():
            fragment = (coun / total_not_good_config) * constants.TASK_2_NUM_QUESTIONS
            dic[task] = int(fragment)
            scaled_total += dic[task] #scaled total ; near the max number of questions but has a remainder; need to distribute it

            scaled_total_after_correction = 0
            if con == list(count_dict.keys())[-1] and task == list(count_dict[con].keys())[-1]:
                # Handle rounding errors by distributing evenly to every task; and then 1 at a time to all tasks
                increase_per_task = (constants.TASK_2_NUM_QUESTIONS - scaled_total)//task_count
                rem = (constants.TASK_2_NUM_QUESTIONS - scaled_total)%task_count
                for con,t_list in count_dict.items():
                    for task,_ in t_list.items():
                        if rem > 0:
                            count_dict[con][task] += increase_per_task + 1
                            rem -= 1
                        else:
                            count_dict[con][task] += increase_per_task
                        scaled_total_after_correction += count_dict[con][task]

    assert scaled_total_after_correction == constants.TASK_2_NUM_QUESTIONS
    return count_dict

def task_2_subop_config_qna(tasks, pouch_subop, root, op_type):
    '''main func for generating task-2 dataset
       
       tasks : json containing tasks
       pouch_subop: json containing mappings between (concept,task,'moderate') -> object_configuration and (concept,task,'bad') -> object_configuration  
       root : path to root dir
       op_type: int for choosing option sampling strategy
    '''
    
    random.seed(constants.DATA_GEN_SEED)
    task_2_qa_database= []
    task_2_q_database = []
    q_number =0
    
    def sample_config(correct_category, ques, unique_options):
        '''sampling options'''
        resample_count = 0
        options = []
        # if op_type == 1: # similar score allowed as long as there is a winner
        #     mod = 5
        #     bad = 0
        if op_type == 2: # similar score allowed as long as there is a winner
            mod = 3
            bad = 2
        elif op_type == 3: # similar score allowed as long as there is a winner
            mod = 2
            bad = 3
        elif op_type == 4: # similar score allowed as long as there is a winner
            mod = 4
            bad = 1
        elif op_type == 5: # similar score allowed as long as there is a winner
            mod = 1
            bad = 4
        elif op_type == 6: # similar score allowed as long as there is a winner
            mod = 5
            bad = 0
        elif op_type == 7: # similar score allowed as long as there is a winner
            mod = 2
            bad = 0
        elif op_type == 8:
            mod = 1
            bad = 1
        elif op_type == 9: # similar score allowed as long as there is a winner
            mod = 2
            bad = 1
        elif op_type == 10:
            mod = 1
            bad = 2
        elif op_type == 11: # similar score allowed as long as there is a winner
            mod = 3
            bad = 0
        elif op_type == 12: # similar score allowed as long as there is a winner
            mod = 3
            bad = 1
        elif op_type == 13:
            mod = 1
            bad = 3
        elif op_type == 14: # similar score allowed as long as there is a winner
            mod = 2
            bad = 2
        elif op_type == 15: # similar score allowed as long as there is a winner
            mod = 4
            bad = 0
        
        while True:
            try:
                if len(pouch_subop[correct_category][ques]['moderate']) >= mod:
                    # pdb.set_trace()
                    moderate_options = random.sample(pouch_subop[correct_category][ques]['moderate'],mod)
                    # pdb.set_trace()
                    for option in moderate_options:
                        options.append(option)
                else:
                    return 0,0,unique_options
                # sorted_data = sorted(pouch_subop[correct_category][ques]['moderate'], key=lambda x: x['material_penalty'] + x['time_penalty'])
                pen_list = [moderate_options[i]['material_penalty'] + moderate_options[i]['time_penalty'] for i in range(len(moderate_options))]
                subop_correct_answer = moderate_options[pen_list.index(min(pen_list))]
                
                # if op_type in [1,3,5] :
                #     assert len(pen_list) == len(set(pen_list))
                # elif op_type in [7,9,11,12,14,15]:
                assert pen_list.count(min(pen_list)) == 1
                
                if bad > 0 and len(pouch_subop[correct_category][ques]['bad']) >= bad:
                    bad_options = random.sample(pouch_subop[correct_category][ques]['bad'],bad)
                    for option in bad_options:
                        options.append(option)
                elif len(pouch_subop[correct_category][ques]['bad']) < bad:
                    return 0,0,unique_options
                if not utils.check_repeat(options,unique_options,2,mod+bad) and resample_count <= 100:
                    #check if the chosen options are already present in unique_options
                    resample_count += 1
                    raise Exception("Repetition in object sampling!")
                elif resample_count > 100:
                    return -1,-1,unique_options
                    

            except Exception as error:
                #to go back to resampling
                print(f'oops! {error}')
                options = []
                continue
        
            unique_options.append(sorted([option['id'] for option in options]))
            random.shuffle(options)
            options_dict = {chr(65 + i): option for i, option in enumerate(options)}
            correct_answer = next((key for key, value in options_dict.items() if value == subop_correct_answer), None)
            # print('Successful Sampling!')
            return options_dict, correct_answer, unique_options

   
    # List of questions
    for cat,task_list in tqdm(tasks.items(),desc='Categories'):
        for ques in tqdm(task_list, desc='Tasks'):
            unique_options = list()
            count_dict = calculate_fragments_task_2()
            task_q_count = min(count_dict[cat][ques], max_comb_count(cat,ques,pouch_subop,2,op_type))
            for n in range(task_q_count):
                # print(task_q_count)
                question = f"Which of the following objects would be best suited for the purpose of \"{cat}\" when tasked to \"{ques}\"?"
                options, correct_answer, unique_options = sample_config(cat,ques,unique_options)
                
                if options in [0,-1]:
                    break
                q_number+=1
                # Create the JSON structure
                qa_database = {
                    "question_id": q_number,
                    "question": question,
                    "context":cat,
                    "options": options,
                    "correct_answer": correct_answer
                }

                q_database = {
                    "question_id": q_number,
                    "question": question,
                    "context":cat,
                    "options": options,
                    "correct_answer": {}
                }
                task_2_qa_database.append(qa_database)
                task_2_q_database.append(q_database)
    
    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_2/Variation_{op_type}/GT/question_answer_database.json"), "w") as json_file:
        json.dump(task_2_qa_database, json_file,indent=4)
    
    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_2/Variation_{op_type}/GT/question_database.json"), "w")as json_file:
        json.dump(task_2_q_database, json_file,indent=4)

    print(utils.check_dataset(os.path.join(root,f"data/task_2/Variation_{op_type}/GT/question_database.json"),2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--objects", type=str, default='data/utils/objects.json')
    parser.add_argument("--tasks", type=str, default='data/utils/tasks.json')
    parser.add_argument("--oracle", type=str, default='data/utils/oracle.json' )
    parser.add_argument("--pouch_oracle", type=str, default='data/utils/pouch_config_oracle.json')
    parser.add_argument("--all_config", type=str, default ='data/utils/possible_configurations_v1.json')
    parser.add_argument('--pouch_subop',type=str,default='data/utils/pouch_suboptimal.json')
    parser.add_argument('--root',type=str,default='path-to-thortils')
    args = parser.parse_args()
    
    objects = utils.load_dataset(os.path.join(args.root,args.objects))
    tasks = utils.load_dataset(os.path.join(args.root,args.tasks))
    oracle = utils.load_dataset(os.path.join(args.root,args.oracle))
    pouch_oracle = utils.load_dataset(os.path.join(args.root,args.pouch_oracle))
    all_config = utils.load_dataset(os.path.join(args.root,args.all_config))
    pouch_subop = utils.load_dataset(os.path.join(args.root,args.pouch_subop))

    #task: 2 : V1 is useless
    for i in range(2,16):
        task_2_subop_config_qna(tasks, pouch_subop, args.root, op_type=i)
        print(f"Successfully Created Variation: {i} : Task 2 Dataset")
    for i in range(1,13):
        task_1_ideal_config_qna(tasks,oracle, pouch_oracle, all_config, args.root, op_type=i)
        print(f"Successfully Created Variation: {i} : Task 1 Dataset")
    #task: 0 : V1 is useless : here version is equivalent to number of options
    for i in range(2,6):
        task_0_create_object_level_qna(objects, tasks, oracle, args.root, num_options = i)
        print(f"Successfully Created Variation: {i} : Task 0 Dataset")
    
