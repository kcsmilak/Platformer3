#import pgzrun
import pygame
import random

import csv

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
        self.rect.topleft = (self.x, self.y)
        #self.left = self.x
        #self.right = self.x
        #self.top = self.y
        #self.bottom = self.y        

    #def colliderect(self, obstacle):
    #    #print(self.rect)
    #    #print(obstacle.rect)
    #    collided = self.rect.colliderect(obstacle.rect)
    #    #if (collided): print(collided)
    #    return collided

    def draw(self, screen):
        if (self._surf != 0): screen.blit(self._surf, (self.x,self.y))
        pygame.draw.rect(screen, (200,200,200), self.rect, 1)
        
class Keyboard():
    def __init__(self):
        self.a = False
        self.s = False
        self.d = False
        self.w = False
        self.r = False
        self.q = False
        self.space = False
        self.lshift = False
        
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.q = True
                if event.key == pygame.K_r:
                    self.r = True
                if event.key == pygame.K_a:
                    self.a = True
                if event.key == pygame.K_s:
                    self.s = True
                if event.key == pygame.K_d:
                    print("press d")
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
                    print("lower d")
                    self.d = False
                if event.key == pygame.K_w:
                    print("lower w")
                    self.w = False
                if event.key == pygame.K_SPACE:
                    self.space = False
                if event.key == pygame.K_LSHIFT:
                    self.lshift = False     
      
#################################################################################
# CONSTANTS
#


FPS = 30 

SOUND_ENABLED = False

TITLE = "Platformer"
MAP_URL="https://docs.google.com/spreadsheets/d/1jbsapypHN5FX6k8K7Zs271bY8QSzSMiLkHFi2667nsU/gviz/tq?tqx=out:csv&sheet=live"

ZOOM = 3

WIDTH = 800 * ZOOM
HEIGHT = 600 * ZOOM

MAX_PLATFORMS = 3

GRAVITY = 2 * ZOOM 
GRAVITY_MAX = 40 * ZOOM
HEIGHT_MIN = -200 * ZOOM
JUMP_BOOST = 15 * ZOOM

BACKGROUND_ENTITY = 0
WALL_ENTITY = 1
PLAYER_ENTITY = -1

TILE_SIZE = 16 * ZOOM

DIRECTION_RIGHT = 1
DIRECTION_LEFT = -1

MOVEMENT_RIGHT = 1
MOVEMENT_LEFT = -1
MOVEMENT_IDLE = 0

EDGE_STOP = 0
EDGE_STICK = 1
EDGE_BOUNCE = 2
EDGE_DIE = 3
EDGE_DESTROY = 4

SPEED_NORMAL = 4 * ZOOM
SPEED_SLOW = 1 * ZOOM
SPEED_FAST = 7 * ZOOM

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
        self.jumping = False

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

        ANIMATION_COOLDOWN = 0
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
        elif (self.jumping):
            img = self.jump
            frame = 0
        else:
            img = self.run
            
            frame = (self.frame // 1) % 12
       
        cropped.blit(img, (0, 0), (32 * (frame), 0, 32, 32))

        if (DIRECTION_LEFT == self.direction):
            cropped = pygame.transform.flip(cropped, True, False)
        
        self._surf = cropped
        
        self._surf = pygame.transform.scale(self._surf,( 32 * ZOOM, 32 * ZOOM))
        self._update_pos()        
        

        
    def update(self, obstacles):

        update_round = pygame.time.get_ticks()
        
        dx = 0#self.xspeed
        dy = self.yspeed

        dy += GRAVITY

        #print(f'# update y ={self.rect.y} ys={self.yspeed} dy={dy}')

        # terminal velocity check
        if (dy > GRAVITY_MAX):
            self.airborn = True
            dy = GRAVITY_MAX

        if (self.jumping and not self.airborn):
            dy -= JUMP_BOOST
            self.airborn = True
            print("jump")
        
        if (self.movement == MOVEMENT_RIGHT):
            print("right movement")
            dx += self.speed
        if (self.movement == MOVEMENT_LEFT):
            print("left movement")
            dx -= self.speed
            
        for obstacle in obstacles:
            testrect = pygame.Rect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height)
            if obstacle.rect.colliderect(testrect):
                # check if colliding from the right or left
                diff = 0
                if (dx < 0):
                    print("hitting right side of obstacle")
                    diff = (obstacle.rect.x + obstacle.rect.width) - testrect.x
                    #diff = testrect.x + self.rect.width - obstacle.rect.x
                elif (dx > 0):
                    print("hitting left side of obstacle")
                    diff = (obstacle.rect.x - (testrect.x + testrect.width))
                    #diff = testrect.x + testrect.width - obstacle.rect.x
                else:
                    print("x hit something standing still!")
                print(f'collide x t:{testrect} o:{obstacle.rect} dx:{dx} diff:{diff}')
                
                dx += diff
                
                #self.x = obstacle.x + obstacle.rect.height + self.rect.height

        fork = True
        for obstacle in obstacles:
            testrect = pygame.Rect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height)
            if obstacle.rect.colliderect(testrect):

                diff = 0
                if (dy < 0): # jumping
                    print("bump!")
                    diff = - (testrect.y - (obstacle.rect.y + obstacle.rect.height) )                    
                    print(f'collide y ur: {update_round} b:{self.rect} t:{obstacle.rect} dy:{dy}')
                    fork = True

                elif (dy > 0): # falling
                    diff = (obstacle.rect.y - (testrect.y + testrect.height))
                    self.airborn = False
                    print("hit ground")
                else:
                    print("y hit something standing still dy={dy{}}")
                
                dy += diff#-abs(obstacle.rect.top - self.rect.bottom)
                self.yspeed = 0
                #break
        
        #if dy > 0:
        #    self.airborn = True

        print(f'-- keeping gravity y={self.y - 288} ys={self.yspeed} dy={dy} --> y = {self.y + dy - 288}')

        self.x += dx
        self.y += dy
        self.yspeed = dy
        
        self.animate()


class Tile(Entity):
    def __init__(self, x, y, type, tilemap):
        Entity.__init__(self,"red")        
        cropped = pygame.Surface((16, 16), pygame.SRCALPHA, 32)
        col = type % 100
        row = type // 100
        cropped.blit(tilemap, (0, 0), (16*col, 16*row, 16, 16))
        cropped = pygame.transform.scale(cropped, (TILE_SIZE, TILE_SIZE))
        self._surf = cropped
            
        self.type = type
        
        
        #self._surf = pygame.transform.scale(self._surf, (TILE_SIZE, TILE_SIZE))
            
        self.x = x * TILE_SIZE #+ TILE_SIZE // 2
        self.y = y * TILE_SIZE #+ TILE_SIZE // 2         
        self._update_pos()

        
MAP_DATA = [[1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,-1,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,1,1],
            [1,0,0,0,0,0,0,0,0,1],           
            [1,1,1,1,1,1,1,1,1,1]]
            
class World():
    def __init__(self):
        self.all_entities = []
        self.player = Player()
        self.tilemap = pygame.image.load("tiles.png")
        self.reset()
        self.keyboard = Keyboard()

    
    def reset(self):
        
        self.all_entities.clear()

        map = []
        if (False):
            map = loadDocsCSV(MAP_URL)
        elif (False):
            #load in level data and create world
            with open(f'data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    map_row = []
                    for y, tile in enumerate(row):
                        map_row.append(int(tile))
                    map.append(map_row)
        else:
            map = MAP_DATA
                    
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

        if (keyboard.q):
            return False
        
        if (keyboard.r):
            self.reset()
            return True

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

        if keyboard.w:
            player.jumping = True
        else:
            player.jumping = False
    
        #player.yspeed += GRAVITY        

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
            
        return True



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
        return self.world.update()
            
    def draw(self):
        #pygame.display.set_mode((800, 600), pygame.FULLSCREEN)        
        self.world.draw(self.screen)


#################################################################################
# TEST
#
        
        
world_data = []
#load in level data and create world
with open(f'data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			print( int(tile) )        

            
#################################################################################
# BOILERPLAY PYGAME / PYZERO GAMELOOP
#

game = Game()
    
def update():
    return game.update()

def draw():
    game.draw()
   
def run():
    run = True    
    while run:       
        #for event in pygame.event.get():
        #    #quit game
        #    if event.type == pygame.QUIT:
        #        run = False

        if not update(): break
        draw()
        pygame.display.update()        

# If PyZero
#pgzrun.go()
# ELSE 
run()

pygame.quit()

# ENDIF