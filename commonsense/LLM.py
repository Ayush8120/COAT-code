import os, requests, json, pdb, os, time

from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.generation.utils import GenerationConfig

import constants
from utils import extract_ans, give_key,extract_id_vicuna13b,extract_id_mistral,extract_ans_llama,extract_each_ans_llama

import openai
import google.generativeai as palm
import fastchat
from fastchat.model import load_model, get_conversation_template, add_model_args
from huggingface_hub import InferenceClient


import transformers
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM,AutoModelForSeq2SeqLM
from transformers import AutoTokenizer

# palm.configure(api_key=os.getenv("DEMO_PALM_API_KEY"))
palm.configure(api_key=os.getenv("AYUSH_PALM_API_KEY"))
#palm.configure(api_key=os.getenv("RAGHAV_PALM_API_KEY"))

openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_key = os.getenv("OPENAI_API_KEY")


class ChatModel:
    """
    A class used to represent a Chat Model. This contains methods to confgure models and prompt them.
    """
    def __init__(self, model, model_type = 'API', temperature=0.7, model_path=None, num_gpus=3) -> None:
        """
        Constructs all the necessary attributes for the ChatModel object.

        Parameters
        ----------
            model : str
                the name of the model

            Supported models:
                - AZURE GPT3.5B: 'azure-gpt3.5B'
                - PaLM: 'PaLM'
                - Vicuna7B: 'vicuna7b'
                - Vicuna13B: 'vicuna13b'
                - FastChatT5-3B: 'fastchat-t5-3b'
                - LLama2 7B Chat: 'llama-2-70b-chat-hf'
                - ChatGLM 6B: 'chatglm6b'
                - ChatGLM2 6b: 'chatglm2-6b'
                - Mistral7B: 'mistral7b-instruct'
        """
        self.model = model
        self.device = "cuda"
        self.temperature = temperature
        self.num_gpus = num_gpus
        self.llm = None
        self.tokenizer = None
        self.model_llm = None
        self.pipeline = None


        self.model_paths = {
            'vicuna7b': 'lmsys/vicuna-7b-v1.3',
            'vicuna13b': 'lmsys/vicuna-13b-v1.5',
            'fastchat-t5-3b': 'lmsys/fastchat-t5-3b-v1.0',
            'llama-2-70b-chat-hf': 'meta-llama/Llama-2-70b-chat-hf',
            'llama-2-13b-chat-hf': 'meta-llama/Llama-2-13b-chat-hf',
            'llama-2-7b-chat-hf': 'meta-llama/Llama-2-7b-chat-hf',
            'chatglm6b': 'THUDM/chatglm-6b',
            'chatglm2-6b': 'THUDM/chatglm2-6b',
            'mistral7b-instruct': 'mistralai/Mistral-7B-Instruct-v0.1',
            #'llama-2-13b': 'meta-llama/Llama-2-13b-hf'
        }

        
        if model in ['vicuna7b', 'vicuna13b', 'fastchat-t5-3b']:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model_path = self.model_paths.get(self.model)
            self.configure_local_model()

        elif model in ['chatglm6b', 'chatglm2-6b']:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_paths[model], trust_remote_code=True)
            self.model_llm = AutoModel.from_pretrained(self.model_paths[model], trust_remote_code=True).half().cuda()
            self.model_llm = self.model_llm.eval()

        elif model == 'mistral7b-instruct' and self.num_gpus == 1:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_paths[model],torch_dtype='auto')
            self.model_llm = AutoModelForCausalLM.from_pretrained(self.model_paths[model],torch_dtype='auto')
            self.model_llm.to(self.device)

        elif model == 'mistral7b-instruct' and self.num_gpus == 2:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model_path = self.model_paths.get(self.model)
            self.configure_local_model()

        elif model == 'llama-2-13b-chat-hf':
            self.tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-13b-chat-hf')
            self.pipeline = transformers.pipeline("text-generation", model='meta-llama/Llama-2-13b-chat-hf', torch_dtype=torch.float16, device_map="auto")

        elif model == 'llama-2-7b-chat-hf':
            self.tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat-hf')
            self.pipeline = transformers.pipeline("text-generation", model='meta-llama/Llama-2-7b-chat-hf', torch_dtype=torch.float16, device_map="auto")

    def configure_local_model(self):
        """
        Configures the local model with the necessary parameters.

        This method sets the number of GPUs, the maximum GPU memory,
        the 8-bit load configuration, and the CPU offloading configuration
        using the values defined in the constants module.
        """
        if self.model == 'vicuna13b':
            self.model_llm, self.tokenizer = load_model(
                self.model_path,
                device = self.device,
                num_gpus=3,
                # max_gpu_memory = 'Gib',
                load_8bit=False,
                cpu_offloading=False,
                # revision=self.revision,
                debug="store_true",
            )
        elif self.model == 'vicuna7b':
            self.model_llm, self.tokenizer = load_model(
                self.model_path,
                device = self.device,
                num_gpus=2,
                load_8bit=False,
                cpu_offloading=False,
                # revision=self.revision,
                debug="store_true",
            )
        elif self.model == 'mistral7b-instruct' and self.num_gpus == 2:
            self.model_llm, self.tokenizer = load_model(
                self.model_path,
                device = self.device,
                num_gpus=self.num_gpus,
                load_8bit=False,
                cpu_offloading=False,
                # revision=self.revision,
                debug="store_true",
            )
        self.temperature = self.temperature
        

    def generate_response(self, prompt, task_num):
        """
        Generates a response based on the given prompt and model
        """
        if self.model == 'azure-gpt3.5B':
            return self.gpt_prompt(prompt,task_num)
        elif self.model == 'PaLM':
            return self.palm_prompt(prompt,task_num)
        elif self.model in ['vicuna7b', 'fastchat-t5-3b']:
            return self.fastchat_prompt(prompt)
        elif self.model in ['vicuna13b']:
            return self.fastchat_prompt(prompt,task_num=2)
        elif self.model in ['llama-2-7b-chat-hf', 'llama-2-13b-chat-hf', 'llama-2-70b-chat-hf']:
            return self.llama13b_prompt(prompt,task_num)
        elif self.model in ['chatglm6b','chatglm2-6b']:
            return self.chatglm_prompt(prompt)
        elif self.model == 'mistral7b-instruct' and self.num_gpus == 1:
            return self.mistral_prompt(prompt, task_num)
        elif self.model == 'mistral7b-instruct' and self.num_gpus == 2:
            return self.mistral_prompt_lmsys(prompt, task_num )
            

    def gpt_prompt(self, prompt,task_num):
        
        time.sleep(0.1)
        try:
            response = openai.ChatCompletion.create(
            engine="concept-gpt35",
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=100,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
            )    
            result = response['choices'][0]['message']['content']
            return json.loads(result)
        except Exception as error:
            print('redo')
            return -1

    def palm_prompt(self,prompt):
        assert self.model == 'PaLM', "For using PaLM model, check the spell!"

        response = palm.generate_text(prompt= prompt,temperature=self.temperature)
        # time.sleep(0.1) # 90 requests per minute
        try:    
            mod_response = extract_ans(response.result)
            return json.loads(mod_response)
        except Exception as error:
            print(f'Failed: {response.result}')
            return -1
        
    def huggingface_prompt(self, prompt):
    
        outputs = self.llm.text_generation(prompt)
        processed_outputs = extract_ans(outputs)
        time.sleep(0.5)
        try:
            return json.loads(processed_outputs)
        except Exception as error:
            print(outputs)
            print()
            print(processed_outputs)
            return -1
        

    def llama13b_prompt(self, prompt,task_num):
        
        if task_num == 0:
            max_length = 200
        else:
            max_length = 600
        try:
            if self.model in ['llama-2-7b-chat-hf','llama-2-13b-chat-hf']:
                sequences = self.pipeline(prompt,return_full_text=False, do_sample=True, top_k=10, num_return_sequences=1, eos_token_id=self.tokenizer.eos_token_id, max_length=max_length)
                return json.loads(extract_each_ans_llama(sequences[0]['generated_text']))
            else:
                sequences = self.pipeline(prompt,return_full_text=False, do_sample=True, top_k=10, num_return_sequences=3, eos_token_id=self.tokenizer.eos_token_id, max_length=max_length)
                sequence_list = [json.loads(extract_ans(sequences[i]['generated_text'])) for i in range(len(sequences))]
                processed_outputs = extract_ans_llama(sequence_list)
                return json.loads(processed_outputs)
        except Exception as error:
            return -1

    def fastchat_prompt(self, prompt,task_num=2):
        if task_num == 0:
            new_prompt = str(prompt[0]) +'\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects." + '\n' + str(prompt[1]) + "\nChoose the option that would be best. Your answer should have the object name. Do not give any reason. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option. Example Answer : \{\"answer\" : \"StoveBurner\"\}"

        elif task_num == 1:
            new_prompt = str(prompt[0]) +'\n' + str(prompt[1]) + "\nHere, \'already_in_use\' variable depicts object's availability. \'Free\' means the object can be immediately used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\nFor example: it could be wet, might be getting recharged, is being used by someone else etc, \nWhereas, \'irreversible_using\' means that an object is depleted and cannot be used AT ALL" + '\nUsing CommonSense Reasoning choose the best configuration option. You should focus on commonsense material properties like safety, fragility, weight and also ensure minimum time for task completion by estimating the time required at an abstract level. SAMPLE ANSWER##: { "id": your options ID }'

        elif task_num == 2:
            new_prompt = str(prompt[0]) +'\n' + str(prompt[1]) + "\nHere, \'already_in_use\' variable depicts object's availability. \'Free\' means the object can be immediately used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\nFor example: it could be wet, might be getting recharged, is being used by someone else etc, \nWhereas, \'irreversible_using\' means that an object is depleted and cannot be used AT ALL. Hint: It's better to clean a dirty thing rather than wait for it to become available for use."

        model_answer = "Based on commonsense reasoning,, help me with deciding best option to use solely on the basis of their current physical state variables like (material, availability, temp, condition) and thus ensure saftey and least time to get started with the task"
        further_instruct = 'Suggest me the correct option in JSON format "id": object option ID?'
        msg = new_prompt
        conv = get_conversation_template(self.model_path)
        conv.append_message(conv.roles[0], msg + model_answer + further_instruct)
        conv.append_message(conv.roles[1], None)
        new_prompt = conv.get_prompt()
        inputs = self.tokenizer([new_prompt])
        inputs = {k: torch.tensor(v).to(self.device) for k, v in inputs.items()}
        output_ids = self.model_llm.generate(
            **inputs,
            do_sample=True if self.temperature > 1e-5 else False,
            temperature=self.temperature,
            repetition_penalty=1.2,
            max_new_tokens=100,
        )

        if self.model_llm.config.is_encoder_decoder:
            output_ids = output_ids[0]
        else:
            output_ids = output_ids[0][len(inputs["input_ids"][0]) :]
        outputs = self.tokenizer.decode(
            output_ids, skip_special_tokens=True, spaces_between_special_tokens=False
        )
        try:
            if task_num == 0:
                response = outputs
                input_string = response.strip()
                response = input_string.replace('\n', '')
                response = response.replace('\'', '"')
                if response:
                    result = json.loads(response)
                    options_dict = prompt[1][0]
                    ans = give_key(result.get("answer"),options_dict) 
                    if ans:
                        return json.loads('{' + '\"answer\": ' + '\"' + str(ans[0]) + '\"' + '}')
                    else:
                        raise ValueError("Object Not in Options")
                else:
                    raise ValueError("None")
            elif task_num in [1,2]:    
                response = outputs
                input_string = response.strip()
                response = input_string.replace('\n', '')
                response = response.replace('\'', '"')
                response = extract_id_vicuna13b(response)
                if response:
                    response_dict = json.loads(response) 
                    if "option" in response_dict.keys():
                        return json.loads('{' + '\"answer\": ' + '\"' + str(response_dict.get("option").strip()) + '\"' + '}')
                    else:
                        for alph, val in prompt[1][0].items():
                            if int(list(response_dict.values())[0]) == int(val.get('id')):
                                return json.loads('{' + '\"answer\": ' + '\"' + str(alph) + '\"' + '}')
                        raise ValueError("ID Not in Options")  
                else:
                    raise ValueError("None")
        except Exception as error:
            return -1


    def chatglm_prompt(self, prompt,task_num):
        response, _ = self.model_llm.chat(self.tokenizer, prompt,history=[])
        try:
            output = extract_ans(response)
            return json.loads(output)
        except:
            return -1
    
    def mistral_prompt_lmsys(self,prompt,task_num):
        if task_num == 0:
            new_prompt = str(prompt[0]) +'\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects.\n" + str(prompt[1]) + "\nChoose the option that would be best. Your answer should have the object name. Do not give any reason. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option. Example Answer : \{\"answer\" : \"StoveBurner\"\}"
            new_prompt = f"""<s>[INST]{new_prompt}[/INST] I'm an intelligent household agent, I can help you with deciding what object to use for a task</s>[INST]Suggest me the correct option in JSON format "id": object option ID?[/INST]"""
        
        elif task_num == 1:
            new_prompt = str(prompt[0]) +'\n' + str(prompt[1]) + "\nHere,\'already_in_use\' variable depicts object's availability. \'Free\' means the object can be immediately used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\nFor example: it could be wet, might be getting recharged, is being used by someone else etc,\nWhereas, \'irreversible_using\' means that an object is depleted and cannot be used AT ALL" + '\nUsing CommonSense Reasoning choose the best configuration option. You should focus on commonsense material properties like safety, fragility, weight and also ensure minimum time for task completion by estimating the time required at an abstract level. Answer should be a JSON Dictionary with key as keyword "answer" and the value should be your chosen option\'s numeric "id"'
            new_prompt = f"""<s>[INST]{new_prompt}[/INST] I'm an intelligent household agent, I can help you with deciding what object to use for a task. I'll be giving you the best object to use solely on the basis of their current physical state variables like (material, availability, temp, condition) and thus ensure saftey and least time to get started with the task.</s>[INST]Suggest me the correct option in JSON format "id": object option ID?[/INST]"""
        
        elif task_num == 2:
            new_prompt = str(prompt[0]) +'\n' + str(prompt[1]) + "\nHere,\'already_in_use\' variable depicts object's availability. \'Free\' means the object can be immediately used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\nFor example: it could be wet, might be getting recharged, is being used by someone else etc,\nWhereas, \'irreversible_using\' means that an object is depleted and cannot be used AT ALL" + '\nUsing CommonSense Reasoning choose the best configuration option. You should focus on commonsense material properties like safety, fragility, weight and also ensure minimum time for task completion by estimating the time required at an abstract level. Hint: It\'s better to clean a dirty thing rather than wait for it to become available for use. Answer should be a JSON Dictionary with key as keyword "answer" and the value should be your chosen option\'s numeric "id"'
            new_prompt = f"""<s>[INST]{new_prompt}[/INST] I'm an intelligent household agent, I can help you with deciding what object to use for a task. I'll be giving you the best object to use solely on the basis of their current physical state variables like (material, availability, temp, condition) and thus ensure saftey and least time to get started with the task.</s>[INST]Suggest me the correct option in JSON format "id": object option ID?[/INST]"""

        inputs = self.tokenizer([new_prompt])
        inputs = {k: torch.tensor(v).to(self.device) for k, v in inputs.items()}
        output_ids = self.model_llm.generate(
            **inputs,
            do_sample=True if self.temperature > 1e-5 else False,
            temperature=self.temperature,
            repetition_penalty=1.2,
            max_new_tokens=200,
        )

        if self.model_llm.config.is_encoder_decoder:
            output_ids = output_ids[0]
        else:
            output_ids = output_ids[0][len(inputs["input_ids"][0]) :]
        outputs = self.tokenizer.decode(
            output_ids, skip_special_tokens=True, spaces_between_special_tokens=False
        )
        try:
            if task_num == 0:
                response = outputs
                input_string = response.strip()
                response = input_string.replace('\n', '')
                response = response.replace('\'', '"')
                if response:
                    result = json.loads(response)
                    options_dict = prompt[1][0]
                    ans = give_key(result.get("answer"),options_dict) 
                    if ans:
                        return json.loads('{' + '\"answer\": ' + '\"' + str(ans[0]) + '\"' + '}')
                    else:
                        raise ValueError("Object Not in Options")
                else:
                    raise ValueError("None")
                
            elif task_num in [1,2]:    
                response = outputs
                input_string = response.strip()
                response = input_string.replace('\n', '')
                response = response.replace('\'', '"')
                response = extract_id_mistral(response)
                if response:
                    response_dict = json.loads(response) 
                    if "option" in response_dict.keys():
                        # directly alphabet
                        return json.loads('{' + '\"answer\": ' + '\"' + str(response_dict.get("option").strip()) + '\"' + '}')
                    else:
                        # id and then finding alphabet
                        for alph, val in prompt[1][0].items():
                            if int(list(response_dict.values())[0]) == int(val.get('id')):
                                return json.loads('{' + '\"answer\": ' + '\"' + str(alph) + '\"' + '}')
                        raise ValueError("ID Not in Options")  
                else:
                    raise ValueError("None")
        
        except Exception as error:
            return -1


    def mistral_prompt(self, prompt, task_num):
        
        if task_num == 0:
            new_prompt = str(prompt[0]) +'\n' + "You should focus on safety, feasibility, minimum effort, minimum time aspects.\n" + str(prompt[1]) + "\nChoose the option that would be best. Your answer should have the object name. Do not give any reason. Answer should be a JSON Dictionary with key as keyword 'answer' and the value should be your chosen option. Example Answer : \{\"answer\" : \"StoveBurner\"\}"
            new_prompt = f"""<s>[INST]{new_prompt}[/INST] I'm an intelligent household agent, I can help you with deciding what object to use for a task</s>[INST]Suggest me the correct option in JSON format "id": object option ID?[/INST]"""
        
        elif task_num == 1:
            new_prompt = str(prompt[0]) +'\n' + str(prompt[1]) + "\nHere,\'already_in_use\' variable depicts object's availability. \'Free\' means the object can be immediately used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\nFor example: it could be wet, might be getting recharged, is being used by someone else etc,\nWhereas, \'irreversible_using\' means that an object is depleted and cannot be used AT ALL" + '\nUsing CommonSense Reasoning choose the best configuration option. You should focus on commonsense material properties like safety, fragility, weight and also ensure minimum time for task completion by estimating the time required at an abstract level. Answer should be a JSON Dictionary with key as keyword "answer" and the value should be your chosen option\'s numeric "id"'
            new_prompt = f"""<s>[INST]{new_prompt}[/INST] I'm an intelligent household agent, I can help you with deciding what object to use for a task. I'll be giving you the best object to use solely on the basis of their current physical state variables like (material, availability, temp, condition) and thus ensure saftey and least time to get started with the task.</s>[INST]Suggest me the correct option in JSON format "id": object option ID?[/INST]"""
        
        elif task_num == 2:
            new_prompt = str(prompt[0]) +'\n' + str(prompt[1]) + "\nHere,\'already_in_use\' variable depicts object's availability. \'Free\' means the object can be immediately used without time penalty, 'reversible_using\' means an object can be used after some time but not immediately. Like, it could be occupied temporarily.\nFor example: it could be wet, might be getting recharged, is being used by someone else etc,\nWhereas, \'irreversible_using\' means that an object is depleted and cannot be used AT ALL" + '\nUsing CommonSense Reasoning choose the best configuration option. You should focus on commonsense material properties like safety, fragility, weight and also ensure minimum time for task completion by estimating the time required at an abstract level.Hint: It\'s better to clean a dirty thing rather than wait for it to become available for use. Answer should be a JSON Dictionary with key as keyword "answer" and the value should be your chosen option\'s numeric "id"'
            new_prompt = f"""<s>[INST]{new_prompt}[/INST] I'm an intelligent household agent, I can help you with deciding what object to use for a task. I'll be giving you the best object to use solely on the basis of their current physical state variables like (material, availability, temp, condition) and thus ensure saftey and least time to get started with the task.</s>[INST]Suggest me the correct option in JSON format "id": object option ID?[/INST]"""
        encodeds = self.tokenizer(new_prompt,return_tensors='pt', add_special_tokens=False)
        
        model_inputs = encodeds.to(self.device)
        self.model_llm.to(self.device)
        
        generated_ids = self.model_llm.generate(**model_inputs, max_new_tokens=200, do_sample=True)
        decoded = self.tokenizer.batch_decode(generated_ids)

        try:
            if task_num == 0:
                response = decoded[0]
                input_string = response.strip()
                response = input_string.replace('\n', '')
                response = response.replace('\'', '"')
                result = json.loads(response)
                options_dict = prompt[1][0]
                ans = give_key(result.get("answer"),options_dict) 
                if ans:
                    return json.loads('{' + '\"answer\": ' + '\"' + str(ans[0]) + '\"' + '}')
                else:
                    raise ValueError("Object Not in Options")
            elif task_num in [1,2]:
                response = decoded[0]
                input_string = response.strip()
                response = input_string.replace('\n', '')
                response = response.replace('\'', '"')
                response = extract_id_mistral(response)
                if response:
                    response_dict = json.loads(response) 
                    for alph, val in prompt[1][0].items():
                        if int(list(response_dict.values())[0]) == int(val.get('id')):
                            # print(f'done - {alph}')
                            return json.loads('{' + '\"answer\": ' + '\"' + str(alph) + '\"' + '}')
                    raise ValueError("ID Not in Options")  
                else:
                    raise ValueError("None")            
        
        except Exception as error:
            return -1
