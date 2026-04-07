import pygame
import random
import sys
import os
import base64
import io

# ── 1. 상수 설정 ──────────────────────────────────
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS_BASE = 10
SCORE_LIMIT = 250

# 색상 정의
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

# ── 2. 초기화 및 경로 설정 ──────────────────────────
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
ASSETS_DIR = os.path.join(BASE_DIR, "Graphics")

# ── 3. 에셋 로드 (이미지) ──────────────────────────
def load_image(filename):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    except FileNotFoundError: return None

img_head_up = load_image("head_up.png")
img_head_down = load_image("head_down.png")
img_head_left = load_image("head_left.png")
img_head_right = load_image("head_right.png")

img_body_v = load_image("body_vertical.png")
img_body_h = load_image("body_horizontal.png")
img_body_bl = load_image("body_bottomleft.png")
img_body_br = load_image("body_bottomright.png")
img_body_tl = load_image("body_topleft.png")
img_body_tr = load_image("body_topright.png")

img_tail_up = load_image("tail_up.png")
img_tail_down = load_image("tail_down.png")
img_tail_left = load_image("tail_left.png")
img_tail_right = load_image("tail_right.png")

img_apple = load_image("apple.png")
img_apple_blue = load_image("apple_blue.png")
img_apple_yellow = load_image("apple_yellow.png")

img_portal_a = load_image("portal_entrance.png")
img_portal_b = load_image("portal_exit.png")

# ── 4. 에셋 로드 (사운드 - Base64 임베딩) ─────────────
def load_sound_from_base64(b64_string):
    try:
        if not b64_string: return None
        sound_data = base64.b64decode(b64_string)
        return pygame.mixer.Sound(io.BytesIO(sound_data))
    except Exception:
        return None

EAT_SOUND_B64 = ""
DIE_SOUND_B64 = ""

eat_sound = load_sound_from_base64(EAT_SOUND_B64)
die_sound = load_sound_from_base64(DIE_SOUND_B64)

try:
    pygame.mixer.music.load(os.path.join(ASSETS_DIR, "nastelbom-no-copyright-music-2-507945.mp3"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except: pass

# ── 5. 객체 클래스 ────────────────────────────────
class Snake:
    def __init__(self):
        self.lives = 3
        self.reset()

    def reset(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def update(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        self.body.insert(0, (head_x + dx, head_y + dy))
        if not self.grow: self.body.pop()
        else: self.grow = False

    def draw(self):
        for i, segment in enumerate(self.body):
            gx, gy = segment
            rect = pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            image_to_draw = None
            fallback_color = GREEN

            if i == 0:
                fallback_color = NEON_GREEN
                if self.direction == (0, -1): image_to_draw = img_head_up
                elif self.direction == (0, 1): image_to_draw = img_head_down
                elif self.direction == (-1, 0): image_to_draw = img_head_left
                elif self.direction == (1, 0): image_to_draw = img_head_right

            elif i == len(self.body) - 1:
                prev = self.body[i-1]
                p_v = (gx - prev[0], gy - prev[1])
                if p_v == (0, -1): image_to_draw = img_tail_up
                elif p_v == (0, 1): image_to_draw = img_tail_down
                elif p_v == (-1, 0): image_to_draw = img_tail_left
                elif p_v == (1, 0): image_to_draw = img_tail_right

            else:
                curr = segment
                prev = self.body[i-1]
                nxt = self.body[i+1]
                p_v = (prev[0] - gx, prev[1] - gy)
                n_v = (nxt[0] - gx, nxt[1] - gy)

                if (p_v == (-1, 0) and n_v == (1, 0)) or (p_v == (1, 0) and n_v == (-1, 0)):
                    image_to_draw = img_body_h
                elif (p_v == (0, -1) and n_v == (0, 1)) or (p_v == (0, 1) and n_v == (0, -1)):
                    image_to_draw = img_body_v

                connection_set = {p_v, n_v}
                if connection_set == {(-1, 0), (0, -1)}: image_to_draw = img_body_tl
                elif connection_set == {(1, 0), (0, -1)}: image_to_draw = img_body_tr
                elif connection_set == {(-1, 0), (0, 1)}: image_to_draw = img_body_bl
                elif connection_set == {(1, 0), (0, 1)}: image_to_draw = img_body_br

            if image_to_draw: screen.blit(image_to_draw, rect)
            else: pygame.draw.rect(screen, fallback_color, rect)

class Food:
    def __init__(self, snake_body, bounds):
        self.reset(snake_body, bounds)

    def reset(self, snake_body, bounds):
        min_x, min_y, max_x, max_y = bounds
        min_y = max(min_y, 2) 
        while True:
            self.pos = (random.randrange(min_x, max_x), random.randrange(min_y, max_y))
            if self.pos not in snake_body: break
        
        r = random.random()
        if r < 0.8: self.type, self.color, self.img = "BASIC", RED, img_apple
        elif r < 0.95: self.type, self.color, self.img = "BLUE", BLUE, img_apple_blue
        else: self.type, self.color, self.img = "YELLOW", YELLOW, img_apple_yellow

    def draw(self):
        # 논리적 충돌 타일 (20x20)
        tile_rect = pygame.Rect(self.pos[0] * CELL_SIZE, self.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        
        if self.img:
            ticks = pygame.time.get_ticks()
            
            # 사과 시각적 크기 키우기 로직 (1.8배 확대)
            visual_scale = 1.8
            new_size = int(CELL_SIZE * visual_scale)
            
            # 현재 이미지를 키웁니다.
            scaled_img = pygame.transform.scale(self.img, (new_size, new_size))
            
            # 사과 부드럽게 회전시키기 로직
            angle = (ticks // 15) % 360
            rotated_img = pygame.transform.rotate(scaled_img, angle)
            
            # 이미지를 타일 중앙에 배치
            rotated_rect = rotated_img.get_rect(center=tile_rect.center)
            
            screen.blit(rotated_img, rotated_rect)
        else:
            pygame.draw.rect(screen, self.color, tile_rect)

class Portal:
    def __init__(self, bounds):
        min_x, min_y, max_x, max_y = bounds
        min_y = max(min_y, 2)
        while True:
            self.pos_a = (random.randrange(min_x, max_x), random.randrange(min_y, max_y))
            self.pos_b = (random.randrange(min_x, max_x), random.randrange(min_y, max_y))
            if self.pos_a != self.pos_b and abs(self.pos_a[0] - self.pos_b[0]) > 5: break
        self.timer = FPS_BASE * 15
        self.cooldown = 0

    def draw(self):
        for pos, color in [(self.pos_a, PORTAL_A_COLOR), (self.pos_b, PORTAL_B_COLOR)]:
            rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if img_portal_a and color == PORTAL_A_COLOR: screen.blit(img_portal_a, rect)
            elif img_portal_b and color == PORTAL_B_COLOR: screen.blit(img_portal_b, rect)
            else: pygame.draw.circle(screen, color, rect.center, CELL_SIZE // 2, 2)

# ── 6. 메인 게임 클래스 ───────────────────────────
class AbyssSnakeGame:
    def __init__(self):
        self.state = TITLE
        self.snake = Snake()
        self.darkness_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.reset_game()

    def reset_game(self):
        self.score, self.phase, self.ice_apple_timer = 0, 1, 0
        self.bounds = (0, 0, GRID_WIDTH, GRID_HEIGHT)
        self.snake.lives = 3
        self.snake.reset()
        self.food = Food(self.snake.body, self.bounds)
        self.portal, self.darkness_active = None, False
        self.warning_timer = 0
        self.next_bounds = None

    def handle_input(self):
        direction_changed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == TITLE:
                    if event.key == pygame.K_1: self.mode = 1; self.state = PLAYING; self.reset_game()
                    if event.key == pygame.K_2: self.mode = 2; self.state = PLAYING; self.reset_game()
                    if event.key == pygame.K_q: sys.exit()
                elif self.state == PLAYING and not direction_changed:
                    cur = self.snake.direction
                    if event.key == pygame.K_UP and cur != (0, 1): self.snake.direction = (0, -1); direction_changed = True
                    elif event.key == pygame.K_DOWN and cur != (0, -1): self.snake.direction = (0, 1); direction_changed = True
                    elif event.key == pygame.K_LEFT and cur != (1, 0): self.snake.direction = (-1, 0); direction_changed = True
                    elif event.key == pygame.K_RIGHT and cur != (-1, 0): self.snake.direction = (1, 0); direction_changed = True
                elif self.state in (GAME_OVER, CLEAR):
                    if event.key == pygame.K_r: self.state = PLAYING; self.reset_game()
                    if event.key == pygame.K_m: self.state = TITLE

    def update(self):
        if self.state != PLAYING: return
        self.snake.update()
        head = self.snake.body[0]
        min_x, min_y, max_x, max_y = self.bounds

        if not (min_x <= head[0] < max_x and min_y <= head[1] < max_y) or head in self.snake.body[1:]:
            if die_sound: die_sound.play()
            self.snake.lives -= 1
            if self.snake.lives <= 0: self.state = GAME_OVER
            else: self.snake.reset()
            return

        if head == self.food.pos:
            if eat_sound: eat_sound.play()
            if self.food.type == "BASIC": self.score += 10
            elif self.food.type == "BLUE": self.score += 10; self.ice_apple_timer = 100
            else: self.score += 20; self.snake.lives = min(3, self.snake.lives + 1)
            self.snake.grow = True
            self.food.reset(self.snake.body, self.bounds)

        if self.portal:
            if self.portal.cooldown > 0: self.portal.cooldown -= 1
            self.portal.timer -= 1
            if self.portal.timer <= 0: self.portal = None
            else:
                if head == self.portal.pos_a and self.portal.cooldown == 0:
                    self.snake.body[0] = self.portal.pos_b; self.portal.cooldown = 20
                elif head == self.portal.pos_b and self.portal.cooldown == 0:
                    self.snake.body[0] = self.portal.pos_a; self.portal.cooldown = 20

        if self.mode == 1:
            if self.score >= 50 and self.phase == 1 and self.warning_timer == 0:
                self.next_bounds = (4, 3, GRID_WIDTH - 4, GRID_HEIGHT - 3)
                self.warning_timer = 50
            elif self.score >= 100 and self.phase == 2 and self.warning_timer == 0:
                self.next_bounds = (8, 6, GRID_WIDTH - 8, GRID_HEIGHT - 6)
                self.warning_timer = 50 
                self.darkness_active = True
            elif self.score >= 150 and self.phase == 3 and self.warning_timer == 0:
                self.next_bounds = (12, 9, GRID_WIDTH - 12, GRID_HEIGHT - 9)
                self.warning_timer = 50
            elif self.score >= SCORE_LIMIT: self.state = CLEAR

        if self.warning_timer > 0:
            self.warning_timer -= 1
            if self.warning_timer == 1:
                self.bounds = self.next_bounds
                self.phase += 1
                
                nmx, nmy, nMX, nMY = self.bounds
                if self.portal:
                    px, py = self.portal.pos_a
                    if not (nmx <= px < nMX and nmy <= py < nMY):
                        self.portal = Portal(self.bounds)
                else:
                    self.portal = Portal(self.bounds)
                
                fx, fy = self.food.pos
                if not (nmx <= fx < nMX and nmy <= fy < nMY):
                    self.food.reset(self.snake.body, self.bounds)

    def draw(self):
        screen.fill(BLACK)
        min_x, min_y, max_x, max_y = self.bounds
        bg_rect = pygame.Rect(min_x * CELL_SIZE, min_y * CELL_SIZE, (max_x - min_x) * CELL_SIZE, (max_y - min_y) * CELL_SIZE)
        pygame.draw.rect(screen, GRAY, bg_rect)
        
        for x in range(min_x * CELL_SIZE, max_x * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, LINE_COLOR, (x, min_y * CELL_SIZE), (x, max_y * CELL_SIZE))
        for y in range(min_y * CELL_SIZE, max_y * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, LINE_COLOR, (min_x * CELL_SIZE, y), (max_x * CELL_SIZE, y))

        if self.warning_timer > 0 and (self.warning_timer // 5) % 2 == 0:
            nmx, nmy, nMX, nMY = self.next_bounds
            warn_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            warn_surf.fill((220, 50, 50, 100))
            pygame.draw.rect(warn_surf, (0, 0, 0, 0), (nmx * 20, nmy * 20, (nMX - nmx) * 20, (nMY - nmy) * 20))
            screen.blit(warn_surf, (0, 0))

        if self.portal: self.portal.draw()
        self.food.draw()
        self.snake.draw()

        if self.darkness_active:
            self.darkness_layer.fill((0, 0, 0, 250))
            head_center = (self.snake.body[0][0] * CELL_SIZE + 10, self.snake.body[0][1] * CELL_SIZE + 10)
            pygame.draw.circle(self.darkness_layer, (0, 0, 0, 0), head_center, 100)
            screen.blit(self.darkness_layer, (0, 0))

        pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 40))
        screen.blit(font.render(f"Score: {self.score}  Lives: {self.snake.lives}", True, WHITE), (10, 5))

        if self.state == TITLE:
            self.draw_overlay((10, 10, 30, 200))
            self.draw_txt("ABYSS SNAKE", font_big, NEON_GREEN, 150)
            self.draw_txt("[1] 모드 1: 어비스 탈출", font, BLUE, 280)
            self.draw_txt("[2] 모드 2: 무한의 암흑", font, YELLOW, 330)
            self.draw_txt("[Q] 게임 종료", font, GRAY, 380)
        elif self.state == GAME_OVER:
            self.draw_overlay((200, 0, 0, 100))
            self.draw_txt("YOU WERE CONSUMED...", font_big, RED, 180)
            self.draw_txt(f"최종 점수: {self.score}", font, WHITE, 280)
            self.draw_txt("[R] 다시 도전  [M] 메뉴", font, GREEN, 350)
        elif self.state == CLEAR:
            self.draw_overlay((255, 255, 255, 180))
            self.draw_txt("ESCAPED THE ABYSS!", font_big, PORTAL_A_COLOR, 200)

        pygame.display.flip()

    def draw_txt(self, txt, f, color, y):
        obj = f.render(txt, True, color)
        screen.blit(obj, (WIDTH//2 - obj.get_width()//2, y))

    def draw_overlay(self, color):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(color)
        screen.blit(overlay, (0, 0))

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            clock.tick(7 if self.ice_apple_timer > 0 else 10)
            if self.ice_apple_timer > 0: self.ice_apple_timer -= 1

if __name__ == "__main__":
    game = AbyssSnakeGame()
    game.run()