from peft import PeftModel
from thortils.vision import plotting 
from transformers import LlamaTokenizer, LlamaForCausalLM
import pdb
import random
import os
import thortils as tt
import thortils.constants as constants
import argparse
import numpy as np
from PIL import Image
from llm_query_class import query_llm
from object_mappping import dumb_categories
from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
import google.generativeai as palm

def main(init_func=None, step_func=None):
    '''
    - Trajectory has been already given as a list of commands
    - We load the Alpaca-7b model from Huggingface API to query the utilities
    - The ground truth segmentations and ground truth tags are then prompted to give 3 utility verbs for each object.

    - Ai2Thor to run headless can only be run on CPU Compute therefore 2 lines had to be commented in controller.py (present in miniconda folder)
    - LLM uses GPU. But only 1 could be used , as with multiple it shares the compute leading to errors
    '''
    controls = {
        "w": "MoveAhead",
        "a": "RotateLeft",
        "d": "RotateRight",
        "e": "LookUp",
        "c": "LookDown"
    }
    trajectory = ['a','a','w','w','w','w','w','w','w','w','w','a','a']
    utility_dict = dict()
    sec = 0
    parser = argparse.ArgumentParser(
        description="Precoded command control of an agent in ai2thor")
    parser.add_argument("-s", "--scene",
                        type=str, help="scene. E.g. FloorPlan1",
                        default="FloorPlan1")
    parser.add_argument("-l", "--llm",
                        type=str, help="what LLM to query using",
                        default="palm")
    args = parser.parse_args()

    if args.llm == 'hf-alpaca-7b':
        tokenizer = LlamaTokenizer.from_pretrained("decapoda-research/llama-7b-hf")
        model = LlamaForCausalLM.from_pretrained(
            "decapoda-research/llama-7b-hf",
            load_in_8bit=True,
            device_map="auto",
        )
        model = PeftModel.from_pretrained(model, "tloen/alpaca-lora-7b")
        LLM = query_llm(model, tokenizer, args.llm)
    
    elif args.llm == 'palm':
        LLM = query_llm('text','random', args.llm)
        palm.configure(api_key='AIzaSyB4R3FFMgTozt9jG-HHK4bcAlboDpPZsnc')
    
    controller = Controller(platform=CloudRendering, save_image_per_frame=True, width=400,
    height=400,
    fieldOfView=90) # new scene - headless
    # controller = tt.launch_controller({**constants.CONFIG, **{"scene": args.scene}})
    print(controller.last_event)
    if init_func is not None:
        config = init_func(controller)

    for k in trajectory:
        sec += 1
        if k in controls:
            action = controls[k]
            params = constants.MOVEMENT_PARAMS[action]
            # event = controller.step(action=action,renderImage=True, **params)
            event = controller.step(action=action, renderImage= True,  renderInstanceSegmentation=True, **params)
            _ = controller.step(action="Pass")
            
            '''
            this modern Controller function messes up the event variable if we give "Pass" as the action. Thus neglected the output
            '''
            
            objects = tt.thor_visible_objects(event)
            im = Image.fromarray(event.frame)
            img = np.array(im)
            im.save(os.path.join("./results/LLM/", f"precoded-frame-{sec}.png"))
            cats = [item for sublist in dumb_categories.values() for item in sublist]
            
            if step_func is not None:
                step_func(event, config)
            all_obj = set([objects[i]["name"].split('_')[0].lower() for i in range(len(objects))])
            # print(all_obj)
            '''
            Removing some redundant and useless segmentations
            '''
            # if 'Floor' in all_obj:
            #     all_obj.remove('Floor')
            # if 'Window' in all_obj:
            #     all_obj.remove('Window')
            for obj in set(all_obj):
                if obj in cats:
                    all_obj.remove(obj)
            
            '''
            Querying the LLM
            ''' 
            non_red_obj = [obj for obj in all_obj if obj not in utility_dict.keys()]
            if args.llm =='palm':
                LLM.query_palm(non_red_obj)
            else:
                LLM.query_alpaca('beam', non_red_obj)

            for non_red_object,utility in LLM.utility_dict.items():
                utility_dict[non_red_object] = utility
            # pdb.set_trace()
            '''
            Saving the bounding boxes
            '''
            colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(len(objects))]
            #instance_detections2D gives bounding boxes for all instances; the keys are the object id and the values are the xyxy cordinates
            for j in range(len(objects)):
                if objects[j]["name"].split('_')[0].lower() not in cats:
                    ob_name = objects[j]["name"].split('_')[0].lower()
                    img = plotting.plot_one_box(img, event.instance_detections2D[objects[j]["objectId"]], str(utility_dict[ob_name]), tuple(colors[j]))
                    # print(ob_name, utility_dict[ob_name])
            final = Image.fromarray(img)
            final.save(os.path.join("./results/LLM/", f"LLM-Bbox-{sec}.png"))
    print(utility_dict)
            
if __name__ == "__main__":
    main()
