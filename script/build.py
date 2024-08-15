import os
import subprocess
from threading import Thread
import time
import itertools
from typing import List, Optional
from src.utils.constants import APP_NAME, icon_file_path
from src.utils.utils import clean_up, read_output, print_output, find_root_dir, get_relative_path
from datetime import datetime  # TODO: Use to create timestamp for build versioning
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# ANSI escape codes for hiding and showing the cursor
HIDE_CURSOR: str = "\033[?25l"
SHOW_CURSOR: str = "\033[?25h"

root_dir: Optional[str] = find_root_dir(os.path.dirname(__file__))

paths_to_clean: List[str] = [
    'dist',
    'build',
    f'{APP_NAME}.spec'
]

def build() -> None:
    """Build the application using PyInstaller."""
    
    # Save the original working directory
    original_dir: str = os.getcwd()
    
    if root_dir is not None and original_dir != root_dir:
        # Change to the root directory if it's different
        os.chdir(root_dir)
    
    clean_up(paths_to_clean)
    
    command: List[str] = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--noconsole',
        f'--add-data={icon_file_path};{get_relative_path(icon_file_path)}',
        f'--icon={icon_file_path}',
        f'--name={APP_NAME}',
        'main.py'
    ]
    
    process: subprocess.Popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # type: ignore

    print(f"\n{HIDE_CURSOR}{Fore.BLUE}Building {APP_NAME}", end="")
        
    # Start threads to read stdout and stderr
    stdout_thread: Optional[Thread] = None
    stderr_thread: Optional[Thread] = None
    
    if process.stdout is not None:
        stdout_thread = Thread(target=read_output, args=(process.stdout, print_output))
        stdout_thread.start()

    if process.stderr is not None:
        stderr_thread = Thread(target=read_output, args=(process.stderr, print_output))
        stderr_thread.start()
    
    try:
        # Dot animation
        animation: itertools.cycle = itertools.cycle([".", "..", "..."])
        
        while True:
            # Check if the process has finished
            if process.poll() is not None:
                break
            
            # Print the animated dots
            print(f"\r{Fore.BLUE}Building {APP_NAME}{next(animation):<3}", end="", flush=True)
            time.sleep(0.5)
        
        # Stream the output and errors in real-time
        if process.stdout is not None:
            for line in process.stdout:
                print(line, end='')

        if process.stderr is not None:
            for line in process.stderr:
                print(line, end='')

        # Wait for the process to complete
        process.wait()

        print(f"\n{Fore.GREEN}{APP_NAME} built successfully!\n{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Build interrupted by user.{Style.RESET_ALL}")
    
    finally:
        if stdout_thread is not None and stderr_thread is not None:
            # Ensure threads have finished
            stdout_thread.join()
            stderr_thread.join()

        # Ensure the cursor is shown again
        print(SHOW_CURSOR, end="")
        
        if original_dir != root_dir:
            # Restore the original working directory
            os.chdir(original_dir)

if __name__ == "__main__":
    build()
