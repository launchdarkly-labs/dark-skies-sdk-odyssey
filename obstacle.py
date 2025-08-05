import pygame
import random
from constants import SCREEN_HEIGHT, PIPE_WIDTH, PIPE_GAP

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP)

    def move(self):
        self.x -= 3
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        for rect in [self.top_rect, self.bottom_rect]:
            pygame.draw.rect(screen, (220, 220, 220), rect)
            for i in range(1, 6):
                x = rect.x + int(i * rect.width / 6)
                pygame.draw.line(screen, (180, 180, 180), (x, rect.y), (x, rect.y + rect.height), 2)
            if rect == self.top_rect:
                cap_rect = pygame.Rect(rect.x - 4, rect.bottom - 8, rect.width + 8, 12)
                pygame.draw.rect(screen, (200, 200, 200), cap_rect)
            else:
                base_rect = pygame.Rect(rect.x - 4, rect.y - 4, rect.width + 8, 12)
                pygame.draw.rect(screen, (200, 200, 200), base_rect)

    def off_screen(self):
        return self.x < -PIPE_WIDTH

    def collide(self, bird):
        return self.top_rect.colliderect(bird.rect) or self.bottom_rect.colliderect(bird.rect)
