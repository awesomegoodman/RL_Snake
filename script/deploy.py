import os
import subprocess
import sys
from typing import Optional
from src.utils.utils import get_executable_name, install_pre_commit_hooks, find_root_dir

root_dir: Optional[str] = find_root_dir(os.path.dirname(__file__))

def install_requirements() -> None:
    """Install dependencies from 'requirements.txt'."""
    if root_dir is None:
        raise ValueError("Root directory could not be determined")
    print("\nInstalling dependencies from 'requirements.txt'.\n")
    requirements_file = os.path.join(root_dir, 'requirements.txt')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])

def build_executable() -> None:
    """Run the 'build.py' script to create the executable."""
    try:
        from colorama import init, Fore, Style
        init(autoreset=True)

        subprocess.check_call([sys.executable, '-m', 'script.build'])
    except subprocess.CalledProcessError as e:
        print(f"\n{Fore.RED}Failed to build the executable: {e}{Style.RESET_ALL}\n")

def run_executable() -> None:
    """Run the generated executable from the 'dist/' directory."""
    try:
        from colorama import Fore, Style
        
        if root_dir is None:
            raise ValueError("Root directory could not be determined")

        executable_name: str = get_executable_name()
        executable_path: str = os.path.join(root_dir, 'dist', executable_name)

        if os.path.exists(executable_path):
            print(f"\n{Fore.LIGHTGREEN_EX}Starting the executable '{executable_path}'.{Style.RESET_ALL}\n")
            subprocess.run([executable_path])
        else:
            print(f"\n{Fore.RED}Error: {executable_path} does not exist. Build may have failed.{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\nFailed to run the executable: {e}\n")

def main() -> None:
    install_requirements()
    install_pre_commit_hooks()
    build_executable()
    run_executable()

if __name__ == "__main__":
    main()
