"""
NOTE:
A separate copy of the original project is used for creating the executable (.exe) file.
All necessary files — including the .py scripts, .mp3 sound files, and the .ico icon —
are stored together inside a single dedicated folder.

This complete folder is then used to build and package the game into an application (.exe).
"""


import turtle as ttl
import time
import random
import pygame
import tkinter
import sys  # for clean exit

# === CONFIG ===
DELAY = 0.1
SPEED_INCREMENT = 0.005
SEGMENT_SIZE = 20

BACKGROUND_MUSIC = r"File's Path\snakeBGMusic.mp3"        # Replace With the Path where you saved the mp3 file on your system
EAT_SOUND = r"File's Path\snakeEatSound.mp3"              # Replace With the Path where you saved the mp3 file on your system
GAME_OVER_SOUND = r"File's Path\snakeCollisionSound.mp3"  # Replace With the Path where you saved the mp3 file on your system

# === GLOBAL STATE ===
in_menu = True
paused = False
sound_enabled = True
music_enabled = True
menu_buttons = []

# === SETUP ===
win = ttl.Screen()
win.title("🐍 Snake Game by Varun")
win.bgcolor("black")
win.setup(width=700, height=700)
win.tracer(0)

pygame.mixer.init()

# === BORDER ===
border = ttl.Turtle()
border.hideturtle()
border.pensize(3)
border.color("white")

def safe_clear(turtle_obj):
    try:
        turtle_obj.clear()
    except (tkinter.TclError, ttl.Terminator):
        pass

def draw_border():
    try:
        safe_clear(border)
        width = win.window_width()
        height = win.window_height()
        margin = 20
        border.penup()
        border.goto(-width / 2 + margin, height / 2 - margin)
        border.pendown()
        for _ in range(4):
            border.forward(width - 2 * margin)
            border.right(90)
        border.penup()
    except (tkinter.TclError, ttl.Terminator):
        pass

# === SCORE ===
score = 0
high_score = 0

pen = ttl.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0  High Score: 0", align="center", font=("Courier", 20, "bold"))

# === SOUND ===
def play_music():
    if music_enabled:
        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

def stop_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

def play_sound(sound_file):
    if sound_enabled:
        try:
            pygame.mixer.Sound(sound_file).play()
        except Exception:
            pass

# === MENU SYSTEM ===
menu_writer = ttl.Turtle()
menu_writer.hideturtle()
menu_writer.penup()

class MenuButton:
    def __init__(self, text, y, action):
        self.text = text
        self.y = y
        self.action = action
        self.is_hovered = False

    def draw(self):
        menu_writer.goto(0, self.y)
        menu_writer.color("lime" if self.is_hovered else "white")
        menu_writer.write(self.text, align="center", font=("Courier", 22, "bold"))

def start_game():
    global in_menu, score, paused, head, food, segments, delay
    in_menu = False
    paused = False
    safe_clear(menu_writer)
    win.onclick(None)
    win.bgcolor("black")
    draw_border()

    head = ttl.Turtle()
    head.shape("square")
    head.color("lime")
    head.penup()
    head.goto(0, 0)
    head.direction = "stop"

    food = ttl.Turtle()
    food.shape("circle")
    food.color("red")
    food.penup()
    food.goto(0, 100)

    segments = []
    score = 0
    delay = DELAY

    pen.clear()
    pen.write("Score: 0  High Score: 0", align="center", font=("Courier", 20, "bold"))

    play_music()
    run_game(head, food, segments)

def quit_game():
    global in_menu
    in_menu = True
    try:
        play_sound(GAME_OVER_SOUND)
        time.sleep(0.3)
        stop_music()
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except Exception:
        pass
    try:
        win.bye()
    except Exception:
        pass
    sys.exit(0)  # ensure clean exit of Python process

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    draw_menu()

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        play_music()
    else:
        stop_music()
    draw_menu()

def resume_game():
    global in_menu, paused
    if paused:
        in_menu = False
        paused = False
        safe_clear(menu_writer)
        run_game(head, food, segments)

def draw_menu():
    safe_clear(menu_writer)
    win.bgcolor("black")
    title = ttl.Turtle()
    title.hideturtle()
    title.color("white")
    title.penup()
    title.goto(0, 150)
    title.write("🐍 SNAKE GAME 🐍", align="center", font=("Courier", 32, "bold"))
    title.goto(0, 100)
    title.write("By Varun Kumar", align="center", font=("Courier", 16, "italic"))

    global menu_buttons
    menu_buttons = [
        MenuButton("Start Game", 40, start_game),
        MenuButton("Resume Game", -10, resume_game),
        MenuButton(f"Sound: {'On' if sound_enabled else 'Off'}", -60, toggle_sound),
        MenuButton(f"Music: {'On' if music_enabled else 'Off'}", -110, toggle_music),
        MenuButton("Exit", -160, quit_game),
    ]
    for b in menu_buttons:
        b.draw()

    win.onclick(menu_click_handler)
    win.cv.bind("<Motion>", lambda e: menu_hover_handler(e.x - win.window_width() / 2, win.window_height() / 2 - e.y))
    win.update()

def menu_click_handler(x, y):
    if not in_menu:
        return
    for b in menu_buttons:
        if b.y - 15 < y < b.y + 15:
            b.action()
            
def menu_hover_handler(x, y):
    if not in_menu:
        return
    for b in menu_buttons:
        b.is_hovered = b.y - 15 < y < b.y + 15
    safe_clear(menu_writer)
    for b in menu_buttons:
        b.draw()
    win.update()

# === GAME CONTROLS ===
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

def move():
    if head.direction == "up":
        head.sety(head.ycor() + SEGMENT_SIZE)
    elif head.direction == "down":
        head.sety(head.ycor() - SEGMENT_SIZE)
    elif head.direction == "left":
        head.setx(head.xcor() - SEGMENT_SIZE)
    elif head.direction == "right":
        head.setx(head.xcor() + SEGMENT_SIZE)

def pause_game():
    global paused, in_menu
    paused = True
    in_menu = True
    stop_music()
    draw_menu()

def run_game(head, food, segments):
    global score, high_score, delay
    win.listen()
    win.onkeypress(go_up, "w")
    win.onkeypress(go_down, "s")
    win.onkeypress(go_left, "a")
    win.onkeypress(go_right, "d")
    win.onkeypress(pause_game, "p")
    win.onkeypress(quit_game, "q")

    try:
        while not in_menu:
            if not win.cv.winfo_exists():
                break

            win.update()
            draw_border()

            width = win.window_width() // 2 - 30
            height = win.window_height() // 2 - 30

            # Border collision
            if (head.xcor() > width or head.xcor() < -width or
                    head.ycor() > height or head.ycor() < -height):
                stop_music()
                play_sound(GAME_OVER_SOUND)
                time.sleep(1)
                head.goto(0, 0)
                head.direction = "stop"
                for seg in segments:
                    seg.goto(1000, 1000)
                segments.clear()
                score = 0
                delay = DELAY
                pen.clear()
                pen.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 20, "bold"))
                play_music()

            # Food collision
            if head.distance(food) < 20:
                play_sound(EAT_SOUND)
                x = random.randint(-width + 20, width - 20)
                y = random.randint(-height + 20, height - 20)
                food.goto(x, y)
                new_segment = ttl.Turtle()
                new_segment.speed(0)
                new_segment.shape("square")
                new_segment.color("green")
                new_segment.penup()
                segments.append(new_segment)
                delay = max(0.02, delay - SPEED_INCREMENT)
                score += 10
                if score > high_score:
                    high_score = score
                pen.clear()
                pen.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 20, "bold"))

            # Move segments
            for i in range(len(segments) - 1, 0, -1):
                x = segments[i - 1].xcor()
                y = segments[i - 1].ycor()
                segments[i].goto(x, y)
            if segments:
                segments[0].goto(head.xcor(), head.ycor())

            move()

            # Self-collision
            for seg in segments:
                if seg.distance(head) < 20:
                    stop_music()
                    play_sound(GAME_OVER_SOUND)
                    time.sleep(1)
                    head.goto(0, 0)
                    head.direction = "stop"
                    for s in segments:
                        s.goto(1000, 1000)
                    segments.clear()
                    score = 0
                    delay = DELAY
                    pen.clear()
                    pen.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 20, "bold"))
                    play_music()
                    break

            time.sleep(delay)
    except (tkinter.TclError, ttl.Terminator):
        pass  # graceful exit when window closed

# === START ===
draw_menu()
win.mainloop()

