import pygame
import random
import sys
import os

# --- Initialization ---
pygame.init()
pygame.mixer.init()

# --- Configuration ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FLOOR_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flippy Bird Pro")
clock = pygame.time.Clock()

# --- Defaults ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
PIPE_GREEN = (34, 139, 34)
BIRD_YELLOW = (255, 215, 0)
FLOOR_COLOR = (210, 180, 140)
font = pygame.font.SysFont('Arial', 40, bold=True)
small_font = pygame.font.SysFont('Arial', 20)

# ---------------------------------------------------------
# YOUR SPECIFIC FOLDER PATH
# I have set this to the path you provided.
# ---------------------------------------------------------
GAME_FOLDER = "/Users/rajankumar/Desktop/flippybird"

def load_asset(name, type="image"):
    # We look specifically in your folder
    path = os.path.join(GAME_FOLDER, name)

    if os.path.exists(path):
        print(f"SUCCESS: Found {name}")
        if type == "image":
            return pygame.image.load(path).convert_alpha()
        elif type == "sound":
            return pygame.mixer.Sound(path)
    else:
        # If this prints, the file is NOT in the folder, or named differently
        print(f"ERROR: Could not find '{name}' in {GAME_FOLDER}")
        return None

# Load Assets
print("--- Loading Assets ---")
bg_surface = load_asset("background.png")
bird_surface = load_asset("bird.png")
pipe_surface = load_asset("pipe.png")
base_surface = load_asset("base.png")
intro_surface = load_asset("intro.png")
gameover_surface = load_asset("gameover.png")

jump_sound = load_asset("jump.wav", "sound")
score_sound = load_asset("score.wav", "sound")
hit_sound = load_asset("hit.wav", "sound")
print("----------------------")

# Resize Assets
if bg_surface:
    bg_surface = pygame.transform.scale(bg_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
if bird_surface:
    bird_surface = pygame.transform.scale(bird_surface, (34, 24))
if base_surface:
    base_surface = pygame.transform.scale(base_surface, (SCREEN_WIDTH, 100))
if intro_surface:
    intro_surface = pygame.transform.scale(intro_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Game Variables ---
gravity = 0.25
bird_movement = 0
game_state = "start"
score = 0
high_score = 0
base_x_pos = 0

bird_rect = pygame.Rect(50, 300, 34, 24)
pipe_list = []
scored_pipes = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

def draw_background():
    if bg_surface:
        screen.blit(bg_surface, (0, 0))
    else:
        screen.fill(SKY_BLUE)

def draw_base(x_pos):
    if base_surface:
        screen.blit(base_surface, (x_pos, FLOOR_HEIGHT))
        screen.blit(base_surface, (x_pos + SCREEN_WIDTH, FLOOR_HEIGHT))
    else:
        pygame.draw.rect(screen, FLOOR_COLOR, (0, FLOOR_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_HEIGHT))
        pygame.draw.line(screen, BLACK, (0, FLOOR_HEIGHT), (SCREEN_WIDTH, FLOOR_HEIGHT), 2)

def draw_bird():
    if bird_surface:
        rotated_bird = pygame.transform.rotozoom(bird_surface, -bird_movement * 3, 1)
        screen.blit(rotated_bird, bird_rect)
    else:
        pygame.draw.rect(screen, BIRD_YELLOW, bird_rect)
        pygame.draw.rect(screen, BLACK, bird_rect, 2)

def create_pipe():
    random_pipe_pos = random.choice([200, 250, 300, 350, 400])
    bottom_pipe = pygame.Rect(SCREEN_WIDTH + 20, random_pipe_pos, 50, FLOOR_HEIGHT - random_pipe_pos)
    top_pipe = pygame.Rect(SCREEN_WIDTH + 20, random_pipe_pos - 150 - FLOOR_HEIGHT, 50, FLOOR_HEIGHT)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 3
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe_surface:
            if pipe.bottom >= FLOOR_HEIGHT:
                scaled_pipe = pygame.transform.scale(pipe_surface, (pipe.width, pipe.height))
                screen.blit(scaled_pipe, pipe)
            else:
                scaled_pipe = pygame.transform.scale(pipe_surface, (pipe.width, pipe.height))
                flipped_pipe = pygame.transform.flip(scaled_pipe, False, True)
                screen.blit(flipped_pipe, pipe)
        else:
            pygame.draw.rect(screen, PIPE_GREEN, pipe)
            pygame.draw.rect(screen, BLACK, pipe, 2)

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            if hit_sound: hit_sound.play()
            return True
    if bird_rect.top <= -50 or bird_rect.bottom >= FLOOR_HEIGHT:
        if hit_sound: hit_sound.play()
        return True
    return False

def score_display(game_state):
    if game_state == 'active':
        score_surf = font.render(str(int(score)), True, WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH / 2, 50))
        score_shadow = font.render(str(int(score)), True, BLACK)
        screen.blit(score_shadow, (score_rect.x+2, score_rect.y+2))
        screen.blit(score_surf, score_rect)
    
    if game_state == 'game_over':
        if gameover_surface:
            go_rect = gameover_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
            screen.blit(gameover_surface, go_rect)
        else:
            over_text = font.render("GAME OVER", True, WHITE)
            over_rect = over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
            over_shadow = font.render("GAME OVER", True, BLACK)
            screen.blit(over_shadow, (over_rect.x+2, over_rect.y+2))
            screen.blit(over_text, over_rect)

        high_score_surf = small_font.render(f'Score: {int(score)} | Best: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
        bg_rect = pygame.Rect(high_score_rect.x - 10, high_score_rect.y - 5, high_score_rect.width + 20, high_score_rect.height + 10)
        pygame.draw.rect(screen, BLACK, bg_rect)
        screen.blit(high_score_surf, high_score_rect)
        
        restart_text = small_font.render("Press SPACE to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 90))
        screen.blit(restart_text, restart_rect)

def show_start_screen():
    if intro_surface:
        screen.blit(intro_surface, (0,0))
    else:
        screen.fill(SKY_BLUE)
        title = font.render("FLIPPY BIRD", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
        screen.blit(title, title_rect)
    
    msg = small_font.render("Press SPACE to Start", True, WHITE)
    msg_rect = msg.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
    bg_rect = pygame.Rect(msg_rect.x - 10, msg_rect.y - 5, msg_rect.width + 20, msg_rect.height + 10)
    pygame.draw.rect(screen, BLACK, bg_rect)
    screen.blit(msg, msg_rect)

# --- Main Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "start":
                    game_state = "active"
                    bird_movement = 0
                    pipe_list.clear()
                    scored_pipes.clear()
                    score = 0
                    bird_rect.center = (50, 300)
                    bird_movement = -6
                    if jump_sound: jump_sound.play()
                elif game_state == "active":
                    bird_movement = -6
                    if jump_sound: jump_sound.play()
                elif game_state == "game_over":
                    game_state = "start"

        if event.type == SPAWNPIPE and game_state == "active":
            pipe_list.extend(create_pipe())

    draw_background()

    if game_state == "start":
        base_x_pos -= 1
        draw_base(base_x_pos)
        if base_x_pos <= -SCREEN_WIDTH:
            base_x_pos = 0
        show_start_screen()

    elif game_state == "active":
        bird_movement += gravity
        bird_rect.centery += bird_movement
        draw_bird()
        
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        base_x_pos -= 3
        draw_base(base_x_pos)
        if base_x_pos <= -SCREEN_WIDTH:
            base_x_pos = 0

        if check_collision(pipe_list):
            game_state = "game_over"
            if score > high_score: high_score = score
        
        for pipe in pipe_list:
            if pipe.bottom >= FLOOR_HEIGHT and pipe.centerx < bird_rect.centerx and pipe not in scored_pipes:
                score += 1
                scored_pipes.append(pipe)
                if score_sound: score_sound.play()

        if pipe_list and pipe_list[0].right < -10:
             pipe_list.pop(0)

        score_display('active')

    elif game_state == "game_over":
        draw_pipes(pipe_list)
        draw_base(base_x_pos)
        draw_bird()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0,0))
        
        score_display('game_over')
    
    pygame.display.update()
    clock.tick(120)