import tkinter as tk
from tkinter import ttk
import json,os, argparse
import utils

'''
This is a game for getting the possible values of variables for a given object
'''

# Questions and choices
questions = [
    "mass",
    "material",
    "temperature",
    "already_in_use",
    "condition",
]

choices = [
    ["light", "medium", "heavy", "super-heavy"],
    ["Metal", "Wood", "Plastic", "Glass", "Ceramic", "Stone", "Fabric", "Rubber", "Food", "Paper", "Wax", "Soap", "Sponge", "Organic"],
    ["Cold", "RoomTemp", "Hot"],
    ["free","reversible-using","irreversible-using"],
    ["dirty", "clean", "broken"]
]

# List of object names
objects = utils.load_dataset('./data/task_1_results/Exp_1/GT_used/objects.json')
object_names = []
for key in objects:
    object_names.extend(objects[key])

def load_responses():
    if os.path.exists(f"./data/task_1_results/Exp_1/GT_used/{username}_var_responses.json") and os.stat(f"./data/task_1_results/Exp_1/GT_used/{username}_var_responses.json").st_size > 0:
        with open(f"./data/task_1_results/Exp_1/GT_used/{username}_var_responses.json", "r") as file:
            return json.load(file)
    else:
        return {}


username = input("Please Enter Your Name:")
responses = load_responses()
current_object_index = 0  # Initialize the current object index
    
def next_question():
    global current_object_index
    update_responses()
    if current_object_index < len(object_names) - 1:
        update_responses()
        current_object_index += 1
        update_question_ui()
        update_object_name_label()
        update_next_button()

def update_responses():
    if object_names[current_object_index] not in responses:
        responses[object_names[current_object_index]] = {}  # Initialize responses for the current object
    
    for i, question in enumerate(questions):
        selected_choices = []
        
        for j, choice_var in enumerate(choice_vars[i]):
            if choice_var.get() == 1:
                selected_choices.append(choices[i][j])
        if question in responses[object_names[current_object_index]]:
            responses[object_names[current_object_index]][question].extend(selected_choices)
            responses[object_names[current_object_index]][question] = list(set(responses[object_names[current_object_index]][question]))
        else:
            responses[object_names[current_object_index]][question] = selected_choices
            responses[object_names[current_object_index]][question] = list(set(responses[object_names[current_object_index]][question]))
        # responses[object_names[current_object_index]][question] = selected_choices

def update_question_ui():
    for i, question in enumerate(questions):
        selected_choices = responses.get(object_names[current_object_index], {}).get(question, [])
        for j, choice_var in enumerate(choice_vars[i]):
            choice_var.set(1 if choices[i][j] in selected_choices else 0)

def update_object_name_label():
    object_name_label.config(text=f"Object: {object_names[current_object_index]}")

def update_next_button():
    if current_object_index == len(object_names) - 1:
        next_button.pack_forget()  # Remove the "Next" button if it's the last object
    else:
        next_button.pack(pady=10)

def end_game():
    responses[object_names[current_object_index]] = {}  # Initialize responses for the current object
    for i, question in enumerate(questions):
        selected_choices = []
        for j, choice_var in enumerate(choice_vars[i]):
            if choice_var.get() == 1:
                selected_choices.append(choices[i][j])

        responses[object_names[current_object_index]][question] = selected_choices

    # if current_object_index == len(object_names) - 1:
    # Save responses to JSON file
    if not ideal_config:
        with open(f"./data/task_1_results/Exp_1/GT_used/{username}_var_responses.json", "w") as file:
            json.dump(responses, file, indent=4)
    elif ideal_config:
        with open(f"./data/task_1_results/Exp_1/GT_used/ideal_config.json", "w") as file:
            json.dump(responses, file, indent=4)    
    print("Responses saved to responses.json")

    window.destroy()

def start_game():
    global next_button,object_name_label,end_button
    start_frame.pack_forget() #Hide the start frame
    create_question_frames()
    create_widgets_after_start()
    update_question_ui()  # Initialize the UI for the first object
    update_object_name_label()
    update_next_button()
    
def create_widgets_after_start():
    global next_button,object_name_label, end_button
    # Object name label
    object_name_label = tk.Label(window, text="Object:" + object_names[current_object_index], font=("Arial", 14, "bold"), fg=label_color, bg=bg_color)
    object_name_label.pack(anchor="w")

    # Next button
    next_button = ttk.Button(window, text="Next", command=next_question, style="NextButton.TButton")
    next_button.pack(pady=10)

    # End button
    end_button = ttk.Button(window, text="End", command=end_game, style="EndButton.TButton")    
    end_button.pack(pady=10)

def create_question_frames():
    # Create and place widgets
    global choice_vars
    choice_vars = []
    for i, question in enumerate(questions):
        tk.Label(window, text=f"Question {i + 1}: {question}", font=("Arial", 12, "bold"), fg=label_color, bg=bg_color).pack(anchor="w")
        frame = ttk.Frame(window, padding=10)
        frame.configure(style="Choice.TFrame")
        
        choice_vars_for_question = []
        for choice in choices[i]:
            choice_var = tk.IntVar()
            choice_vars_for_question.append(choice_var)
            tk.Checkbutton(frame, text=choice, variable=choice_var, onvalue=1, offvalue=0, bg=bg_color).pack(anchor="w")
        
        choice_vars.append(choice_vars_for_question)
        frame.pack()

if __name__ == "__main__":
    # Create GUI window
    parser = argparse.ArgumentParser()
    parser.add_argument("--ideal_config", type=str, default=True)
    args = parser.parse_args()
    
    global ideal_config 
    ideal_config = args.ideal_config
    
    window = tk.Tk()
    window.title("Trivia Adventure")

    # Set colors
    bg_color = "#f4f4f4"
    label_color = "#000080"  # Dark blue
    button_color = "#d64e00"  # Reddish orange

    window.configure(bg=bg_color)
    question_frames = []

    # Start frame for the start screen
    start_frame = ttk.Frame(window, padding=20)
    start_frame.pack()

    tk.Label(start_frame, text="Welcome to Object-Trivia Adventure!", font=("Arial", 16, "bold"), fg=label_color, bg=bg_color).pack()
    tk.Label(start_frame, text="This game will challenge your knowledge about different objects and their properties.", font=("Arial", 12), fg=label_color, bg=bg_color).pack(pady=10)
    tk.Label(start_frame, text="You will be asked a series of questions about various objects, and you need to select the appropriate answers.", font=("Arial", 12), fg=label_color, bg=bg_color).pack(pady=10)
    tk.Button(start_frame, text="Start Game", command=start_game, bg=button_color, fg="white").pack()  # Use background and foreground options


    # # Object name label
    # object_name_label = tk.Label(window, text="Object:"+ object_names[current_object_index], font=("Arial", 14, "bold"), fg=label_color, bg=bg_color)
    # object_name_label.pack(anchor="w")

    # # Next button
    # next_button = ttk.Button(window, text="Next", command=next_question, style="NextButton.TButton")
    # next_button.pack(pady=10)

    # # End button
    # end_button = ttk.Button(window, text="End", command=end_game, style="EndButton.TButton")
    # end_button.pack(pady=10)

    # Create custom styles for the buttons
    style = ttk.Style()
    style.configure("NextButton.TButton", foreground="white", background="#007f00")  # Green
    style.configure("EndButton.TButton", foreground="white", background="#d64e00")  # Reddish orange
    style.configure("StartButton.TButton", foreground="white", background="#007f00")  # Green

    # # Update the next button status initially
    # update_next_button()

    # Start GUI event loop
    window.mainloop()

        