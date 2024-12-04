import pygame
from components.constants import WIDTH, HEIGHT, BACKGROUND_COLOR
from components.map_management import get_last_used_map, list_maps

def menu_screen():
    """
    Display the main menu and return the user's selection.
    """
    screen = pygame.display.get_surface()
    font = pygame.font.Font(None, 36)
    options = ["Load Map", "Start New"]
    current_selection = 0

    while True:
        screen.fill(BACKGROUND_COLOR)
        title = font.render("Rover Mapping Menu", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == current_selection else (150, 150, 150)
            text = font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 50))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    current_selection = (current_selection + 1) % len(options)
                elif event.key == pygame.K_UP:
                    current_selection = (current_selection - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[current_selection] == "Load Map":
                        last_map = get_last_used_map()
                        return last_map if last_map else list_maps()[0]
                    elif options[current_selection] == "Start New":
                        return None