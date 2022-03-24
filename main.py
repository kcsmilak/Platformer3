#import pgzrun
import pygame
pygame.init()
import random
import helpers
from helpers import *

import csv

#################################################################################
# PYZERO CLASSES
#


class MyActor(pygame.sprite.Sprite):
    def __init__(self, imageName):
        pygame.sprite.Sprite.__init__(self)
        self._x = 0
        self._y = 0
        self._surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        self._update_pos()
       
    def _update_pos(self):
        self.rect = self._surf.get_rect()
        self.rect.topleft = (self.x, self.y)
      

    @property
    def right(self):
        return self.rect.right

    @property
    def left(self):
        return self.rect.left

    @property
    def top(self):
        return self.rect.top

    @property
    def bottom(self):
        return self.rect.bottom

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._update_pos()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._update_pos()

    @property
    def image(self):
        return self._surf
        
    #def colliderect(self, obstacle):
    #    #print(self.rect)
    #    #print(obstacle.rect)
    #    collided = self.rect.colliderect(obstacle.rect)
    #    #if (collided): print(collided)
    #    return collided

    def draw(self, screen):
        if (self._surf != 0): screen.blit(self._surf, (self.x,self.y))
        #pygame.draw.rect(screen, (200,200,200), self.rect, 1)

      
#################################################################################
# CONSTANTS
#


FPS = 30 

SOUND_ENABLED = True

TITLE = "Platformer"
MAP_URL="https://docs.google.com/spreadsheets/d/1jbsapypHN5FX6k8K7Zs271bY8QSzSMiLkHFi2667nsU/gviz/tq?tqx=out:csv&sheet=live"

ZOOM = 1

WIDTH = 800 * ZOOM
HEIGHT = 600 * ZOOM

MAX_PLATFORMS = 3

GRAVITY = 2 * ZOOM 
GRAVITY_MAX = 40 * ZOOM
HEIGHT_MIN = -200 * ZOOM
JUMP_BOOST = 20 * ZOOM

BACKGROUND_ENTITY = 0
WALL_ENTITY = 1
PLAYER_ENTITY = -1

TILE_SIZE = 16 * ZOOM

LOOKING_RIGHT = 1
LOOKING_LEFT = -1

MOVEMENT_RIGHT = 1
MOVEMENT_LEFT = -1
MOVEMENT_IDLE = 0

EDGE_STOP = 0
EDGE_STICK = 1
EDGE_BOUNCE = 2
EDGE_DIE = 3
EDGE_DESTROY = 4
EDGE_IGNORE = 5

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
        self.shoot_cooldown = 0
        self.movement = MOVEMENT_IDLE
        self.looking = LOOKING_RIGHT
        self.lifetime = -1
        self.edgeBehavior = EDGE_BOUNCE
        self.jumping = False

    def update(self):
        pass

class Mob(Entity):
    def __init__(self, imageName):
        Entity.__init__(self, imageName)
        
    def move(self):

        entity = self
       
        # try to move in x direction
        entity.x += entity.xspeed

        # if hit edge, bounce or die
        if (self.right > self.max_right):
            if (EDGE_BOUNCE == self.edgeBehavior):
                self.xspeed *= -1
                self.right = self.max_right
            elif (EDGE_IGNORE == self.edgeBehavior):
                pass
        
        elif (self.left < self.min_left):
            if (EDGE_BOUNCE == self.edgeBehavior):
                self.xspeed *= -1
                self.left = self.min_left
            elif (EDGE_IGNORE == self.edgeBehavior):
                pass
    
        entity.y += entity.yspeed

        # if hit edge, bounce
        if (entity.bottom > entity.max_bottom):
            if (EDGE_BOUNCE == self.edgeBehavior):
                entity.yspeed *= -1
                entity.bottom = entity.max_bottom           
            elif (EDGE_IGNORE == self.edgeBehavior):
                pass
            
        elif (entity.top < entity.min_top):
            if (EDGE_BOUNCE == self.edgeBehavior):
                entity.yspeed *= -1
                entity.top = entity.min_top
            elif (EDGE_IGNORE == self.edgeBehavior):
                pass

        if (self.lifetime >= 0):
            self.lifetime -= 1
            if (self.lifetime <=0):
                self.hit = True              

class Bullet(Mob):
    def __init__(self, x, y, dx):
        Mob.__init__(self, "red.png")
        self.x = x
        self.y = y
        self.xspeed = dx
        self._surf = pygame.transform.scale(pygame.image.load("red.png"), (5,5))
        self._update_pos()
        self.lifetime = 30
        self.edgeBehavior = EDGE_IGNORE

    def update(self, player, obstacles, world):
        self.move()

        if pygame.sprite.spritecollide(self, obstacles, False):
            self.hit = True

        
        
class Player(Entity):

    SHOOT_COOLDOWN = 5
    ANIMATION_COOLDOWN = 0    
    
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

        
        if pygame.time.get_ticks() - self.last_animation > self.ANIMATION_COOLDOWN:
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
        if (MOVEMENT_IDLE == self.movement and not self.jumping):
            img = self.idle
            frame = (self.frame // 1) % 11 
        elif (self.jumping):
            img = self.jump
            frame = 0
        else:
            img = self.run
            
            frame = (self.frame // 1) % 12
       
        cropped.blit(img, (0, 0), (32 * (frame), 0, 32, 32))

        if (LOOKING_LEFT == self.looking):
            cropped = pygame.transform.flip(cropped, True, False)
        
        self._surf = cropped
        
        self._surf = pygame.transform.scale(self._surf,( 32 * ZOOM *1, 32 * ZOOM * 1))
        self._update_pos()        
        

        
    def update(self, obstacles, world):

        update_round = pygame.time.get_ticks()
        
        dx = 0#self.xspeed
        dy = self.yspeed

        dy += GRAVITY

        #print(f'# update y ={self.rect.y} ys={self.yspeed} dy={dy}')

        self.shoot_cooldown -= 1
        if (self.shooting and self.shoot_cooldown <= 0):
            self.shoot_cooldown = self.SHOOT_COOLDOWN
            # Shoot something!
            print('shoot')
            world.addBullet(self.x + 5, self.y + 15, 10 * self.looking, 0)
            

            
        # terminal velocity check
        if (dy > GRAVITY_MAX):
            self.airborn = True
            dy = GRAVITY_MAX

        if (self.jumping and not self.airborn):
            dy -= JUMP_BOOST
            self.airborn = True
            print("jump")
        
        if (self.movement == MOVEMENT_RIGHT):
            #print("right movement")
            dx += self.speed
        if (self.movement == MOVEMENT_LEFT):
            #print("left movement")
            dx -= self.speed
            
        for obstacle in obstacles:
            testrect = pygame.Rect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height)
            if obstacle.rect.colliderect(testrect):
                # check if colliding from the right or left
                diff = 0
                if (dx < 0):
                    #print("hitting right side of obstacle")
                    diff = (obstacle.rect.x + obstacle.rect.width) - testrect.x
                    #diff = testrect.x + self.rect.width - obstacle.rect.x
                elif (dx > 0):
                    #print("hitting left side of obstacle")
                    diff = (obstacle.rect.x - (testrect.x + testrect.width))
                    #diff = testrect.x + testrect.width - obstacle.rect.x
                else:
                    #print("x hit something standing still!")
                    pass
                print(f'collide x t:{testrect} o:{obstacle.rect} dx:{dx} diff:{diff}')
                
                dx += diff
                
                #self.x = obstacle.x + obstacle.rect.height + self.rect.height

        fork = True
        for obstacle in obstacles:
            testrect = pygame.Rect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height)
            if obstacle.rect.colliderect(testrect):

                diff = 0
                if (dy < 0): # jumping
                    #print("bump!")
                    diff = - (testrect.y - (obstacle.rect.y + obstacle.rect.height) )                    
                    #print(f'collide y ur: {update_round} b:{self.rect} t:{obstacle.rect} dy:{dy}')
                    fork = True

                elif (dy > 0): # falling
                    diff = (obstacle.rect.y - (testrect.y + testrect.height))
                    self.airborn = False
                    #print("hit ground")
                else:
                    #print("y hit something standing still dy={dy{}}")

                    pass
                
                dy += diff#-abs(obstacle.rect.top - self.rect.bottom)
                self.yspeed = 0
                #break
        
        #if dy > 0:
        #    self.airborn = True

        #print(f'-- keeping gravity y={self.y - 288} ys={self.yspeed} dy={dy} --> y = {self.y + dy - 288}')

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
        self.tiles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = Player()
        self.tilemap = pygame.image.load("tiles.png")
        self.reset()

    
    def reset(self):
        
        self.tiles.empty()

        map = []
        if (True):
            map = helpers.loadDocsCSV(MAP_URL)
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
                    self.tiles.add(tile)
                elif (PLAYER_ENTITY == tileType):
                    self.player = Player()
                    self.player.x = x * TILE_SIZE
                    self.player.y = y * TILE_SIZE
                    

    def addBullet(self, x, y, dx, dy):
        self.bullets.add(Bullet(x,y,dx))
        pass
    
    def update(self):
        # update scene (e.g.: background, lighting, tile animations)
        self.tiles.update()

        # update moving entities (e.g.: platforms, bullets)
        self.bullets.update(self.player, self.tiles, self)
        
        # update player (avoid tiles, callback shooting)
        self.player.update(self.tiles, self)
    
        # update mobs (ai, motion, collisions)
       
        # update player actions

        # remove hit entities
        for entity in self.bullets:
            if (entity.hit):
                self.bullets.remove(entity)

        # handle hit Player
        if (self.player.hit):
            self.player.hit = False
            print("ouch!")
            
        return True



    def draw(self,screen):
        # draw background
        screen.fill((100,100,100)) 

        # draw tiles
        self.tiles.draw(screen)
        
        # draw entities
        self.bullets.draw(screen)

        # draw player
        self.player.draw(screen)

        # draw hud




class Game():
    def __init__(self):
        self.world = World()
        
        if (SOUND_ENABLED):
            pygame.mixer.init()
            
            pygame.mixer.music.load('music2.mp3')
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1, 0.0, 5000)
            
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Shooter')
        self.keyboard = helpers.Keyboard()        
        
    def update(self):
        pygame.time.Clock().tick(FPS)

        keyboard = self.keyboard
        player = self.world.player
        
        # handle input

        if (keyboard.q):
            return False
        
        if (keyboard.r):
            self.reset()
            return True

        # update which direction the player is facing, regardless of movement
        if (keyboard.d):
            player.looking = LOOKING_RIGHT
        elif (keyboard.a):
            player.looking = LOOKING_LEFT

        # can be moving either left, or right, or stationary
        if (keyboard.d and not keyboard.a):
            player.movement = MOVEMENT_RIGHT
        elif (keyboard.a and not keyboard.d):
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

        if keyboard.space:
            player.shooting = True
        else:
            player.shooting = False
        
        
        self.world.update()
        debugui.update()
        return True
            
    def draw(self):
        #pygame.display.set_mode((800, 600), pygame.FULLSCREEN)        
        self.world.draw(self.screen)
        debugui.draw(self.screen)


            
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
        for event in pygame.event.get():
            #quit game
            if event.type == pygame.QUIT:
                run = False
            elif (event.type == pygame.KEYDOWN or event.type == pygame.KEYUP):
                game.keyboard.handleEvent(event)            

        if not update(): break
        draw()
        pygame.display.update()        

# If PyZero
#pgzrun.go()
# ELSE 
run()

pygame.quit()

# ENDIF