import json , random, pdb
from tqdm import tqdm
import constants
from database import Shelf
from collections import Counter
import re, math

"""
Utils for extracting useful information from LLM outputs using Regex and String Operations
"""
def extract_each_ans_llama(input_string):
    input_string = input_string.strip()
    input_string = input_string.replace('\n', '')
    pattern1= r'[\'"][A-Z][\'"]'
    pattern2 = r'\([A-Z]\)'
    pattern3= r'[\'"][A-Z]:'
    pattern4 = r'[\'"][A-Z]'
    pattern7 = r'Option\s[A-E]'
    pattern8 = r'option\s[A-E]'
    pattern9 = r'[\'"]answer[\'"]: [\'"][A-Za-z][\'"]'
    pattern10 = r'[\'"]answer[\'"]:[\'"][A-Za-z][\'"]'
    
    if re.findall(pattern9, input_string):
        out = '{' + re.findall(pattern9, input_string)[0].replace('\'','"') + '}'
        # pdb.set_trace()
        return out
    elif re.findall(pattern10, input_string):
        out = '{' + re.findall(pattern10, input_string)[0].replace('\'','"') + '}'
        return out
    
    elif re.findall(pattern7, input_string):
        out = '{' + '"answer"' + ': "' + re.findall(pattern7, input_string)[0].split('Option ')[1] + '"' + '}'
        return out
    elif re.findall(pattern8, input_string):
        out = '{' + '"answer"' + ': "' + re.findall(pattern8, input_string)[0].split('option ')[1] + '"' + '}'
        return out
    elif re.findall(pattern1, input_string):
        out = '{' + '"answer"' + ': ' + re.findall(pattern1, input_string)[0].replace('\'','"') + '}'
        return out
    elif re.findall(pattern2, input_string):
        out = '{' + '"answer"' + ': ' + re.findall(pattern2, input_string)[0].strip('()') + '}'
        return out
    elif re.findall(pattern3, input_string):
        out = '{' + '"answer"' + ': "' + re.findall(pattern3, input_string)[0][1] + '"'+ '}'
        return out
    elif re.findall(pattern4, input_string):
        out = '{' + '"answer"' + ': "' + re.findall(pattern4, input_string)[0][1] + '"'+ '}'
        return out
    else:
        return None
    
def give_key(target_value, my_dict):
    # If sure only 1 occurrence of target value 
    ans = [key for key, value in my_dict.items() if value.replace(" ", "").lower() == target_value.replace(" ", "").lower()]
    if len(ans):
        return ans
    else:
        return None

def extract_ans(input_string):
    input_string = input_string.strip()
    input_string = input_string.replace('\n', '')
    if len(input_string) == 1:
        return "{" + f'"answer": "{input_string}"' + "}"

    pattern = r'[\'"]answer[\'"]: [\'"][A-Za-z][\'"]'
    pattern2 = r'[\'"]answer[\'"]:[\'"][A-Za-z][\'"]'

    if re.findall(pattern, input_string):
        return '{' + re.findall(pattern, input_string)[0].replace('\'','"') + '}'
    elif re.findall(pattern2, input_string):
        return '{' + re.findall(pattern2, input_string)[0].replace('\'','"') + '}'
    else:
        return None

def extract_ans_llama(input_string_list):
    options = [ans["answer"] for ans in input_string_list]
    option_counts = Counter(options)

    # Finding the option with the maximum occurrences
    max_option = max(option_counts, key=option_counts.get)
    if option_counts[max_option] >= math.ceil(len(input_string_list)/2):
        return '{' + '"answer"' + ': "' + str(max_option) + '"' + '}'
    else:
        return -1

def extract_id_mistral(input_string):
    input_string = input_string.strip()
    input_string = input_string.replace('\n', '')
    
    pattern = r'[\'"]answer[\'"]:\s*[\'"]?\d+[\'"]?'
    pattern2 = r'ID\s*\d+'
    pattern3 = r'id\s*\d+'
    pattern5 = r'ID:\s*\d+'
    pattern6 = r'id:\s*\d+'
    pattern4 = r'[\'"]id[\'"]:\s*[\'"]?\d+[\'"]?'
    pattern7 = r'Option\s[A-E]\s'
    pattern8 = r'option\s[A-E]\s'
    
    if re.findall(pattern, input_string):
        return '{' + re.findall(pattern, input_string)[0].replace('\'','"') + '}'
    elif re.findall(pattern2, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern2, input_string)[0].split('ID')[1] + '"' + '}'
    elif re.findall(pattern3, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern3, input_string)[0].split('id')[1] + '"' + '}'
    elif re.findall(pattern5, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern5, input_string)[0].split('ID:')[1] + '"' + '}'
    elif re.findall(pattern6, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern6, input_string)[0].split('id:')[1] + '"' + '}'
    elif re.findall(pattern4, input_string):
        return '{' + re.findall(pattern4, input_string)[0].replace('\'','"') + '}'
    elif re.findall(pattern7, input_string):
        return '{' + '"option"' + ': "' + re.findall(pattern7, input_string)[0].split('Option ')[1] + '"' + '}'
    elif re.findall(pattern8, input_string):
        return '{' + '"option"' + ': "' + re.findall(pattern8, input_string)[0].split('option ')[1] + '"' + '}'
    
    else:
        return None

def extract_id_vicuna13b(input_string):
    input_string = input_string.strip()
    input_string = input_string.replace('\n', '')
    
    pattern = r'[\'"]answer[\'"]:\s*[\'"]?\d+[\'"]?'
    pattern2 = r'ID\s*\d+'
    pattern3 = r'id\s*\d+'
    pattern4 = r'[\'"]id[\'"]:\s*[\'"]?\d+[\'"]?'
    pattern5 = r'ID:\s*\d+'
    pattern6 = r'id:\s*\d+'
    pattern7 = r'Option\s[A-E]\s'
    pattern8 = r'option\s[A-E]\s'
    if re.findall(pattern, input_string):
        return '{' + re.findall(pattern, input_string)[0].replace('\'','"') + '}'
    elif re.findall(pattern4, input_string):
        return '{' + re.findall(pattern4, input_string)[0].replace('\'','"') + '}'
    elif re.findall(pattern2, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern2, input_string)[0].split('ID')[1] + '"' + '}'
    elif re.findall(pattern3, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern3, input_string)[0].split('id')[1] + '"' + '}'
    elif re.findall(pattern5, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern5, input_string)[0].split('ID:')[1] + '"' + '}'
    elif re.findall(pattern6, input_string):
        return '{' + '"id"' + ': "' + re.findall(pattern6, input_string)[0].split('id:')[1] + '"' + '}'
    elif re.findall(pattern7, input_string):
        return '{' + '"option"' + ': "' + re.findall(pattern7, input_string)[0].split('Option ')[1] + '"' + '}'
    elif re.findall(pattern8, input_string):
        return '{' + '"option"' + ': "' + re.findall(pattern8, input_string)[0].split('option ')[1] + '"' + '}'
    else:
        return None

# Load dataset from JSON file
def load_dataset(filename):
    """Loading Datasets"""
    dataset = None
    try:
        with open(filename, "r") as file:
            dataset = json.load(file)
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return dataset

def load_responses(ROOT_OUTPUT_DIR, run, temp):
    """Loading Response Database"""
    shelf = Shelf(ROOT_OUTPUT_DIR, run, temp)

    responses = {}
    for key in shelf.list_keys():
        responses[int(key)] = shelf.get(key)['answer']
    return responses

def evaluate_accuracy(correct_answer_filename, ROOT_OUTPUT_DIR, run, temp, web_gpt = False):
    """Evaluation script to get accuracy"""
    # Load true responses
    dataset = load_dataset(correct_answer_filename)
    true_responses = {entry["question_id"]: entry["correct_answer"] for entry in dataset}

    # Load predicted responses
    predicted_responses = load_responses(ROOT_OUTPUT_DIR, run, temp)

    assert len(true_responses) == len(predicted_responses)
    correct = 0
    total = len(true_responses)
    print('------------------------------------------------------------------------------------------------------')
    for question_id, true_response in true_responses.items():
        if not web_gpt:
            predicted_response = predicted_responses[question_id]
        else:
            predicted_response = predicted_responses[str(question_id)]

        if predicted_response and predicted_response == true_response:
            correct += 1

    accuracy = correct / total * 100
    return accuracy


def prompt_and_save(dataset, LLM, run, task_num, shelf, error_shelf, retry_count):
    """an upper level function that takes ChatModel Object (which tells what LLM we are currently evaluating)
    then decides prompt and calls generate_response of the ChatModel Object.
    It then receives the answer and stores successful and unsuccessful responses 
    in Shelf and ErrorShelf respectively"""
    for _, entry in tqdm(enumerate(dataset), total=len(dataset)):

        output = {}
        question_id = entry["question_id"]
        question = entry["question"]
        options = [entry["options"]]
        output['id'] = question_id
        output['question'] = question

        if shelf.is_exists(str(question_id)):
            continue

        if task_num in [1,2]:
            keys_to_remove = ['material_penalty', 'time_penalty']
            options_list = [{outer_key: {inner_key: inner_value for inner_key, inner_value in inner_dict.items() if inner_key not in keys_to_remove} for outer_key, inner_dict in outer_dict.items()} for outer_dict in options]

        if LLM.model in ['vicuna7b', 'llama-2-7b-chat-hf','llama-2-13b-chat-hf', 'llama-2-70b-chat-hf','PaLM','azure-gpt3.5B']:
            if task_num== 0:
                prompt = str(question) +'\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects." + '\n' + str(options) + "\nChoose the option that would be best. Answer should be a JSON Dictionary. Do not give any reason. Strictly follow given format. For example a sample answer looks like: {\"answer\": \"<your chosen option's alphabet code between [A/B/C/D/E]>\"}\n\nAnswer:"
            elif task_num == 1:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'reversible_using\' means an object can be used after some waiting time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting charged, is being used by someone else etc,  Whereas, irreversible_using means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\nChoose the object that would be best considering all the physical variables.You should focus on safety, fragility of object, where material suitable or not and minimum time aspects.Do not give any reason.Answer should be a JSON Dictionary.For example a sample answer looks like: {\"answer\": \"<chosen option [A/B/C/D/E]>\"}\n\nAnswer:"
            elif task_num == 2:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'reversible_using\' means an object can be used after some waiting time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting charged, is being used by someone else etc,  Whereas, irreversible_using means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\nChoose the object that would be best considering all the physical variables.You should focus on safety, fragility of object, where material suitable or not and minimum time aspects. Hint: cleaning takes lesser time than waiting for an object to become available.Do not give any reason.Answer should be a JSON Dictionary. For example a sample answer looks like: {\"answer\": \"<chosen option [A/B/C/D/E]>\"}\n\nAnswer:"

        elif LLM.model in ['PaLM_prev','azure-gpt3.5B_prev']:
            if task_num== 0:
                prompt = str(question) +'\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects." + '\n' + str(options) + "\nChoose the object that would be best. Answer should be a JSON Dictionary. Your answer should have the option and not the object name. Strictly follow given format. Answer should be a JSON Dictionary. For example a sample answer looks like: {\"answer\": \"<your chosen option's alphabet code between [A/B/C/D/E]>\"}}\n\nAnswer:\n "
            elif task_num == 1:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting charged, is being used by someone else etc,  Whereas, irreversible_using means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\nChoose the object that would be best considering all the physical variables. You should focus on safety, feasibility, fragility and other properties of objects, minimum effort, minimum time aspects. Answer should be a JSON Dictionary. For example a sample answer looks like: {\"answer\": \"<your chosen option's alphabet code between [A/B/C/D/E]>\"}\n\nAnswer:"
            elif task_num == 2:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting charged, is being used by someone else etc,  Whereas, irreversible_using means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\nChoose the object that would be best considering all the physical variables. You should focus on safety, feasibility, fragility and other properties of objects, minimum effort, minimum time aspects. Answer should be a JSON Dictionary. For example a sample answer looks like: {\"answer\": \"<your chosen option's alphabet code between [A/B/C/D/E]>\"}\n\nAnswer:"

        elif LLM.model in ['chatglm6b','chatglm2-6b']:
            if task_num== 0:
                prompt = str(question) +'\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects." + '\n' + str(options) + "\nChoose the option that would be best. Your answer should not have the object name. Do not give any reason. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option's alphabet code between [A/B/C/D/E]. Some example responses are: {\"answer\": \"A\"} or {\"answer\": \"B\"} or {\"answer\": \"C\"} or {\"answer\": \"D\"} or {\"answer\": \"E\"}"
            elif task_num == 1:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'Free\ means the object can be readily used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting recharged, is being used by someone else etc,\n  Whereas, \'irreversible_using\' means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\n . Choose the best configuration. You should focus on safety, feasibility, fragility and other properties of objects, minimum effort, minimum time aspects. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option's alphabet code between [A/B/C/D/E]. Some example responses are: {\"answer\": \"A\"} or {\"answer\": \"B\"} or {\"answer\": \"C\"} or {\"answer\": \"D\"} or {\"answer\": \"E\"}"
            elif task_num == 2:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'Free\ means the object can be readily used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting recharged, is being used by someone else etc,\n  Whereas, \'irreversible_using\' means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\n . Choose the best configuration. You should focus on safety, feasibility, fragility and other properties of objects, minimum effort, minimum time aspects. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option's alphabet code between [A/B/C/D/E]. Some example responses are: {\"answer\": \"A\"} or {\"answer\": \"B\"} or {\"answer\": \"C\"} or {\"answer\": \"D\"} or {\"answer\": \"E\"}"

        elif LLM.model in ['macaw-11b']:
            pdb.set_trace()
            if task_num== 0:
                prompt = str(question) +'\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects." + '\n' + str(options) + "\nChoose the option that would be best. Your answer should not have the object name. Do not give any reason. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option's alphabet code between [A/B/C/D/E]. Some example responses are: {\"answer\": \"A\"} or {\"answer\": \"B\"} or {\"answer\": \"C\"} or {\"answer\": \"D\"} or {\"answer\": \"E\"}"
            elif task_num == 1:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'Free\ means the object can be readily used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting recharged, is being used by someone else etc,\n  Whereas, \'irreversible_using\' means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\n . Choose the best configuration. You should focus on safety, feasibility, fragility and other properties of objects, minimum effort, minimum time aspects. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option's alphabet code between [A/B/C/D/E]. Some example responses are: {\"answer\": \"A\"} or {\"answer\": \"B\"} or {\"answer\": \"C\"} or {\"answer\": \"D\"} or {\"answer\": \"E\"}"
            elif task_num == 2:
                prompt = str(question) +'\n' + "Here, \'already_in_use\' variable depicts object's availability. \'Free\ means the object can be readily used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\n For example: could be wet, is getting recharged, is being used by someone else etc,\n  Whereas, \'irreversible_using\' means that an object is depleted and cannot be used." + '\n' + str(options_list) + "\n . Choose the best configuration. You should focus on safety, feasibility, fragility and other properties of objects, minimum effort, minimum time aspects. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option's alphabet code between [A/B/C/D/E]. Some example responses are: {\"answer\": \"A\"} or {\"answer\": \"B\"} or {\"answer\": \"C\"} or {\"answer\": \"D\"} or {\"answer\": \"E\"}"
        
        elif LLM.model in ['mistral7b-instruct','vicuna13b']:
            if task_num== 0:
                prompt = [question,options]
            elif task_num == 1:
                prompt = [question,options_list]    
            elif task_num == 2:
                prompt = [question,options_list]
       
        #generate answer
        result = LLM.generate_response(prompt,task_num)
        
        #for each unsuccessful response we return result = -1 to trigger this
        if result == -1 and retry_count < constants.RETRY_COUNT:
            error_shelf.put(str(question_id), entry)
            continue

        elif result == -1 and retry_count >= constants.RETRY_COUNT:
            if task_num == 0:
                output['answer'] = random.choice('ABCD')
                output['reason'] = "LLM Error"
            else:
                output['answer'] = random.choice('ABCDE')
                output['reason'] = "LLM Error"
            error_shelf.remove(str(question_id))
            shelf.put(str(question_id), output)
            continue

        if error_shelf.is_exists(str(question_id)):
            error_shelf.remove(str(question_id))

        if LLM.model in [
            'llama-2-7b-chat-hf', 'llama-2-13b-chat-hf', 'vicuna7b', 'vicuna13b' ,'llama-2-70b-chat-hf',
            'chatglm6b', 'chatglm2-6b', 'PaLM', 'mistral7b-instruct', 'azure-gpt3.5B'
        ]:
            output['answer'] = result['answer']
        
        shelf.put(str(question_id), output)