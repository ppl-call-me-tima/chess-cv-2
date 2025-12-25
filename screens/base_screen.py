class BaseScreen:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
    
    def on_enter(self):
        pass

    async def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass
