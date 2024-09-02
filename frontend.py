import tkinter as tk
from tkinter import simpledialog, messagebox
import requests

SERVER_URL = "http://127.0.0.1:5000/chat"

def send_message():
    user_input = simpledialog.askstring("Input", "Enter your query:")
    if not user_input:
        messagebox.showwarning("Input Error", "No message entered.")
        return

    try:
        response = requests.post(SERVER_URL, json={'message': user_input})
        if response.status_code == 200:
            bot_response = response.json().get('response', 'No response from server.')
            if isinstance(bot_response, str):
                messagebox.showinfo("Response", bot_response)
            else:
                response_text = "\n".join([str(item) for item in bot_response])
                messagebox.showinfo("Response", response_text)
        else:
            messagebox.showerror("Error", f"Server returned status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Could not connect to server.\nDetails: {e}")

# Create the main window

root = tk.Tk()
root.title("Test Window")

label = tk.Label(root, text="Tkinter is working!")
label.pack(pady=20)

button = tk.Button(root, text="Close", command=root.destroy)
button.pack(pady=10)

root.mainloop()
