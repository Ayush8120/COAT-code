import textwrap
from transformers import GenerationConfig
import google.generativeai as palm
import pdb
import os
palm.configure(api_key='AIzaSyB4R3FFMgTozt9jG-HHK4bcAlboDpPZsnc')
    
class query_llm():
    """A class for creating an object that allows us to prompt various language models to give us best utilities associated with the objects.
    It updates the utility dict with the utility queried to keep a track of non-redundant objects"""
    def __init__(self, model, tokenizer, llm) -> None:
        
        self.utility_dict = dict()
        self.model = model
        self.tokenizer = tokenizer
        self.prompt = (
        f"### Instruction:\n{f'In a house setting, Like an apple is primarily used for eating, and cooking. Give 3 primary uses for [].Answer very concisely in 4-5 words'}\n\n### Response:"""
    )
        self.llm = llm


    def query_alpaca(self, sampling_type, obj_list, temp=0.8):
        
        self.obj_list = obj_list
        if sampling_type == 'beam':
            generation_config = GenerationConfig(
                do_sample=True,
                num_beams=4,
            )
            for object in self.obj_list:
                self.prompt = (
                                f"### Instruction:\n{f'In a house setting, Like an apple is primarily used for eating, and cooking. Give the 2 primary uses for {object}. Output should be 2 such verbs ONLY.'}\n\n### Response:"""
                            )
                inputs = self.tokenizer(self.prompt, return_tensors="pt")
                input_ids = inputs["input_ids"].cuda()
                generation_output = self.model.generate(
                    input_ids=input_ids,
                    generation_config=generation_config,
                    return_dict_in_generate=False,
                    max_new_tokens=64,
                )
                answer = self.tokenizer.decode(generation_output[0][input_ids.shape[1]:])
                paragraphed = '\n'.join(textwrap.wrap(answer))
                self.utility_dict[object] = paragraphed
                
    def query_palm(self, obj_list):
        
        self.obj_list = obj_list
        for object in self.obj_list:
            response = palm.generate_text(prompt=f"In a house setting, Like an apple is primarily used for eating, and cooking. Give the 2 primary uses for {object}. Output should be 2 such uses ONLY. Your answer shouldn't include any other words")
            self.utility_dict[object] = response.result
        
