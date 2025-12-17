class BaseScreen:
    def __init__(self, manager):
        self.manager = manager
    
    def on_enter(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass
