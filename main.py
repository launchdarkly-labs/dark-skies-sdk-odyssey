
import pygame
import sys
import random
import os
import json
from modals import Modal
ASTEROID_IMG_PATH = "assets/Asteroids/Asteroid Large.png"
BUG_IMG_PATH = "assets/BUG.png"
ERROR_IMG_PATH = "assets/Error.png"

BKG_IMG_PATH = "assets/Tile Galaxy BK - 3480x999.png"
if os.path.exists(BKG_IMG_PATH):
    _bkg_img = pygame.image.load(BKG_IMG_PATH)
    SCREEN_WIDTH = _bkg_img.get_width() // 2  # Half the original width
    SCREEN_HEIGHT = _bkg_img.get_height()
    del _bkg_img
else:
    SCREEN_WIDTH = 200  # Half of 400
    SCREEN_HEIGHT = 600

# Game Constants
BIRD_WIDTH = 136
BIRD_HEIGHT = 96
PIPE_WIDTH = 52
PIPE_HEIGHT = 320
PIPE_GAP = 250
GRAVITY = 0.25
JUMP_STRENGTH = -6.5
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)

# Load custom fonts
FONT_PATH = "assets/Fonts/Everything else/PixelDigivolve-mOm9.ttf"
FONT_ITALIC_PATH = "assets/Fonts/Everything else/PixelDigivolveItalic-dV8R.ttf"

# Sound file paths (add your sound files to assets/sounds/)
JUMP_SOUND_PATH = "assets/sounds/jump.wav"
HIT_SOUND_PATH = "assets/sounds/hit.wav"
SCORE_SOUND_PATH = "assets/sounds/score.wav"
GAME_OVER_SOUND_PATH = "assets/sounds/game_over.wav"
BACKGROUND_MUSIC_PATH = "assets/sounds/background.wav"

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
        # Load van images and scale to bird size
        self.image_normal = pygame.image.load("assets/sprites/LD VAN.png").convert_alpha()
        self.image_normal = pygame.transform.smoothscale(self.image_normal, (self.width, self.height))
        # Always re-scale crashed van to match normal van size
        crashed_img = pygame.image.load("assets/sprites/LD Crashed Van.png").convert_alpha()
        self.image_crashed = pygame.transform.smoothscale(crashed_img, (self.width, self.height))
        self.rect.width = self.width
        self.rect.height = self.height

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = int(self.y)
        # Animate wing
        self.animation_counter += 1
        if self.animation_counter % 7 == 0:
            self.wing_up = not self.wing_up

    def draw(self, screen, crashed=False):
        # Draw the van image at the bird's position
        if crashed:
            screen.blit(self.image_crashed, (self.rect.x, self.rect.y))
        else:
            screen.blit(self.image_normal, (self.rect.x, self.rect.y))

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP)
        # Randomly select images for top and bottom obstacles
        asteroid_img = pygame.image.load(ASTEROID_IMG_PATH).convert_alpha()
        asteroid_img = pygame.transform.smoothscale(asteroid_img, (asteroid_img.get_width() // 2, asteroid_img.get_height() // 2))
        bug_img = pygame.image.load(BUG_IMG_PATH).convert_alpha()
        error_img = pygame.image.load(ERROR_IMG_PATH).convert_alpha()
        self.obstacle_images = [asteroid_img, bug_img, error_img]
        self.top_img = random.choice(self.obstacle_images)
        self.bottom_img = random.choice(self.obstacle_images)
        # Get new image sizes
        self.top_img_size = self.top_img.get_size()
        self.bottom_img_size = self.bottom_img.get_size()

    def move(self):
        self.x -= 3
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        # Tile the top image to fill the top_rect height
        y = self.top_rect.y
        while y < self.top_rect.y + self.top_rect.height:
            h = min(self.top_img_size[1], self.top_rect.y + self.top_rect.height - y)
            img = self.top_img
            if h < self.top_img_size[1]:
                img = self.top_img.subsurface((0, 0, self.top_img_size[0], h))
            screen.blit(img, (self.top_rect.x, y))
            y += self.top_img_size[1]
        # Tile the bottom image to fill the bottom_rect height
        y = self.bottom_rect.y
        while y < self.bottom_rect.y + self.bottom_rect.height:
            h = min(self.bottom_img_size[1], self.bottom_rect.y + self.bottom_rect.height - y)
            img = self.bottom_img
            if h < self.bottom_img_size[1]:
                img = self.bottom_img.subsurface((0, 0, self.bottom_img_size[0], h))
            screen.blit(img, (self.bottom_rect.x, y))
            y += self.bottom_img_size[1]

    def off_screen(self):
        return self.x < -PIPE_WIDTH

    def collide(self, bird):
        return self.top_rect.colliderect(bird.rect) or self.bottom_rect.colliderect(bird.rect)




def load_sounds():
    """Load all sound effects safely with error handling"""
    sounds = {}
    sound_files = {
        'jump': JUMP_SOUND_PATH,
        'hit': HIT_SOUND_PATH,
        'score': SCORE_SOUND_PATH,
        'game_over': GAME_OVER_SOUND_PATH
    }
    
    for sound_name, sound_path in sound_files.items():
        try:
            if os.path.exists(sound_path):
                sounds[sound_name] = pygame.mixer.Sound(sound_path)
                print(f"Loaded sound: {sound_name}")
            else:
                print(f"Sound file not found: {sound_path}")
                sounds[sound_name] = None
        except pygame.error as e:
            print(f"Error loading sound {sound_name}: {e}")
            sounds[sound_name] = None
    
    return sounds

def load_background_music():
    """Load and start background music"""
    try:
        if os.path.exists(BACKGROUND_MUSIC_PATH):
            pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
            pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print("Background music loaded and playing")
        else:
            print(f"Background music file not found: {BACKGROUND_MUSIC_PATH}")
    except pygame.error as e:
        print(f"Error loading background music: {e}")

def play_sound(sounds, sound_name, volume=1.0):
    """Play a sound effect if it exists"""
    if sounds.get(sound_name):
        sound = sounds[sound_name]
        sound.set_volume(volume)
        sound.play()

def set_sound_volume(sounds, volume):
    """Set volume for all sound effects (0.0 to 1.0)"""
    for sound in sounds.values():
        if sound:
            sound.set_volume(volume)

def load_trivia():
    """Load trivia questions from JSON file"""
    with open("assets/trivia.json", "r") as f:
        return json.load(f)

def show_trivia_modal(screen, clock, trivia_text):
    """Display a trivia modal that waits for user input"""
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        # Dim the background
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # semi-transparent black
        screen.blit(overlay, (0, 0))

        # Create modal box
        font = pygame.font.Font(FONT_PATH, 32)
        wrapped_text = wrap_text(trivia_text, font, screen.get_width() - 80)
        box_height = 80 + len(wrapped_text) * 35  # Extra space for instruction text
        box_rect = pygame.Rect(40, screen.get_height() // 2 - box_height // 2, screen.get_width() - 80, box_height)
        
        # Draw modal box with dark background for white text
        pygame.draw.rect(screen, (40, 40, 40), box_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, box_rect, 2, border_radius=10)

        # Draw trivia text
        for i, line in enumerate(wrapped_text):
            rendered = font.render(line, True, WHITE)
            screen.blit(rendered, (box_rect.x + 20, box_rect.y + 20 + i * 35))

        # Draw instruction text
        instruction_font = pygame.font.Font(FONT_PATH, 24)
        instruction = instruction_font.render("Press any key to continue...", True, WHITE)
        instruction_rect = instruction.get_rect(center=(box_rect.centerx, box_rect.bottom - 25))
        screen.blit(instruction, instruction_rect)
        
        pygame.display.update()

def render_text_with_outline(font, text, text_color, outline_color, outline_width=2):
    """Render text with an outline for better visibility"""
    # Render the outline first
    outline_surfaces = []
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                outline_surfaces.append((outline_surface, dx, dy))
    
    # Render the main text
    text_surface = font.render(text, True, text_color)
    
    # Calculate total size needed
    width = text_surface.get_width() + 2 * outline_width
    height = text_surface.get_height() + 2 * outline_width
    
    # Create final surface
    final_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Blit outline
    for outline_surface, dx, dy in outline_surfaces:
        final_surface.blit(outline_surface, (outline_width + dx, outline_width + dy))
    
    # Blit main text
    final_surface.blit(text_surface, (outline_width, outline_width))
    
    return final_surface

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width"""
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

def show_splash_screen(screen, clock):
    """Display the splash screen and wait for user input to continue"""
    # Load and scale the splash screen image
    splash_img = pygame.image.load("assets/START SCREEN.png").convert()
    splash_img = pygame.transform.scale(splash_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Display splash screen
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        # Draw splash screen
        screen.blit(splash_img, (0, 0))
        
        # Add "Press any key to continue" text
        font = pygame.font.Font(FONT_PATH, 36)
        text = render_text_with_outline(font, 'Press any key to start!', WHITE, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(text, text_rect)
        
        pygame.display.update()

def draw_window(screen, bird, pipes, score, hit_count=0):
    # Draw galaxy background scaled to fit the window
    scaled_bg = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))
    # Pass game_over state to bird.draw
    crashed = globals().get('game_over', False)
    bird.draw(screen, crashed=crashed)
    for pipe in pipes:
        pipe.draw(screen)
    font = pygame.font.Font(FONT_PATH, 36)
    score_text = render_text_with_outline(font, f'Score: {score}', WHITE, BLACK)
    screen.blit(score_text, (10, 10))
    
    # Display hit count
    hit_text = render_text_with_outline(font, f'Hits: {hit_count}/10', WHITE, BLACK)
    screen.blit(hit_text, (10, 50))
    
    pygame.display.update()

def main():
    pygame.init()
    pygame.mixer.init()  # Initialize the mixer for sound
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Dark Skies')
    clock = pygame.time.Clock()
    
    # Load sounds and music
    sounds = load_sounds()
    set_sound_volume(sounds, 0.7)  # Set sound effects to 70% volume
    load_background_music()
    
    # Show splash screen first
    show_splash_screen(screen, clock)
    
    # Load background image and trivia data
    global background_img
    background_img = pygame.image.load(BKG_IMG_PATH).convert()
    trivia_data = load_trivia()
    
    bird = Bird()
    # Add more obstacles and make the first appear sooner
    pipe_spacing = 500  # horizontal distance between pipes
    num_pipes = max(3, SCREEN_WIDTH // pipe_spacing)
    pipes = [Pipe(SCREEN_WIDTH // 2 + i * pipe_spacing) for i in range(num_pipes)]
    # No clouds
    score = 0
    hit_count = 0  # Track number of obstacle hits
    running = True
    global game_over
    game_over = False

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bird.jump()
                    play_sound(sounds, 'jump')
                if event.key == pygame.K_r and game_over:
                    main()
                    return
                if event.key == pygame.K_m:
                    # Toggle music mute/unmute
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

        if not game_over:
            bird.move()
            remove = []
            add_pipe = False
            for pipe in pipes:
                pipe.move()
                if pipe.collide(bird) and not hasattr(pipe, 'hit'):
                    # Mark this pipe as hit to prevent multiple hits
                    pipe.hit = True
                    hit_count += 1
                    play_sound(sounds, 'hit')
                    
                    # Show trivia modal
                    if trivia_data:
                        trivia_item = random.choice(trivia_data)
                        show_trivia_modal(screen, clock, trivia_item['text'])
                    
                    # Check if player has hit 10 obstacles
                    if hit_count >= 10:
                        game_over = True
                        play_sound(sounds, 'game_over')
                        
                if pipe.x + PIPE_WIDTH < bird.x and not hasattr(pipe, 'scored'):
                    score += 1
                    pipe.scored = True
                    play_sound(sounds, 'score')
                if pipe.off_screen():
                    remove.append(pipe)
            for r in remove:
                pipes.remove(r)
                add_pipe = True
            if add_pipe:
                pipes.append(Pipe(SCREEN_WIDTH))
            if bird.y > SCREEN_HEIGHT - bird.height or bird.y < 0:
                game_over = True
                play_sound(sounds, 'game_over')
        draw_window(screen, bird, pipes, score, hit_count)
        if game_over:
            font = pygame.font.Font(FONT_PATH, 48)
            if hit_count >= 10:
                over_text = render_text_with_outline(font, '10 Hits Reached! Press R to Restart', WHITE, BLACK)
            else:
                over_text = render_text_with_outline(font, 'Game Over! Press R to Restart', WHITE, BLACK)
            screen.blit(over_text, (20, SCREEN_HEIGHT // 2 - 24))
            pygame.display.update()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
