import random
import utils
import os
import argparse
import pdb
from tqdm import tqdm
import json 
from phrases import phrases

TASK_0_NUM_QUESTIONS = 500

def u_task_create_object_level_qna(objects, root, num_options):
    '''main func for creating utility/concept level dataset
    
        objects: objects.json , contains concept-> object GT mappings
        root: path to root dir
        num_options: num of options to be sampled per question (sampling strategy)

    '''
    u_task_qa_database= []
    u_task_q_database = []
    q_number =0

    object_list = set([ob for cat,ob_list in objects.items() for ob in ob_list ])
    def sample_objects(concept, num_options, unique_options):
        '''sampling the options and the correct option'''
        options = []
        #adding correct option    
        correct_answer = random.sample(objects[concept],1)
        options.extend(correct_answer)
        rem_objects = set(object_list) - set(objects[concept])
        while True:
            try:
                options.extend(random.sample(rem_objects,num_options -1))    
            except Exception as error:
                options = []
                continue
        
            unique_options.append(sorted([option for option in options]))
            random.shuffle(options)
            options_dict = {chr(65 + i): option for i, option in enumerate(options)}    
            correct_answer = next((key for key, value in options_dict.items() if value == correct_answer[0]), None)
            
            return options_dict, correct_answer, unique_options

    object_list = set([ob for cat,ob_list in objects.items() for ob in ob_list ])
    
    concept_freq_list =  [len(value) for _,value in objects.items()]
    total = sum(concept_freq_list)
    
    #question freq is decided by count of GT objects per concept/utility
    fragments = dict.fromkeys(objects.keys())
    for i,length in enumerate(concept_freq_list):
        fragment = (length / total) * TASK_0_NUM_QUESTIONS
        fragments[list(objects.keys())[i]] = int(fragment)

    # Handle rounding errors by adjusting the last fragment
    fragments[list(objects.keys())[-1]] += TASK_0_NUM_QUESTIONS - sum(fragments.values())
    print(fragments)
    
    # List of questions
    for cat in tqdm(objects.keys(),desc='Categories'):
        unique_options = list()
        for _ in range(fragments[cat]):

            question = f"Which of the following objects can be described as '{phrases[cat]}'?"
            while True:
                try:
                    options, correct_answer,unique_options = sample_objects(cat, num_options, unique_options)
                    if options in [0,-1]:
                        print('encountered an issue.... retrying')
                        continue
                except Exception as e:
                    print(f'Error - {e}')    
                break
            q_number += 1
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
            u_task_qa_database.append(qa_database)
            u_task_q_database.append(q_database)
    
    if not os.path.exists(os.path.join(root,f"data/task_u/Variation_{num_options}/GT_used/")):
        # Create the folder
        os.makedirs(os.path.join(root,f"data/task_u/Variation_{num_options}/GT_used/"))
        
    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_u/Variation_{num_options}/GT_used/question_database.json"), "w") as json_file:
        json.dump(u_task_q_database, json_file,indent=4)

    # Save the JSON data to a file
    with open(os.path.join(root,f"data/task_u/Variation_{num_options}/GT_used/question_answer_database.json"), "w") as json_file:
        json.dump(u_task_qa_database, json_file,indent=4)
    print(utils.check_dataset(os.path.join(root,f"data/task_u/Variation_{num_options}/GT_used/question_database.json"),0))


if __name__ == "__main__":
    root = 'path-to-thortils'
    objects = utils.load_dataset(os.path.join(root,'data/utils/objects.json'))
    u_task_create_object_level_qna(objects,root, 2)
    u_task_create_object_level_qna(objects,root, 3)
    u_task_create_object_level_qna(objects,root, 4)
    u_task_create_object_level_qna(objects,root, 5)
