import tkinter as tk
from tkinter import ttk
import json

# Questions and choices
questions = [
    "Mass",
    "Material",
    "Temperature"
]

choices = [
    ["0-1 Kg", "1-5 Kg", "5-10 Kg", "10-30 Kg"],
    ["Metal", "Wood", "Plastic", "Glass", "Ceramic", "Stone", "Fabric", "Rubber", "Food", "Paper", "Wax", "Soap", "Sponge", "Organic"],
    ["Cold", "RoomTemp", "Hot"]
]

responses = {}  # Dictionary to store responses

def submit():
    for i, question in enumerate(questions):
        selected_choices = []
        for j, choice_var in enumerate(choice_vars[i]):
            if choice_var.get() == 1:
                selected_choices.append(choices[i][j])

        responses[question] = selected_choices  # Add response to the dictionary

    # Save responses to JSON file
    with open("responses.json", "w") as file:
        json.dump(responses, file, indent=4)

    # Store or process responses as needed
    print(responses)
    window.destroy()

# Create GUI window
window = tk.Tk()
window.title("Trivia Adventure")

# Set colors
bg_color = "#f4f4f4"
label_color = "#000080"  # Dark blue
button_color = "#d64e00"  # Reddish orange

window.configure(bg=bg_color)

# Create and place widgets
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

# Submit button
submit_button = ttk.Button(window, text="Submit", command=submit, style="SubmitButton.TButton")
submit_button.pack(pady=10)

# Create custom styles for the widgets
style = ttk.Style()

style.configure("Choice.TFrame", background=bg_color)
style.configure("SubmitButton.TButton", foreground="white", background=button_color)

# Start GUI event loop
window.mainloop()
