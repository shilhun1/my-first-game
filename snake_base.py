import pygame
import random
import sys
import os

# ── 1. 상수 설정 ──────────────────────────────────
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS_BASE = 10
SCORE_LIMIT = 250

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
LINE_COLOR = (50, 50, 50)
RED = (220, 50, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
NEON_GREEN = (57, 255, 20)
GREEN = (50, 200, 50)
PORTAL_A_COLOR = (0, 191, 255)
PORTAL_B_COLOR = (255, 140, 0)

TITLE, PLAYING, GAME_OVER, CLEAR = "TITLE", "PLAYING", "GAME_OVER", "CLEAR"

# ── 2. 초기화 ─────────────────────────────────────
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abyss Snake")
clock = pygame.time.Clock()

font = pygame.font.SysFont("malgungothic, applegothic", 30)
font_big = pygame.font.SysFont("malgungothic, applegothic", 70)

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# ── 3. 경로 찾기 유틸 ─────────────────────────────
def first_existing_dir(candidates):
    for path in candidates:
        norm = os.path.normpath(path)
        if os.path.isdir(norm):
            return norm
    return os.path.normpath(candidates[0])

def find_file_by_prefix(folder, prefixes, exts=None):
    if not os.path.isdir(folder):
        return None

    if exts is None:
        exts = [".png", ".wav", ".mp3", ".ogg"]

    try:
        files = os.listdir(folder)
    except Exception:
        return None

    lowered = [(f, f.lower()) for f in files]

    for prefix in prefixes:
        prefix = prefix.lower()
        for original, lower_name in lowered:
            if lower_name.startswith(prefix) and any(lower_name.endswith(ext) for ext in exts):
                return os.path.join(folder, original)

    for prefix in prefixes:
        prefix = prefix.lower()
        for original, lower_name in lowered:
            if prefix in lower_name and any(lower_name.endswith(ext) for ext in exts):
                return os.path.join(folder, original)

    return None

# ── 4. 에셋 폴더 자동 탐색 ─────────────────────────
# 1순위: 프로젝트 폴더 내부
# 2순위: OneDrive Desktop\Graphics 내부
SNAKE_ASSETS_DIR = first_existing_dir([
    os.path.join(BASE_DIR, "abyss_snake_assets", "Graphics"),
    os.path.join(BASE_DIR, "Graphics", "abyss_snake_assets", "Graphics"),
    os.path.join(BASE_DIR, "..", "..", "..", "Desktop", "Graphics", "abyss_snake_assets", "Graphics"),
])

PORTAL_ASSETS_DIR = first_existing_dir([
    os.path.join(BASE_DIR, "abyss_portal_anim", "Graphics"),
    os.path.join(BASE_DIR, "Graphics", "abyss_portal_anim", "Graphics"),
    os.path.join(BASE_DIR, "..", "..", "..", "Desktop", "Graphics", "abyss_portal_anim", "Graphics"),
])

SOUND_DIR = first_existing_dir([
    os.path.join(BASE_DIR, "snake_sound"),
    os.path.join(BASE_DIR, "Graphics", "snake_sound"),
    os.path.join(BASE_DIR, "..", "..", "..", "Desktop", "Graphics", "snake_sound"),
])

print("[snake assets dir]", SNAKE_ASSETS_DIR)
print("[portal assets dir]", PORTAL_ASSETS_DIR)
print("[sound dir]", SOUND_DIR)

# ── 5. 파일 로드 ─────────────────────────────────
def load_image(folder, filename):
    path = os.path.join(folder, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    except Exception as e:
        print(f"[이미지 로드 실패] {path} / {e}")
        return None

def load_sound(path):
    try:
        if path and os.path.exists(path):
            return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"[사운드 로드 실패] {path} / {e}")
    return None

# snake head
img_head_up = load_image(SNAKE_ASSETS_DIR, "head_up.png")
img_head_down = load_image(SNAKE_ASSETS_DIR, "head_down.png")
img_head_left = load_image(SNAKE_ASSETS_DIR, "head_left.png")
img_head_right = load_image(SNAKE_ASSETS_DIR, "head_right.png")

# snake body
img_body_v = load_image(SNAKE_ASSETS_DIR, "body_vertical.png")
img_body_h = load_image(SNAKE_ASSETS_DIR, "body_horizontal.png")
img_body_bl = load_image(SNAKE_ASSETS_DIR, "body_bottomleft.png")
img_body_br = load_image(SNAKE_ASSETS_DIR, "body_bottomright.png")
img_body_tl = load_image(SNAKE_ASSETS_DIR, "body_topleft.png")
img_body_tr = load_image(SNAKE_ASSETS_DIR, "body_topright.png")

# snake tail
img_tail_up = load_image(SNAKE_ASSETS_DIR, "tail_up.png")
img_tail_down = load_image(SNAKE_ASSETS_DIR, "tail_down.png")
img_tail_left = load_image(SNAKE_ASSETS_DIR, "tail_left.png")
img_tail_right = load_image(SNAKE_ASSETS_DIR, "tail_right.png")

# apples
img_apple = load_image(SNAKE_ASSETS_DIR, "apple.png")
img_apple_blue = load_image(SNAKE_ASSETS_DIR, "apple_blue.png")
img_apple_yellow = load_image(SNAKE_ASSETS_DIR, "apple_yellow.png")

# eat animation
eat_frames = [load_image(SNAKE_ASSETS_DIR, f"eat_{i}.png") for i in range(5)]

# portal animation
portal_a_frames = [load_image(PORTAL_ASSETS_DIR, f"portal_entrance_{i}.png") for i in range(4)]
portal_b_frames = [load_image(PORTAL_ASSETS_DIR, f"portal_exit_{i}.png") for i in range(4)]

# sounds
eat_sound_path = find_file_by_prefix(SOUND_DIR, ["eatsound", "eat"])
die_sound_path = find_file_by_prefix(SOUND_DIR, ["diesound", "die"])
bgm_path = find_file_by_prefix(SOUND_DIR, ["nastelbom", "music", "bgm"], exts=[".mp3", ".ogg", ".wav"])

eat_sound = load_sound(eat_sound_path)
die_sound = load_sound(die_sound_path)

if bgm_path:
    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"[BGM 로드 실패] {bgm_path} / {e}")

# ── 6. 객체 클래스 ────────────────────────────────
class Snake:
    def __init__(self):
        self.lives = 3
        self.reset()

    def reset(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
        self.eat_anim_timer = 0

    def update(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        self.body.insert(0, (head_x + dx, head_y + dy))

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def draw(self):
        for i, segment in enumerate(self.body):
            gx, gy = segment
            rect = pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            image_to_draw = None
            fallback_color = GREEN

            if i == 0:
                fallback_color = NEON_GREEN

                if self.eat_anim_timer > 0:
                    frame_idx = min(4, (10 - self.eat_anim_timer) // 2)
                    base_img = eat_frames[frame_idx] if frame_idx < len(eat_frames) else None

                    if base_img:
                        if self.direction == (1, 0):
                            image_to_draw = base_img
                        elif self.direction == (-1, 0):
                            image_to_draw = pygame.transform.flip(base_img, True, False)
                        elif self.direction == (0, -1):
                            image_to_draw = pygame.transform.rotate(base_img, 90)
                        elif self.direction == (0, 1):
                            image_to_draw = pygame.transform.rotate(base_img, -90)

                if image_to_draw is None:
                    if self.direction == (0, -1):
                        image_to_draw = img_head_up
                    elif self.direction == (0, 1):
                        image_to_draw = img_head_down
                    elif self.direction == (-1, 0):
                        image_to_draw = img_head_left
                    elif self.direction == (1, 0):
                        image_to_draw = img_head_right

            elif i == len(self.body) - 1:
                prev = self.body[i - 1]
                p_v = (gx - prev[0], gy - prev[1])

                if p_v == (0, -1):
                    image_to_draw = img_tail_up
                elif p_v == (0, 1):
                    image_to_draw = img_tail_down
                elif p_v == (-1, 0):
                    image_to_draw = img_tail_left
                elif p_v == (1, 0):
                    image_to_draw = img_tail_right

            else:
                prev, nxt = self.body[i - 1], self.body[i + 1]
                p_v = (prev[0] - gx, prev[1] - gy)
                n_v = (nxt[0] - gx, nxt[1] - gy)

                if (p_v == (-1, 0) and n_v == (1, 0)) or (p_v == (1, 0) and n_v == (-1, 0)):
                    image_to_draw = img_body_h
                elif (p_v == (0, -1) and n_v == (0, 1)) or (p_v == (0, 1) and n_v == (0, -1)):
                    image_to_draw = img_body_v
                else:
                    connection_set = {p_v, n_v}
                    if connection_set == {(-1, 0), (0, -1)}:
                        image_to_draw = img_body_tl
                    elif connection_set == {(1, 0), (0, -1)}:
                        image_to_draw = img_body_tr
                    elif connection_set == {(-1, 0), (0, 1)}:
                        image_to_draw = img_body_bl
                    elif connection_set == {(1, 0), (0, 1)}:
                        image_to_draw = img_body_br

            if image_to_draw:
                screen.blit(image_to_draw, rect)
            else:
                pygame.draw.rect(screen, fallback_color, rect)

class Food:
    def __init__(self, snake_body, bounds):
        self.reset(snake_body, bounds)

    def reset(self, snake_body, bounds):
        min_x, min_y, max_x, max_y = bounds
        min_y = max(min_y, 2)

        while True:
            self.pos = (random.randrange(min_x, max_x), random.randrange(min_y, max_y))
            if self.pos not in snake_body:
                break

        r = random.random()
        if r < 0.8:
            self.type, self.color, self.img = "BASIC", RED, img_apple
        elif r < 0.95:
            self.type, self.color, self.img = "BLUE", BLUE, img_apple_blue
        else:
            self.type, self.color, self.img = "YELLOW", YELLOW, img_apple_yellow

    def draw(self):
        tile_rect = pygame.Rect(self.pos[0] * CELL_SIZE, self.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        if self.img:
            ticks = pygame.time.get_ticks()
            scaled_img = pygame.transform.scale(self.img, (int(CELL_SIZE * 1.4), int(CELL_SIZE * 1.4)))
            rotated_img = pygame.transform.rotate(scaled_img, (ticks // 12) % 360)
            screen.blit(rotated_img, rotated_img.get_rect(center=tile_rect.center))
        else:
            pygame.draw.rect(screen, self.color, tile_rect)

class Portal:
    def __init__(self, bounds):
        min_x, min_y, max_x, max_y = bounds
        min_y = max(min_y, 2)

        while True:
            self.pos_a = (random.randrange(min_x, max_x), random.randrange(min_y, max_y))
            self.pos_b = (random.randrange(min_x, max_x), random.randrange(min_y, max_y))
            if self.pos_a != self.pos_b and abs(self.pos_a[0] - self.pos_b[0]) > 5:
                break

        self.timer = FPS_BASE * 15
        self.cooldown = 0

    def draw(self):
        frame = (pygame.time.get_ticks() // 120) % 4

        rect_a = pygame.Rect(self.pos_a[0] * CELL_SIZE, self.pos_a[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        rect_b = pygame.Rect(self.pos_b[0] * CELL_SIZE, self.pos_b[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        img_a = portal_a_frames[frame] if frame < len(portal_a_frames) else None
        img_b = portal_b_frames[frame] if frame < len(portal_b_frames) else None

        if img_a:
            screen.blit(img_a, rect_a)
        else:
            pygame.draw.circle(screen, PORTAL_A_COLOR, rect_a.center, CELL_SIZE // 2, 2)

        if img_b:
            screen.blit(img_b, rect_b)
        else:
            pygame.draw.circle(screen, PORTAL_B_COLOR, rect_b.center, CELL_SIZE // 2, 2)

# ── 7. 메인 게임 클래스 ───────────────────────────
class AbyssSnakeGame:
    def __init__(self):
        self.state = TITLE
        self.mode = 1
        self.snake = Snake()
        self.darkness_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.phase = 1
        self.ice_apple_timer = 0
        self.bounds = (0, 2, GRID_WIDTH, GRID_HEIGHT)
        self.snake.lives = 3
        self.snake.reset()
        self.food = Food(self.snake.body, self.bounds)
        self.portal = None
        self.darkness_active = False
        self.warning_timer = 0
        self.next_bounds = None

    def handle_input(self):
        direction_changed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == TITLE:
                    if event.key == pygame.K_1:
                        self.mode = 1
                        self.state = PLAYING
                        self.reset_game()
                    elif event.key == pygame.K_2:
                        self.mode = 2
                        self.state = PLAYING
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                elif self.state == PLAYING and not direction_changed:
                    cur = self.snake.direction
                    if event.key == pygame.K_UP and cur != (0, 1):
                        self.snake.direction = (0, -1)
                        direction_changed = True
                    elif event.key == pygame.K_DOWN and cur != (0, -1):
                        self.snake.direction = (0, 1)
                        direction_changed = True
                    elif event.key == pygame.K_LEFT and cur != (1, 0):
                        self.snake.direction = (-1, 0)
                        direction_changed = True
                    elif event.key == pygame.K_RIGHT and cur != (-1, 0):
                        self.snake.direction = (1, 0)
                        direction_changed = True
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_m:
                        self.state = TITLE
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                elif self.state in (GAME_OVER, CLEAR):
                    if event.key == pygame.K_r:
                        self.state = PLAYING
                        self.reset_game()
                    elif event.key == pygame.K_m:
                        self.state = TITLE
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def update(self):
        if self.state != PLAYING:
            return

        self.snake.update()
        head = self.snake.body[0]
        mx, my, max_x, max_y = self.bounds

        if not (mx <= head[0] < max_x and my <= head[1] < max_y) or head in self.snake.body[1:]:
            if die_sound:
                die_sound.play()

            self.snake.lives -= 1

            if self.snake.lives <= 0:
                self.state = GAME_OVER
            else:
                self.snake.reset()
            return

        if head == self.food.pos:
            if eat_sound:
                eat_sound.play()

            self.snake.eat_anim_timer = 10

            if self.food.type == "BASIC":
                self.score += 10
            elif self.food.type == "BLUE":
                self.score += 10
                self.ice_apple_timer = 100
            else:
                self.score += 20
                self.snake.lives = min(3, self.snake.lives + 1)

            self.snake.grow = True
            self.food.reset(self.snake.body, self.bounds)

        if self.portal:
            if self.portal.cooldown > 0:
                self.portal.cooldown -= 1

            if head == self.portal.pos_a and self.portal.cooldown == 0:
                self.snake.body[0] = self.portal.pos_b
                self.portal.cooldown = 20
            elif head == self.portal.pos_b and self.portal.cooldown == 0:
                self.snake.body[0] = self.portal.pos_a
                self.portal.cooldown = 20

        if self.mode == 1:
            if self.score >= 50 and self.phase == 1 and self.warning_timer == 0:
                self.next_bounds = (4, 3, GRID_WIDTH - 4, GRID_HEIGHT - 3)
                self.warning_timer = 50
            elif self.score >= 100 and self.phase == 2 and self.warning_timer == 0:
                self.next_bounds = (8, 6, GRID_WIDTH - 8, GRID_HEIGHT - 6)
                self.warning_timer = 50
                self.darkness_active = True
            elif self.score >= SCORE_LIMIT:
                self.state = CLEAR

        if self.warning_timer > 0:
            self.warning_timer -= 1

            if self.warning_timer == 1:
                self.bounds = self.next_bounds
                self.phase += 1

                if self.portal:
                    if not (self.bounds[0] <= self.portal.pos_a[0] < self.bounds[2]):
                        self.portal = Portal(self.bounds)
                else:
                    self.portal = Portal(self.bounds)

                if not (self.bounds[0] <= self.food.pos[0] < self.bounds[2] and
                        self.bounds[1] <= self.food.pos[1] < self.bounds[3]):
                    self.food.reset(self.snake.body, self.bounds)

        if self.snake.eat_anim_timer > 0:
            self.snake.eat_anim_timer -= 1

    def draw(self):
        screen.fill(BLACK)

        mx, my, max_x, max_y = self.bounds
        pygame.draw.rect(screen, GRAY, (mx * CELL_SIZE, my * CELL_SIZE, (max_x - mx) * CELL_SIZE, (max_y - my) * CELL_SIZE))

        for x in range(mx * CELL_SIZE, max_x * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, LINE_COLOR, (x, my * CELL_SIZE), (x, max_y * CELL_SIZE))
        for y in range(my * CELL_SIZE, max_y * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, LINE_COLOR, (mx * CELL_SIZE, y), (max_x * CELL_SIZE, y))

        if self.warning_timer > 0 and (self.warning_timer // 5) % 2 == 0 and self.next_bounds:
            warn = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            warn.fill((220, 50, 50, 100))
            pygame.draw.rect(
                warn, (0, 0, 0, 0),
                (
                    self.next_bounds[0] * CELL_SIZE,
                    self.next_bounds[1] * CELL_SIZE,
                    (self.next_bounds[2] - self.next_bounds[0]) * CELL_SIZE,
                    (self.next_bounds[3] - self.next_bounds[1]) * CELL_SIZE
                )
            )
            screen.blit(warn, (0, 0))

        if self.portal:
            self.portal.draw()

        self.food.draw()
        self.snake.draw()

        if self.darkness_active:
            self.darkness_layer.fill((0, 0, 0, 250))
            pygame.draw.circle(
                self.darkness_layer,
                (0, 0, 0, 0),
                (self.snake.body[0][0] * CELL_SIZE + CELL_SIZE // 2,
                 self.snake.body[0][1] * CELL_SIZE + CELL_SIZE // 2),
                100
            )
            screen.blit(self.darkness_layer, (0, 0))

        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 40))
        screen.blit(font.render(f"Score: {self.score}  Lives: {self.snake.lives}", True, WHITE), (10, 5))

        if self.state == TITLE:
            self.draw_overlay((10, 10, 30, 200))
            self.draw_txt("ABYSS SNAKE", font_big, NEON_GREEN, 150)
            self.draw_txt("[1] 탈출 모드  [2] 무한 모드", font, BLUE, 300)
            self.draw_txt("[Q] 종료", font, WHITE, 350)

        elif self.state == GAME_OVER:
            self.draw_overlay((200, 0, 0, 100))
            self.draw_txt("CONSUMED...", font_big, RED, 180)
            self.draw_txt("[R] 다시 도전  [M] 메뉴  [Q] 종료", font, WHITE, 350)

        elif self.state == CLEAR:
            self.draw_overlay((255, 255, 255, 180))
            self.draw_txt("ESCAPED!", font_big, PORTAL_A_COLOR, 200)
            self.draw_txt("[M] 메인 메뉴  [Q] 종료", font, GRAY, 350)

        pygame.display.flip()

    def draw_txt(self, txt, f, color, y):
        obj = f.render(txt, True, color)
        screen.blit(obj, (WIDTH // 2 - obj.get_width() // 2, y))

    def draw_overlay(self, color):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill(color)
        screen.blit(ov, (0, 0))

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()

            current_fps = 7 if self.ice_apple_timer > 0 else FPS_BASE
            if self.mode == 2:
                current_fps = min(20, FPS_BASE + self.score // 50)

            clock.tick(current_fps)

            if self.ice_apple_timer > 0:
                self.ice_apple_timer -= 1

if __name__ == "__main__":
    game = AbyssSnakeGame()
    game.run()