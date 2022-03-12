#import pgzrun
import pygame
import random

#################################################################################
# START HELPER
#

import io
try:
    # Python2
    from urllib2 import urlopen
except ImportError:
    # Python3
    from urllib.request import urlopen
    
def loadDocsCSV(url):
    map = []
    str = io.BytesIO(urlopen(url).read()).read().decode('UTF-8')        
    for row in str.split("\n"):
        newrow = []
        for cell in row.split(","):
            newrow.append(int(cell.strip("\"")))
        map.append(newrow)
    return map

# END HELPER

#################################################################################
# CONSTANTS
#


FPS = 60 

TITLE = "Platformer"
MAP_URL="https://docs.google.com/spreadsheets/d/1jbsapypHN5FX6k8K7Zs271bY8QSzSMiLkHFi2667nsU/gviz/tq?tqx=out:csv&sheet=live"

WIDTH = 800
HEIGHT = 600

MAX_PLATFORMS = 3

GRAVITY = 1
GRAVITY_MAX = 10
HEIGHT_MIN = -200
JUMP_BOOST = 11

BACKGROUND_ENTITY = 0
WALL_ENTITY = 1
PLAYER_ENTITY = -1
PLATFORM_ENTITY = -7
BALL_ENTITY = -8
BULLET_ENTITY = -9

SHOOT_COOLDOWN = 10
TILE_SIZE = 16

DIRECTION_RIGHT = 1
DIRECTION_LEFT = -1

MOVEMENT_RIGHT = 1
MOVEMENT_LEFT = -1

MOVEMENT_JUMPING = 3
MOVEMENT_IDLE = 0

EDGE_STOP = 0
EDGE_STICK = 1
EDGE_BOUNCE = 2
EDGE_DIE = 3
EDGE_DESTROY = 4


class MyActor(pygame.sprite.Sprite):
    def __init__(self, imageName):
        pygame.sprite.Sprite.__init__(self)
        self.x = 0
        self.y = 0
        self._surf = 0
        self._update_pos()
       
    def _update_pos(self):
        self.left = self.x
        self.right = self.x
        self.top = self.y
        self.bottom = self.y
        #self.rect = self._surf.get_rect()

    def colliderect(self, actor):
        return False

    def draw(self, screen):
        screen.blit(self._surf, (self.x,self.y))
        

class Entity(MyActor):
    def __init__(self, imageName):
        MyActor.__init__(self, imageName)
        self.xspeed = 0
        self.yspeed = 0
        self.max_right = WIDTH
        self.min_left = 0
        self.min_top = 0
        self.max_bottom = HEIGHT
        self.airborn = False
        self.hit = False
        self.id = random.randint(1,1024)
        self.type = -1
        self.solid = True
        self.shooting = False
        self.edgeBounce = True
        self.shootCooldown = 0
        self.movement = MOVEMENT_IDLE
        self.direction = DIRECTION_RIGHT
        self.lifetime = -1
        self.edgeBehavior = EDGE_BOUNCE


        
    def move(self, player):
        entity = self

        hitEdge = False
        
        # try to move in x direction
        entity.x += entity.xspeed

        # if hit edge, bounce or die
        if (self.right > self.max_right):
            if (EDGE_BOUNCE == self.edgeBehavior):
                self.xspeed *= -1
                self.right = self.max_right
                hitEdge = True
        
        elif (self.left < self.min_left):
            if (EDGE_BOUNCE == self.edgeBehavior):
                self.xspeed *= -1
                self.left = self.min_left
                hitEdge = True
        
        # if hit player, do something
        if entity.colliderect(player):
            # if platform, push the player
            if (PLATFORM_ENTITY == entity.type):
                player.x += entity.xspeed
            # if ball, hurt the player
            elif (BALL_ENTITY == entity.type):
                player.hit = True
                entity.hit = True
    
        entity.y += entity.yspeed

        # if hit edge, bounce
        if (entity.bottom > entity.max_bottom):
            if (EDGE_BOUNCE == self.edgeBehavior):
                entity.yspeed *= -1
                entity.bottom = entity.max_bottom           
                hitEdge = True
            
        elif (entity.top < entity.min_top):
            if (EDGE_BOUNCE == self.edgeBehavior):
                entity.yspeed *= -1
                entity.top = entity.min_top
                hitEdge = True

        if hitEdge:
            self.hit = True

        if (self.lifetime >= 0):
            self.lifetime -= 1
            if (self.lifetime <=0):
                self.hit = True              
        
class Player(Entity):
    def __init__(self):
        Entity.__init__(self, "red")
        self.type = PLAYER_ENTITY
        self.min_top = -200        
        self.x, self.y = 100, 100
        self.frame = 0
        self.run = pygame.image.load("run.png")
        self.idle = pygame.image.load("idle.png")
        self.jump = pygame.image.load("jump.png")
        
    def updateImage(self):
        cropped = pygame.Surface((32, 32), pygame.SRCALPHA, 32)

        img = 0
        frame = 0
        if (MOVEMENT_IDLE == self.movement):
            img = self.idle
            frame = (self.frame // 1) % 11 
        elif (MOVEMENT_JUMPING == self.movement):
            img = self.jump
            frame = 0
        else:
            img = self.run
            frame = (self.frame // 1) % 12
       
        cropped.blit(img, (0, 0), (32 * (frame), 0, 32, 32))

        if (DIRECTION_LEFT == self.direction):
            cropped = pygame.transform.flip(cropped, True, False)
        
        self.frame += 1
        self._surf = cropped
        
        #self._surf = pygame.transform.scale(self._surf,( 48, 48))
        self._update_pos()        
        

        
    def move(self, obstacles):
        entity = self

        # try to move in x direction
        entity.x += entity.xspeed

        # if hit edge, bounce
        if (entity.right > entity.max_right):
            entity.xspeed *= -1
            entity.right = entity.max_right
        
        elif (entity.left < entity.min_left):
            entity.xspeed *= -1
            entity.left = entity.min_left                
        else:
            for obstacle in obstacles:
                if entity.colliderect(obstacle):
                    if (obstacle.solid):
                        entity.x -= entity.xspeed                        
                        entity.xspeed = 0

        
        entity.y += entity.yspeed

        # if hit edge, bounce
        if (entity.bottom > entity.max_bottom):
            entity.yspeed *= -1
            entity.bottom = entity.max_bottom

            entity.yspeed = 0
            entity.airborn = False               
            
        elif (entity.top < entity.min_top):
            entity.yspeed *= -1
            entity.top = entity.min_top

        else:
            for obstacle in obstacles:
                if entity.colliderect(obstacle):
                    if (obstacle.solid):
                        entity.y -= entity.yspeed
                        if (entity.yspeed > 0):
                            entity.airborn = False
                        entity.yspeed = 0
                        entity.x += obstacle.xspeed
                        break
            if entity.yspeed > 0:
                entity.airborn = True

        self.updateImage()


class Tile(Entity):
    def __init__(self, x, y, type):
        Entity.__init__(self,"red")        
        cropped = pygame.Surface((16, 16), pygame.SRCALPHA, 32)
        img = pygame.image.load("tiles.png")
        col = type % 100
        row = type // 100
        cropped.blit(img, (0, 0), (16*col, 16*row, 16, 16))
        self._surf = cropped
            
        self.type = type
        
        
        #self._surf = pygame.transform.scale(self._surf, (TILE_SIZE, TILE_SIZE))
        self._update_pos()
            
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE         


class World():
    def __init__(self):
        self.all_entities = []
        self.player = 0
        self.reset()

    def reset(self):
        self.all_entities.clear()

        map = loadDocsCSV(MAP_URL)
               
        for y in range(len(map)):
            for x in range(len(map[y])):
                tileType = map[y][x]
                if (tileType > 0):
                    tile = Tile(x, y, tileType)
                    self.all_entities.append(tile)
                elif (PLAYER_ENTITY == tileType):
                    self.player = Player()
                    self.player.x = x * TILE_SIZE
                    self.player.y = y * TILE_SIZE
    
        #for i in range(0, MAX_PLATFORMS):
        #    self.all_entities.append(Platform(i))    

        #for i in range(0, MAX_BALLS):
        #    self.all_entities.append(Ball()) 


    
    def update(self):
        player = self.player
        entities = self.all_entities


        # update background
                
        # update tiles
    
        # update player
    
        # ai mobs    
        # update mobs    
    
        # update world    
        # draw world
    
        # update player actions   
        
        self.handleInput()
        
        # move entities
        for entity in entities:          
            entity.move(player)

        # move player
        player.move(entities)

        # remove hit entities
        for entity in entities:
            if (entity.hit):
                entities.remove(entity)

        # handle hit Player
        if (player.hit):
            player.hit = False
            print("ouch!")

    def handleInput(self):

        return
        if (keyboard.r):
            self.reset()
            return

        player = self.player


        if (keyboard.b):
            self.all_entities.append(Ball())    
        
        if (keyboard.d):
            player.direction = DIRECTION_RIGHT
            player.movement = MOVEMENT_RIGHT
        elif (keyboard.a):
            player.direction = DIRECTION_LEFT
            player.movement = MOVEMENT_RIGHT            
        else:
            player.movement = MOVEMENT_IDLE

        if (player.airborn):
            player.movement = MOVEMENT_JUMPING
            
        player.xspeed = 0
        dx = 0
        if (keyboard.LSHIFT):
            dx = 7
        elif (keyboard.S):
            dx = 2
        else:
            dx = 5
        #player.yspeed = 0
        if (keyboard.d):

            player.xspeed += dx 
        elif (keyboard.a):
            player.xspeed -= dx 
        #else:
            #player.xspeed = 0
            #pass

        if (keyboard.space) and not player.shooting:
            # shoot
            player.shooting = True
            player.shootCooldown = SHOOT_COOLDOWN
            bullet = Bullet(player.x+(player.width//2*player.direction),player.y + player.height//2,10 * player.direction,0)
            self.all_entities.append(bullet)
        elif player.shootCooldown > 0: # add cooldown here
            player.shootCooldown -= 1
        else:
            player.shooting = False
    
        if keyboard.w and not player.airborn:
            player.yspeed -= JUMP_BOOST
            player.airborn = True
            player.movement = MOVEMENT_JUMPING
    
        player.yspeed += GRAVITY

    def draw(self,screen):
        # draw background
        screen.fill((100,100,100)) 

        # draw tiles
        
        # draw entities
        for entity in self.all_entities:
            entity.draw(screen)

        # draw player
        self.player.draw(screen)

        # draw hud




class Game():
    def __init__(self):
        self.world = World()
    
        pygame.init()
        pygame.mixer.init()
        
        pygame.mixer.music.load('music2.mp3')
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1, 0.0, 5000)
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Shooter')
        
    def update(self):
        pygame.time.Clock().tick(FPS)    
        self.world.update()
    
    def draw(self):
        #pygame.display.set_mode((0, 0), pygame.FULLSCREEN)        
        self.world.draw(self.screen)






#################################################################################
# BOILERPLAY PYGAME / PYZERO GAMELOOP
#

game = Game()
    
def update():
    game.update()

def draw():
    game.draw()
   
def run():
    run = True    
    while run:       
        for event in pygame.event.get():
            #quit game
            if event.type == pygame.QUIT:
                run = False

        update()
        draw()
        pygame.display.update()        

# If PyZero
#pgzrun.go()
# ELSE 
run()

pygame.quit()

# ENDIF