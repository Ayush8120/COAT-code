# Official Codebase for 'Physical Reasoning and Object Planning for Household Embodied Agents' 
-------------------------------
This repository consists of code for he following aspects:
    
    1. Dataset Creation
    2. Evaluating the Datasets
    3. Ai2Thor experiment

-------------------------------

Download the datasets and store them in task_u, task_0, task_1, task_2, task_fi, task_fm folders. The directory structure is maintained in the google drive

-------------------------------

## Dataset Creation Code:

present at `thortils/data`

    set the root as : `thortils`
    ## Task-u :
    requires: objects.json
        - run  `task_u_dataset_gen.py`; it creates task_u dataset

    ## Task-0 : 
    requires: objects.json, tasks.json, oracle.json
        - Add your task, concept, concept objects, and oracle objects in the jsons
        - run `task_0-1-2_dataset_gen.py` ; it creates task_0 dataset

    ## Task-1 : 
    requires: tasks.json, oracle.json, pouch_oracle.json, all_config.json 
        - run `task_0-1-2_dataset_gen.py` ; it creates task_1 dataset 

    ## Task-2 : 
    requires: tasks.json, pouch_subop.json
        - run `task_0-1-2_dataset_gen.py` ; it creates task_2 dataset 
    
    ## Full Pipeline Data Creation:
    set root as `thortils/data
    requires : tasks.json,oracle.json, pouch_subop.json, all_config.json and full_pipeline_datasets_helper.py
        - run `full-pipeline-dataset-creation.py`
        - script contains function to generate both F_ideal and F_moderate datasets


## Evaluation Code [for task-0,1,2 evaluations]

present at `/commonsense`

    set the root as `/thortils/data`
    - run the `evaluation_script.py`
    - `LLM.py` defines a class for setting a language model and prompting it.
    - `database.py` allows us to create caching mechanism for resuming evaluations 
    - `constants.py` sets the constants important for running evaluations
    

##  Some points about AI2Thor Experiment code
    - install AI2thor and thortils repository
    - code is present in the directory thortils/
    - check out constants.py and controller.py in thortils/thortils folder (Ai2thor repo)
    - supress the GPU for Ai2thor in miniconda/.../controller.py ; undo if it was unnecessary
    - bbox_conceptnet_query_teleop.py : [teleop] Object names from Ai2thor semantic segmentation (GT) - pass to conceptnet - make a dictionary of object-utility pairings - saves RGB frames with bounding box utility labellings
    - precoded_traj_llm_query.py : [pre-coded trajectory] Object names from Ai2thor semantic segmentation (GT) - pass to PalM/Alpaca7B - make a dictionary of object-utility pairings - saves RGB frames with bounding box utility labellings.

