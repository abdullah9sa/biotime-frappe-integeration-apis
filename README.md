# Punch Processor

A Python-based application to automate the processing of employee punch data and syncing it with Frappe. The application uses a simple GUI built with Tkinter and supports logging, periodic updates, and duplicate punch prevention by maintaining monthly records of processed punches.

---

## Features

- **Authentication**: Fetches a token from the API for secure data retrieval.
- **Periodic Updates**: Automatically fetches punch data at user-defined intervals.
- **Duplicate Prevention**: Keeps track of processed punch IDs in monthly JSON files to avoid reprocessing.
- **Integration with Frappe**: Syncs punch data with a Frappe-based system using API keys.
- **Logging**: Maintains logs for debugging and activity tracking.
- **User-Friendly GUI**: Simple interface for configuration and operation.
- **Auto-Start**: Automatically starts processing on app launch.
- **Easy Termination**: Includes a button to stop and close the application.

---

## Requirements

- Python 3.7+
- `requests` library
- `tkinter` (bundled with Python by default)
- Permissions to create log files and JSON files in the application directory.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/punch-processor.git
   cd punch-processor

----------

Usage
Configuration:

Fill in the required fields in the GUI (Base URL, Username, Password, Frappe API Key/Secret, etc.).
Specify the interval for checking punch data (in minutes).
Start/Stop:

The application starts processing automatically upon launch.
Use the Start/Stop button to toggle processing.
Logs:

View the latest logs in the GUI under the Logs section.
Detailed logs are saved in app.log.
Punch Tracking:

Processed punch IDs are saved in punches_<year>_<month>.json files in the current directory.
The application prevents duplicate punches by checking against these files.
Close the Application:

Click the Close button to safely terminate the application.
File Structure
app.py: Main application script.
app.log: Log file for activity and error tracking.
punches_<year>_<month>.json: JSON files for tracking processed punch IDs.
Logging
Logs are stored in the app.log file.
Includes info-level logs for normal operations and error-level logs for issues encountered.
