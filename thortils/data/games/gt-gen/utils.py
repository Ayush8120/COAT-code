import json,pdb
from tqdm import tqdm
import constants
import google.generativeai as palm
import os
from pprint import pprint

# palm.configure(api_key=os.getenv("AYUSH_PALM_API_KEY"))
palm.configure(api_key=os.getenv("RAGHAV_PALM_API_KEY"))

def check_repeat(options, unique_options, task, opt_count):
    assert len(options) == opt_count, 'You messed up in sampling!'
    combination = []
    for config in options:
        if task in [1,2]:
            combination.append(config['id'])
        elif task == 0:
            combination.append(config)
    combination = sorted(combination)
    
    assert len(combination) == len(set(combination)), "Ouch..!! Sampled same object more than once!"
    
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
        for config in ques_card['options'].values():
            if task in [1,2]:
                combination.append(config['id'])
            elif task == 0:
                combination.append(config)
        combination = sorted(combination)
        if task in [1,2]:
            combination.append(ques_card['context'])
        else:
            combination.append(ques_card['concept'])
        combination.append(ques_card['question'])
        if tuple(combination) in unique_options:
            print("Repetitive Options Sampled!")       
        else:
            unique_options.append((combination))
    return len(unique_options)

def find_first_alpha_char(input_string):
    for i,char in enumerate(input_string):
        if char.isalpha():
            # print(char)
            return i,char
    return None

def fixing_front(bad_string):
    j,_ = find_first_alpha_char(bad_string)
    bad_string = bad_string[j:]
    final = "{\"" + bad_string
    # print(f"after front : {final}")
    return final

def fixing_end(bad_string):
    j,_ = find_first_alpha_char(reversed(bad_string))
    bad_string = bad_string[:len(bad_string) - j]
    final = bad_string + "\"}"
    # print(f"after end : {final}")
    return final

def fix_mid(bad_string):

    # between "answer" and answer key
    answer_part = bad_string.split("answer")[1]
    i,character = find_first_alpha_char(answer_part)
    answer_part = answer_part[i:]
    answer = bad_string.split("answer")[0] + "answer\": \"" + answer_part
    # print(f"after start-mid : {answer}")
    
    # between "reason" and reason value
    reason_part = answer.split("reason")[1]
    j,character = find_first_alpha_char(reason_part)
    reason = reason_part[j:]
    final = answer.split("reason")[0][:-1] + "\"reason\": \"" + reason
    # print(f"after-reason-mid ; {final}")

    #       "E'
    k,character = find_first_alpha_char(final.split("answer")[1].split("reason")[0])
    index = final.index(character) # Since capital A,B,C,D,E won't appear in "answer" key
    answer = final[:index+1] + '\"' + final[index+2:]

    final_answer = answer.replace( "\\", "", 1)
    return final_answer
    
    
def process_ouput(bad_string):
    output = fixing_front(bad_string)
    output = fixing_end(output)
    output = fix_mid(output)
    # output = output[1:-1].replace('}','')
    # print("final" + output)
    return output

# Load dataset from JSON file
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
    

# Evaluation script to get accuracy
def evaluate_accuracy(prediction_filename, correct_answer_filename, web_gpt = False):
    # Load true responses
    dataset = load_dataset(correct_answer_filename)
    true_responses = {entry["question_id"]: entry["correct_answer"] for entry in dataset}

    # Load predicted responses
    predicted_responses = load_dataset(prediction_filename)
    
    correct = 0
    total = len(true_responses)
    for question_id, true_response in true_responses.items():
        if not web_gpt:
            predicted_response = predicted_responses[question_id-1]["answer"]
        else:
            predicted_response = predicted_responses[str(question_id)]
        assert len(true_responses) == len(predicted_responses) , print(str(len(predicted_responses)) +"re-do the exp- you have mismatching predicted and gt")
        if predicted_response and predicted_response == true_response:
            correct += 1
    
    accuracy = correct / total * 100
    return accuracy


# Function for prompting and saving responses in a JSON file
def prompt_and_save(dataset, responses_filename, LLM, run, task_num):
    responses = []
    for _, entry in tqdm(enumerate(dataset)):
        output = {}
        question_id = entry["question_id"]
        question = entry["question"]
        options = [entry["options"]]
        output['id'] = question_id
        output['question'] = question

        if task_num== 0:
            pre_prompt = str(question) +'\n\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects. Here, reversible_using means an object can be used after some time, but not immediately. Whereas, irreversible_using means that an object is busy and cannot be used." + '\n\n' + str(options) + "\n\n . Choose the object that would be best. Answer should be a JSON Dictionary. For example a sample answer looks like: {\"answer\": \"A\" , \"reason\": \"Your reason for choosing option A\"}}"
        elif task_num == 1:
            pre_prompt = str(question) +'\n\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects. Here, reversible_using means an object can be used after some time, but not immediately. Whereas, irreversible_using means that an object is busy and cannot be used." + '\n\n' + str(options) + "\n\n . Choose the object that would be best. Answer should be a JSON Dictionary. For example a sample answer looks like: {\"answer\": \"A\" , \"reason\": \"Your reason for choosing option A\"}}"
        elif task_num == 2:
            pre_prompt = str(question) +'\n\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects. Here, reversible_using means an object can be used after some time, but not immediately. Whereas, irreversible_using means that an object is busy and cannot be used." + '\n\n' + str(options) + "\n\n . Choose the object that would be best. Answer should be a JSON Dictionary. For example a sample answer looks like: {\"answer\": \"A\" , \"reason\": \"Your reason for choosing option A\"}}"

        if LLM.model =='PaLM':
            result = LLM.palm_prompt(prompt= pre_prompt)
                
            # print(mod_response)
            # mod_response = process_ouput(mod_response)
            # print(mod_response)
            # result = json.loads(mod_response)
            output['answer'] = result['answer']
            output['reason'] = result['reason']
        
        elif LLM.model == 'AZURE_GPT3.5':
            result = LLM.gpt_prompt(prompt= pre_prompt)
            # result = json.loads(result)
            output['answer'] = result['answer']
            output['reason'] = result['reason']
            # pprint(output)

        elif LLM.model == "vicuna7b" or "vicuna13b":

            while True:
                result = LLM.fastchat_prompt(prompt = pre_prompt )
                print(result)
                try:
                    mod_response = process_ouput(result)
                    result = json.loads(mod_response)
                    break
                except:
                    # print('redo_below')
                    # print(mod_response)
                    print('reattempt')
                    continue
    
            output['answer'] = result['answer']
            output['reason'] = result['reason']
        
        # elif LLM_Shop.model == 'fastchat-t5-3b':

        #     result = LLM_Shop.fastchat_prompt(prompt = pre_prompt + '\n\n' + question +'\n\n' + "\n" + str(options) + "\n\n ")
        #     pdb.set_trace()
        #     output['answer'] = result
        #     # output['reason'] = result['reason']

        responses.append(output)
        
    with open(responses_filename, "w") as file:
        json.dump(responses, file, indent=4)

# acc = evaluate_accuracy('./data/GPT_Web_task_1_responses.json',1,True)
# pdb.set_trace()

# stry = "{\"answer\": \"A\" , \"reason\": \"To clean the sink, I would need water and soap, which can be obtained from the SinkBasin. Other options do not provide the necessary tools for cleaning\"}"
# ac = process_ouput(stry)
# pdb.set_trace()