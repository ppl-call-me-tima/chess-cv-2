from dotenv import load_dotenv
load_dotenv(dotenv_path="dimensions.env", override=True)

import pygame
import asyncio

from constants import WINDOW_WIDTH, WINDOW_HEIGHT

from managers.screen_manager import ScreenManager
from managers.camera_manager import CameraManager

from screens.menu_screen import MenuScreen
from screens.detect_screen import DetectScreen
from screens.setup_screen import SetupScreen

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("ChessCV")

    screen_manager = ScreenManager(screen)
    camera_manager = CameraManager()

    screen_manager.add_screen("menu", MenuScreen(screen_manager))
    screen_manager.add_screen("detect", DetectScreen(screen_manager, camera_manager))
    screen_manager.add_screen("setup", SetupScreen(screen_manager, camera_manager))

    screen_manager.set_screen("menu")

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            await screen_manager.handle_event(event)
        
        screen_manager.update()
        screen.fill((30, 30, 30))
        screen_manager.draw(screen)

        pygame.display.flip()

        await asyncio.sleep(1/60)
        continue
    
    await screen_manager.screens["detect"].detection_manager.position.engine_quit()

if __name__ == "__main__":
    asyncio.run(main())
