import pygame
import sys
import OpenGL.GL as GL


from core.input import Input
from core.utils import Utils


class Base:
    def __init__(self, screen_size=(512, 512)):
        # Initialize all pygame modules
        pygame.init()
        self.screen_size = screen_size
        # Indicate rendering details
        self.display_flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.FULLSCREEN
        #self.display_flags = pygame.DOUBLEBUF | pygame.OPENGL

        # Initialize buffers to perform antialiasing
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        # Use a core OpenGL profile for cross-platform compatibility
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        # Create and display the window
        self._screen = pygame.display.set_mode((0,0), self.display_flags)
        #self._screen = pygame.display.set_mode(self.screen_size, self.display_flags)
        # Set the text and icon that appears in the title bar of the window
        pygame.display.set_caption("BeachRush")
        icon = pygame.image.load('images/icon.png')
        pygame.display.set_icon(icon)
        # Determine if main loop is active
        self._running = True
        # Manage time-related data and operations
        self._clock = pygame.time.Clock()
        # Manage user input
        self._input = Input()
        # number of seconds application has been running
        self._time = 0
        # 
        self.resize = False

        pygame.mouse.set_visible(False)
        # Print the system information
        Utils.print_system_info()

    @property
    def delta_time(self):
        return self._delta_time

    @property
    def input(self):
        return self._input

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    def initialize(self):
        """ Implement by extending class """
        pass

        '''
        
    def toggle_fullscreen(self):
        if self._screen.get_flags() & pygame.FULLSCREEN:

            self.display_flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
            self._screen = pygame.display.set_mode(self.screen_size, self.display_flags)
        else:
            self.display_flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE | pygame.FULLSCREEN
            self._screen = pygame.display.set_mode((0, 0), self.display_flags)
            '''

    def update(self):
        """ Implement by extending class """
        pass

    def run(self):
        # Startup #
        self.initialize()
        # main loop #
        while self._running:
            # process input #
            self._input.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    
            
            if self._input.quit:
                self._running = False

            #if self._input._fullscreen:
                #self.toggle_fullscreen()

            pygame.mouse.set_pos(self._screen.get_width() // 2, self._screen.get_height() // 2)
            # seconds since iteration of run loop
            self._delta_time = self._clock.get_time() / 1000
            # Increment time application has been running
            self._time += self._delta_time
            # Update #
            self.update()

            if self._input._fullscreen:
                self._input._fullscreen = False

            # Render #
            # Display image on screen
            pygame.display.flip()
            # Pause if necessary to achieve 60 FPS
            self._clock.tick(60)
        # Shutdown #
        pygame.quit()
        sys.exit()
