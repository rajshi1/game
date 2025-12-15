import pygame
import random
import sys
import os
import asyncio

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

# --- Web-Safe Asset Loading ---
def load_asset(name, type="image"):
    if os.path.exists(name):
        if type == "image":
            return pygame.image.load(name).convert_alpha()
        elif type == "sound":
            return pygame.mixer.Sound(name)
    return None

# Load Assets
bg_surface = load_asset("background.png")
bird_surface = load_asset("bird.png")
pipe_surface = load_asset("pipe.png")
base_surface = load_asset("base.png")
intro_surface = load_asset("intro.png")
gameover_surface = load_asset("gameover.png")

jump_sound = load_asset("jump.wav", "sound")
score_sound = load_asset("score.wav", "sound")
hit_sound = load_asset("hit.wav", "sound")

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
START_SPEED = 3
MAX_SPEED = 8
pipe_list = []
scored_pipes = []

# --- Drawing Functions ---
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

def draw_bird(bird_rect, bird_movement):
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

def move_pipes(pipes, speed):
    for pipe in pipes:
        pipe.centerx -= speed
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

def check_collision(pipes, bird_rect):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            if hit_sound: hit_sound.play()
            return True
    if bird_rect.top <= -50 or bird_rect.bottom >= FLOOR_HEIGHT:
        if hit_sound: hit_sound.play()
        return True
    return False

def score_display(game_state, score, high_score):
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
        
        restart_text = small_font.render("Press SPACE or TAP to Restart", True, WHITE)
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
    
    msg = small_font.render("Press SPACE or TAP to Start", True, WHITE)
    msg_rect = msg.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
    bg_rect = pygame.Rect(msg_rect.x - 10, msg_rect.y - 5, msg_rect.width + 20, msg_rect.height + 10)
    pygame.draw.rect(screen, BLACK, bg_rect)
    screen.blit(msg, msg_rect)


# --- Main Loop (Mobile Compatible) ---
async def main():
    bird_movement = 0
    game_state = "start"
    score = 0
    high_score = 0
    base_x_pos = 0
    game_speed = START_SPEED
    
    bird_rect = pygame.Rect(50, 300, 34, 24)
    global pipe_list, scored_pipes
    
    SPAWNPIPE = pygame.USEREVENT
    current_spawn_rate = 1200
    pygame.time.set_timer(SPAWNPIPE, current_spawn_rate)

    while True:
        # Detect Input (Tap or Key)
        jump_command = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Check for Spacebar
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    jump_command = True
            
            # Check for Mouse Click / Screen Tap
            if event.type == pygame.MOUSEBUTTONDOWN:
                jump_command = True

            if event.type == SPAWNPIPE and game_state == "active":
                pipe_list.extend(create_pipe())

        # Logic using the single "jump_command" flag
        if jump_command:
            if game_state == "start":
                game_state = "active"
                bird_movement = 0
                pipe_list.clear()
                scored_pipes.clear()
                score = 0
                bird_rect.center = (50, 300)
                bird_movement = -6
                game_speed = START_SPEED
                current_spawn_rate = 1200
                pygame.time.set_timer(SPAWNPIPE, current_spawn_rate)
                if jump_sound: jump_sound.play()
                
            elif game_state == "active":
                bird_movement = -6
                if jump_sound: jump_sound.play()
                
            elif game_state == "game_over":
                game_state = "start"

        draw_background()

        if game_state == "start":
            base_x_pos -= 1
            draw_base(base_x_pos)
            if base_x_pos <= -SCREEN_WIDTH:
                base_x_pos = 0
            show_start_screen()

        elif game_state == "active":
            if game_speed < MAX_SPEED:
                game_speed += 0.002
                new_spawn_rate = int(1200 - (game_speed * 50))
                if new_spawn_rate < 600: new_spawn_rate = 600
                if abs(new_spawn_rate - current_spawn_rate) > 50:
                    current_spawn_rate = new_spawn_rate
                    pygame.time.set_timer(SPAWNPIPE, current_spawn_rate)

            bird_movement += gravity
            bird_rect.centery += bird_movement
            draw_bird(bird_rect, bird_movement)
            
            pipe_list = move_pipes(pipe_list, game_speed)
            draw_pipes(pipe_list)

            base_x_pos -= game_speed
            draw_base(base_x_pos)
            if base_x_pos <= -SCREEN_WIDTH:
                base_x_pos = 0

            if check_collision(pipe_list, bird_rect):
                game_state = "game_over"
                if score > high_score: high_score = score
            
            for pipe in pipe_list:
                if pipe.bottom >= FLOOR_HEIGHT and pipe.centerx < bird_rect.centerx and pipe not in scored_pipes:
                    score += 1
                    scored_pipes.append(pipe)
                    if score_sound: score_sound.play()

            if pipe_list and pipe_list[0].right < -10:
                 pipe_list.pop(0)

            score_display('active', score, high_score)

        elif game_state == "game_over":
            draw_pipes(pipe_list)
            draw_base(base_x_pos)
            draw_bird(bird_rect, bird_movement)
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0,0))
            
            score_display('game_over', score, high_score)
        
        pygame.display.update()
        clock.tick(120)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
