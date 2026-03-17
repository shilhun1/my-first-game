import pygame
import sys
import random

pygame.init()

# 화면 크기 정의 (오류 원인 해결)
WIDTH = 800
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Move the Circle")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# 원 위치
x, y = WIDTH // 2, HEIGHT // 2
radius = 30
speed = 7

# 떨어지는 사각형
rect_width = 50
rect_height = 50
rect_x = random.randint(0, WIDTH - rect_width)
rect_y = -rect_height
rect_speed = 5

score = 0
running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            x -= speed
        if keys[pygame.K_RIGHT]:
            x += speed
        if keys[pygame.K_UP]:
            y -= speed
        if keys[pygame.K_DOWN]:
            y += speed

        # 화면 밖으로 못 나가게
        x = max(radius, min(WIDTH - radius, x))
        y = max(radius, min(HEIGHT - radius, y))

        # 사각형 내려오기
        rect_y += rect_speed

        if rect_y > HEIGHT:
            rect_y = -rect_height
            rect_x = random.randint(0, WIDTH - rect_width)
            score += 1

        # 충돌 판정
        closest_x = max(rect_x, min(x, rect_x + rect_width))
        closest_y = max(rect_y, min(y, rect_y + rect_height))

        distance_x = x - closest_x
        distance_y = y - closest_y

        if distance_x**2 + distance_y**2 < radius**2:
            game_over = True

    # 화면 그리기
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (x, y), radius)
    pygame.draw.rect(screen, BLUE, (rect_x, rect_y, rect_width, rect_height))

    # 점수 표시
    score_text = font.render(f"Score: {score}", True, RED)
    screen.blit(score_text, (10, 10))

    # 게임 오버 표시
    if game_over:
        over_text = font.render("GAME OVER", True, RED)
        screen.blit(over_text, (WIDTH // 2 - 120, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()