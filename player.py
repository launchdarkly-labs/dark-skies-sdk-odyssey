import pygame
from constants import SCREEN_HEIGHT, BIRD_WIDTH, BIRD_HEIGHT, GRAVITY, JUMP_STRENGTH

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.wing_up = True
        self.animation_counter = 0

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = int(self.y)
        self.animation_counter += 1
        if self.animation_counter % 7 == 0:
            self.wing_up = not self.wing_up

    def draw(self, screen):
        center = (int(self.x + self.width // 2), int(self.y + self.height // 2))
        pygame.draw.ellipse(screen, (255, 255, 0), self.rect)
        if self.wing_up:
            wing_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 6, 14, 8)
        else:
            wing_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 14, 14, 8)
        pygame.draw.ellipse(screen, (200, 200, 0), wing_rect)
        beak_tip = (self.rect.right + 6, center[1])
        beak_base1 = (self.rect.right, center[1] - 4)
        beak_base2 = (self.rect.right, center[1] + 4)
        pygame.draw.polygon(screen, (255, 128, 0), [beak_tip, beak_base1, beak_base2])
        eye_center = (self.rect.x + self.width - 10, self.rect.y + 8)
        pygame.draw.circle(screen, (0, 0, 0), eye_center, 3)