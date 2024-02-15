# pip install tkinterdnd2-universal

import tkinter as tk
from tkinter import scrolledtext 
from tkinterdnd2 import DND_FILES, TkinterDnD

# make the UI more interesting
root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()
root.geometry("400x400")

# put a label that says "Drag files to here"
insert_file_label = tk.Label(root, text="Drag and drop file below")
insert_file_label.pack()

lb = tk.Listbox(root)

# register the listbox as a drop target
lb.drop_target_register(DND_FILES)
lb.dnd_bind('<<Drop>>', lambda e: lb.insert(tk.END, e.data))
lb.config(width=20, height=5)

# list box only have single selection
lb.config(selectmode=tk.SINGLE)
lb.pack()

# add button to send the listbox items to the console
def send_listbox():
    for i in lb.get(0, tk.END):
        print(i)
    
send_button = tk.Button(root, text="Send Listbox", command=send_listbox)
send_button.config(height=2, width=10)
send_button.pack()

# add a button to clear the listbox
def clear_listbox():
    lb.delete(0, tk.END)
    
clear_button = tk.Button(root, text="Clear Listbox", command=clear_listbox)
clear_button.config(height=2, width=10)
clear_button.pack()

insert_text_label = tk.Label(root, text="Insert text below")
insert_text_label.pack()

textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, 
                                      width=40, height=10) 
textbox.pack()

# send button that sends the text to console
def send_text():
    print(textbox.get("1.0", tk.END))
    textbox.delete("1.0", tk.END)
    
send_button = tk.Button(root, text="Send Text", command=send_text)
send_button.config(height=2, width=10)
send_button.pack()


root.mainloop()

