import pygame
import sys

class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)
        self.options = ["Start Game", "Exit"]
        self.selected_option = 0

    def draw_menu(self):
        self.screen.fill((0, 0, 0))
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = (255, 0, 0)
            else:
                color = (100, 100, 100)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 200 + i * 100))
            self.screen.blit(text, text_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:
                            return "start_game"
                        elif self.selected_option == 1:
                            pygame.quit()
                            sys.exit()

            self.draw_menu()
            pygame.display.flip()
            self.clock.tick(60)