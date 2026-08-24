"""
Pac-Man clone written in Python using Pygame.

Controls:
    A / S / D / W - Move Pac-Man (Left / Down / Right / Up)
    P             - Pause / Unpause
    Q             - Quit
    R             - Restart after game over / win
    Mouse click or S/W to navigate the Start Menu, D or Enter to select

Run with:
    python pacman.py
"""

import sys
import math
import random
import pygame

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# ----------------------------------------------------------------------
# Configuration & Constants
# ----------------------------------------------------------------------
TILE = 24                      # Base size of one cell in pixels
FPS = 60
PACMAN_SPEED = 2.0
GHOST_SPEED = 2.0
FRIGHTENED_SPEED = 1.0

BLACK = (0, 0, 0)
BLUE = (33, 33, 222)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 184, 255)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
FRIGHTENED_COLOR = (33, 33, 222)
DOT_COLOR = (255, 184, 174)
TEXT_COLOR = (255, 255, 255)
GREY = (120, 120, 120)

# WASD Controls
KEY_DIRECTIONS = {
    pygame.K_a: (-1, 0),   # Left
    pygame.K_s: (0, 1),    # Down
    pygame.K_d: (1, 0),    # Right
    pygame.K_w: (0, -1),   # Up
}

MAZE = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #      # ##.######",
    "      .   #  GGG #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#...##................##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....P.....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#............##............#",
    "############################",
]

ROWS = len(MAZE)
COLS = max(len(r) for r in MAZE)
BASE_WIDTH = COLS * TILE
BASE_HEIGHT = ROWS * TILE + 60


def cell_center(col, row):
    return col * TILE + TILE // 2, row * TILE + TILE // 2


def is_wall(col, row, is_ghost=False):
    if row < 0 or row >= ROWS:
        return False
    if col < 0 or col >= COLS:
        return False
    line = MAZE[row]
    if col >= len(line):
        return False
    ch = line[col]
    if is_ghost and ch == '-':
        return False  # Ghosts can pass through the ghost house door
    return ch in ('#', '-')


# ----------------------------------------------------------------------
# Sound Manager
# ----------------------------------------------------------------------
class SoundManager:
    def __init__(self):
        self.enabled = False
        self.music_on = True
        self.sounds = {}
        self.music_channel = None
        self._music = None

        try:
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False
            return

        if not NUMPY_AVAILABLE:
            self.enabled = False
            return

        try:
            self.sounds["dot"] = self._tone(440, 0.05, volume=0.2)
            self.sounds["power"] = self._tone(220, 0.2, volume=0.3, wave="square")
            self.sounds["death"] = self._tone(150, 0.5, volume=0.3, wave="sawtooth", descend=True)
            self.sounds["eat_ghost"] = self._tone(660, 0.2, volume=0.3, wave="square")
            self.sounds["win"] = self._tone(880, 0.4, volume=0.3)
            self._music = self._build_music_loop()
        except Exception:
            self.enabled = False

    def _tone(self, freq, duration, volume=0.3, wave="sine", descend=False):
        sample_rate = 44100
        n = int(sample_rate * duration)
        t = np.linspace(0, duration, n, False)
        if descend:
            freqs = np.linspace(freq, freq * 0.4, n)
            phase = np.cumsum(freqs) / sample_rate
        else:
            phase = freq * t

        if wave == "square":
            wave_data = np.sign(np.sin(2 * np.pi * phase))
        elif wave == "sawtooth":
            wave_data = 2 * (phase - np.floor(0.5 + phase))
        else:
            wave_data = np.sin(2 * np.pi * phase)

        fade = min(200, n // 4)
        envelope = np.ones(n)
        if fade > 0:
            envelope[:fade] = np.linspace(0, 1, fade)
            envelope[-fade:] = np.linspace(1, 0, fade)
        wave_data = wave_data * envelope * volume

        audio = np.repeat((wave_data * 32767).astype(np.int16).reshape(-1, 1), 2, axis=1)
        audio = np.ascontiguousarray(audio)
        return pygame.sndarray.make_sound(audio)

    def _build_music_loop(self):
        sample_rate = 44100
        notes = [330, 392, 440, 392]
        duration = 0.18
        n_per_note = int(sample_rate * duration)
        chunks = []
        for freq in notes:
            t = np.linspace(0, duration, n_per_note, False)
            w = np.sin(2 * np.pi * freq * t)
            fade = n_per_note // 6
            env = np.ones(n_per_note)
            if fade > 0:
                env[:fade] = np.linspace(0, 1, fade)
                env[-fade:] = np.linspace(1, 0, fade)
            chunks.append(w * env * 0.1)
        wave_data = np.concatenate(chunks)
        audio = np.repeat((wave_data * 32767).astype(np.int16).reshape(-1, 1), 2, axis=1)
        audio = np.ascontiguousarray(audio)
        return pygame.sndarray.make_sound(audio)

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def start_music(self):
        if self.enabled and self.music_on and self._music is not None:
            if self.music_channel is None or not self.music_channel.get_busy():
                self.music_channel = self._music.play(loops=-1)

    def stop_music(self):
        if self.music_channel is not None:
            self.music_channel.stop()
            self.music_channel = None

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            self.start_music()
        else:
            self.stop_music()
        return self.music_on


# ----------------------------------------------------------------------
# Entities
# ----------------------------------------------------------------------
class Entity:
    def __init__(self, col, row, speed, color):
        self.col = col
        self.row = row
        self.x, self.y = cell_center(col, row)
        self.speed = speed
        self.base_speed = speed
        self.color = color
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.radius = TILE // 2 - 2

    @property
    def grid_pos(self):
        return int(self.x // TILE), int(self.y // TILE)

    def at_center(self):
        cx, cy = cell_center(*self.grid_pos)
        return abs(self.x - cx) < self.speed and abs(self.y - cy) < self.speed

    def can_move(self, direction, is_ghost=False):
        if direction == (0, 0):
            return True
        col, row = self.grid_pos
        dcol, drow = direction
        return not is_wall(col + dcol, row + drow, is_ghost=is_ghost)

    def snap_to_grid(self):
        cx, cy = cell_center(*self.grid_pos)
        self.x, self.y = cx, cy

    def wrap(self):
        max_x = COLS * TILE
        if self.x < 0:
            self.x += max_x
        elif self.x >= max_x:
            self.x -= max_x


class PacMan(Entity):
    def __init__(self, col, row):
        super().__init__(col, row, PACMAN_SPEED, YELLOW)
        self.mouth_angle = 0
        self.mouth_dir = 1
        self.alive = True

    def update(self):
        if self.next_direction != (0, 0):
            if self.direction == (0, 0):
                if self.can_move(self.next_direction):
                    self.direction = self.next_direction
            elif self.next_direction == (-self.direction[0], -self.direction[1]):
                self.direction = self.next_direction
            elif self.at_center() and self.can_move(self.next_direction):
                self.snap_to_grid()
                self.direction = self.next_direction

        if not self.can_move(self.direction) and self.at_center():
            self.direction = (0, 0)
            self.snap_to_grid()

        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        self.wrap()

        if self.direction != (0, 0):
            self.mouth_angle += self.mouth_dir * 4
            if self.mouth_angle >= 45 or self.mouth_angle <= 5:
                self.mouth_dir *= -1

    def draw(self, screen):
        angle_map = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}
        base_angle = angle_map.get(self.direction, 0)

        start_angle = base_angle + self.mouth_angle / 2
        end_angle = base_angle + 360 - self.mouth_angle / 2

        points = [(int(self.x), int(self.y))]
        steps = 20
        for i in range(steps + 1):
            a = math.radians(start_angle + (end_angle - start_angle) * i / steps)
            px = int(self.x + self.radius * math.cos(a))
            py = int(self.y - self.radius * math.sin(a))
            points.append((px, py))

        if len(points) > 2:
            pygame.draw.polygon(screen, self.color, points)


GHOST_NAMES = ["Blinky", "Pinky", "Inky", "Clyde"]
GHOST_COLORS = [RED, PINK, CYAN, ORANGE]


class Ghost(Entity):
    def __init__(self, col, row, color, name, delay=0):
        super().__init__(col, row, GHOST_SPEED, color)
        self.name = name
        self.frightened = False
        self.frightened_timer = 0
        self.home = (col, row)
        self.eaten = False
        self.in_house = True
        self.house_delay = delay
        self.house_timer = delay
        self.exit_target = (13, 11)  # Target outside the house door

    def reset_state(self):
        self.x, self.y = cell_center(*self.home)
        self.direction = (0, 0)
        self.frightened = False
        self.eaten = False
        self.in_house = True
        self.house_timer = self.house_delay

    def choose_direction(self, target):
        col, row = self.grid_pos
        options = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        reverse = (-self.direction[0], -self.direction[1])

        valid = [d for d in options if self.can_move(d, is_ghost=True) and d != reverse]
        if not valid:
            valid = [d for d in options if self.can_move(d, is_ghost=True)]
        if not valid:
            return (0, 0)

        if self.frightened and not self.eaten:
            return random.choice(valid)

        def dist(d):
            nx, ny = col + d[0], row + d[1]
            return (nx - target[0]) ** 2 + (ny - target[1]) ** 2

        valid.sort(key=dist)
        return valid[0]

    def get_target(self, pacman, blinky_pos):
        if self.in_house:
            return self.exit_target
        if self.eaten:
            return self.home
        if self.frightened:
            return (random.randint(0, COLS), random.randint(0, ROWS))

        pac_col, pac_row = pacman.grid_pos
        p_dir_x, p_dir_y = pacman.direction

        if self.name == "Blinky":
            return pac_col, pac_row
        elif self.name == "Pinky":
            return pac_col + p_dir_x * 4, pac_row + p_dir_y * 4
        elif self.name == "Inky":
            pivot_x = pac_col + p_dir_x * 2
            pivot_y = pac_row + p_dir_y * 2
            b_x, b_y = blinky_pos
            vec_x = pivot_x - b_x
            vec_y = pivot_y - b_y
            return pivot_x + vec_x, pivot_y + vec_y
        elif self.name == "Clyde":
            col, row = self.grid_pos
            distance = math.hypot(pac_col - col, pac_row - row)
            return (pac_col, pac_row) if distance > 8 else (0, ROWS)

        return pac_col, pac_row

    def update(self, pacman, blinky_pos):
        # Manage Ghost House Wait & Exit Logic
        if self.in_house:
            if self.house_timer > 0:
                self.house_timer -= 1
                return
            target = self.exit_target
            if self.grid_pos == self.exit_target or self.row <= 11:
                self.in_house = False
        else:
            target = self.get_target(pacman, blinky_pos)

        if self.at_center() or self.direction == (0, 0):
            self.snap_to_grid()
            self.direction = self.choose_direction(target)

        speed = FRIGHTENED_SPEED if (self.frightened and not self.eaten) else self.base_speed
        if self.eaten:
            speed = self.base_speed * 1.5

        self.x += self.direction[0] * speed
        self.y += self.direction[1] * speed
        self.wrap()

        if self.frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.frightened = False

        if self.eaten and self.grid_pos == self.home:
            self.eaten = False
            self.frightened = False
            self.in_house = True
            self.house_timer = 30

    def draw(self, screen):
        color = self.color
        if self.eaten:
            color = (60, 60, 60)
        elif self.frightened:
            color = WHITE if (self.frightened_timer // 10) % 2 == 1 and self.frightened_timer < 120 else FRIGHTENED_COLOR

        r = self.radius
        ix, iy = int(self.x), int(self.y)

        pygame.draw.circle(screen, color, (ix, iy - 2), r)
        pygame.draw.rect(screen, color, (ix - r, iy - 2, r * 2, r + 2))

        foot_w = r * 2 / 3
        for i in range(3):
            fx = ix - r + i * foot_w
            pygame.draw.polygon(
                screen, color,
                [(fx, iy + r), (fx + foot_w / 2, iy + r - 5), (fx + foot_w, iy + r)]
            )

        eye_offset = r / 2.2
        pygame.draw.circle(screen, WHITE, (int(ix - eye_offset), iy - 4), 4)
        pygame.draw.circle(screen, WHITE, (int(ix + eye_offset), iy - 4), 4)

        pupil_dx = self.direction[0] * 2
        pupil_dy = self.direction[1] * 2
        pygame.draw.circle(screen, (0, 0, 150),
                           (int(ix - eye_offset + pupil_dx), int(iy - 4 + pupil_dy)), 2)
        pygame.draw.circle(screen, (0, 0, 150),
                           (int(ix + eye_offset + pupil_dx), int(iy - 4 + pupil_dy)), 2)


# ----------------------------------------------------------------------
# Game States & Main Logic
# ----------------------------------------------------------------------
STATE_MENU = "menu"
STATE_PLAYING = "playing"


class Button:
    def __init__(self, rect, label_fn):
        self.rect = pygame.Rect(rect)
        self.label_fn = label_fn

    def draw(self, screen, font, selected):
        color = YELLOW if selected else WHITE
        border_color = YELLOW if selected else GREY
        pygame.draw.rect(screen, border_color, self.rect, width=3, border_radius=8)
        text = font.render(self.label_fn(), True, color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
        self.surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        pygame.display.set_caption("Pac-Man Clone")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)
        self.menu_font = pygame.font.SysFont("arial", 26, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)

        self.sound = SoundManager()
        self.state = STATE_MENU
        self.menu_index = 0

        cx = BASE_WIDTH // 2
        cy = BASE_HEIGHT // 2
        self.menu_buttons = [
            Button((cx - 110, cy - 60, 220, 50), lambda: "Start"),
            Button((cx - 110, cy + 10, 220, 50), self._music_label),
            Button((cx - 110, cy + 80, 220, 50), lambda: "Exit"),
        ]

        self.reset()

    def _music_label(self):
        return f"Music: {'On' if self.sound.music_on else 'Off'}"

    def reset(self):
        self.dots = set()
        self.power_pellets = set()
        pac_start = (14, 26)
        ghost_spawns = []

        for row, line in enumerate(MAZE):
            for col, ch in enumerate(line):
                if ch == '.':
                    self.dots.add((col, row))
                elif ch == 'o':
                    self.power_pellets.add((col, row))
                elif ch == 'P':
                    pac_start = (col, row)
                elif ch == 'G':
                    ghost_spawns.append((col, row))

        if not ghost_spawns:
            ghost_spawns = [(13, 14), (14, 14), (15, 14), (16, 14)]

        delays = [0, 120, 240, 360]  # Staggered entry out of ghost house
        self.pacman = PacMan(*pac_start)
        self.ghosts = [
            Ghost(ghost_spawns[i % len(ghost_spawns)][0],
                  ghost_spawns[i % len(ghost_spawns)][1],
                  GHOST_COLORS[i], GHOST_NAMES[i], delay=delays[i])
            for i in range(4)
        ]

        self.score = 0
        self.lives = 3
        self.paused = False
        self.game_over = False
        self.won = False

    def start_game(self):
        self.reset()
        self.state = STATE_PLAYING
        self.sound.start_music()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def scale_mouse_pos(self, pos):
        win_w, win_h = self.window.get_size()
        scale = min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT)
        off_x = (win_w - BASE_WIDTH * scale) / 2
        off_y = (win_h - BASE_HEIGHT * scale) / 2

        x = (pos[0] - off_x) / scale
        y = (pos[1] - off_y) / scale
        return int(x), int(y)

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.quit_game()
            elif event.key == pygame.K_s:
                self.menu_index = (self.menu_index + 1) % len(self.menu_buttons)
            elif event.key == pygame.K_w:
                self.menu_index = (self.menu_index - 1) % len(self.menu_buttons)
            elif event.key in (pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                self.activate_menu_item(self.menu_index)

        elif event.type == pygame.MOUSEMOTION:
            mpos = self.scale_mouse_pos(event.pos)
            for i, btn in enumerate(self.menu_buttons):
                if btn.is_hovered(mpos):
                    self.menu_index = i

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mpos = self.scale_mouse_pos(event.pos)
            for i, btn in enumerate(self.menu_buttons):
                if btn.is_hovered(mpos):
                    self.activate_menu_item(i)

    def activate_menu_item(self, index):
        if index == 0:
            self.start_game()
        elif index == 1:
            self.sound.toggle_music()
        elif index == 2:
            self.quit_game()

    def handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.quit_game()
            elif event.key == pygame.K_p:
                self.paused = not self.paused
            elif event.key == pygame.K_r and (self.game_over or self.won):
                self.state = STATE_MENU
                self.sound.stop_music()
            elif event.key in KEY_DIRECTIONS:
                self.pacman.next_direction = KEY_DIRECTIONS[event.key]

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if self.state == STATE_MENU:
                self.handle_menu_input(event)
            else:
                self.handle_playing_input(event)

    def update(self):
        if self.state != STATE_PLAYING or self.paused or self.game_over or self.won:
            return

        self.pacman.update()

        pos = self.pacman.grid_pos
        if pos in self.dots:
            self.dots.discard(pos)
            self.score += 10
            self.sound.play("dot")
        if pos in self.power_pellets:
            self.power_pellets.discard(pos)
            self.score += 50
            self.sound.play("power")
            for g in self.ghosts:
                if not g.eaten:
                    g.frightened = True
                    g.frightened_timer = 360

        if not self.dots and not self.power_pellets:
            self.won = True
            self.sound.play("win")

        blinky_pos = self.ghosts[0].grid_pos
        for g in self.ghosts:
            g.update(self.pacman, blinky_pos)

        for g in self.ghosts:
            if abs(g.x - self.pacman.x) < TILE * 0.6 and abs(g.y - self.pacman.y) < TILE * 0.6:
                if g.frightened and not g.eaten:
                    g.eaten = True
                    g.frightened = False
                    self.score += 200
                    self.sound.play("eat_ghost")
                elif not g.eaten and not g.in_house:
                    self.sound.play("death")
                    self.lose_life()
                    break

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            pac_start = (14, 26)
            for row, line in enumerate(MAZE):
                for col, ch in enumerate(line):
                    if ch == 'P':
                        pac_start = (col, row)

            self.pacman.col, self.pacman.row = pac_start
            self.pacman.x, self.pacman.y = cell_center(*pac_start)
            self.pacman.direction = (0, 0)
            self.pacman.next_direction = (0, 0)

            for g in self.ghosts:
                g.reset_state()

    def draw_maze(self):
        for row, line in enumerate(MAZE):
            for col, ch in enumerate(line):
                x, y = col * TILE, row * TILE
                if ch == '#':
                    pygame.draw.rect(self.surface, BLUE, (x, y, TILE, TILE), border_radius=4)
                elif ch == '-':
                    pygame.draw.rect(self.surface, PINK, (x, y + TILE // 2 - 2, TILE, 4))

        for (col, row) in self.dots:
            cx, cy = cell_center(col, row)
            pygame.draw.circle(self.surface, DOT_COLOR, (cx, cy), 3)

        for (col, row) in self.power_pellets:
            cx, cy = cell_center(col, row)
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                pygame.draw.circle(self.surface, DOT_COLOR, (cx, cy), 7)

    def draw_hud(self):
        y = ROWS * TILE
        pygame.draw.rect(self.surface, BLACK, (0, y, COLS * TILE, 60))
        score_surf = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.surface.blit(score_surf, (10, y + 18))

        lives_text = self.font.render("Lives:", True, TEXT_COLOR)
        self.surface.blit(lives_text, (COLS * TILE - 190, y + 18))
        for i in range(self.lives):
            pygame.draw.circle(self.surface, YELLOW, (COLS * TILE - 90 + i * 26, y + 30), 8)

        if self.paused:
            self.draw_center_text("PAUSED", YELLOW)
        elif self.game_over:
            self.draw_center_text("GAME OVER - Press R for Menu", RED)
        elif self.won:
            self.draw_center_text("YOU WIN! - Press R for Menu", (0, 255, 0))

    def draw_center_text(self, text, color):
        surf = self.big_font.render(text, True, color)
        rect = surf.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))
        bg = pygame.Surface((rect.width + 20, rect.height + 20))
        bg.set_alpha(200)
        bg.fill(BLACK)
        self.surface.blit(bg, (rect.x - 10, rect.y - 10))
        self.surface.blit(surf, rect)

    def draw_menu(self):
        self.surface.fill(BLACK)
        title = self.big_font.render("PAC-MAN", True, YELLOW)
        title_rect = title.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2 - 140))
        self.surface.blit(title, title_rect)

        for i, btn in enumerate(self.menu_buttons):
            btn.draw(self.surface, self.menu_font, i == self.menu_index)

        hint = self.small_font.render(
            "Move: A S D W   |   Pause: P   |   Quit: Q   |   Menu: S/W to navigate, D/Enter to select",
            True, GREY,
        )
        hint_rect = hint.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT - 30))
        self.surface.blit(hint, hint_rect)

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
        else:
            self.surface.fill(BLACK)
            self.draw_maze()
            self.pacman.draw(self.surface)
            for g in self.ghosts:
                g.draw(self.surface)
            self.draw_hud()

        win_w, win_h = self.window.get_size()
        scale = min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT)
        scaled_w = int(BASE_WIDTH * scale)
        scaled_h = int(BASE_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(self.surface, (scaled_w, scaled_h))
        self.window.fill(BLACK)
        self.window.blit(scaled_surface, ((win_w - scaled_w) // 2, (win_h - scaled_h) // 2))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()