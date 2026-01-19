# 🐍 Snake Game – Version 1.0.0

Overview
Snake Game (v1.0.0) is a modern and visually enhanced version of the classic arcade snake game, built entirely in Python.
This project holds a special place as it was originally created in 2022, when the developer was in 12th grade, during the last few months of school life.
It represents not only the beginning of a programming journey but also the curiosity and creativity that inspired learning through building.

The game uses the turtle graphics library for visuals and integrates pygame for background music and sound effects, making it both nostalgic and engaging.
It combines simplicity with a polished design to give players a fun and complete gaming experience.

# 🎮 About the Game

The Snake Game follows the timeless arcade concept — control the snake to eat food appearing randomly on the screen and grow in size, while avoiding collisions with walls or your own body.
Every bite increases your score and speed, making the game progressively challenging.

The game also includes smooth background music, a start/pause menu, and clear visual feedback, making it much more refined than traditional console-based snake versions.
It’s a great blend of logic, timing, and reflexes — ideal for quick fun and casual coding demonstration.

# 🧩 Features

Interactive Main Menu – Start, Resume, Pause, or Quit with ease.

Smooth Gameplay – Optimized for responsive movement using turtle.

Sound Effects & Music – Background tracks and event sounds powered by pygame.mixer.

Dynamic Scoring System – Real-time updates for score and high score.

Custom Icon – Unique .ico file integrated with the game’s executable.

Executable Support – Runs as a .exe file using PyInstaller.

Clean UI Design – Simple, distraction-free, and enjoyable for all ages.

# 🕹️ Controls

W → Move Up

S → Move Down

A → Move Left

D → Move Right

P → Pause / Open Menu

Q → Quit Game

These easy-to-remember controls make the game highly accessible and smooth to play.

# 🧱 Game Mechanics

At launch, the snake appears at the center of the screen.
Randomly placed food items encourage the player to move strategically and grow the snake.
Each piece of food adds 10 points to the score and slightly increases speed, raising the difficulty as you progress.

If the snake collides with a wall or itself, a collision sound plays, and the game resets while preserving the high score.
Players can pause anytime using the P key and resume whenever they wish.

# 🧠 Technical Details

Programming Language: Python 3.12

Graphics Library: Turtle

Sound Library: Pygame

Executable Builder: PyInstaller

Platform: Windows

Version: 1.0.0

The game is lightweight and works seamlessly on almost any Windows system without requiring heavy resources or installations.

# 🧑‍💻 About the Developer

This game was designed and developed by Varun Kumar in 2022, during his final months of high school.
Back then, Varun was deeply curious about how games work — which led him to explore Python graphics and event handling.
Creating this Snake Game was one of his earliest projects that blended logic, design, and creativity.

Now a passionate developer and student of the University of Delhi, Varun continues to work on more advanced software projects, including AI systems, automation tools, and full-fledged applications.
This game remains a nostalgic reminder of where the journey began.

# 📂 Project Structure

The main project folder includes:

SnakeGames.py – Core Python file containing all logic and graphics.

SnakeIcon.ico – Game icon file used in the executable.

snakeBGMusic.mp3 – Background music track during gameplay.

snakeEatSound.mp3 – Sound played when the snake eats food.

snakeCollisionSound.mp3 – Sound triggered upon collision/game over.

dist/SnakeGames.exe – Final compiled game executable.

All components work together to deliver a smooth and cohesive gaming experience.

# ⚙️ How to Run or Build

To play the game, ensure you have Python 3.12 and required libraries installed.

Install dependencies using:

pip install pygame
pip install pillow


Run the game directly by executing:

python SnakeGames.py


To create your own executable version, use this command:

python -m PyInstaller --onefile --noconsole --icon="SnakeIcon.ico" "SnakeGames.py"


After building, open the dist folder to find your .exe file and play instantly.

# 🏆 Future Enhancements (Planned for v1.1.0)

Save and Load High Score System

Custom Themes (Dark, Light, Neon)

Power-ups & Bonus Food Items

Level-Based Progression

Android Version (Mobile Port)

Volume and Music Control Options

These additions will bring new layers of engagement and personalization to future releases.

# 💬 Feedback

If you enjoyed playing the game or found it interesting from a development perspective, feel free to share your feedback or suggestions.
You can open an issue or leave a comment on GitHub — every piece of input helps in making the next version even better.

Don’t forget to ⭐ star the repository if you liked this project — it truly motivates continued work and updates.

# 🐍 Developed and Designed with ❤️ by Varun Kumar

Version: 1.0.0
Created: 2022 (During 12th Grade)
Institution: University of Delhi
Language: Python
