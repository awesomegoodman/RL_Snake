import os
import shutil
import platform
import subprocess
from typing import List, Callable, Optional, TextIO

def find_root_dir(start_dir: str, markers: Optional[List[str]] = None) -> Optional[str]:
    """
    Traverse up the directory hierarchy from `start_dir` until a directory containing
    one of the specified `markers` files is found.

    :param start_dir: The starting directory for the search.
    :param markers: List of filenames that indicate the root directory. Defaults to any of the following:
                     ['main.py', 'Dockerfile', 'requirements.txt', 'README.md', 
                      '.gitignore', '.gitattributes', 'pre-commit-config.yaml', 'pyproject.toml'].
    :return: The path to the root directory, or None if no root directory is found.
    """
    if markers is None:
        markers = ['requirements.txt', 'README.md']

    current_dir = os.path.abspath(start_dir)

    while current_dir != os.path.dirname(current_dir):  # Root directory reached
        if any(os.path.isfile(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    return None

def get_relative_path(target_path: str) -> str:
    """
    Get the relative path of `target_path` with respect to `base_dir`.

    :param target_path: The target file or directory path.
    :return: The relative path to `target_path`.
    """
    root_dir = find_root_dir(os.path.dirname(__file__))
    target_path = os.path.abspath(target_path)
    
    target_dir = os.path.dirname(target_path)

    return os.path.relpath(target_dir, start=root_dir)

def clean_up(paths: List[str]) -> None:
    """Remove specified files and directories."""
    for path in paths:
        if os.path.isdir(path):
            print(f"Removing directory {path}...")
            shutil.rmtree(path)
        elif os.path.isfile(path):
            print(f"Removing file {path}...")
            os.remove(path)
        else:
            print(f"Path {path} does not exist or is not a file or directory.")
        
def read_output(stream: TextIO, callback: Callable[[str], None]) -> None:
    """Read the output from a stream and pass it to a callback function."""
    for line in iter(stream.readline, ''):
        callback(line)
        
def print_output(line: str) -> None:
    print(line, end='')
    
def install_pre_commit_hooks() -> None:
    """Install pre-commit hooks."""
    print("\nInstalling pre-commit hooks.\n")
    subprocess.check_call(['pre-commit', 'install'])
    
def get_executable_name() -> str:
    """Get the executable name based on the operating system."""
    from .constants import APP_NAME
    
    system = platform.system()
    if system == "Windows":
        return f'{APP_NAME}.exe'
    elif system == "Darwin":  # macOS
        return APP_NAME
    elif system == "Linux":
        return APP_NAME
    else:
        raise ValueError(f"Unsupported OS: {system}")
    
def load_high_score() -> int:
    """Load high score from file. If file or line does not exist, return 0."""
    from .constants import text_file_path
    
    if not os.path.exists(text_file_path):
        return 0
    
    lines = []
    with open(text_file_path, "r") as file:
        lines = file.readlines()
    
    for line in lines:
        if line.startswith("HIGH_SCORE="):
            try:
                return int(line.split('=')[1])
            except ValueError:
                return 0
    return 0

def save_high_score(high_score: int) -> None:
    """Save the high score to the file, ensuring it is on the correct line."""
    from .constants import text_file_path
    
    lines = []
    if os.path.exists(text_file_path):
        with open(text_file_path, "r") as file:
            lines = file.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if line.startswith("HIGH_SCORE="):
            lines[i] = f"HIGH_SCORE={high_score}\n"
            found = True
            break
    
    if not found:
        lines.append(f"HIGH_SCORE={high_score}\n")
    
    with open(text_file_path, "w") as file:
        file.writelines(lines)
