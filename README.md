# Snake Game with Q-Learning Agent

This project is a Python implementation of the classic Snake game, enhanced with a Q-Learning Agent that allows an AI to learn and play the game. You can play the game manually or let the AI take control, and there are several ways to run the game, depending on your setup and preferences.

## Directory Structure

```plaintext
.
├── assets/
│   ├── icons/
│   │   └── icon.ico
│   └── soundtrack/
├── dist/
├── saved/
├── script/
│   ├── build.py
│   └── deploy.py
├── src/
│   └── utils/
│       ├── constants.py
│       └── types.py
│       ├── utils.py
├── weights/
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── main.py
├── pyproject.toml
├── README.md
└── requirements.txt
```

- **assets/**: Contains all static resources used by the game.
  - **icons/**: Stores icon files used by the application.
    - `icon.ico`: The icon file for the application.
  - **soundtrack/**: Contains background music files and SFX used in the game.
- **dist/**: Contains the executable.
- **saved/**: Holds files that save game data, such as high scores or other user progress.
- **script/**: Contains scripts for building, deploying, and managing the project.
  - **build.py**: Script to build an executable for your operating system.
  - **deploy.py**: Script that installs dependencies, builds the executable, and runs it.
- **src/**: Contains source code for the project.
  - **utils/**: Directory for utility functions.
    - **constants.py**: Defines constants and paths used throughout the project, including configuration and file paths.
    - **types.py**: Defines type annotations for the project.
    - **utils.py**: Contains utility functions.
- **weights/**: Stores the Q-table weights used by the Q-Learning Agent.
- **main.py**: The main script for the Snake game.

## How to Run the Game

### Option 1: Using Docker (Cross-Platform)

1. **Build the Docker Image**:

   ```bash
   docker build -t snake-game .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -it --rm snake-game
   ```

### Option 2: Build the Executable

- **OS Dependency**: Build the executable by running `build.py`. Ensure Python and dependencies are installed first.
  ```bash
  python -m script.build
  ```

### Option 3: Running the Python Script Directly

- If you have Python and pip installed, you can run the game by executing the `main.py` script:
  ```bash
  python main.py
  ```

### Option 4: The All-in-One Solution (Recommended)

- The most straightforward way to run the game is by using the `deploy.py` script, which installs dependencies, builds the executable, and runs the game in one step:
  ```bash
  python -m script.deploy
  ```

## Game Modes

- **Human-Agent**: Uncomment the `play_as_human()` function at the end of `main.py` to play manually.
- **RL-Agent**: Uncomment the `train_agent()` function at the end of `main.py` to train the AI using Q-Learning.

## Controls

### Human-Agent Controls

- Use the arrow keys (`Up`, `Down`, `Left`, `Right`) to control the snake.
- Press `Enter` or `R` to restart the game after a game-over.
- Press `Esc` or `Q` to quit the game.

### Q-Learning Agent Controls

- The Q-Learning Agent will automatically start learning once `train_agent()` is run.
- During training, press `S` to save the Q-table.
- Press `Esc` or `Q` to stop training and exit the game.

## Q-Learning Explanation

### Value Function

The **Value Function** \( V(s) \) determines the expected value of a state \( s \), representing the cumulative reward an agent can expect to receive by starting from state \( s \) and following a specific policy. It is defined as:

```
V(s) = E[r + γ * V(s')]
```

Where:

- `r` is the immediate reward after transitioning to state `s'`.
- `γ` (gamma) is the discount factor, which determines the importance of future rewards. It ranges from `0` to `1`.

### Action-Value Function

The **Action-Value Function** \( Q(s, a) \) represents the expected value (cumulative reward) of taking action `a` in state `s`, and then following a specific policy. It is defined as:

```
Q(s, a) = E[r + γ * V(s')]
```

### Optimal Q-Value (Bellman Equation)

The **Optimal Q-Value** \( Q^\*(s, a) \) is computed using the Bellman Equation, which considers the best possible future action:

```
Q^*(s, a) = E[r + γ * max_a' Q^*(s', a')]
```

This equation forms the basis of Q-Learning, where the agent aims to maximize its cumulative reward by choosing actions that lead to the highest possible future rewards.

### State Value

The **State Value** \( V(s) \) can be determined by choosing the action `a` that maximizes the Q-value:

```
V(s) = max_a Q(s, a)
```

## Adjusting the Game Speed

The game speed is controlled by the `SPEED` variable in the `utils/constants.py` script:

```python
SPEED = 100
```

- **Faster Game**: Reduce the `SPEED` value to increase the game speed.
- **Training Q-Learning Agent**: Set `SPEED = 1` to allow the Q-Learning Agent to train quickly.

## Saving and Loading Q-Table

The Q-Table is automatically saved to the `weights/` directory after each training session or when the `S` key is pressed. The agent will load the Q-table from the file when training or testing begins.

## Contributions

Feel free to contribute by forking the repository, creating a branch, and submitting a pull request with your improvements.

## Acknowledgments

This project is inspired by the classic Snake game, enhanced with reinforcement learning techniques.
