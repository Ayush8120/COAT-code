import os
import argparse
import constants
from utils import load_dataset, evaluate_accuracy , prompt_and_save
from LLM import ChatModel
from database import Shelf,ErrorShelf

def process_run(args, run, LLM, temp):
    """
    Takes a dataset, LLM and run evaluations.
    LLM : ChatModel Object
    temp: temperature 
    
    returns: accuracy
    """
    ROOT_DIR = os.path.join(
        args.rootdir,
        f"task_{args.task_id}", f"Variation_{args.var_id}")
    
    if not os.path.exists(os.path.join(ROOT_DIR, "GT")):
        os.makedirs(os.path.join(ROOT_DIR, "GT"), exist_ok=True)
    
    ROOT_OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs", f"{args.model}/run_{run}")
    GT_QA_DATABASE_PATH = os.path.join(ROOT_DIR, "GT/question_answer_database.json")
    print(GT_QA_DATABASE_PATH)
    
    if not os.path.exists(ROOT_OUTPUT_DIR):
        os.makedirs(ROOT_OUTPUT_DIR, exist_ok=True)
    
    shelf = Shelf(ROOT_OUTPUT_DIR, run, temp)
    error_shelf = ErrorShelf(ROOT_OUTPUT_DIR,run,temp)

    dataset = load_dataset(
        filename=GT_QA_DATABASE_PATH
    )

    print()
    print(f"Total number of Questions: {len(dataset)}")
    print(f"Number of Cached Responses: {shelf.total()}")
    print(f"Number of Error Responses: {error_shelf.total()}")
    print(f"Number of Responses to be generated: {len(dataset) - shelf.total()}")
    print()

    while shelf.total() < len(dataset):
            """
            shelf contains successful responses
            """
            prompt_and_save(
                dataset=dataset,
                LLM=LLM,
                run=run,
                task_num=args.task_id,
                shelf=shelf,
                error_shelf=error_shelf,
                retry_count = 0
            ) 
            retry_count = 0
            while error_shelf.total() != 0 and retry_count <= constants.RETRY_COUNT:
                error_dataset = error_shelf.list_values()
                prompt_and_save(dataset=error_dataset, 
                    LLM=LLM, run=run,
                    task_num=args.task_id,
                    shelf=shelf,
                    error_shelf=error_shelf,
                    retry_count = retry_count
                )
                retry_count += 1
            if retry_count >= constants.RETRY_COUNT:
                break
                
    accuracy = evaluate_accuracy(
        correct_answer_filename=GT_QA_DATABASE_PATH,
        ROOT_OUTPUT_DIR=ROOT_OUTPUT_DIR,
        run=run,
        temp=temp
    )
    print(f"Accuracy: {accuracy:.2f}")
    return accuracy

def report_findings(args, av_acc_per_temp, temp_range):
    print(f"Experiment Results: {args.model}")
    print(f"Runs_per_temp : {constants.RUNS_PER_TEMP}\n")
    print("-" * 33, end="\n")
    print("| Temperature |   Avg_Accuracy\t|")
    print("-" * 33, end="\n")
    for i, result in enumerate(av_acc_per_temp):
        print(f"|{temp_range[::-1][i]:10.2f}   | {result:10.2f}%\t|")
    print("-" * 33, end="\n")

if __name__ == "__main__":

    """
    Supported models:
        - AZURE GPT3.5B: 'azure-gpt3.5B'
        - Cohere
        - PaLM: 'PaLM'
        - Vicuna7B: 'vicuna7b'
        - Vicuna13B: 'vicuna13b'
        - FastChatT5-3B: 'fastchat-t5-3b'
        - LLama2 70B Chat-HF: 'Llama-2-70b-chat-hf'
        - ChatGLM 6B : 'chatglm6b
        - Mistrl7B : 'mistral7b-instruct'
        - Macaw11B : 'macaw-11b'
    """


    parser = argparse.ArgumentParser()
    parser.add_argument("--rootdir", type=str, default='path-to-thortils/data')
    parser.add_argument("--model", type=str, default='PaLM')
    parser.add_argument('--model_type', type=str, default='llama-2-7b-chat-hf')
    parser.add_argument("--model_path", type=str, default='/scratch/ggml_models/vicuna/7B/ggml-model-q4_0.gguf')
    # parser.add_argument("--run", type=str, default='run_0')
    parser.add_argument("--task_id", type=int, default=0)
    parser.add_argument("--var_id", type=int, default=1)
    parser.add_argument("--num_gpus", type=int, default=1)
    args = parser.parse_args()

    TASK_ID = args.task_id
    VAR_ID = args.var_id
    #task-0 , var : [2,3,4,5]
    #task-1 , var: [1,2,..12]
    #task-2 , var: [2,3,..15]
    def run_task(args):
        av_acc_per_temp  = []
        LLM = ChatModel(
                model=args.model,
                model_type=args.model_type,
                model_path=args.model_path,
                num_gpus= args.num_gpus
            )
        temp_range = [0.7]
        for _, temp in enumerate(temp_range[::-1]):

            print()
            print(f"TEMPERATURE: {temp:.2f}")
            print()

            LLM.temperature = temp
            experiment_results = list() 
            
            for run in range(constants.RUNS_PER_TEMP):
                print(f"Run: {run+1}/{constants.RUNS_PER_TEMP}")
                accuracy = process_run(args, run, LLM, temp)
                experiment_results.append(accuracy)
            
            av = sum(experiment_results)/len(experiment_results)
            av_acc_per_temp.append(av) #average value for a temp by averaging accuracy of runs
            print(f"\n\nAverage Accuracy: {av:.2f}% Temp: {LLM.temperature:.2f} Task: {args.task_id}\n\n")
            
        report_findings(args, av_acc_per_temp, temp_range)
    run_task(args)
