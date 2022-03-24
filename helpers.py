import pygame
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
        self.right = False
        self.left = False
        self.up = False
        self.down = False

    def setKey(self, key, value):
        if key == pygame.K_q:
            self.q = value
        if key == pygame.K_r:
            self.r = value
        if key == pygame.K_a:
            self.a = value
        if key == pygame.K_s:
            self.s = value
        if key == pygame.K_d:
            self.d = value
        if key == pygame.K_w:
            self.w = value
        if key == pygame.K_SPACE:
            self.space = value
        if key == pygame.K_LSHIFT:
            self.lshift = value  
        if key == pygame.K_RIGHT:
            self.right = value
        if key == pygame.K_LEFT:
            self.left = value
        if key == pygame.K_UP:
            self.up = value
        if key == pygame.K_DOWN:
            self.down = value

    def handleEvent(self,event):
        if event.type == pygame.KEYDOWN:
            self.setKey(event.key, True)
        if event.type == pygame.KEYUP:
            self.setKey(event.key, False)



class DebugUI():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 50
        self.height = 50
        self.font_size = 12
        self.spacing = 4
        self.data = {}
        self.font = False
        self.data['ticks'] = 0
    
    def draw(self, screen):
        row = 0
        if (not self.font): self.initFont() 
        for key in self.data:
            key_text = key
            for i in range(0,8 - len(key)):
                key_text += ' '
            text = self.font.render(f'{key_text}= {self.data[key]}', True, (255,0,0), (0,255,0))
            screen.blit(text, (self.x,self.y + row * (self.font_size + self.spacing)))
            row += 1
    
    def update(self):
        self.data['ticks'] += 1

    def initFont(self):
        self.font = pygame.font.SysFont('lucidaconsole', self.font_size)
        

debugui = DebugUI()