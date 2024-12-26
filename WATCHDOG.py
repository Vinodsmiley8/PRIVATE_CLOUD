import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import threading
import itertools

class FileChangeHandler(FileSystemEventHandler):
    """Handles file change events."""
    def __init__(self, file_to_watch, script_to_run):
        self.file_to_watch = file_to_watch
        self.script_to_run = script_to_run

    def on_modified(self, event):
        """Triggered when the file is modified."""
        if event.src_path == self.file_to_watch:
            # print(f"\n{self.file_to_watch} has been modified. Running {self.script_to_run}...")
            subprocess.run(["python", self.script_to_run], check=True)

def loading_animation(stop_event):
    """Displays a loading spinner animation."""
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    while not stop_event.is_set():
        print(f"\rMonitoring file... {next(spinner)}", end='', flush=True)
        time.sleep(0.1)
    print("\rMonitoring file... Done!", end='', flush=True)

def monitor_file(file_to_watch, script_to_run):
    """Monitors a file for changes and runs a script when changes occur."""
    if not os.path.exists(file_to_watch):
        print(f"File {file_to_watch} does not exist. Creating it...")
        with open(file_to_watch, 'w') as f:
            f.write("")  # Create an empty file

    directory_to_watch = os.path.dirname(file_to_watch)
    event_handler = FileChangeHandler(file_to_watch, script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=False)
    observer.start()

    stop_event = threading.Event()
    animation_thread = threading.Thread(target=loading_animation, args=(stop_event,))
    animation_thread.start()

    print(f"Monitoring {file_to_watch} for changes...")
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
        stop_event.set()
        animation_thread.join()
        print("\nStopped monitoring.")

    observer.join()

if __name__ == "__main__":
    file_to_watch = r"C:\Users\gocha\OneDrive\Desktop\MEGA\MEGA PRIVATE SERVER\SERVER.txt"
    script_to_run = r"C:\Users\gocha\OneDrive\Desktop\MEGA\MEGA PRIVATE SERVER\server_html_creater.py"
    
    monitor_file(file_to_watch, script_to_run)
