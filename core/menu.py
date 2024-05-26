import pygame
import sys
import os

class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)
        self.option_boxes = []
        self.options = ["Start Game", "Scoreboard", "Exit"]
        self.selected_option = 0
        self.background_image = pygame.image.load("images/2.png").convert()
        self.mouse_active = False
        self.last_mouse_pos = pygame.mouse.get_pos()

        music_file = 'music/beachbeat.mp3'
        if not os.path.isfile(music_file):
            print(f"Music file not found: {music_file}")
        else:
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                print(f"Playing music: {music_file}")
            except pygame.error as e:
                print(f"Failed to load music file: {music_file}, error: {e}")

    def draw_menu(self):
        self.screen.blit(self.background_image, (0, 0))

        box_width = 300
        box_height = 80
        margin = 20
        total_height = len(self.options) * (box_height + margin) - margin
        start_y = (self.screen.get_height() - total_height) // 2

        self.option_boxes = []

        for i, option in enumerate(self.options):
            box_x = (self.screen.get_width() - box_width) // 2
            box_y = start_y + i * (box_height + margin)

            option_box = pygame.Rect(box_x, box_y, box_width, box_height)
            
            if i == self.selected_option:
                color = (255, 87, 51)
            else:
                color = (51, 125, 255)
            pygame.draw.rect(self.screen, color, option_box)

            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=option_box.center)
            self.screen.blit(text, text_rect)

            self.option_boxes.append(option_box)

    def show_Scoreboard(self):
        try:
            with open("time_records.txt", "r") as file:
                times = []
                for line in file:
                    try:
                        time_str = line.strip().replace("Time: ", "").replace(" seconds", "")
                        time = float(time_str)
                        times.append(time)
                    except ValueError:
                        continue
                times = sorted(times)[:10] 
        except FileNotFoundError:
            times = []

        self.screen.fill((0, 0, 0))
        title = self.font.render("Scoreboard", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 50))

        for i, time in enumerate(times):
            text = self.font.render(f"{i+1}. {time:.2f} s", True, (255, 255, 255))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 150 + i * 50))

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
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            if mouse_pos != self.last_mouse_pos:
                self.mouse_active = True
                self.last_mouse_pos = mouse_pos
            else:
                self.mouse_active = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.mouse_active = False
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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True

            for i, option_box in enumerate(self.option_boxes):
                if option_box.collidepoint(mouse_pos):
                    if self.mouse_active:
                        self.selected_option = i
                    if mouse_clicked:
                        self.selected_option = i
                        if i == 0:
                            return "start_game"
                        elif i == 1:
                            self.show_Scoreboard()
                        elif i == 2:
                            pygame.quit()
                            sys.exit()

            self.draw_menu()
            pygame.display.flip()
            pygame.display.set_caption("BeachRush")
            icon = pygame.image.load('images/icon.png')
            pygame.display.set_icon(icon)
            self.clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((800, 600))
    menu = GameMenu(screen)
    menu.run()