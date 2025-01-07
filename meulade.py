
import pygame
import gui

def main():
    app = gui.AppGUI()
    clock = pygame.time.Clock()
    
    while app.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.running = False
            app.handle_event(event)
        
        app.update()  # Add this line to update cursor blink
        app.draw()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
