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
    print("map loaded")
    return map

# END HELPER



#################################################################################
# PYZERO CLASSES
#


class MyActor(pygame.sprite.Sprite):
    def __init__(self, imageName):
        pygame.sprite.Sprite.__init__(self)
        self.x = 0
        self.y = 0
        self._surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        self._update_pos()
       
    def _update_pos(self):

        self.rect = self._surf.get_rect()
        self.rect.center = ( self.x, self.y)
        #self.left = self.x
        #self.right = self.x
        #self.top = self.y
        #self.bottom = self.y        

    def colliderect(self, obstacle):
        collided = self.rect.colliderect(obstacle.rect)
        if (collided): print(collided)
        return collided

    def draw(self, screen):
        if (self._surf != 0): screen.blit(self._surf, (self.x,self.y))
        
class Keyboard():
    def __init__(self):
        self.a = False
        self.s = False
        self.d = False
        self.w = False
        self.r = False
        self.space = False
        self.lshift = False
        
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.r = True
                if event.key == pygame.K_a:
                    self.a = True
                if event.key == pygame.K_s:
                    self.s = True
                if event.key == pygame.K_d:
                    self.d = True
                if event.key == pygame.K_w:
                    self.w = True
                if event.key == pygame.K_SPACE:
                    self.space = True
                if event.key == pygame.K_LSHIFT:
                    self.lshift = True     
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    self.r = False
                if event.key == pygame.K_a:
                    self.a = False
                if event.key == pygame.K_s:
                    self.s = False
                if event.key == pygame.K_d:
                    self.d = False
                if event.key == pygame.K_w:
                    self.w = False
                if event.key == pygame.K_SPACE:
                    self.space = False
                if event.key == pygame.K_LSHIFT:
                    self.lshift = False     
      
#################################################################################
# CONSTANTS
#


FPS = 60 

SOUND_ENABLED = False

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

SPEED_NORMAL = 3
SPEED_SLOW = 1
SPEED_FAST = 6

#################################################################################
# GAME
#

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

    def update(self):
        pass

class Mob(Entity):
    def __init__(self, imageName):
        Entity.__init__(self, imageName)
        
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
        self.last_animation = pygame.time.get_ticks()
        self.animate()
        
    def animate(self):

        ANIMATION_COOLDOWN = 40
        if pygame.time.get_ticks() - self.last_animation > ANIMATION_COOLDOWN:
            #pass
            #print("time to animate")
            self.last_animation = pygame.time.get_ticks()
            self.frame += 1
        else:
            #print(pygame.time.get_ticks())
            #print("skipping animation")
            pass
        
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
        
        self._surf = cropped
        
        #self._surf = pygame.transform.scale(self._surf,( 48, 48))
        self._update_pos()        
        

        
    def update(self, obstacles):
        entity = self

        dx = 0
        dy = 0

        if (self.movement == MOVEMENT_RIGHT):
            print("trying to move right")
            dx += self.speed
        if (self.movement == MOVEMENT_LEFT):
            dx -= self.speed
            
        for obstacle in obstacles:
            if obstacle.colliderect(self):
                print("collide x")
                dx = 0
                self.x = obstacle.x + obstacle.rect.height + self.rect.height

        for obstacle in obstacles:
            if obstacle.colliderect(self):
                print("collide y")
                dy = 0
                break
        
        if dy > 0:
            entity.airborn = True

        entity.x += dx
        entity.y += dy
        
        self.animate()


class Tile(Entity):
    def __init__(self, x, y, type, tilemap):
        Entity.__init__(self,"red")        
        cropped = pygame.Surface((16, 16), pygame.SRCALPHA, 32)
        col = type % 100
        row = type // 100
        cropped.blit(tilemap, (0, 0), (16*col, 16*row, 16, 16))
        self._surf = cropped
            
        self.type = type
        
        
        #self._surf = pygame.transform.scale(self._surf, (TILE_SIZE, TILE_SIZE))
        #self._update_pos()
            
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE         

   

class World():
    def __init__(self):
        self.all_entities = []
        self.player = Player()
        self.tilemap = pygame.image.load("tiles.png")
        self.reset()
        self.keyboard = Keyboard()

    
    def reset(self):
        
        self.all_entities.clear()

        map = loadDocsCSV(MAP_URL)
               
        for y in range(len(map)):
            for x in range(len(map[y])):
                tileType = map[y][x]
                if (tileType > 0):
                    tile = Tile(x, y, tileType, self.tilemap)
                    self.all_entities.append(tile)
                elif (PLAYER_ENTITY == tileType):
                    self.player = Player()
                    self.player.x = x * TILE_SIZE
                    self.player.y = y * TILE_SIZE
        
    
    def update(self):
        player = self.player
        entities = self.all_entities

        # handle input
        keyboard = self.keyboard
        keyboard.update()

        
        if (keyboard.r):
            self.reset()
            return

        # update which direction the player is facing, regardless of movement
        if (keyboard.d):
            player.direction = DIRECTION_RIGHT
        elif (keyboard.a):
            player.direction = DIRECTION_LEFT

        # can be moving either left, or right, or stationary
        if (keyboard.d):
            player.movement = MOVEMENT_RIGHT
        elif (keyboard.a):
            player.movement = MOVEMENT_LEFT            
        else:
            player.movement = MOVEMENT_IDLE

        #if (player.airborn):
        #    player.movement = MOVEMENT_JUMPING

        # can be sprinting, crouching, or normal
        if (keyboard.lshift):
            player.speed = SPEED_FAST
        elif (keyboard.s):
            player.speed = SPEED_SLOW
        else:
            player.speed = SPEED_NORMAL

        if keyboard.w and not player.airborn:
            player.yspeed -= JUMP_BOOST
            player.airborn = True
            #player.movement = MOVEMENT_JUMPING
    
        player.yspeed += GRAVITY        

        # update background
                
        # update tiles
    
        # update player
        player.update(entities)
    
        # ai mobs    
        # update mobs    
    
        # update world    
        # draw world
    
        # update player actions   
                
        # move entities
        #for entity in entities:          
        #    entity.move(player)

        # move player
        #player.move(entities)

        # remove hit entities
        for entity in entities:
            if (entity.hit):
                entities.remove(entity)

        # handle hit Player
        if (player.hit):
            player.hit = False
            print("ouch!")



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
        
        if (SOUND_ENABLED):
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