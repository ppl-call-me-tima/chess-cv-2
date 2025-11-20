class ScreenManager:
    def __init__(self, surface):
        self.surface = surface
        self.screens = {}
        self.current_screen = None

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def set_screen(self, name):
        if name in self.screens:
            self.current_screen = self.screens[name]
            self.current_screen.on_enter()

    def handle_event(self, event):
        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, time_delta):
        if self.current_screen:
            self.current_screen.update(time_delta)

    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)
