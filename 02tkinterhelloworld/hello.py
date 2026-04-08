import tkinter as tk

root = tk.Tk()  # Create main window

root.title("My First App")
root.geometry("400x300")

label = tk.Label(root, text="Hello Tanbir 👋")
label.pack()

button = tk.Button(root, text="Click Me")
button.pack()

root.mainloop()  # Run the app