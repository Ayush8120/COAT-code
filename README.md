## Official Codebase for 'Physical Reasoning and Object Planning for Household Embodied Agents' [TMLR May 2024]

[OpenReview](https://openreview.net/forum?id=xYkdmEGhIM) | [Datasets](https://github.com/Ayush8120/COAT)

-------------------------------
This repository consists of code for he following aspects:
    
    1. Ai2Thor experiment
    2. Dataset Creation
    3. Evaluating the Datasets

-------------------------------
###  AI2Thor Experiment
| ConceptNet | PaLM | Alpaca7B |
|---|---|---|
| !["ConceptNet Output"](https://github.com/Ayush8120/COAT-code/blob/main/utility-bbox.png)<br>_Closed set utilities from ConceptNet_ | !["Alt text 2"](https://github.com/Ayush8120/COAT-code/blob/main/utility-bbox-palm.png)<br>_Open set utilities from PaLM_ | !["Alpaca7B Output"](https://github.com/Ayush8120/COAT-code/blob/main/utility-bbox-alpaca.png)<br>_Open set utilities from Alpaca7B_ |


Code present in `thortils/` folder

##### install AI2thor 
    pip install ai2thor

##### Install [thortils](https://github.com/zkytony/thortils) repository
    
    - concept_query.py : contains standalone code to query conceptnet
    - bbox_conceptnet_query_teleop.py : [teleop] makes a dictionary of object-utility pairings(conceptnet) - saves RGB frames with bounding box utility labellings
    - precoded_traj_llm_query.py : [pre-coded trajectory] make a dictionary of object-utility pairings(PaLM/Alpaca7B) - saves RGB frames with bounding box utility labellings.

<!--- check out constants.py and controller.py in thortils/thortils folder (Ai2thor repo) -->
<!--- supress the GPU for Ai2thor in miniconda/.../controller.py ; undo if it was unnecessary -->
    
Video Summary of AI2thor experiemnt : [Youtube Video Link](https://youtu.be/P6JwobOAl5o)

-------------------------------
### Dataset Creation Code:

1. Download the datasets and store them at `thortils/data/` in task_u, task_0, task_1, task_2, task_fi, task_fm folders. 
2. The directory structure is maintained in the google drive

-----
Code for creating datasets is located in `thortils/data`

    For running scipts pass the args.root as `/thortils`
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
    For running scipts pass the args.root as `/thortils/data`
    requires : tasks.json,oracle.json, pouch_subop.json, all_config.json and full_pipeline_datasets_helper.py
        - run `full-pipeline-dataset-creation.py`
        - script contains function to generate both F_ideal and F_moderate datasets


### Evaluation Code [for task-0,1,2 evaluations]

`export API_KEY='your PALM API KEY'`
    
Code for evaluating language models is located at `/commonsense`
    
    For running scipts pass the args.root as `/thortils/data`
 
    - run the `evaluation_script.py`
    - `LLM.py` defines a class for setting a language model and prompting it.
    - `database.py` allows us to create caching mechanism for resuming evaluations 
    - `constants.py` sets the constants important for running evaluations
