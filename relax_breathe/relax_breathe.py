import pygame
import time
import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Initialize pygame
def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Yoga Breathing Exercise")
    
    # Initialize the mixer for sound
    pygame.mixer.init()
    
    return screen

def load_sounds():
    in_sound = pygame.mixer.Sound(resource_path("in.mp3"))
    hold_sound = pygame.mixer.Sound(resource_path("hold.mp3"))
    out_sound = pygame.mixer.Sound(resource_path("out.mp3"))
    return in_sound, hold_sound, out_sound


# Define the colors and setup
def setup_colors():
    return {
        'background_color': (30, 30, 30),
        'ball_color': (247, 230, 227),  # Light blush (#F7E6E3)
        'mustard_yellow': (191, 174, 74),  # Mustard yellow (#BFAE4A)
        'soft_pink': (224, 149, 146),  # Soft pink (#E09592)
        'light_grey': (228, 228, 226),  # Light grey (#E4E4E2)
        'corner_dot_color': (71, 72, 68),  # Dark grey (#474844)
        'text_color': (255, 255, 255)  # White
    }

def setup_positions():
    screen_width, screen_height = 800, 600
    center_x, center_y = screen_width // 2, screen_height // 2
    square_size = 400
    top_left = (center_x - square_size // 2, center_y - square_size // 2)
    top_right = (center_x + square_size // 2, center_y - square_size // 2)
    bottom_right = (center_x + square_size // 2, center_y + square_size // 2)
    bottom_left = (center_x - square_size // 2, center_y + square_size // 2)
    return top_left, top_right, bottom_right, bottom_left, center_x, center_y

def render_text(screen, font, text, center_x, center_y, alpha):
    text_surface = font.render(text, True, (255, 255, 255))
    text_surface.set_alpha(alpha)
    screen.blit(text_surface, text_surface.get_rect(center=(center_x, center_y)))

# Calculate fade-in effect and determine which text and line color to show
def determine_phase(elapsed_time, side_duration, positions, colors, sounds, last_phase):
    # Unpack sounds tuple
    in_sound, hold_sound, out_sound = sounds
    top_left, top_right, bottom_right, bottom_left = positions[:4]
    total_cycle_time = side_duration * 4

    # Breathing in phase (IN)
    if elapsed_time <= side_duration:
        fraction = elapsed_time / side_duration
        ball_x = top_left[0] + fraction * (top_right[0] - top_left[0])
        ball_y = top_left[1]
        if last_phase != "IN":
            in_sound.play()  # Play the in sound
        return "IN", colors['mustard_yellow'], (ball_x, ball_y), fraction

    # Holding breath phase (HOLD)
    elif elapsed_time <= 2 * side_duration:
        fraction = (elapsed_time - side_duration) / side_duration
        ball_x = top_right[0]
        ball_y = top_right[1] + fraction * (bottom_right[1] - top_right[1])
        if last_phase != "HOLD":
            hold_sound.play()  # Play the hold sound
        return "HOLD", colors['soft_pink'], (ball_x, ball_y), fraction

    # Breathing out phase (OUT)
    elif elapsed_time <= 3 * side_duration:
        fraction = (elapsed_time - 2 * side_duration) / side_duration
        ball_x = bottom_right[0] - fraction * (bottom_right[0] - bottom_left[0])
        ball_y = bottom_right[1]
        if last_phase != "OUT":
            out_sound.play()  # Play the out sound
        return "OUT", colors['light_grey'], (ball_x, ball_y), fraction

    # Holding breath phase again (HOLD)
    else:
        fraction = (elapsed_time - 3 * side_duration) / side_duration
        ball_x = bottom_left[0]
        ball_y = bottom_left[1] - fraction * (bottom_left[1] - top_left[1])
        if last_phase != "HOLD":
            hold_sound.play()  # Play the hold sound again
        return "HOLD", colors['soft_pink'], (ball_x, ball_y), fraction

def draw_square(screen, positions, colors):
    top_left, top_right, bottom_right, bottom_left = positions[:4]
    pygame.draw.line(screen, colors['mustard_yellow'], top_left, top_right, 5)   # Top
    pygame.draw.line(screen, colors['soft_pink'], top_right, bottom_right, 5)    # Right
    pygame.draw.line(screen, colors['light_grey'], bottom_right, bottom_left, 5) # Bottom
    pygame.draw.line(screen, colors['soft_pink'], bottom_left, top_left, 5)      # Left

def draw_ball(screen, ball_pos, ball_color):
    pygame.draw.circle(screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), 20)

def draw_corner_dots(screen, positions, corner_dot_color):
    for pos in positions[:4]:
        pygame.draw.circle(screen, corner_dot_color, pos, 10)

# Main game loop
def game_loop(screen, colors, positions, sounds):
    font = pygame.font.Font(None, 100)  # Font size for the breathing instructions
    side_duration = 4
    running = True
    start_time = time.time()
    last_phase = ""

    while running:
        screen.fill(colors['background_color'])
        elapsed_time = (time.time() - start_time) % (side_duration * 4)

        # Determine phase and render text, ball position, etc.
        text, line_color, ball_pos, alpha_fraction = determine_phase(elapsed_time, side_duration, positions, colors, sounds, last_phase)
        alpha = int(alpha_fraction * 255)  # Fade effect for text
        last_phase = text  # Keep track of the last phase to avoid playing the sound multiple times

        # Draw the elements
        draw_square(screen, positions, colors)
        draw_ball(screen, ball_pos, colors['ball_color'])
        render_text(screen, font, text, positions[4], positions[5], alpha)  # positions[4], positions[5] are center_x, center_y
        draw_corner_dots(screen, positions, colors['corner_dot_color'])

        # Update the display
        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

# Main function
def main():
    screen = init_pygame()
    colors = setup_colors()
    positions = setup_positions()
    sounds = load_sounds()  # Load the sounds
    game_loop(screen, colors, positions, sounds)

# Run the program
if __name__ == "__main__":
    main()
