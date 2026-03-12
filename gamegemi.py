import pygame
import random
import math

# 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Particle Aurora")

clock = pygame.time.Clock()

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        # 물리 엔진: 더 퍼지는 느낌을 위해 랜덤 범위 조정
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # 수명 및 크기
        self.max_life = random.randint(30, 60)
        self.life = self.max_life
        self.initial_size = random.randint(4, 8)
        
        # 네온 컬러 테마 (Cyan, Pink, Purple 계열)
        self.color = random.choice([
            [255, 50, 255], # Pink
            [50, 255, 255], # Cyan
            [150, 50, 255], # Purple
            [255, 255, 255] # White
        ])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # 중력 및 저항
        self.vy += 0.1
        self.vx *= 0.98
        self.vy *= 0.98
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            # 수명에 따른 투명도 및 크기 계산
            alpha = int((self.life / self.max_life) * 255)
            current_size = (self.life / self.max_life) * self.initial_size
            
            # 메인 입자 그리기 (발광 느낌을 위해 원을 중첩하거나 부드럽게 표현)
            # Pygame에서 기본 circle은 투명도를 지원하지 않으므로, 별도 Surface 사용 가능하나 
            # 여기서는 간단히 크기를 줄여가며 색상을 연하게 조절합니다.
            r = max(0, min(255, self.color[0]))
            g = max(0, min(255, self.color[1]))
            b = max(0, min(255, self.color[2]))
            
            # 발광 효과 (바깥쪽 큰 원)
            pygame.draw.circle(surf, (r//4, g//4, b//4), (int(self.x), int(self.y)), int(current_size * 2))
            # 중심 입자
            pygame.draw.circle(surf, (r, g, b), (int(self.x), int(self.y)), int(current_size))

def main():
    particles = []
    running = True
    
    # 배경을 위한 별도 Surface (잔상 효과용)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(40) # 이 수치가 낮을수록 잔상이 길게 남습니다.
    overlay.fill((10, 10, 25))

    while running:
        # 배경 그리기 (완전 초기화 대신 살짝 덮기)
        screen.blit(overlay, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 마우스 클릭/누름 감지
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            for _ in range(10): # 클릭 시 입자 생성량 증가
                particles.append(Particle(*mouse_pos))

        # 입자 업데이트 및 그리기
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if self_life := p.life <= 0:
                particles.remove(p)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()