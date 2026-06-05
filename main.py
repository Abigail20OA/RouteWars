import pygame


WIDTH = 1000
HEIGHT = 650
TITLE = "ROUTE WARS"
BACKGROUND_COLOR = (90, 90, 90)
TEXT_COLOR = (245, 245, 245)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 42, bold=True)
    text_surface = font.render("ROUTE WARS - PROTOTIPO INICIAL", True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
