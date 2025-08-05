import pygame
import time

class Modal:
    def __init__(self, text, duration=5):
        self.text = text
        self.duration = duration  # in seconds
        self.start_time = None
        self.active = False

    def show(self):
        self.start_time = time.time()
        self.active = True

    def update(self):
        if self.active and (time.time() - self.start_time > self.duration):
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        # Dim the background
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # semi-transparent black
        screen.blit(overlay, (0, 0))

        # Render modal text box
        font = pygame.font.SysFont(None, 32)
        wrapped = self.wrap_text(self.text, font, screen.get_width() - 80)
        box_height = 40 + len(wrapped) * 30
        box_rect = pygame.Rect(40, screen.get_height() // 2 - box_height // 2, screen.get_width() - 80, box_height)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), box_rect, 2, border_radius=10)

        # Draw each line of wrapped text
        for i, line in enumerate(wrapped):
            rendered = font.render(line, True, (0, 0, 0))
            screen.blit(rendered, (box_rect.x + 20, box_rect.y + 20 + i * 30))

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
