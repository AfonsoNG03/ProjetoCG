import pygame
<<<<<<< HEAD
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
=======
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Initialize Pygame
pygame.init()

# Set the display dimensions
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
# Use a core OpenGL profile for cross-platform compatibility
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

# Set up the OpenGL perspective
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -2)


# Function to render text
def draw_text(text, position):
    font = pygame.font.Font(None, 32)
    text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2f(*position)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Set text color
    glColor3f(1.0, 1.0, 1.0)

    # Draw text
    draw_text("Hello, OpenGL!", (0.15, 0.65))

    # Update the display
    pygame.display.flip()
    pygame.time.wait(10)
>>>>>>> Afonso
