import sys
import os
from tkinter import *
import random
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union # type: ignore
import numpy as np
import pickle
from src.utils.types import  QTable, State, StateKey
from  src.utils.constants import APP_NAME, GAME_WIDTH, GAME_HEIGHT, SPEED, SPACE_SIZE, BODY_PARTS, SNAKE_COLOR, SNAKE_HEAD_COLOR, FOOD_COLOR, BACKGROUND_COLOR, BACKGROUND_MUSIC_FILES, HUMAN_AGENT, RL_AGENT, episodes, icon_file_path, soundtrack_path, text_file_path, q_table_file_path
from src.utils.utils import load_high_score, save_high_score


class QLearningAgent:
    def __init__(self, alpha: float = 0.1, gamma: float = 0.99, epsilon: float = 1.0, epsilon_decay: float = 0.995, epsilon_min: float = 0.01) -> None:
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table: QTable = QTable(__root__={})  # Q-table

    def get_state_key(self, state: Optional[State]) -> StateKey:
        if state is None:
            raise ValueError("State cannot be None.")
        
        head_x, head_y = state['head']
        food_x, food_y = state['food']
        body = tuple(tuple(part) for part in state['body'])
        near_border = state['near_border']
        
        # Calculate relative position of the food to the snake's head
        rel_food_x = food_x - head_x
        rel_food_y = food_y - head_y

        # Calculate relative positions of the snake's body parts to the snake's head
        rel_body = tuple((part_x - head_x, part_y - head_y) for part_x, part_y in body)
        
        return (rel_food_x, rel_food_y, len(state['body']), rel_body, near_border)

    def choose_action(self, state: State) -> int:
        if np.random.rand() < self.epsilon:
            return np.random.choice(4)  # Explore: choose random action

        state_key = self.get_state_key(state)
        q_table_root = self.q_table['__root__']

        if state_key not in q_table_root:
            q_table_root[state_key] = np.zeros(4)  # Initialize Q-values for new state
        
        return int(np.argmax(q_table_root[state_key]))  # Exploit: choose best action

    def learn(self, state: State, action: int, reward: int, next_state: State, done: bool) -> None:
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        q_table_root = self.q_table['__root__']

        if state_key not in q_table_root:
            q_table_root[state_key] = np.zeros(4)
        if next_state_key not in q_table_root:
            q_table_root[next_state_key] = np.zeros(4)

        q_update = reward
        if not done:
            q_update += self.gamma * np.max(q_table_root[next_state_key])

        q_table_root[state_key][action] = (1 - self.alpha) * q_table_root[state_key][action] + self.alpha * q_update

        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def save_q_table(self, file_path: str) -> None:
        with open(file_path, 'wb') as f:
            pickle.dump(self.q_table['__root__'], f)

    @staticmethod
    def load_q_table(file_path: str) -> QTable:
            with open(file_path, 'rb') as f:
                q_table_data = pickle.load(f)
                return QTable(__root__=q_table_data)


class Direction:
    def __init__(self, opening_direction: str = 'Down') -> None:
        self.current_direction: str = opening_direction
        self.opening_direction: str = opening_direction
        self.directions: List[str] = ['Up', 'Down', 'Left', 'Right']

    def change_direction(self, direction_event: Optional[Event] = None, new_direction: Optional[str] = None) -> None:
        if direction_event:
            new_direction = direction_event.keysym

        if new_direction == 'Left' and self.current_direction != 'Right':
            self.current_direction = new_direction
        elif new_direction == 'Right' and self.current_direction != 'Left':
            self.current_direction = new_direction
        elif new_direction == 'Up' and self.current_direction != 'Down':
            self.current_direction = new_direction
        elif new_direction == 'Down' and self.current_direction != 'Up':
            self.current_direction = new_direction

    def get_direction(self) -> str:
        return self.current_direction
    
    def reset(self) -> None:
        self.current_direction = self.opening_direction


class Food:
    def __init__(
        self, 
        canvas: Canvas, 
        x_coord: int = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE,
        y_coord: int = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
    ) -> None:
        self.coordinates: List[int] = [x_coord, y_coord]
        canvas.create_oval(x_coord, y_coord, x_coord + SPACE_SIZE, y_coord + SPACE_SIZE, fill=FOOD_COLOR, tags="food")


class Snake:
    def __init__(self, canvas: Canvas) -> None:
        self.body_size: int = BODY_PARTS
        self.canvas: Canvas = canvas
        self.coordinates: List[List[int]] = []
        self.squares: List[int] = []

        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])
                
        for index, (x, y) in enumerate(self.coordinates):
            if index == 0:
                # Head color
                square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_HEAD_COLOR, tags="snake")
            else:
                # Body color
                square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tags="snake")
            self.squares.append(square)

    def is_food_eaten(self, food: Food) -> bool:
        snake_head_coord_x, snake_head_coord_y = self.coordinates[0]
        food_coord_x, food_coord_y = food.coordinates[0], food.coordinates[1]

        return snake_head_coord_x == food_coord_x and snake_head_coord_y == food_coord_y

    def is_border_collision(self) -> bool:
        x, y = self.coordinates[0]

        return x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT

    def is_self_collision(self) -> bool:
        head_x, head_y = self.coordinates[0]
        for body_part in self.coordinates[1:]:
            if head_x == body_part[0] and head_y == body_part[1]:
                return True
        return False

    def turn(self, direction: Direction) -> None:
        x, y = self.coordinates[0]

        if direction.get_direction() == "Up":
            y -= SPACE_SIZE
        elif direction.get_direction() == "Down":
            y += SPACE_SIZE
        elif direction.get_direction() == "Left":
            x -= SPACE_SIZE
        elif direction.get_direction() == "Right":
            x += SPACE_SIZE

        self.coordinates.insert(0, [x, y])

        # Create a new square for the head with the head color
        head_square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_HEAD_COLOR)

        # Insert the head square at the start of the squares list
        self.squares.insert(0, head_square)

        # Change the previous head square to the body color
        if len(self.squares) > 1:
            self.canvas.itemconfig(self.squares[1], fill=SNAKE_COLOR)


class Score:
    _instance: Optional['Score'] = None

    def __new__(cls: Type['Score'], *args: Any, **kwargs: Any) -> 'Score':
        if cls._instance is None:
            cls._instance = super(Score, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.current_score: int = 0
        self.saved_high_score: int = load_high_score()
        self.high_score: int = self.saved_high_score

    def update_score(self, points: int = 1) -> int:
        self.current_score += points
        return self.current_score

    def reset(self) -> None:
        if self.current_score > self.high_score:
            self.high_score = self.current_score
        self.current_score = 0
    
    def save_high_score(self) -> None:
        if self.high_score > self.saved_high_score:
            save_high_score(self.high_score)
        
    def reset_high_score(self) -> None:
        """Resets the high score to zero and saves it to the file."""
        self.high_score = 0
        save_high_score(0)


class Game:
    def __init__(self, player_type: Union[Literal['RL_Agent'], Literal['Human_Agent']]) -> None: # type: ignore
        self.score: Score = Score()
        self.direction: Direction = Direction()
        self.window: Tk = Tk()
        self.canvas: Canvas = Canvas(self.window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
        
        # Frame for scores
        self.score_frame: Frame = Frame(self.window)
        self.score_frame.pack(fill=BOTH, expand=True)

        # Label for high score
        self.high_score_label: Label = Label(self.score_frame, text=f"High Score: {self.score.high_score}", font=('consolas', 30))
        self.high_score_label.pack(side=TOP, pady=1)
        
        # Label for current score
        self.label: Label = Label(self.score_frame, text=f"Score: {self.score.current_score}", font=('consolas', 25))
        self.label.pack(side=TOP, pady=1)
        
        self.snake: Optional[Snake] = None
        self.food: Optional[Food] = None
        self.running: bool = True
        self.paused: bool = False
        self.setup_done: bool = False
        self.player_type: Union[Literal['RL_Agent'], Literal['Human_Agent']] = player_type
        self.rl_agent: Optional[QLearningAgent] = None
        self.total_reward: int = 0  # For RL_Agent
        self.quit: bool = False  # For RL_Agent training
        self.reset_count: int = 0
        self.max_resets: int = episodes

    def display_paused_message(self) -> None:
        self.canvas.create_rectangle(
            0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
            fill='black', stipple='gray50', tags="paused_overlay"
        )
        self.canvas.create_text(
            self.canvas.winfo_width() / 2, 
            self.canvas.winfo_height() / 2, 
            text="PAUSED", 
            font=('consolas', 50), 
            fill='yellow', 
            tags="paused_message"
        )
    
    def clear_paused_message(self) -> None:
        self.canvas.delete("paused_overlay")
        self.canvas.delete("paused_message")
    
    def toggle_pause(self) -> None:
        if self.is_game_over() or not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.display_paused_message()
        else:
            self.clear_paused_message()
            self.update_game()

    def run_setup(self) -> None:
        self.window.title(APP_NAME)
        self.window.iconbitmap(icon_file_path)
        self.window.resizable(False, False)

        self.label.pack()
        self.canvas.pack()
        self.window.update()

        window_width: int = self.window.winfo_width()
        window_height: int = self.window.winfo_height()
        screen_width: int = self.window.winfo_screenwidth()
        screen_height: int = self.window.winfo_screenheight()

        x: int = int((screen_width / 2) - (window_width / 2))
        y: int = int((screen_height / 2) - (window_height / 2))

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        if self.player_type == HUMAN_AGENT:
            self.window.bind('<Left>', lambda event: self.direction.change_direction(event))
            self.window.bind('<Right>', lambda event: self.direction.change_direction(event))
            self.window.bind('<Up>', lambda event: self.direction.change_direction(event))
            self.window.bind('<Down>', lambda event: self.direction.change_direction(event))
            
        self.window.bind('<Escape>', lambda event: self.on_closing())
        self.window.bind("<q>", lambda event: self.on_closing())
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.window.bind("<m>", lambda event: self.score.reset_high_score())
        
        if self.player_type == RL_AGENT and self.rl_agent is not None:
            self.window.bind('<s>', lambda event: (self.rl_agent.save_q_table(q_table_file_path), print("Weights saved"))) # type: ignore
  
            if os.path.exists(q_table_file_path):
                q_table = QLearningAgent.load_q_table(q_table_file_path)
                self.rl_agent.q_table = q_table
                
        self.window.bind('<p>', lambda event: self.toggle_pause())
        self.window.bind('<space>', lambda event: self.toggle_pause())

        self.setup_done = True

    def create_food(self) -> Optional[Food]:
        
        if self.snake is None:
            return None
        
        snake_body_set: set = set(tuple(coord) for coord in self.snake.coordinates)
        all_positions: set = set((x, y) for x in range(0, GAME_WIDTH, SPACE_SIZE) for y in range(0, GAME_HEIGHT, SPACE_SIZE))
        available_positions: List[tuple] = list(all_positions - snake_body_set)
        
        if available_positions:
            x, y = random.choice(available_positions)
            return Food(self.canvas, x, y)
        else:
            raise Exception("No available position to place food")

    def create_snake(self) -> Snake:
        return Snake(self.canvas)

    def run_game(self) -> None:
        self.run_setup()
        snake: Snake = Snake(self.canvas)
        food: Food = Food(self.canvas)
        self.snake, self.food = snake, food
        
        self.update_game()
        self.window.mainloop()
        
    def on_closing(self) -> None:
        self.score.save_high_score()
        if self.player_type == RL_AGENT and self.rl_agent is not None:
            print("Training interrupted, saving Q-table...")
            agent.save_q_table(q_table_file_path)
            os._exit(0)
        self.running = False
        self.quit = True
        self.window.destroy()

    def is_game_over(self) -> Optional[bool]:
        
        if self.snake is None:
            return None
        
        return self.snake.is_border_collision() or self.snake.is_self_collision()
    
    def check_window(self) -> None:
        try:
            if not self.window.winfo_exists():
                self.running = False
                return
        except TclError:
            self.running = False
            return
    
    def update_game(self) -> None:
        self.check_window()
        
        if not self.running or self.paused:
            return
        
        if self.player_type == RL_AGENT:
            self.rl_agent_logic()
        else:
            self.human_agent_logic()
            
    def human_agent_logic(self) -> None:
        
        if self.snake is None or self.food is None:
            return
        
        self.snake.turn(self.direction)
            
        if self.snake.is_food_eaten(self.food):
            current_score: int = self.score.update_score()
            self.label.config(text=f"Score: {current_score}")
            self.canvas.delete("food")
            self.food = self.create_food()
        else:
            del self.snake.coordinates[-1]
            self.canvas.delete(self.snake.squares[-1])
            del self.snake.squares[-1]

            if self.is_game_over():
                self.game_over()
                return
        
        self.window.after(SPEED, self.update_game)
    
    def rl_agent_logic(self) -> None:
        
        if self.snake is None or self.food is None:
            return
        
        state = self.get_state()
        
        if state is None:
            return

        action = agent.choose_action(state)
        self.perform_action(action)
        next_state = self.get_state()

        if self.snake.is_food_eaten(self.food):
            current_score = self.score.update_score()
            self.label.config(text=f"Score: {current_score}")
            self.canvas.delete("food")
            self.food = self.create_food()
            reward = 5
        else:
            del self.snake.coordinates[-1]
            self.canvas.delete(self.snake.squares[-1])
            del self.snake.squares[-1]
            
            if self.is_game_over():
                if self.score.current_score > self.score.high_score:
                    self.score.high_score = self.score.current_score
                    self.high_score_label.config(text=f"High Score: {self.score.high_score}")
                reward = -10
                agent.learn(state, action, reward, next_state, not self.running) # type: ignore
                self.total_reward += reward
                self.reset_game()
                return
            else:
                reward = 0
            
        agent.learn(state, action, reward, next_state, not self.running) # type: ignore
        self.total_reward += reward

        self.window.after(SPEED, self.update_game)
            
    def reset_game(self) -> None:
        if self.reset_count >= self.max_resets:
            if self.player_type == RL_AGENT and self.rl_agent is not None:
                print("Training completed, Q-table saved.")
                agent.save_q_table(q_table_file_path)
            self.game_over()
            return

        if (self.reset_count + 1) % 100 == 0:
            print(f"Episode {self.reset_count + 1}/{episodes}, Total Reward: {self.total_reward}")
            
        self.reset_count += 1
        
        if self.canvas:
            self.canvas.delete("all")
        else:
            self.canvas = Canvas(self.window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
            self.canvas.pack()
            
        self.score.reset()
        self.direction.reset()
        self.label.config(text=f"Score: {self.score.current_score}")
        self.snake = self.create_snake()
        self.food = self.create_food()
        self.update_game()

    def restart_game(self) -> None:
        
        self.check_window()

        if not self.setup_done:
            self.run_game()
            self.running = True
            return
        
        if self.player_type == RL_AGENT:
            self.reset_count = 0
        
        self.running = True
        self.reset_game()

    def game_over(self) -> None:
        self.running = False
        
        if self.score.current_score > self.score.high_score:
            self.score.high_score = self.score.current_score
            self.high_score_label.config(text=f"High Score: {self.score.high_score}")

        self.canvas.delete("all")
        if self.player_type == RL_AGENT and self.rl_agent is not None:
            self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, font=('consolas', 40), text="TRAINING COMPLETED", fill="green", tags="gameover")
        else:
            self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, font=('consolas', 70), text="GAME OVER", fill="red", tags="gameover")
        self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2 + self.canvas.winfo_height() / 4, font=('Arial', 10), text="Press ENTER to restart or ESC to quit", fill="white", tags="restart_text")
        # self.canvas.create_text(GAME_WIDTH / 2, GAME_HEIGHT / 2 + 30, text="Press R to restart or Q to quit", fill="white", font=("Arial", 18))
        self.window.bind('<Return>', lambda event: self.restart_game())
        self.window.bind("<r>", lambda event: self.restart_game())

    def get_state(self) -> Optional[State]:
        
        if self.snake is None or self.food is None:
            return None
        
        head_x, head_y = self.snake.coordinates[0]
        food_x, food_y = self.food.coordinates
        body = self.snake.coordinates[1:]

        return State(
            head=(head_x, head_y),
            food=(food_x, food_y),
            body=body,
            near_border=(
                head_x == 0 or head_x == GAME_WIDTH - SPACE_SIZE,
                head_y == 0 or head_y == GAME_HEIGHT - SPACE_SIZE
            )
        )

    def perform_action(self, action: int) -> None:
        
        if self.snake is None or self.food is None:
            return
        
        self.direction.change_direction(new_direction=self.direction.directions[action])
        self.snake.turn(self.direction)


agent = QLearningAgent()

def train_agent() -> None:
    game = Game(RL_AGENT)
    game.rl_agent = agent

    game.run_game() 
    
    # TODO: Test the agent after training

def play_as_human() -> None:
    game = Game(HUMAN_AGENT)
    game.restart_game()


if __name__ == "__main__":
    play_as_human()
    # train_agent()
