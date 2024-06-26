'''
This file is to generate the JSON containing question and empty correct answer for the evaluating the full pipeline:
    - This would include a mixture of all types of reasoning
    - object name[concept level, context level], physical state
    - will be across 2 option, 3option, 4option, 5option
    * 2 major types - Fi and Fm : ideal and moderate correct answers
'''
import json,random, argparse
import os
import constants
import utils
from collections import OrderedDict
from tqdm import tqdm
from full_pipeline_datasets_info import idealDataset
from phrases import phrases

random.seed(constants.DATA_GEN_SEED)
          
def task_f_ideal_config_qna(tasks, oracle, pouch_oracle, all_config,root, num_options):
    '''
    generates Fi dataset : a full pipeline dataset with the correct answer as the ideal physical configuration of oracle object
    
        tasks : json containing tasks
        oracle: json containing Ground Truth (concept,task) -> object mappings
        pouch_oracle : json containing (concept,task) -> ideal_object_configuration mappings
        all_config : json containing all commonly occurring physical configurations of objects
        root : path to root dir
        op_type: int for choosing option sampling strategy
    '''
    
    random.seed(constants.DATA_GEN_SEED)
    
    task_fi_qa_database= [[] for _ in range(len(idealDataset[num_options]))]
    task_fi_q_database = [[] for _ in range(len(idealDataset[num_options]))]
    q_number = [0]* len(idealDataset[num_options])
    def task_f_ideal_sample_config(correct_category, ques, unique_options):
        resample_count = 0
        options = []
        context_wrong_options = []
        concept_wrong_options = []
        random_options = []
        
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
        
        #remaining options

        for config in all_config:
                #context bag (same object - mod, bad)
                if config["object_name"] == ideal_correct_answer[0]['object_name'] and not any(all(config.get(key) == value for key, value in prob_answer.items()) for prob_answer in pouch_oracle[correct_category][ques]):
                    context_wrong_options.append(config)
                #context bag - concat (different obj - mod, bad)
                elif config["object_name"] in oracle[correct_category][ques] and config["object_name"] != ideal_correct_answer[0]['object_name'] and not any(all(config.get(key) == value for key, value in prob_answer.items()) for prob_answer in pouch_oracle[correct_category][ques]):
                    context_wrong_options.append(config)
                #concept bag
                elif config["object_name"] not in oracle[correct_category][ques] and config["object_name"] in objects[correct_category] and not any(all(config.get(key) == value for key, value in prob_answer.items()) for prob_answer in pouch_oracle[correct_category][ques]):
                    concept_wrong_options.append(config)
                #random bag
                elif config["object_name"] not in oracle[correct_category][ques] and config["object_name"] not in objects[correct_category] :
                    random_options.append(config)
        per_ques_dataset_entry = []
        per_ques_correct_answer = []
        for x in range(len(idealDataset[num_options])):
            contextCount = idealDataset[num_options][x][0]
            conceptCount = idealDataset[num_options][x][1]
            randomCount =  idealDataset[num_options][x][2]
            options = []
            resample_count = 0
            
            while True:
                try:
                    if len(context_wrong_options) >= contextCount and len(concept_wrong_options) >= conceptCount:
                        options.extend([final_answer])
                        options.extend(random.sample(context_wrong_options,contextCount))
                        options.extend(random.sample(concept_wrong_options,conceptCount))
                        # pdb.set_trace()
                        options.extend(random.sample(random_options,randomCount))
                    else:
                        print('not enough')
                        options_dict = [-1]
                        per_ques_correct_answer.extend([-1])
                        break

                    if utils.check_repeat(options,unique_options[x],'fi',num_options):
                        break
                    elif not utils.check_repeat(options,unique_options[x],'fi',num_options) and resample_count <= 100:
                        resample_count += 1
                        raise Exception('Repetition in Sampling!')
                    elif resample_count > 100:
                        print('skippig question')
                        options_dict = [-1]
                        per_ques_correct_answer[x] = -1
                        print(per_ques_correct_answer)
                        print(options_dict)
                        break
                        
                except Exception as err:
                    options = []
                    print(f'{err}')
                    print('resampling')
            
            if len(options) == num_options: 
                unique_options[x].append(sorted([option['id'] for option in options]))     
                random.shuffle(options)
                options_dict = {chr(65 + i): option for i, option in enumerate(options)}
                correct_answer = next((key for key, value in options_dict.items() if value == final_answer), None)
                per_ques_correct_answer.append(correct_answer)
            
            
            per_ques_dataset_entry.append(options_dict)
        return per_ques_dataset_entry, per_ques_correct_answer, unique_options
    
    # List of questions
    unique_options = [[] for _ in range(len(idealDataset[num_options]))]
    for cat,task_list in tqdm(tasks.items(),desc='Categories'):    
        for ques in tqdm(task_list,desc='Tasks'):
            count_dict = calculate_fragments_task_1()
            task_q_count = count_dict[cat][ques]
            for _ in range(task_q_count):
                
                question = f"Which of the following objects is best suitable as '{phrases[cat]}' during the task of \"{ques}\"?"
                options, correct_answer,unique_options = task_f_ideal_sample_config(cat,ques,unique_options)
                # pdb.set_trace()
                assert len(options) == len(correct_answer)

                for x,option_i in enumerate(options):
                    print(x)
                    print(correct_answer)
                    q_number[x] +=1 
                    if option_i != [-1] and option_i != [0]:
                        # Create the JSON structure
                        qa_database = {
                            "question_id": q_number[x],
                            "question": question,
                            "context":cat,
                            "options": option_i,
                            "correct_answer": correct_answer[x]
                        }

                        q_database = {
                            "question_id": q_number[x],
                            "question": question,
                            "context":cat,
                            "options": option_i,
                            "correct_answer": {}
                        }
                        task_fi_qa_database[x].append(qa_database)
                        task_fi_q_database[x].append(q_database)
    for x,_ in enumerate(idealDataset[num_options]):
    # Save the JSON data to a file
        if not os.path.exists(os.path.join(root,f"task_fi/{num_options}-options/Variation_{x}/GT_used/")):
            # Create the folder
            os.makedirs(os.path.join(root,f"task_fi/{num_options}-options/Variation_{x}/GT_used/"))
            
        with open(os.path.join(root,f"task_fi/{num_options}-options/Variation_{x}/GT_used/question_answer_database.json"), "w") as json_file:
            json.dump(task_fi_qa_database[x], json_file,indent=4)
        
        # Save the JSON data to a file
        with open(os.path.join(root,f"task_fi/{num_options}-options/Variation_{x}/GT_used/question_database.json"), "w") as json_file:
            json.dump(task_fi_q_database[x], json_file,indent=4)

        print(utils.check_dataset(os.path.join(root,f"task_fi/{num_options}-options/Variation_{x}/GT_used/question_database.json"),'fi'))

def task_f_mod_config_qna(tasks, oracle, pouch_subop, all_config,root, num_options):
    '''Generating Fm dataset : full pipeline dataset with correct answer as most
       appropriate moderate physical configuration of the oracle object
       
       tasks : json containing tasks
       pouch_subop: json containing mappings between (concept,task,'moderate') -> object_configuration and (concept,task,'bad') -> object_configuration  
       root : path to root dir
       op_type: int for choosing option sampling strategy
    '''
    
    random.seed(constants.DATA_GEN_SEED)
    task_fm_qa_database= [[] for _ in range(len(idealDataset[num_options]))]
    task_fm_q_database = [[] for _ in range(len(idealDataset[num_options]))]
    q_number = [0]* len(idealDataset[num_options])
    def task_f_mod_sample_config(correct_category, ques, unique_options):
        '''sampling options'''
        resample_count = 0
        options = []
        context_worse_options = []
        concept_wrong_options = []
        random_options = []
        
        #adding correct option    
        mod_correct_answer = random.sample(pouch_subop[correct_category][ques]['moderate'],1)
        #to add the 'id' in correct option as when generating correct options we don't have that.
        index = mod_correct_answer[0]['id']
        final_answer = OrderedDict([('id', index)] + list(mod_correct_answer[0].items()))
        options.extend([final_answer])
        
        #remaining options
        for config in pouch_subop[correct_category][ques]['moderate']:
                #context bag (same object - mod, bad)
                #context bag - concat (different obj - mod, bad)
                if config["object_name"] in oracle[correct_category][ques] and (config['time_penalty'] + config['material_penalty']) > (mod_correct_answer[0]['material_penalty'] + mod_correct_answer[0]['time_penalty']):
                    context_worse_options.append(config)
        for config in all_config:
                #concept bag
                if config["object_name"] not in oracle[correct_category][ques] and config["object_name"] in objects[correct_category]:
                    concept_wrong_options.append(config)
                #random bag
                elif config["object_name"] not in oracle[correct_category][ques] and config["object_name"] not in objects[correct_category] :
                    random_options.append(config)
        per_ques_dataset_entry = []
        per_ques_correct_answer = []
        for x in range(len(idealDataset[num_options])):
            contextCount = idealDataset[num_options][x][0]
            conceptCount = idealDataset[num_options][x][1]
            randomCount =  idealDataset[num_options][x][2]
            options = []
            resample_count = 0
            
            while True:
                try:
                    if len(context_worse_options) >= contextCount and len(concept_wrong_options) >= conceptCount:
                        options.extend([final_answer])
                        options.extend(random.sample(context_worse_options,contextCount))
                        options.extend(random.sample(concept_wrong_options,conceptCount))
                        options.extend(random.sample(random_options,randomCount))
                    else:
                        print('not enough')
                        # time.sleep(1)
                        options_dict = [-1]
                        per_ques_correct_answer.extend([-1])
                        break

                    if utils.check_repeat(options,unique_options[x],'fm',num_options):
                        break
                    elif not utils.check_repeat(options,unique_options[x],'fm',num_options) and resample_count <= 100:
                        resample_count += 1
                        raise Exception('Repetition in Sampling!')
                    elif resample_count > 100:
                        print('skippig question')
                        options_dict = [-1]
                        per_ques_correct_answer[x] = -1
                        print(per_ques_correct_answer)
                        print(options_dict)
                        break
                        
                except Exception as err:
                    options = []
                    print(f'{err}')
                    print('resampling')
            
            if len(options) == num_options: 
                for option in options:
                    #not all options will have penalty keys (ideal doesnot have)
                    if 'time_penalty' not in option.keys():
                        option['time_penalty'] = 'n'
                    if 'material_penalty' not in option.keys():
                        option['material_penalty'] = 'n'
                        
                unique_options[x].append(sorted([option['id'] for option in options]))     
                random.shuffle(options)
                options_dict = {chr(65 + i): option for i, option in enumerate(options)}
                correct_answer = next((key for key, value in options_dict.items() if value == final_answer), None)
                per_ques_correct_answer.append(correct_answer)
            
            per_ques_dataset_entry.append(options_dict)
        return per_ques_dataset_entry, per_ques_correct_answer, unique_options
    
    # List of questions
    unique_options = [[] for _ in range(len(idealDataset[num_options]))]
    for cat,task_list in tqdm(tasks.items(),desc='Categories'):    
        for ques in tqdm(task_list,desc='Tasks'):
            count_dict = calculate_fragments_task_1()
            task_q_count = count_dict[cat][ques]
            for _ in range(task_q_count):
                
                question = f"Which of the following objects is best suitable as '{phrases[cat]}' during the task of \"{ques}\"?"
                options, correct_answer,unique_options = task_f_mod_sample_config(cat,ques,unique_options)
                assert len(options) == len(correct_answer)

                for x,option_i in enumerate(options):
                    # print(x)
                    # print(correct_answer)
                    q_number[x] +=1 
                    if option_i != [-1] and option_i != [0]:
                        # Create the JSON structure
                        qa_database = {
                            "question_id": q_number[x],
                            "question": question,
                            "context":cat,
                            "options": option_i,
                            "correct_answer": correct_answer[x]
                        }

                        q_database = {
                            "question_id": q_number[x],
                            "question": question,
                            "context":cat,
                            "options": option_i,
                            "correct_answer": {}
                        }
                        task_fm_qa_database[x].append(qa_database)
                        task_fm_q_database[x].append(q_database)
    for x,_ in enumerate(idealDataset[num_options]):
    # Save the JSON data to a file
        if not os.path.exists(os.path.join(root,f"task_fm/{num_options}-options/Variation_{x}/GT_used/")):
            # Create the folder
            os.makedirs(os.path.join(root,f"task_fm/{num_options}-options/Variation_{x}/GT_used/"))
            
        with open(os.path.join(root,f"task_fm/{num_options}-options/Variation_{x}/GT_used/question_answer_database.json"), "w") as json_file:
            json.dump(task_fm_qa_database[x], json_file,indent=4)
        
        # Save the JSON data to a file
        with open(os.path.join(root,f"task_fm/{num_options}-options/Variation_{x}/GT_used/question_database.json"), "w") as json_file:
            json.dump(task_fm_q_database[x], json_file,indent=4)

        print(utils.check_dataset(os.path.join(root,f"task_fm/{num_options}-options/Variation_{x}/GT_used/question_database.json"),'fi'))

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--objects", type=str, default='utils/objects.json')
    parser.add_argument("--tasks", type=str, default='utils/tasks.json')
    parser.add_argument("--oracle", type=str, default='utils/oracle.json' )
    parser.add_argument("--pouch_oracle", type=str, default='utils/pouch_config_oracle.json')
    parser.add_argument("--all_config", type=str, default ='utils/possible_configurations_v1.json')
    parser.add_argument('--pouch_subop',type=str,default='utils/pouch_suboptimal.json')
    parser.add_argument('--root',type=str,default='path-to-thortils/data')
    args = parser.parse_args()
    
    objects = utils.load_dataset(os.path.join(args.root,args.objects))
    tasks = utils.load_dataset(os.path.join(args.root,args.tasks))
    oracle = utils.load_dataset(os.path.join(args.root,args.oracle))
    pouch_oracle = utils.load_dataset(os.path.join(args.root,args.pouch_oracle))
    all_config = utils.load_dataset(os.path.join(args.root,args.all_config))
    pouch_subop = utils.load_dataset(os.path.join(args.root,args.pouch_subop))
    num_options = int(input('how many options?'))
    
    task_f_ideal_config_qna(tasks,oracle, pouch_oracle, all_config, args.root, num_options)
    task_f_mod_config_qna(tasks,oracle, pouch_subop, all_config, args.root, num_options)
