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

    @image.setter
    def image(self, value):
        self._surf = value
        self._update_pos()
        
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
NINJA_ENTITY = -2

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

    def update(self, player, obstacles, mobs, world):
        self.move()

        if pygame.sprite.spritecollide(self, obstacles, False):
            self.hit = True

        #if pygame.sprite.spritecollide(self, player, False):
        #    self.hit = True
        
        for mob in pygame.sprite.spritecollide(self, mobs, False):
            print("hit mob")
            mob.hit = True
            self.hit = True


class AnnimationRibbon():
    def __init__(self, path):
        self.ribbon = pygame.image.load(path)
        self.num_frames = 1
        self.x = 0
        self.y = 0
        self.frame_width = self.ribbon.get_width()
        self.frame_height = self.ribbon.get_height()
        self.frame = 0

    def chopByWidth(self, width):
        self.num_frames = self.ribbon.get_width() // width
        self.frame_width = width
    
    @property
    def image(self):
        cropped = pygame.Surface((32, 32), pygame.SRCALPHA)
        cropped.blit(self.ribbon, (-(self.x + self.frame * self.frame_width),0))
        return cropped

    def nextFrame(self):
        self.frame += 1
        if (self.frame >= self.num_frames): self.frame = 0

class Animation():
    DOUBLE_JUMP = 6
    FALL = 4
    HIT = 5
    IDLE = 1
    JUMP = 2
    RUN = 3
    WALL_JUMP = 7

    def __init__(self):
        self._ribbons = {}
        self._type = -1
        self._frame = 0
        pass

    def addByWidth(self, type, path, frame_width):
        ribbon = AnnimationRibbon(path)
        ribbon.chopByWidth(frame_width)
        self._ribbons[type] = ribbon       
        self.type = type

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value
 
    def animate(self):
        self._ribbons[self.type].nextFrame()
    
    @property
    def image(self):
        image = self._ribbons[self.type].image
        return image
    

class Ninja(Mob):
    def __init__(self,x,y):
        Entity.__init__(self, "red.png")
        self.x = x
        self.y = y

        self.animation = Animation()
        self.animation.addByWidth(Animation.RUN, "Images/ninja/Run (32x32).png", 32)
        self.animation.addByWidth(Animation.HIT, "Images/ninja/Hit (32x32).png", 32)
        self.animation.addByWidth(Animation.IDLE, "Images/ninja/Idle (32x32).png", 32)
        self.animation.addByWidth(Animation.FALL, "Images/ninja/Fall (32x32).png", 32)
        self.animation.addByWidth(Animation.JUMP, "Images/ninja/Jump (32x32).png", 32)
        self.animation.addByWidth(Animation.WALL_JUMP, "Images/ninja/Wall Jump (32x32).png", 32)
        self.animation.addByWidth(Animation.DOUBLE_JUMP, "Images/ninja/Double Jump (32x32).png", 32)

        self.animation.type = Animation.IDLE


    def move(self, player, obstacles, world):
        if pygame.sprite.spritecollide(self, obstacles, False):
            self.hit = True

        alerted = False
        if (abs(player.x - self.x) < 100 and abs(player.y - self.y) < 100):
            alerted = True
        else:
            alerted = False

        if alerted: 
            self.animation.type = Animation.DOUBLE_JUMP 
        else: 
            self.animation.type = Animation.IDLE
            
    def animate(self):
        self.animation.animate()
        self.image = self.animation.image
    
    def update(self, player, obstacles, world):
        self.move(player, obstacles, world)
        self.animate()
       
        
class Player(Entity):

    SHOOT_COOLDOWN = 5
    ANIMATION_COOLDOWN = 0    
    
    def __init__(self):
        Entity.__init__(self, "red")
        self.type = PLAYER_ENTITY
        self.min_top = -200        
        self.x, self.y = 100, 100
        self.frame = 0

        character = "Virtual Guy"
        path = "Images/Main Characters"
        
        self.run = pygame.image.load(f'{path}/{character}/Run (32x32).png')
        self.idle = pygame.image.load(f'{path}/{character}/Idle (32x32).png')
        self.jump = pygame.image.load(f'{path}/{character}/Jump (32x32).png')
        
        
        self.last_animation = pygame.time.get_ticks()
        self.animate()
        
    def animate(self):
       
        if pygame.time.get_ticks() - self.last_animation > self.ANIMATION_COOLDOWN:
            self.last_animation = pygame.time.get_ticks()
            self.frame += 1

        
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
        
        dx = 0
        dy = self.yspeed

        dy += GRAVITY

        self.shoot_cooldown -= 1
        if (self.shooting and self.shoot_cooldown <= 0):
            self.shoot_cooldown = self.SHOOT_COOLDOWN
            world.addBullet(self.x + 5, self.y + 15, 10 * self.looking, 0)
                      
        # terminal velocity check
        if (dy > GRAVITY_MAX):
            self.airborn = True
            dy = GRAVITY_MAX

        if (self.jumping and not self.airborn):
            dy -= JUMP_BOOST
            self.airborn = True
        
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
                    diff = (obstacle.rect.x + obstacle.rect.width) - testrect.x
                elif (dx > 0):
                    diff = (obstacle.rect.x - (testrect.x + testrect.width))
                
                dx += diff

        for obstacle in obstacles:
            testrect = pygame.Rect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height)
            if obstacle.rect.colliderect(testrect):

                diff = 0
                if (dy < 0): # jumping
                    diff = - (testrect.y - (obstacle.rect.y + obstacle.rect.height) )                    

                elif (dy > 0): # falling
                    diff = (obstacle.rect.y - (testrect.y + testrect.height))
                    self.airborn = False
                
                dy += diff
                self.yspeed = 0

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
        self.mobs = pygame.sprite.Group()
        self.tilemap = pygame.image.load("Images/Terrain/Terrain (16x16).png")
        self.map_width = 0
        self.reset()
        self.surface = pygame.Surface((WIDTH*2, HEIGHT*2))
        self.camera = pygame.Rect(WIDTH//2 - 300/2, HEIGHT - 300, 400, 300)

    
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

        self.map_width = len(map[0])
        print(self.map_width)
                    
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
                elif (NINJA_ENTITY == tileType):
                    self.mobs.add(Ninja(x * TILE_SIZE, y * TILE_SIZE))                  

    def addBullet(self, x, y, dx, dy):
        self.bullets.add(Bullet(x,y,dx))
        pass
    
    def update(self):
        # update scene (e.g.: background, lighting, tile animations)
        self.tiles.update()

        # update moving entities (e.g.: platforms, bullets)
        self.bullets.update(self.player, self.tiles, self.mobs, self)
        
        # update player (avoid tiles, callback shooting)
        self.player.update(self.tiles, self)
    
        # update mobs (ai, motion, collisions)
        self.mobs.update(self.player, self.tiles, self)
       
        # update player actions

        # remove hit entities
        for entity in self.bullets:
            if (entity.hit):
                self.bullets.remove(entity)

        for entity in self.mobs:
            if (entity.hit):
                self.mobs.remove(entity)
                
                
        # handle hit Player
        if (self.player.hit):
            self.player.hit = False
            print("ouch!")
            
        return True

    def draw(self,screen):

        surface = self.surface

        
        # draw background
        surface.fill((100,100,100)) 

        # draw tiles
        self.tiles.draw(surface)
        
        # draw entities
        self.bullets.draw(surface)

        self.mobs.draw(surface)

        # draw player
        self.player.draw(surface)

        # draw hud

        zoom = 2

        debugui.data['p.x'] = self.player.x
        debugui.data['p.y'] = self.player.y

        
        debugui.data['c.x'] = self.camera.x
        debugui.data['c.y'] = self.camera.y
        
        xmargin = 100
        if self.player.x < self.camera.x + xmargin:
            self.camera.x = self.player.x - xmargin
        elif self.player.x + self.player.rect.width > self.camera.x + self.camera.width - xmargin:
            self.camera.x = self.player.x - self.camera.width + self.player.rect.width + xmargin


        ymargin = 50
        if self.player.y < self.camera.y + ymargin:
            self.camera.y = self.player.y - ymargin
        elif self.player.y + self.player.rect.height > self.camera.y + self.camera.height - ymargin:
            self.camera.y = self.player.y - self.camera.height + self.player.rect.height + ymargin
            
        # adjust offset if close to edge
        if self.camera.x < 0: self.camera.x = 0

        # zoom
        temp = pygame.Surface((WIDTH, HEIGHT))        
        temp.blit(surface, (0, 0), ((self.camera.x,self.camera.y), (self.camera.width, self.camera.height)))
        temp = pygame.transform.scale(temp, (zoom * temp.get_width(), zoom * temp.get_height()))
        screen.blit(temp, (0, 0), ((0,0), (temp.get_width(),temp.get_height())))

        #screen.blit(surface, (0, 0), ((0,0), (surface.get_width(),surface.get_height())))
        



class Game():
    def __init__(self):
        self.world = World()
        
        if (SOUND_ENABLED):
            pygame.mixer.init()
            
            pygame.mixer.music.load('Sounds/music2.mp3')
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