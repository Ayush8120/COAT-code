import tkinter as tk
from tkinter import messagebox
import random
import json,os

if os.path.exists("./data/task_0_question_database.json") and os.stat("./data/task_0_question_database.json").st_size > 0:
    with open("./data/task_0_question_database.json", "r") as file:
        questions = json.load(file)

class QuizApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.current_question = 0
        self.responses = {}  # Dictionary to store responses

        self.question_label = tk.Label(root, text="", wraplength=400)
        self.question_label.pack(pady=20)

        self.option_buttons = []
        for option in "ABCDE":
            button = tk.Button(root, text="", command=lambda o=option: self.save_response(o))
            self.option_buttons.append(button)
            button.pack(fill="both", expand=True)

        self.next_question_button = tk.Button(root, text="Next Question", command=self.next_question, state=tk.DISABLED)
        

        # Styling improvements
        self.root.configure(bg="#F0F4F8")  # Set background color
        self.question_label.config(font=("Helvetica", 16), wraplength=600, bg="#F0F4F8")
        self.next_question_button.config(font=("Lucida Sans", 16,"bold"), bg="#4CAF50", activebackground="#45A049", activeforeground="white", disabledforeground="#000000")
        self.next_question_button.pack(pady=10)
        option_color = "#D3E0EA"
        for button in self.option_buttons:
            button.config(font=("Helvetica", 14,"bold"), padx=20, pady=10, bg=option_color, fg="#333333")
            
        
        self.load_question()

    def load_question(self):
        question_data = questions[self.current_question]
        self.question_label.config(text=question_data["question"])

        options = question_data["options"]
        for i, option in enumerate("ABCDE"):
            self.option_buttons[i].config(text=f"{option}: {options[option]}")

    def save_response(self, selected_option):
        question_id = questions[self.current_question]["question_id"]
        
        self.responses[question_id] = selected_option
        self.next_question_button.config(state=tk.NORMAL)
        questions[self.current_question]["correct_answer"] = selected_option
        with open(f"./data/task_0_question_answer_database_{self.username}.json", "w") as file:
            json.dump(questions, file,indent=4)

        for button in self.option_buttons:
            button.config(state=tk.DISABLED)

    def next_question(self):
        self.current_question += 1
        if self.current_question < len(questions):
            self.load_question()
            self.next_question_button.config(state=tk.DISABLED)
            for button in self.option_buttons:
                button.config(state=tk.NORMAL)
        else:
            messagebox.showinfo("Quiz Completed", "Quiz completed!\nResponses saved.")
            self.root.destroy()

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Human Choices Collection App")
    window.geometry("800x600")  # Set initial window size
    username = input("Please Enter Your Name:")
    app = QuizApp(window,username)
    window.eval('tk::PlaceWindow %s center' % window.winfo_pathname(window.winfo_id()))
    window.mainloop()
