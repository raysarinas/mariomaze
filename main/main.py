import pygame, random
import pygame.gfxdraw
from walls import *
from chars import *
from buildgraph import *
from pathfinding import *
from moveghost import *

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

class Game:
    def __init__(self, surface):
        self.surface = surface
        self.done = False
        self.cont = True
        self.all_sprite_list = pygame.sprite.Group()
        self.block_list = pygame.sprite.Group()

        for i in range(1):
            self.block = Block(BLACK, 25, 25)
            self.block.rect.x = 25 + i
            self.block.rect.y = 25 + i
            self.block.left_boundary = 10
            self.block.top_boundary = 10
            self.block.right_boundary = 550
            self.block.bottom_boundary = 350
            self.all_sprite_list.add(self.block)
            self.block_list.add(self.block)

        #self.wall_list, self.all_sprite_list = makeWalls(self.all_sprite_list)
        self.wall_list, self.all_sprite_list, self.walls = generate_walls(self.all_sprite_list)
        #print(self.walls)
        # FOR TESTING VERTICES AND GRAPH STUFF
        self.valid, self.badrects, self.goodrects, self.vedges, self.hedges, self.graph, self.location = generate_graph(self.surface, SCREEN_WIDTH, SCREEN_HEIGHT, self.walls, self.wall_list)

        self.player = Player(10, SCREEN_HEIGHT - 36)
        self.peach = Peach(590 - 18, 10)
        self.player.walls = self.wall_list
        self.all_sprite_list.add(self.player, self.peach)

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.changespeed(-5, 0)
                elif event.key == pygame.K_RIGHT:
                    self.player.changespeed(5, 0)
                elif event.key == pygame.K_UP:
                    self.player.changespeed(0, -5)
                elif event.key == pygame.K_DOWN:
                    self.player.changespeed(0, 5)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.changespeed(5, 0)
                elif event.key == pygame.K_RIGHT:
                    self.player.changespeed(-5, 0)
                elif event.key == pygame.K_UP:
                    self.player.changespeed(0, 5)
                elif event.key == pygame.K_DOWN:
                    self.player.changespeed(0, -5)


    # # DETECT COLLISION
    # def collision(self):
    #     # player collision with peach
    #     hitPeach = pygame.sprite.collide_rect(self.player, self.peach)
    #     if hitPeach:
    #         self.done = True
    #         self.surface.fill(BLUE)
    #     hitGhost = pygame.sprite.collide_rect(self.player, self.block)
    #     if hitGhost:
    #         self.done = True
    #         self.surface.fill(BLUE)
    #         #self.running = False

    # DETECT COLLISION
    def collision(self):
        # player collision with peach
        hitPeach = pygame.sprite.collide_rect(self.player, self.peach)
        #hitGhost = pygame.sprite.collide_rect(self.player, self.block)
        if hitPeach:
            #self.done
            self.finishScreen()

        hitGhost = pygame.sprite.collide_rect(self.player, self.block)
        if hitGhost:
            self.finishScreen()


    def checkSpacePressed(self):
        # Get the events that occur in pygame
        for event in pygame.event.get():
            # User has clicked on the exit sign of the window
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # User has pressed the entered key
            if event.type == KEYUP and event.key == K_SPACE:
                return True




    def play(self):
        self.done = False
        time_since_path_last_found = 0
        clock = pygame.time.Clock()
        while not self.done:
            dt = clock.tick()
            self.handle_event()
            self.all_sprite_list.update()
            self.surface.fill(BLACK)
            blocks_hit_list = pygame.sprite.spritecollide(self.player, self.block_list, True)

            for block in blocks_hit_list:
                print('hit!')
            self.all_sprite_list.draw(self.surface)

            time_since_path_last_found += dt
            # dt is measured in milliseconds, therefore 1000 ms = 1 seconds
            path = []
            if time_since_path_last_found > 200: # find coordinates every 2 seconds
                path = findpath(self.player.rect.x, self.player.rect.y, self.block.rect.x, self.block.rect.y, self.graph, self.location)
                time_since_path_last_found = 0 # reset it to 0 so you can count again

            newghostx = moveghost_x(path, self.location, self.graph, self.block.rect.x)
            newghosty = moveghost_y(path, self.location, self.graph, self.block.rect.y)
            if newghostx != None:
                #self.block.change_x = newghostx
                self.block.rect.x = newghostx
                # while len(path) != 0:
                #     point = path.pop()
                #     while point:
                #         while point != self.block.rect.x:
                #             self.block.change_x = newghostx
                #     self.block.change_x = 0
            else:
                self.block.change_x = 0
                #self.block.rect.x = newghostx
            if newghosty != None:
                #self.block.change_y = newghosty
                self.block.rect.y = newghosty
            else:
                self.block.change_y = 0



            # DRAW VERTICES ON TOP OF EVERYTHING
            for rect in self.badrects:
                pygame.draw.rect(self.surface, pygame.Color('red'), rect)
            for rect in self.goodrects:
                pygame.draw.rect(self.surface, pygame.Color('green'), rect)
            for rect in self.vedges:
                pygame.draw.rect(self.surface, pygame.Color('orange'), rect)
            for rect in self.hedges:
                pygame.draw.rect(self.surface, pygame.Color('purple'), rect)

            pygame.display.flip()
            self.collision()


    def finishScreen(self):
        fontWin = pygame.font.SysFont(None, 40, True)
        textWin = fontWin.render('Game Over?', True, pygame.Color('white'), pygame.Color('black'))
        self.surface.blit(textWin, ((self.surface.get_width()/2)/2, (self.surface.get_height()/2)/2))
        fontAsk = pygame.font.SysFont(None, 100, True)
        textAsk = fontWin.render('Play Again? Press Space', True, pygame.Color('white'), pygame.Color('black'))
        self.surface.blit(textAsk, ((self.surface.get_width()/2)/2, ((self.surface.get_height()/2)/2)+100))

        # pressed = False
        #
        #
        # pressed = self.checkSpacePressed
        # # If they did press enter
        # if pressed:
        #     # Change result to 1 to indicate that the user wants to keep playing
        #      result = 1
        # return result

    # def GameOverScreen(self):
    #     fontWin = pygame.font.SysFont(None, 40, True)
    #     textWin = fontWin.render('u got caught by a mf ghost!', True, pygame.Color('white'), pygame.Color('black'))
    #     self.surface.blit(textWin, ((self.surface.get_width()/2)/2, (self.surface.get_height()/2)/2))
    #     fontAsk = pygame.font.SysFont(None, 100, True)
    #     textAsk = fontWin.render('Play Again? Press Space', True, pygame.Color('white'), pygame.Color('black'))
    #     self.surface.blit(textAsk, ((self.surface.get_width()/2)/2, ((self.surface.get_height()/2)/2)+100))



        gameOver = False
        pygame.display.flip()
        waiting = True
        while waiting:
            print('collided')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    waiting = False


def main():
    pygame.init() # initialize pygame
    pygame.font.init() # for drawing words and stuff mayhaps?
    surface = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT]) # make screen
    pygame.display.set_caption('Some sort of mario maze game I guess')
    game = Game(surface)
    game.play()

main()
pygame.quit()
