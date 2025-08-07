
import pygame
import sys
import random
import os
import json
from modals import Modal
from launchdarkly_client import LaunchDarklyClient
ASTEROID_IMG_PATH = "assets/Asteroids/Asteroid Large.png"
BUG_IMG_PATH = "assets/BUG.png"
ERROR_IMG_PATH = "assets/Error.png"

BKG_IMG_PATH = "assets/Tile Galaxy BK - 1080x1920.png"
if os.path.exists(BKG_IMG_PATH):
    _bkg_img = pygame.image.load(BKG_IMG_PATH)
    # Use a reasonable game window size based on the background
    bg_width, bg_height = _bkg_img.get_size()
    if bg_width > bg_height:  # Landscape background
        SCREEN_WIDTH = min(1200, bg_width)  # Cap at reasonable size
        SCREEN_HEIGHT = int(SCREEN_WIDTH * (bg_height / bg_width))
    else:  # Portrait background
        SCREEN_HEIGHT = min(800, bg_height)  # Cap at reasonable size  
        SCREEN_WIDTH = int(SCREEN_HEIGHT * (bg_width / bg_height))
    del _bkg_img
else:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

# Game Constants

# global mute state controlled by LD
is_muted = False
BIRD_WIDTH = 133
BIRD_HEIGHT = 76
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
        self.gap_rect = pygame.Rect(self.x, self.height, PIPE_WIDTH, PIPE_GAP)
        # Use asteroids as main obstacles
        asteroid_large_img = pygame.image.load("assets/Asteroids/Asteroid Large.png").convert_alpha()
        asteroid_small_img = pygame.image.load("assets/Asteroids/Asteroid Small.png").convert_alpha()
        # Scale asteroids to appropriate sizes
        self.asteroid_large = pygame.transform.smoothscale(asteroid_large_img, (80, 80))
        self.asteroid_small = pygame.transform.smoothscale(asteroid_small_img, (50, 50))
        # Load error symbol for single placement (not tiled)
        self.error_img = pygame.image.load(ERROR_IMG_PATH).convert_alpha()
        self.error_img = pygame.transform.smoothscale(self.error_img, (40, 40))
        # Choose asteroids for obstacles
        self.top_asteroids = self._generate_asteroid_pattern(self.top_rect)
        self.bottom_asteroids = self._generate_asteroid_pattern(self.bottom_rect)
        # Add single error symbol in varying position
        self.error_positions = self._generate_error_positions()

    def _generate_asteroid_pattern(self, rect):
        """Generate asteroid positions to fill the obstacle area"""
        asteroids = []
        y = rect.y
        while y < rect.y + rect.height:
            # Randomly choose asteroid size
            if random.random() < 0.6:  # 60% chance for large asteroid
                asteroid_img = self.asteroid_large
                size = 80
            else:
                asteroid_img = self.asteroid_small  
                size = 50
            
            # Add some random horizontal offset for variety
            x_offset = random.randint(-10, 10)
            asteroids.append({
                'img': asteroid_img,
                'x': rect.x + x_offset,
                'y': y,
                'size': size
            })
            y += size - 10  # Slight overlap for better coverage
        return asteroids

    def _generate_error_positions(self):
        """Generate single error symbol positions in varying locations"""
        error_positions = []
        # Add one error symbol to top or bottom area (randomly)
        # Make sure we have valid ranges for positioning
        error_size = 40  # Size of error image
        max_x = max(10, PIPE_WIDTH - error_size)
        min_x = 5
        
        # This modification display the symbol at the middle of the gap.
        x = self.gap_rect.x + (PIPE_WIDTH / 2)
        y = self.gap_rect.y + (PIPE_GAP / 2)
        error_positions.append({'x': x, 'y': y})
        # if random.random() < 0.5 and self.top_rect.height > error_size:
        #     # Place in top area
        #     x = self.x + random.randint(min_x, max_x)
        #     max_y = max(self.top_rect.y + 10, self.top_rect.y + self.top_rect.height - error_size)
        #     min_y = self.top_rect.y + 10
        #     if max_y > min_y:
        #         y = random.randint(min_y, max_y)
        #         error_positions.append({'x': x, 'y': y})
        # elif self.bottom_rect.height > error_size:
        #     # Place in bottom area
        #     x = self.x + random.randint(min_x, max_x)
        #     max_y = max(self.bottom_rect.y + 10, self.bottom_rect.y + self.bottom_rect.height - error_size)
        #     min_y = self.bottom_rect.y + 10
        #     if max_y > min_y:
        #         y = random.randint(min_y, max_y)
        #         error_positions.append({'x': x, 'y': y})
        return error_positions

    def move(self):
        self.x -= 3
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        self.gap_rect.x = self.x
        # Update asteroid positions
        for asteroid in self.top_asteroids:
            asteroid['x'] = self.x + (asteroid['x'] - (self.x + 3))
        for asteroid in self.bottom_asteroids:
            asteroid['x'] = self.x + (asteroid['x'] - (self.x + 3))
        # Update error positions
        for error_pos in self.error_positions:
            error_pos['x'] -= 3

    def draw(self, screen):
        # Draw asteroids in top area
        for asteroid in self.top_asteroids:
            screen.blit(asteroid['img'], (asteroid['x'], asteroid['y']))
        
        # Draw asteroids in bottom area  
        for asteroid in self.bottom_asteroids:
            screen.blit(asteroid['img'], (asteroid['x'], asteroid['y']))
            
        # Draw single error symbols in varying positions
        for error_pos in self.error_positions:
            screen.blit(self.error_img, (error_pos['x'], error_pos['y']))

    def off_screen(self):
        return self.x < -PIPE_WIDTH

    def collide(self, bird):
        return self.top_rect.colliderect(bird.rect) or self.bottom_rect.colliderect(bird.rect)

    def hit_symbol(self, bird):
        return self.gap_rect.colliderect(bird.rect)



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
            if sound_path and os.path.exists(sound_path):
                sounds[sound_name] = pygame.mixer.Sound(sound_path)
                print(f"Loaded sound: {sound_name}")
            else:
                if sound_path:
                    print(f"Sound file not found: {sound_path}")
                else:
                    print(f"Sound disabled: {sound_name}")
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
            if is_muted:
                pygame.mixer.music.set_volume(0.0)  # muted
            else:
                pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print("Background music loaded and playing")
        else:
            print(f"Background music file not found: {BACKGROUND_MUSIC_PATH}")
    except pygame.error as e:
        print(f"Error loading background music: {e}")

def play_sound(sounds, sound_name, volume=1.0):
    """Play a sound effect if it exists and not muted"""
    if is_muted:
        return  # don't play any sounds if muted by LD
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
    """Load trivia questions from JSON file and filter by enabled difficulties"""
    with open("assets/trivia.json", "r") as f:
        trivia_data = json.load(f)
    
    # filter trivia based on LD flags
    return trivia_data

def filter_trivia_by_client(trivia_data, ld_client):
    """Filter trivia based on LaunchDarkly client (called from main)"""
    if ld_client:
        trivia_data = ld_client.filter_trivia_by_difficulty(trivia_data)
    
    return trivia_data

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
        
        # Add "Click anywhere to start" text (updated per designer feedback)
        font = pygame.font.Font(FONT_PATH, 36)
        text = render_text_with_outline(font, 'Click anywhere to start!', WHITE, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(text, text_rect)
        
        pygame.display.update()

def show_instructions_screen(screen, clock):
    """Display the instructions screen and wait for user input to continue"""
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        # Fill screen with dark background
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Title
        title_font = pygame.font.Font(FONT_PATH, 48)
        title_text = render_text_with_outline(title_font, 'HOW TO PLAY', WHITE, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Instructions text
        instructions = [
            "Gameplay:",
            "",
            "• Press SPACE to jump",
            "",
            "• Dodge obstacles representing SDK misconfigurations",
            "",
            "• Trivia modals will pause the game periodically",
            "  with tips and questions",
            "",
            "• Survive as long as possible!",
            "",
            "",
            "Click anywhere to start playing..."
        ]
        
        # Draw instructions
        font = pygame.font.Font(FONT_PATH, 32)
        small_font = pygame.font.Font(FONT_PATH, 28)
        
        y_start = 180
        line_height = 40
        
        for i, line in enumerate(instructions):
            if line.startswith("•"):
                # Bullet points - use smaller font and indent
                text = render_text_with_outline(small_font, line, WHITE, BLACK)
                x_pos = SCREEN_WIDTH // 2 - 200
            elif line == "Gameplay:" or line == "Click anywhere to start playing...":
                # Main headers
                text = render_text_with_outline(font, line, WHITE, BLACK)
                x_pos = SCREEN_WIDTH // 2 - text.get_width() // 2
            elif line.startswith("  "):
                # Sub-bullet points - smaller font, more indent
                text = render_text_with_outline(small_font, line, (200, 200, 200), BLACK)
                x_pos = SCREEN_WIDTH // 2 - 180
            else:
                # Regular text
                text = render_text_with_outline(font, line, WHITE, BLACK)
                x_pos = SCREEN_WIDTH // 2 - text.get_width() // 2
            
            screen.blit(text, (x_pos, y_start + i * line_height))
        
        pygame.display.update()

def draw_window(screen, bird, pipes, score, hit_count=0):
    # Draw galaxy background maintaining aspect ratio to prevent distortion
    bg_width, bg_height = background_img.get_size()
    scale_x = SCREEN_WIDTH / bg_width
    scale_y = SCREEN_HEIGHT / bg_height
    scale = min(scale_x, scale_y)  # Use smaller scale to maintain aspect ratio
    
    new_width = int(bg_width * scale)
    new_height = int(bg_height * scale)
    scaled_bg = pygame.transform.smoothscale(background_img, (new_width, new_height))
    
    # Center the background if it doesn't fill the entire screen
    x_offset = (SCREEN_WIDTH - new_width) // 2
    y_offset = (SCREEN_HEIGHT - new_height) // 2
    screen.fill(BLACK)  # Fill with black in case background doesn't cover entire screen
    screen.blit(scaled_bg, (x_offset, y_offset))
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
    
    # initializing LD client
    ld_client = LaunchDarklyClient()
    
    # set global mute state from LD flag
    global is_muted
    is_muted = ld_client and ld_client.should_mute_sound()
    
    # Load sounds and music
    sounds = load_sounds()
    
    # LD flag to control initial sound volume
    if is_muted:
        set_sound_volume(sounds, 0.0)  # muted
        print("Sound muted by LaunchDarkly flag")
        # Also mute background music
        load_background_music()
        pygame.mixer.music.set_volume(0.0)
    else:
        set_sound_volume(sounds, 0.7)  # at normal volume
        print("Sound enabled")
        load_background_music()
    
    # Show splash screen first
    show_splash_screen(screen, clock)
    
    # Show instructions screen
    show_instructions_screen(screen, clock)
    
    # Load background image and trivia data
    global background_img
    background_img = pygame.image.load(BKG_IMG_PATH).convert()
    trivia_data = load_trivia()
    
    # filter trivia based on LD flags
    trivia_data = filter_trivia_by_client(trivia_data, ld_client)
    
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
                    
                    # Check if player has hit 10 obstacles
                    if hit_count >= 10:
                        game_over = True
                        play_sound(sounds, 'game_over')

                if pipe.hit_symbol(bird) and not hasattr(pipe, 'score'):
                    pipe.score = True
                    # Show trivia modal
                    if trivia_data:
                        trivia_item = random.choice(trivia_data)
                        show_trivia_modal(screen, clock, trivia_item['text'])
                        
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
            # Draw game over overlay using the provided game over screen
            try:
                game_over_img = pygame.image.load("assets/Game Over Text.png").convert_alpha()
                # Scale the game over overlay to fit the screen appropriately
                overlay_width = SCREEN_WIDTH - 100  # Leave some margin
                overlay_height = game_over_img.get_height() * (overlay_width / game_over_img.get_width())
                scaled_overlay = pygame.transform.smoothscale(game_over_img, (int(overlay_width), int(overlay_height)))
                
                # Center the overlay on screen
                overlay_x = (SCREEN_WIDTH - overlay_width) // 2
                overlay_y = (SCREEN_HEIGHT - overlay_height) // 2
                screen.blit(scaled_overlay, (overlay_x, overlay_y))
                
                # Add restart instruction below the overlay
                font = pygame.font.Font(FONT_PATH, 36)
                restart_text = render_text_with_outline(font, 'Press R to Restart', WHITE, BLACK)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, overlay_y + overlay_height + 50))
                screen.blit(restart_text, restart_rect)
            except:
                # Fallback to text-based game over if image fails to load
                font = pygame.font.Font(FONT_PATH, 48)
                if hit_count >= 10:
                    over_text = render_text_with_outline(font, '10 Hits Reached! Press R to Restart', WHITE, BLACK)
                else:
                    over_text = render_text_with_outline(font, 'Game Over! Press R to Restart', WHITE, BLACK)
                screen.blit(over_text, (20, SCREEN_HEIGHT // 2 - 24))
            pygame.display.update()
    
    if ld_client:
        ld_client.close()
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
