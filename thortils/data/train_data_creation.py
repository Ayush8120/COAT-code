import utils as utils
import pdb, os, math, re, json, sys
import argparse, random
import finetune_config
'''
we take slices of our previously curated task-u,0,1,2 datasets to finetune PaLM language model 
'''
def check_ft_data(dataset):
    '''checking that no repetitions occur in dataset'''
    q_pouch = []
    for q in dataset:
        q_pouch.extend([q['question_id']])
    print(len(q_pouch))
    print(len(set(q_pouch)))
    assert len(q_pouch) == len(set(q_pouch)), 'Repeat samples found please redo!'

def get_util_distribution(objects,total_count):
    '''utility vs ques distribution'''
    ob = 0
    count_obj_util = {}
    for util,obj_list in objects.items():
        count_obj_util[util] = len(obj_list)
        ob += len(obj_list)    
    count_each_util = {cat: int((count_obj_util[cat]*total_count)/ob) for cat,_ in tasks.items()}
    while True:
        for i in count_each_util.keys():    
            # pdb.set_trace()
            count_each_util[i] += 1
            if sum(count_each_util.values()) == total_count:
                # assert sum(count_each_util.values()) == total_count, 'You messed up!'
                print('Generated per utility ques distribution!')
                return count_obj_util, count_each_util
            
def get_task_distribution(tasks,oracle,total_count):
    '''(utility,task) vs ques distribution'''
    _, count_each_util = get_util_distribution(objects,total_count = total_count)
    count_each_task = {}
    c_t = 0
    for cat,task_list in tasks.items():
        count_each_task[cat] = {}
        cat_all_task_oracle = [item for sublist in list(oracle[cat].values()) for item in sublist]
        for task in task_list:
            t = int((len(oracle[cat][task])/len(cat_all_task_oracle))* count_each_util[cat])
            count_each_task[cat][task] = t
            c_t += t
    for c in count_each_task.keys():    
        # pdb.set_trace()
        for t in count_each_task[c].keys(): 
            if sum(count_each_task[c].values()) == count_each_util[c]:
                break
            count_each_task[c][t] += 1
    print('Generated per <utility,task> ques distribution!')            
    return count_each_task

def set_remove(full, selected):
    sel = []
    rem = []
    for s in selected:
        sel.extend([s['question_id']])
    for qu in full:
        if qu['question_id'] not in sel:
            rem.extend([qu])
    return rem

def sample_examples(args, objects,tasks,oracle, data_type = 'p2'):
    '''sample question-answer pairs from previously created datasets'''
    if data_type == 'p1':
        '''sample question-answer pairs from previously created datasets [task-1]'''
        count_each_task = get_task_distribution(tasks,oracle,total_count = finetune_config.TASK_1_EX_COUNT/3)
        task_1_qna_1 = utils.load_dataset(os.path.join(args.root, args.task_1_1))
        task_1_qna_2 = utils.load_dataset(os.path.join(args.root, args.task_1_2))
        task_1_qna_3 = utils.load_dataset(os.path.join(args.root, args.task_1_3))

        config_pouch_1_1 = {}
        config_pouch_1_2 = {}
        config_pouch_1_3 = {}
        data_1_full = []
        data_1_eval = []
        for c,t in tasks.items():
            config_pouch_1_1[c] = {}
            config_pouch_1_2[c] = {}
            config_pouch_1_3[c] = {}
            for ti in t:
                config_pouch_1_1[c][ti] = []
                config_pouch_1_2[c][ti] = []
                config_pouch_1_3[c][ti] = []
            
        for q in task_1_qna_1:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_1_1[q['context']][t].append(q) 
        for q in task_1_qna_2:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_1_2[q['context']][t].append(q) 
        for q in task_1_qna_3:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_1_3[q['context']][t].append(q) 

        less_1 = 0
        less_2 = 0
        less_3 = 0
        corn_1 = []
        corn_2 = []
        corn_3 = []
        for c in count_each_task.keys():
            for t in count_each_task[c].keys():
                x1 = len(config_pouch_1_1[c][t]) - count_each_task[c][t]
                x2 = len(config_pouch_1_2[c][t]) - count_each_task[c][t]
                x3 = len(config_pouch_1_3[c][t]) - count_each_task[c][t]
                
                if x1 >= 0:    
                    random.seed(0)
                    data_1_1 = random.sample(config_pouch_1_1[c][t], count_each_task[c][t])
                    rem_1 = set_remove(config_pouch_1_1[c][t], data_1_1)
                    eval_data_1_1 = random.sample(rem_1, min(len(rem_1), count_each_task[c][t]))
                    data_1_eval.extend(eval_data_1_1) 
                    if x1 > 40:
                        corn_1.append((c,t,x1))
                    data_1_full.extend(data_1_1)
                    
                if x2 >= 0:
                    data_1_2 = random.sample(config_pouch_1_2[c][t], count_each_task[c][t])
                    rem_2 = set_remove(config_pouch_1_2[c][t], data_1_2)
                    eval_data_1_2 = random.sample(rem_2, min(len(rem_2), count_each_task[c][t]))
                    data_1_eval.extend(eval_data_1_2) 
                    if x2 > 40:
                        corn_2.append((c,t,x2))
                    data_1_full.extend(data_1_2)
                    
                if x3 >= 0:
                    data_1_3 = random.sample(config_pouch_1_3[c][t], count_each_task[c][t])
                    rem_3 = set_remove(config_pouch_1_3[c][t], data_1_3) 
                    eval_data_1_3 = random.sample(rem_3, min(len(rem_3), count_each_task[c][t]))                    
                    data_1_eval.extend(eval_data_1_3) 
                    if x3 > 40:
                        corn_3.append((c,t,x3))
                    data_1_full.extend(data_1_3)

                if x1 < 0:
                    less_1 += abs(x1)
                    data_1_1 = random.sample(config_pouch_1_1[c][t], len(config_pouch_1_1[c][t]))         
                    data_1_full.extend(data_1_1)
                    rem_1 = set_remove(config_pouch_1_1[c][t], data_1_1)
                    eval_data_1_1 = random.sample(rem_1, min(len(rem_1), count_each_task[c][t]))
                    data_1_eval.extend(eval_data_1_1)

                if x2 < 0:
                    less_2 += abs(x2)
                    data_1_2 = random.sample(config_pouch_1_2[c][t], len(config_pouch_1_2[c][t]))
                    data_1_full.extend(data_1_2)
                    rem_2 = set_remove(config_pouch_1_2[c][t], data_1_2)
                    eval_data_1_2 = random.sample(rem_2, min(len(rem_2), count_each_task[c][t]))
                    data_1_eval.extend(eval_data_1_2)
                                    
                if x3 < 0:
                    less_3 += abs(x3)
                    data_1_3 = random.sample(config_pouch_1_3[c][t], len(config_pouch_1_3[c][t]))                
                    data_1_full.extend(data_1_3)
                    rem_3 = set_remove(config_pouch_1_3[c][t], data_1_3)
                    eval_data_1_3 = random.sample(rem_3, min(len(rem_3), count_each_task[c][t]))
                    data_1_eval.extend(eval_data_1_3)
        flag = 0
        while True:
            for tup in corn_1:
                if less_1 != 0:
                    temp = random.sample(config_pouch_1_1[tup[0]][tup[1]],1)
                    less_1 -= 1
                    data_1_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        
        flag = 0
        while True:
            for tup in corn_2:
                if less_2 != 0:
                    temp = random.sample(config_pouch_1_2[tup[0]][tup[1]],1)
                    less_2 -= 1
                    data_1_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        
        flag = 0
        while True:
            for tup in corn_3:
                if less_3 != 0:
                    temp = random.sample(config_pouch_1_3[tup[0]][tup[1]],1)
                    less_3 -= 1
                    data_1_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        
        if not os.path.exists(os.path.join(args.root,f"ft_data/task_1/Variation_1_2_3/GT_used/")):
            # Create the folder
            os.makedirs(os.path.join(args.root,f"ft_data/task_1/Variation_1_2_3/GT_used/"))
        if not os.path.exists(os.path.join(args.root,f"ft_data/task_1/Variation_1_2_3/eval/")):
            # Create the folder
            os.makedirs(os.path.join(args.root,f"ft_data/task_1/Variation_1_2_3/eval/"))
                
        with open(os.path.join(args.root,f"ft_data/task_1/Variation_1_2_3/eval/raw_question_answer_database.json"), "w") as json_file:
            json.dump(data_1_eval, json_file,indent=4)

        with open(os.path.join(args.root,f"ft_data/task_1/Variation_1_2_3/GT_used/raw_question_answer_database.json"), "w") as json_file:
            json.dump(data_1_full, json_file,indent=4)

        #check no repeat samples
        check_ft_data(data_1_full)
        print('Finetune data for task-1 sampled, done and dusted!')

    if data_type == 'p2':
        '''sample question-answer pairs from previously created datasets [task-2]''' 
        count_each_task = get_task_distribution(tasks,oracle,total_count = finetune_config.TASK_2_EX_COUNT/5)
        task_2_qna_1 = utils.load_dataset(os.path.join(args.root, args.task_2_1))
        task_2_qna_2 = utils.load_dataset(os.path.join(args.root, args.task_2_2))
        task_2_qna_3 = utils.load_dataset(os.path.join(args.root, args.task_2_3))
        task_2_qna_4 = utils.load_dataset(os.path.join(args.root, args.task_2_4))
        task_2_qna_5 = utils.load_dataset(os.path.join(args.root, args.task_2_5))

        config_pouch_2_1 = {}
        config_pouch_2_2 = {}
        config_pouch_2_3 = {}
        config_pouch_2_4 = {}
        config_pouch_2_5 = {}
        


        data_2_full = []
        data_2_eval = []
        for c,t in tasks.items():
            config_pouch_2_1[c] = {}
            config_pouch_2_2[c] = {}
            config_pouch_2_3[c] = {}
            config_pouch_2_4[c] = {}
            config_pouch_2_5[c] = {}
            
            for ti in t:
                config_pouch_2_1[c][ti] = []
                config_pouch_2_2[c][ti] = []
                config_pouch_2_3[c][ti] = []
                config_pouch_2_4[c][ti] = []
                config_pouch_2_5[c][ti] = []
            
        for q in task_2_qna_1:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_2_1[q['context']][t].append(q) 
        for q in task_2_qna_2:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_2_2[q['context']][t].append(q) 
        for q in task_2_qna_3:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_2_3[q['context']][t].append(q) 
        for q in task_2_qna_4:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_2_4[q['context']][t].append(q) 
        for q in task_2_qna_5:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_2_5[q['context']][t].append(q) 

        less_1 = 0
        less_2 = 0
        less_3 = 0
        less_4 = 0
        less_5 = 0

        corn_1 = []
        corn_2 = []
        corn_3 = []
        corn_4 = []
        corn_5 = []
        
        for c in count_each_task.keys():
            for t in count_each_task[c].keys():
                x1 = len(config_pouch_2_1[c][t]) - count_each_task[c][t]
                x2 = len(config_pouch_2_2[c][t]) - count_each_task[c][t]
                x3 = len(config_pouch_2_3[c][t]) - count_each_task[c][t]
                x4 = len(config_pouch_2_4[c][t]) - count_each_task[c][t]
                x5 = len(config_pouch_2_5[c][t]) - count_each_task[c][t]
                
                if x1 >= 0:    
                    random.seed(0)
                    data_2_1 = random.sample(config_pouch_2_1[c][t], count_each_task[c][t])
                    rem_1 = set_remove(config_pouch_2_1[c][t], data_2_1)
                    eval_data_2_1 = random.sample(rem_1, min(len(rem_1), count_each_task[c][t]))
                    data_2_eval.extend(eval_data_2_1) 
                    if x1 > 40:
                        corn_1.append((c,t,x1))
                    data_2_full.extend(data_2_1)
                    
                if x2 >= 0:
                    data_2_2 = random.sample(config_pouch_2_2[c][t], count_each_task[c][t])
                    rem_2 = set_remove(config_pouch_2_2[c][t], data_2_2)
                    eval_data_2_2 = random.sample(rem_2, min(len(rem_2), count_each_task[c][t]))
                    data_2_eval.extend(eval_data_2_2) 
                    if x2 > 40:
                        corn_2.append((c,t,x2))
                    data_2_full.extend(data_2_2)
                    
                if x3 >= 0:
                    data_2_3 = random.sample(config_pouch_2_3[c][t], count_each_task[c][t])
                    rem_3 = set_remove(config_pouch_2_3[c][t], data_2_3) 
                    eval_data_2_3 = random.sample(rem_3, min(len(rem_3), count_each_task[c][t]))                    
                    data_2_eval.extend(eval_data_2_3) 
                    if x3 > 40:
                        corn_3.append((c,t,x3))
                    data_2_full.extend(data_2_3)
                
                if x4 >= 0:
                    data_2_4 = random.sample(config_pouch_2_4[c][t], count_each_task[c][t])
                    rem_4 = set_remove(config_pouch_2_4[c][t], data_2_4) 
                    eval_data_2_4 = random.sample(rem_4, min(len(rem_4), count_each_task[c][t]))                    
                    data_2_eval.extend(eval_data_2_4) 
                    if x4 > 40:
                        corn_4.append((c,t,x4))
                    data_2_full.extend(data_2_4)

                if x5 >= 0:
                    data_2_5 = random.sample(config_pouch_2_5[c][t], count_each_task[c][t])
                    rem_5 = set_remove(config_pouch_2_5[c][t], data_2_5) 
                    eval_data_2_5 = random.sample(rem_5, min(len(rem_5), count_each_task[c][t]))                    
                    data_2_eval.extend(eval_data_2_5) 
                    if x5 > 40:
                        corn_5.append((c,t,x5))
                    data_2_full.extend(data_2_5)

                if x1 < 0:
                    less_1 += abs(x1)
                    data_2_1 = random.sample(config_pouch_2_1[c][t], len(config_pouch_2_1[c][t]))         
                    data_2_full.extend(data_2_1)
                    rem_1 = set_remove(config_pouch_2_1[c][t], data_2_1)
                    eval_data_2_1 = random.sample(rem_1, min(len(rem_1), count_each_task[c][t]))
                    data_2_eval.extend(eval_data_2_1)

                if x2 < 0:
                    less_2 += abs(x2)
                    data_2_2 = random.sample(config_pouch_2_2[c][t], len(config_pouch_2_2[c][t]))
                    data_2_full.extend(data_2_2)
                    rem_2 = set_remove(config_pouch_2_2[c][t], data_2_2)
                    eval_data_2_2 = random.sample(rem_2, min(len(rem_2), count_each_task[c][t]))
                    data_2_eval.extend(eval_data_2_2)
                                    
                if x3 < 0:
                    less_3 += abs(x3)
                    data_2_3 = random.sample(config_pouch_2_3[c][t], len(config_pouch_2_3[c][t]))                
                    data_2_full.extend(data_2_3)
                    rem_3 = set_remove(config_pouch_2_3[c][t], data_2_3)
                    eval_data_2_3 = random.sample(rem_3, min(len(rem_3), count_each_task[c][t]))
                    data_2_eval.extend(eval_data_2_3)

                if x4 < 0:
                    less_4 += abs(x4)
                    data_2_4 = random.sample(config_pouch_2_4[c][t], len(config_pouch_2_4[c][t]))                
                    data_2_full.extend(data_2_4)
                    rem_4 = set_remove(config_pouch_2_4[c][t], data_2_4)
                    eval_data_2_4 = random.sample(rem_4, min(len(rem_4), count_each_task[c][t]))
                    data_2_eval.extend(eval_data_2_4)
                
                if x5 < 0:
                    less_5 += abs(x5)
                    data_2_5 = random.sample(config_pouch_2_5[c][t], len(config_pouch_2_5[c][t]))                
                    data_2_full.extend(data_2_5)
                    rem_5 = set_remove(config_pouch_2_5[c][t], data_2_5)
                    eval_data_2_5 = random.sample(rem_5, min(len(rem_5), count_each_task[c][t]))
                    data_2_eval.extend(eval_data_2_5)
        flag = 0
        while True:
            for tup in corn_1:
                if less_1 != 0:
                    temp = random.sample(config_pouch_2_1[tup[0]][tup[1]],1)
                    less_1 -= 1
                    data_2_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        
        flag = 0
        while True:
            for tup in corn_2:
                if less_2 != 0:
                    temp = random.sample(config_pouch_2_2[tup[0]][tup[1]],1)
                    less_2 -= 1
                    data_2_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        
        flag = 0
        while True:
            for tup in corn_3:
                if less_3 != 0:
                    temp = random.sample(config_pouch_2_3[tup[0]][tup[1]],1)
                    less_3 -= 1
                    data_2_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        flag = 0
        while True:
            for tup in corn_4:
                if less_4 != 0:
                    temp = random.sample(config_pouch_2_4[tup[0]][tup[1]],1)
                    less_4 -= 1
                    data_2_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        flag = 0
        while True:
            for tup in corn_5:
                if less_5 != 0:
                    temp = random.sample(config_pouch_2_5[tup[0]][tup[1]],1)
                    less_5 -= 1
                    data_2_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        
        if not os.path.exists(os.path.join(args.root,f"ft_data/task_2/Variation_1_2_3_4_5/GT_used/")):
            # Create the folder
            os.makedirs(os.path.join(args.root,f"ft_data/task_2/Variation_1_2_3_4_5/GT_used/"))
        if not os.path.exists(os.path.join(args.root,f"ft_data/task_2/Variation_1_2_3_4_5/eval/")):
            # Create the folder
            os.makedirs(os.path.join(args.root,f"ft_data/task_2/Variation_1_2_3_4_5/eval/"))
                
        with open(os.path.join(args.root,f"ft_data/task_2/Variation_1_2_3_4_5/eval/raw_question_answer_database.json"), "w") as json_file:
            json.dump(data_2_eval, json_file,indent=4)

        with open(os.path.join(args.root,f"ft_data/task_2/Variation_1_2_3_4_5/GT_used/raw_question_answer_database.json"), "w") as json_file:
            json.dump(data_2_full, json_file,indent=4)

        #check no repeat samples
        check_ft_data(data_2_full)
        print('Finetune data for task-2 sampled, done and dusted!')

    if data_type == 'o':
        '''sample question-answer pairs from previously created datasets [task-0]'''
    
        # decide the utility proportion
        count_obj_util, count_each_util = get_util_distribution(objects,total_count = finetune_config.TASK_U_EX_COUNT)
        # for object level : concept objects ke proportion mai
        #task-0 distribution : oracle of <util,task> / oracle <util,all task> * count of questions allocated for that utility
        count_each_task = get_task_distribution(tasks,oracle,total_count = finetune_config.TASK_0_EX_COUNT)
        # print(count_each_task)
        # print(count_each_util)

        #load task u datset
        task_u_qna = utils.load_dataset(os.path.join(args.root, args.task_u))
        u_data = []
        u_data_eval = []
        u_config_pouch = {}
        for c in tasks.keys():
            u_config_pouch[c] = []
        for q in task_u_qna:
            u_config_pouch[q['concept']].append(q) 
        for c in count_each_util.keys():
            try:
                data = random.sample(u_config_pouch[c], count_each_util[c])
                rem = set_remove(u_config_pouch[c], data)
                eval_data = random.sample(rem, min(len(rem), count_each_util[c]))
                u_data.extend(data)
                u_data_eval.extend(eval_data)
            except Exception as e:
                print(f'{e}')
                pdb.set_trace()

        if not os.path.exists(os.path.join(args.root,f"ft_data/task_u/Variation_5/GT_used/")):
                # Create the folder
                os.makedirs(os.path.join(args.root,f"ft_data/task_u/Variation_5/GT_used/"))

        if not os.path.exists(os.path.join(args.root,f"ft_data/task_u/Variation_5/eval/")):
                # Create the folder
                os.makedirs(os.path.join(args.root,f"ft_data/task_u/Variation_5/eval/"))
        
        with open(os.path.join(args.root,f"ft_data/task_u/Variation_5/eval/raw_question_answer_database.json"), "w") as json_file:
            json.dump(u_data_eval, json_file,indent=4)

        with open(os.path.join(args.root,f"ft_data/task_u/Variation_5/GT_used/raw_question_answer_database.json"), "w") as json_file:
            json.dump(u_data, json_file,indent=4)

        check_ft_data(u_data)
        print('Finetune data for task-u sampled, done and dusted!')
        # load task 0 dataset
        task_0_qna = utils.load_dataset(os.path.join(args.root,args.task_0))
        config_pouch_0 = {}
        data_0_full = []
        data_0_eval = []
        for c,t in tasks.items():
            config_pouch_0[c] = {}
            for ti in t:
                config_pouch_0[c][ti] = []
            
        for q in task_0_qna:
            t = re.findall(r'"([^"]*)"', q['question'])[-1]
            config_pouch_0[q['concept']][t].append(q) 
        
        less = 0
        corn = []
        for c in count_each_task.keys():
            for t in count_each_task[c].keys():
                x = len(config_pouch_0[c][t]) - count_each_task[c][t]
                if x >= 0:    
                    random.seed(0)
                    data_0 = random.sample(config_pouch_0[c][t], count_each_task[c][t])
                    rem = set_remove(config_pouch_0[c][t], data_0)
                    eval_data_0 = random.sample(rem, min(len(rem), count_each_task[c][t]))
                    data_0_eval.extend(eval_data_0) 
                    if x > 40:
                        corn.append((c,t,x))
                    data_0_full.extend(data_0)
                else:
                    less += abs(x)
                    data_0 = random.sample(config_pouch_0[c][t], len(config_pouch_0[c][t]))                
                    data_0_full.extend(data_0)
                    rem = set_remove(config_pouch_0[c][t], data_0)
                    eval_data_0 = random.sample(rem, min(len(rem), count_each_task[c][t]))
                    data_0_eval.extend(eval_data_0) 
                    
        flag = 0
        while True:
            for tup in corn:
                if less != 0:
                    temp = random.sample(config_pouch_0[tup[0]][tup[1]],1)
                    less -= 1
                    data_0_full.extend(temp)
                else:
                    flag = 1
                    break
            if flag == 1:
                break
        
        if not os.path.exists(os.path.join(args.root,f"ft_data/task_0/Variation_4/GT_used/")):
                # Create the folder
                os.makedirs(os.path.join(args.root,f"ft_data/task_0/Variation_4/GT_used/"))
        if not os.path.exists(os.path.join(args.root,f"ft_data/task_0/Variation_4/eval/")):
                # Create the folder
                os.makedirs(os.path.join(args.root,f"ft_data/task_0/Variation_4/eval/"))
                
        with open(os.path.join(args.root,f"ft_data/task_0/Variation_4/eval/raw_question_answer_database.json"), "w") as json_file:
            json.dump(data_0_eval, json_file,indent=4)

        with open(os.path.join(args.root,f"ft_data/task_0/Variation_4/GT_used/raw_question_answer_database.json"), "w") as json_file:
            json.dump(data_0_full, json_file,indent=4)

        #check no repeat samples
        check_ft_data(data_0_full)
        print('Finetune data for task-0 sampled, done and dusted!')

if __name__ == '__main__':

    while True:
        try:
            data_type = input('Do you want Object Level[o] or Physical State Level[p(1/2)]?')
            if data_type not in ['o','p1','p2']:
                raise Exception('Oops! Invalid input')
            else:
                break
        except Exception as err:
            print('Please enter valid input!')

    parser = argparse.ArgumentParser()
    parser.add_argument("--objects", type=str, default='utils/objects.json')
    parser.add_argument("--tasks", type=str, default='utils/tasks.json')
    parser.add_argument("--oracle", type=str, default='utils/oracle.json' )
    parser.add_argument('--root',type=str,default='path to thortils/data')
    parser.add_argument('--task_u', type=str, default='task_u/Variation_5/GT_used/question_answer_database.json')
    parser.add_argument('--task_0', type=str, default='task_0/Variation_4/GT/question_answer_database.json')
    parser.add_argument('--task_1_1', type=str, default='task_1/Variation_1/GT/question_answer_database.json')
    parser.add_argument('--task_1_2', type=str, default='task_1/Variation_2/GT/question_answer_database.json')
    parser.add_argument('--task_1_3', type=str, default='task_1/Variation_3/GT/question_answer_database.json')
    parser.add_argument('--task_2_1', type=str, default='task_2/Variation_1/GT/question_answer_database.json')
    parser.add_argument('--task_2_2', type=str, default='task_2/Variation_2/GT/question_answer_database.json')
    parser.add_argument('--task_2_3', type=str, default='task_2/Variation_3/GT/question_answer_database.json')
    parser.add_argument('--task_2_4', type=str, default='task_2/Variation_4/GT/question_answer_database.json')
    parser.add_argument('--task_2_5', type=str, default='task_2/Variation_5/GT/question_answer_database.json')

    args = parser.parse_args()
    
    objects = utils.load_dataset(os.path.join(args.root,args.objects))
    tasks = utils.load_dataset(os.path.join(args.root,args.tasks))
    oracle = utils.load_dataset(os.path.join(args.root,args.oracle))
    
    sample_examples(args, objects,tasks,oracle,data_type)
