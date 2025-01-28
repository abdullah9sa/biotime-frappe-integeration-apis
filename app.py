import tkinter as tk
from tkinter import scrolledtext
import requests
import json
from datetime import datetime, timedelta
import logging
import threading
import os
# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

running = False
timer = None

def get_token(base_url, username, password):
    try:
        token_url = f"{base_url}/jwt-api-token-auth/"
        payload = {"username": username, "password": password}
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            logging.info("Token fetched successfully.")
            return response.json().get("token")
        else:
            logging.error(f"Error fetching token: {response.text}")
    except Exception as e:
        logging.error(f"Exception while fetching token: {e}")
    return None

def fetch_data(base_url, token, api_endpoint):
    try:
        headers = {'Authorization': f'JWT {token}'}
        response = requests.get(f"{base_url}/{api_endpoint}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error fetching {api_endpoint}: {response.text}")
    except Exception as e:
        logging.error(f"Exception while fetching {api_endpoint}: {e}")
    return None


def save_punch(punch_id):
    month_file = f"punches_{datetime.now().strftime('%Y_%m')}.json"
    if not os.path.exists(month_file):
        with open(month_file, 'w') as f:
            json.dump([], f)

    with open(month_file, 'r') as f:
        processed_punches = json.load(f)

    if punch_id not in processed_punches:
        processed_punches.append(punch_id)
        with open(month_file, 'w') as f:
            json.dump(processed_punches, f)
        return True
    return False

def start_form():
    global running, timer
    base_url = base_url_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    frappe_url = frappe_url_entry.get()
    frappe_key = frappe_key_entry.get()
    frappe_secret = frappe_secret_entry.get()
    punch_time_var = int(punch_time_entry.get())

    if running:
        token = get_token(base_url, username, password)
        if token:
            punches = fetch_data(base_url, token, "iclock/api/transactions/")
            if punches:
                time_limit = datetime.now() - timedelta(minutes=punch_time_var)
                recent_punches = [
                    t for t in punches.get("data", [])
                    if 'punch_time' in t and datetime.fromisoformat(t['punch_time']) >= time_limit
                ]
                for punch in recent_punches:
                    punch_id = punch.get("id")
                    emp_code = punch.get("emp_code")
                    punch_time = punch.get("punch_time")
                    log_type = punch.get("punch_state_display")
                    log_type_new = "Out" if log_type == "Check Out" else "In"
                    if punch_id and save_punch(punch_id):
                        create_frappe_checkin(frappe_url, frappe_key, frappe_secret, emp_code, punch_time, log_type_new)
            update_logs()

        if timer:
            timer.cancel()
        timer = threading.Timer(punch_time_var * 60, start_form)
        timer.start()

def create_frappe_checkin(frappe_url, api_key, api_secret, employee_code, punch_time, log_type):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'token {api_key}:{api_secret}'
        }
        payload = json.dumps({
            "employee": employee_code,
            "time": punch_time,
            "log_type": log_type,
            "punch_type": "Remote Punch"
        })
        response = requests.post(frappe_url, headers=headers, data=payload)
        if response.status_code == 200:
            logging.info(f"Successfully created check-in for {employee_code}.")
        else:
            logging.error(f"Error creating check-in for {employee_code}: {response.text}")
    except Exception as e:
        logging.error(f"Exception while creating frappe check-in: {e}")

def update_logs():
    try:
        with open("app.log", "r") as log_file:
            lines = log_file.readlines()[-10:]
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, "".join(lines))
    except Exception as e:
        logging.error(f"Error updating logs in UI: {e}")

def toggle_running():
    global running, timer
    running = not running
    status_label.config(text="Running" if running else "Stopped", fg="green" if running else "red")
    if running:
        if timer:
            timer.cancel()
        start_form()
    else:
        if timer:
            timer.cancel()
            timer = None

def close_app():
    global timer
    if timer:
        timer.cancel()
    root.destroy()

# GUI setup
root = tk.Tk()
root.title("Punch Processor")
root.geometry("600x700")

tk.Label(root, text="Base URL").pack(pady=5)
base_url_entry = tk.Entry(root, width=50)
base_url_entry.insert(0, "http://127.0.0.1:8081")
base_url_entry.pack()

tk.Label(root, text="Username").pack(pady=5)
username_entry = tk.Entry(root, width=50)
username_entry.pack()

tk.Label(root, text="Password").pack(pady=5)
password_entry = tk.Entry(root, width=50, show="*")
password_entry.pack()

tk.Label(root, text="Frappe URL").pack(pady=5)
frappe_url_entry = tk.Entry(root, width=50)
frappe_url_entry.pack()

tk.Label(root, text="Frappe API Key").pack(pady=5)
frappe_key_entry = tk.Entry(root, width=50)
frappe_key_entry.pack()

tk.Label(root, text="Frappe API Secret").pack(pady=5)
frappe_secret_entry = tk.Entry(root, width=50)
frappe_secret_entry.pack()

tk.Label(root, text="Punch Time (minutes)").pack(pady=5)
punch_time_entry = tk.Entry(root, width=20)
punch_time_entry.insert(0, "10")
punch_time_entry.pack()

tk.Label(root, text="Logs (Last 10 entries):").pack(pady=10)
log_text = scrolledtext.ScrolledText(root, width=70, height=15)
log_text.pack()

status_label = tk.Label(root, text="Stopped", fg="red", font=("Arial", 14))
status_label.pack(pady=10)

toggle_button = tk.Button(root, text="Start/Stop", command=toggle_running)
toggle_button.pack(pady=10)

close_button = tk.Button(root, text="Close", command=close_app)
close_button.pack(pady=10)

# Start automatically
running = True
status_label.config(text="Running", fg="green")
start_form()

root.mainloop()