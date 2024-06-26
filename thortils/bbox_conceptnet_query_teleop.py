# Keyboard control of Ai2Thor
import pdb
import os
from PIL import Image
import thortils as tt
import thortils.constants as constants
from thortils.utils import getch
import argparse
import time
from thortils.vision import plotting
import random
import numpy as np
from concept_query import query_conceptnet
from object_mappping import dumb_categories,difficult
from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering

def print_controls(controls):
    reverse = {controls[k]:k for k in controls}
    ss =f"""
            {reverse['MoveAhead']}
        (MoveAhead)

    {reverse['RotateLeft']}                 {reverse['RotateRight']}
(RotateLeft)     (RotateRight)

    {reverse['LookUp']}
(LookUp)

    {reverse['LookDown']}
(LookDown)

    q
(quit)
    """
    print(ss)


def main(init_func=None, step_func=None):
    '''
    - We Teleop using Keyboard here
    - Headless : you send commands but instead of showing the window it directly saves as an image
    - We query the conceptnet database for the utilities here. (GT semantic segmentation are utilized)
    - The GPU usage for Ai2Thor had to be supressed due to Vulkan-tools unavailability (miniconda folder.../controller.py)
    - Saves both the RGB frames and bounding boxes with queried utilities as labellings 
    '''
    
    utility_dict = dict()
    sec = 0
    parser = argparse.ArgumentParser(
        description="Keyboard control of agent in ai2thor")
    parser.add_argument("-s", "--scene",
                        type=str, help="scene. E.g. FloorPlan1",
                        default="FloorPlan1")
    args = parser.parse_args()

    controls = {
        "w": "MoveAhead",
        "a": "RotateLeft",
        "d": "RotateRight",
        "e": "LookUp",
        "c": "LookDown"
    }
    print_controls(controls)
    controller = Controller(platform=CloudRendering, save_image_per_frame=True,gpu_device=None) # new scene - headless
    # controller = tt.launch_controller({**constants.CONFIG, **{"scene": args.scene, "headless": False}}) #previous scene - head
    if init_func is not None:
        config = init_func(controller)

    while True:
        sec += 1
        k = getch()
        if k == "q":
            print("bye.")
            break

        if k in controls:
            action = controls[k]
            params = constants.MOVEMENT_PARAMS[action]
            event = controller.step(action=action, renderImage= True,  renderInstanceSegmentation=True, **params)
            _ = controller.step(action="Pass")
            im = Image.fromarray(event.frame)
            img = np.array(im)
            im.save(os.path.join("./", f"RGB-frame-{sec}.png"))
            objects = tt.thor_visible_objects(event)
            
            '''
            edge case for double word (eg: butter_knife) and weird words 
            '''
            dumb_cats = [item for sublist in dumb_categories.values() for item in sublist]
            if step_func is not None:
                step_func(event, config)
            all_obj = set([objects[i]["name"].split('_')[0].lower() for i in range(len(objects))])
            
            '''
            Removing some redundant and useless segmentations
            '''
            # if 'Floor' in all_obj:
            #     all_obj.remove('Floor')
            # if 'Window' in all_obj:
            #     all_obj.remove('Window')
            for obj in set(all_obj):
                if obj in dumb_cats:
                    all_obj.remove(obj)
          
            '''
            Querying the ConceptNet
            Across frames we see some repetitive objects , we maintain a dictionary to only query the newly observed objects
            '''
            non_red_obj = [obj for obj in all_obj if obj not in utility_dict.keys()]
            non_red_corrected_space = ['null']*len(non_red_obj)
            for i,obj in enumerate(non_red_obj):
                # print(i,obj)
                if obj in difficult:
                    non_red_corrected_space[i] = difficult[str(obj)]
                else:
                    non_red_corrected_space[i] = str(obj)
            
            # print(non_red_corrected_space)
            results = query_conceptnet(non_red_corrected_space)
            for i,result in enumerate(results):
                if result != [[]]:
                    for edge in result:
                        print(f"{edge[0]['start']['label']} --{edge[0]['rel']['label']}--> {edge[0]['end']['label']}")
                        utility_dict[non_red_obj[i]] = edge[0]['end']['label']
                else:
                    utility_dict[non_red_obj[i]] = 'TODO'
            
            '''
            Saving the bounding boxes
            '''
            colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(len(objects))]
            #instance_detections2D gives bounding boxes for all instances; the keys are the object id and the values are the xyxy cordinates
            for j in range(len(objects)):
                if objects[j]["name"].split('_')[0].lower() not in dumb_cats:
                    ob_name = objects[j]["name"].split('_')[0].lower()
                    img = plotting.plot_one_box(img, event.instance_detections2D[objects[j]["objectId"]], str(utility_dict[ob_name]), tuple(colors[j]))
                    # print(ob_name, utility_dict[ob_name])
            final = Image.fromarray(img)
            final.save(os.path.join("./", f"box-{sec}.png"))
            print(utility_dict)
            
if __name__ == "__main__":
    main()

