import pygame
import sys

class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)
        self.option_boxes = []  # List to hold the option boxes
        self.options = ["Start Game", "Scoreboard", "Exit"]
        self.selected_option = 0
        self.background_image = pygame.image.load("images/2.png").convert()


    def draw_menu(self):
        # Imagem de fundo
        self.screen.blit(self.background_image, (0, 0))

        # Dimensões dos retângulos
        box_width = 300
        box_height = 80
        margin = 20
        total_height = len(self.options) * (box_height + margin) - margin
        start_y = (self.screen.get_height() - total_height) // 2

        # Clear option boxes list
        self.option_boxes = []

        for i, option in enumerate(self.options):
            box_x = (self.screen.get_width() - box_width) // 2
            box_y = start_y + i * (box_height + margin)

            # Draw the option box
            option_box = pygame.Rect(box_x, box_y, box_width, box_height)
            
            # Cor da caixa selecionada
            if i == self.selected_option:
                color = (255, 87, 51)  # Alaranjado para selecionada
            else:
                color = (51, 125, 255)  # Azulesco para não selecionada
            pygame.draw.rect(self.screen, color, option_box)

            # Draw the option text
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=option_box.center)
            self.screen.blit(text, text_rect)

            # Add option box to the list
            self.option_boxes.append(option_box)

    def show_Scoreboard(self):
        # Load the times from the file
        try:
            with open("time_records.txt", "r") as file:
                times = []
                for line in file:
                    try:
                        time_str = line.strip().replace("Time: ", "").replace(" seconds", "")
                        time = float(time_str)
                        print(f"Read time: {time}")  # Debug printa cada linha lida
                        times.append(time)
                    except ValueError:
                        print(f"Invalid entry skipped: {line.strip()}")  # Debug: printa linhas inválidas e
                        continue
                times = sorted(times)[:10] 
        except FileNotFoundError:
            print("File not found: time_records.txt")  # Debug não encontrou nada
            times = []

        # Debug: linhas
        print("Sorted times:")
        for time in times:
            print(time)

        self.screen.fill((0, 0, 0))
        title = self.font.render("Scoreboard", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 50))

        for i, time in enumerate(times):
            text = self.font.render(f"{i+1}. {time:.2f} s", True, (255, 255, 255))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 150 + i * 50))

        # De volta ao menu
        instruction = self.font.render("Press ESC to return to menu", True, (255, 255, 255))
        self.screen.blit(instruction, (self.screen.get_width() // 2 - instruction.get_width() // 2, 650))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

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
                            self.show_Scoreboard()
                        elif self.selected_option == 2:
                            pygame.quit()
                            sys.exit()

            self.draw_menu()
            pygame.display.flip()
            self.clock.tick(60)
