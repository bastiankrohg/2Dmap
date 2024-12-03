import sys 
import pygame
from components.map_management import load_map, reset_map
from components.constants import MENU_FONT_SIZE

pygame.font.init()
menu_font = pygame.font.SysFont(None, MENU_FONT_SIZE)


def draw_button(screen, text, x, y, width, height, color, text_color):
    """Draws a button with text."""
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = menu_font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def menu_screen(screen, auto_save):
    """Main menu screen."""
    running = True
    selected_map = None

    buttons = [
        ("Load a Saved Map", 200, 150, 400, 50, (50, 150, 150)),
        ("Start with a New Map", 200, 230, 400, 50, (150, 50, 50)),
        (f"Toggle Auto-Save: {'ON' if auto_save else 'OFF'}", 200, 310, 400, 50, (100, 100, 200)),
        ("Exit", 200, 390, 400, 50, (200, 100, 100)),
    ]

    while running:
        screen.fill((30, 30, 30))

        # Draw title
        title_text = menu_font.render("Main Menu", True, (255, 255, 255))
        screen.blit(title_text, (400 - title_text.get_width() // 2, 50))

        # Draw buttons
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        for i, (text, x, y, width, height, color) in enumerate(buttons):
            draw_button(screen, text, x, y, width, height, color, (255, 255, 255))

            if x < mouse[0] < x + width and y < mouse[1] < y + height:
                pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height), 3)  # Hover effect
                if click[0]:  # Left mouse button pressed
                    if i == 0:  # Load a saved map
                        return "load", auto_save
                    elif i == 1:  # Start new map
                        reset_map()
                        return "new", auto_save
                    elif i == 2:  # Toggle auto-save
                        auto_save = not auto_save
                        buttons[2] = (f"Toggle Auto-Save: {'ON' if auto_save else 'OFF'}", 200, 310, 400, 50, (100, 100, 200))
                    elif i == 3:  # Exit
                        pygame.quit()
                        sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Graceful exit on window close
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Exit menu on ESC key

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    return selected_map, auto_save