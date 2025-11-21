class BaseScreen:
    def __init__(self, manager):
        self.manager = manager
    
    def on_enter(self):
        pass

    def handle_event(self, event):
        pass

    # TODO: what is this time delta anyway??
    def update(self, time_delta):
        pass

    def draw(self, surface):
        pass
