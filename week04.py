import pygame
import math

# 1. 초기화 및 창 설정
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("SAT 기반 OBB 충돌 감지 (Z: 가속)")
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BG_HIT = (255, 100, 100) # 충돌 시 배경색 (연한 빨강)

# --- SAT 충돌 함수 ---
def get_axes(points):
    """다각형의 각 변에 수직인 법선 벡터(분리축)들을 구합니다."""
    axes = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        edge = p2 - p1
        # 변에 수직인 벡터 (법선)
        normal = pygame.Vector2(-edge.y, edge.x)
        if normal.length() > 0:
            axes.append(normal.normalize())
    return axes

def project(points, axis):
    """다각형의 점들을 특정 축에 투영하여 최소/최대 범위를 반환합니다."""
    dots = [p.dot(axis) for p in points]
    return min(dots), max(dots)

def check_obb_collision(poly1, poly2):
    """두 다각형(점들의 리스트)이 SAT 알고리즘으로 충돌하는지 확인합니다."""
    # 검사해야 할 모든 축을 가져옵니다 (두 사각형의 모든 변의 법선)
    axes = get_axes(poly1) + get_axes(poly2)
    
    for axis in axes:
        min1, max1 = project(poly1, axis)
        min2, max2 = project(poly2, axis)
        
        # 그림자가 겹치지 않는 축이 하나라도 발견되면 충돌이 아님 (분리축 존재)
        if max1 < min2 or max2 < min1:
            return False
    return True

# 오브젝트 설정
static_pos = pygame.Vector2(400, 300)
static_size = (120, 120)
static_angle = 0

player_size = (80, 80)
player_pos = pygame.Vector2(100, 100)
player_speed = 5

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # 1. 회전 및 이동 로직
    rotation_speed = 5 if keys[pygame.K_z] else 1
    static_angle += rotation_speed

    if keys[pygame.K_LEFT]:  player_pos.x -= player_speed
    if keys[pygame.K_RIGHT]: player_pos.x += player_speed
    if keys[pygame.K_UP]:    player_pos.y -= player_speed
    if keys[pygame.K_DOWN]:  player_pos.y += player_speed

    # 2. 각 오브젝트의 네 모서리 좌표(OBB) 계산
    def get_rotated_corners(pos, size, angle):
        hw, hh = size[0] / 2, size[1] / 2
        corners = [pygame.Vector2(-hw, -hh), pygame.Vector2(hw, -hh), 
                   pygame.Vector2(hw, hh), pygame.Vector2(-hw, hh)]
        return [c.rotate(angle) + pos for c in corners]

    static_corners = get_rotated_corners(static_pos, static_size, static_angle)
    player_corners = get_rotated_corners(player_pos, player_size, 0) # 플레이어는 회전X 가정

    # 3. SAT 충돌 검사 실행
    is_colliding = check_obb_collision(static_corners, player_corners)

    # 4. 그리기
    screen.fill(BG_HIT if is_colliding else WHITE)

    # 오브젝트 본체 그리기
    pygame.draw.polygon(screen, GRAY, static_corners)
    pygame.draw.polygon(screen, GRAY, player_corners)

    # OBB 테두리 (초록)
    pygame.draw.lines(screen, GREEN, True, static_corners, 3)
    pygame.draw.lines(screen, GREEN, True, player_corners, 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
