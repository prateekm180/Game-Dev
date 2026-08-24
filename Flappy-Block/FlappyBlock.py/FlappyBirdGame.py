import turtle
import time
import random

# --- Setup Functions ---
def setup_screen():
    win = turtle.Screen()
    win.title("🐥 Flappy Bird (Turtle Edition)")
    win.bgcolor("sky blue")
    win.setup(width=600, height=600)
    win.tracer(0)
    return win


def setup_bird():
    bird = turtle.Turtle()
    bird.shape("circle")
    bird.color("yellow")
    bird.penup()
    bird.goto(-150, 0)
    bird.dy = 0
    return bird


def setup_score_display():
    score_display = turtle.Turtle()
    score_display.hideturtle()
    score_display.penup()
    score_display.color("black")
    score_display.goto(0, 260)
    return score_display


def create_pipes(pipes, pipe_gap):
    y = random.randint(-150, 150)

    # Top pipe
    top_pipe = turtle.Turtle()
    top_pipe.shape("square")
    top_pipe.color("green")
    top_pipe.shapesize(stretch_wid=20, stretch_len=2)
    top_pipe.penup()
    top_pipe.goto(300, y + pipe_gap + 200)
    pipes.append(top_pipe)

    # Bottom pipe
    bottom_pipe = turtle.Turtle()
    bottom_pipe.shape("square")
    bottom_pipe.color("green")
    bottom_pipe.shapesize(stretch_wid=20, stretch_len=2)
    bottom_pipe.penup()
    bottom_pipe.goto(300, y - pipe_gap - 200)
    pipes.append(bottom_pipe)


def update_score(score, score_display):
    score_display.clear()
    score_display.write(f"Score: {score}", align="center", font=("Courier", 24, "bold"))


def show_game_over(win, score_display, score):
    score_display.goto(0, 0)
    score_display.write(
        f"GAME OVER!\nFinal Score: {score}\nPress 'R' to Restart\nPress 'Q' to Quit",
        align="center",
        font=("Courier", 24, "bold")
    )


def show_start_screen(win):
    title = turtle.Turtle()
    title.hideturtle()
    title.color("black")
    title.penup()
    title.goto(0, 0)
    title.write(
        "🐥 FLAPPY BIRD 🐥\nPress SPACE to Start",
        align="center",
        font=("Courier", 24, "bold")
    )
    win.update()
    return title


# --- Main Game Function ---
def play_game():
    win = setup_screen()
    score_display = setup_score_display()

    # --- Start screen ---
    title = show_start_screen(win)
    started = False

    def start_game():
        nonlocal started
        title.clear()
        started = True

    win.listen()
    win.onkeypress(start_game, "space")

    while not started:
        win.update()
        time.sleep(0.01)

    # --- Initialize game variables ---
    bird = setup_bird()
    gravity = -0.25
    pipe_gap = 160
    pipe_speed = 3.5
    pipe_frequency = 90
    frame = 0
    score = 0
    pipes = []
    game_over = False

    def move_up():
        bird.dy = 5

    win.onkeypress(move_up, "space")
    win.listen()

    # --- Game Loop ---
    try:
        while not game_over:
            win.update()
            time.sleep(0.017)

            # Bird physics
            bird.dy += gravity
            bird.sety(bird.ycor() + bird.dy)

            # Collision with top/bottom walls
            if bird.ycor() < -290 or bird.ycor() > 290:
                game_over = True
                break

            # Pipe creation
            frame += 1
            if frame % pipe_frequency == 0:
                create_pipes(pipes, pipe_gap)

            # Move pipes
            for pipe in pipes:
                pipe.setx(pipe.xcor() - pipe_speed)

            # Collision detection
            for pipe in pipes:
                if (pipe.xcor() - 25 < bird.xcor() < pipe.xcor() + 25 and
                    abs(bird.ycor() - pipe.ycor()) < 180):
                    game_over = True
                    break

            # Remove old pipes and update score
            new_pipes = []
            for pipe in pipes:
                if pipe.xcor() > -320:
                    new_pipes.append(pipe)
                else:
                    if pipe.ycor() > 0:  # Count only once per pair
                        score += 1
                        update_score(score, score_display)
            pipes = new_pipes

    except turtle.Terminator:
        print("Game closed manually.")
        return

    # --- Game Over ---
    show_game_over(win, score_display, score)

    # Restart and Quit mechanisms (safe)
    def restart_game():
        try:
            win.bye()  # Safely close current window
        except:
            pass
        time.sleep(0.5)
        play_game()  # Start fresh

    def quit_game():
        try:
            win.bye()
        except:
            pass
        print("Thanks for playing 🐥!")

    win.onkeypress(restart_game, "r")
    win.onkeypress(quit_game, "q")
    win.listen()
    win.mainloop()


# --- Run the Game ---
play_game()
