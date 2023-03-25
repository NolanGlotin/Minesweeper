import pygame
import random
import numpy


# Menu du jeu
class Menu :

    # Comportement des boutons
    class Button :
        def __init__(self,name,position):
            self.name = name
            self.scale = (96,48)
            self.image = pygame.transform.scale(pygame.image.load('assets/Button'+name+'.png'),(self.scale[0]*1.5,self.scale[1]*1.5))
            self.hoveredImage = pygame.transform.scale(pygame.image.load('assets/Button'+name+'Hovered.png'),(self.scale[0]*1.5,self.scale[1]*1.5))
            self.rect = self.image.get_rect()
            self.rect.center = (position[0], position[1])
            self.isHovered = False
        # Action à effectuer quand le bouton est cliqué
        def onClick(self):
            global scene
            global dim
            if self.name == 'NewGame':
                scene = 'Game'
            elif self.name == 'Quit':
                scene = 'Quit'
            elif self.name == 'Options':
                scene = 'Options'
            elif self.name == 'Menu':
                scene = 'MainMenu'
            else:
                if self.name == '8x8':
                    dim = (8,8)
                elif self.name == '12x12':
                    dim = (12,12)
                elif self.name == '16x16':
                    dim = (16,16)
                elif self.name == '20x20':
                    dim = (20,20)
                scene = 'MainMenu'

    def __init__(self, buttonsList):
        self.fps = 120
        self.buttons = []
        self.buttonsTypes = buttonsList
        self.buttonDist = 100
        self.width, self.height = 300, (len(self.buttonsTypes)+1)*self.buttonDist
        self.screen = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_icon(pygame.image.load('assets/TileFlag.png'))
        pygame.display.set_caption('Minesweeper')
        self.clock = pygame.time.Clock()
        for y in range (len(self.buttonsTypes)):
            btn = self.buttonsTypes[y]
            self.buttons.append(self.Button(btn,(self.width/2,(y+1)*self.buttonDist)))
        self.running = True

    # Actions de  l'utilisateur
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                global scene
                scene = 'Quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in self.buttons:
                    if btn.isHovered:
                        btn.onClick()
                        self.running = False
        mousePos = pygame.mouse.get_pos()
        for btn in self.buttons:
            if btn.rect.collidepoint(mousePos):
                btn.isHovered = True
            else:
                btn.isHovered = False
    # Affichage graphique
    def draw(self):
        self.screen.fill('grey')
        for btn in self.buttons:
            if btn.isHovered:
                self.screen.blit(btn.hoveredImage,btn.rect)
            else:
                self.screen.blit(btn.image,btn.rect)
        pygame.display.flip()
    # Boucle principale
    def run(self):
        while self.running:
            self.handleEvents()
            self.draw()
            self.clock.tick(self.fps)

# Jeu
class Game :

    def __init__(self,dim):
        pygame.display.set_icon(pygame.image.load('assets/TileMine.png'))
        self.title = 'Minesweeper'
        self.unit = 50
        self.offset = 50
        self.width, self.height = dim[0], dim[1]
        self.winWidth , self.winHeight = self.width*self.unit + self.offset*2, self.height*self.unit + self.offset*2
        self.screen = pygame.display.set_mode((self.winWidth,self.winHeight))
        self.clock = pygame.time.Clock()
        self.screen.fill('grey')
        self.fps = 120
        self.mines = (self.width*self.height)//6
        self.loadSprites()
        self.M = self.createMap(self.width, self.height, self.mines)
        self.displayMap()
        self.running = True
        self.playing = True

    # Importation des images
    def loadSprites(self):
        Sprites = ['0','1','2','3','4','5','6','7','8','Exploded','Flag','FlagIncorrect','Mine','Unknown']
        self.TileImages = {}
        for sprite in Sprites:
            self.TileImages[sprite] = pygame.transform.scale(pygame.image.load('assets/Tile'+sprite+'.png'),(self.unit,self.unit))
    # Création aléatoire de la carte
    def createMap(self, width, height, mines):
        M = numpy.zeros((width, height),dtype=int)
        self.Images = numpy.empty(M.shape,dtype=pygame.Surface)
        for i in range (mines):
            x, y = random.randint(0,width-1), random.randint(0,height-1)
            while M[x,y]==-1:
                x, y = random.randint(0,width-1), random.randint(0,height-1)
            M[x,y] = -1
        for x in range (width):
            for y in range (height):
                self.Images[x,y] = 'Unknown'
                if M[x,y]!=-1:
                    count = 0
                    for dx in range (-1,2):
                        for dy in range (-1,2):
                            if 0<=x+dx<width and 0<=y+dy<height and M[x+dx,y+dy]==-1:
                                count += 1
                    M[x,y] = count
        return M

    # Affichage de la carte
    def displayMap(self):
        for x in range (self.Images.shape[0]):
            for y in range (self.Images.shape[1]):
                self.screen.blit(self.TileImages[self.Images[x,y]],(self.offset+x*self.unit,self.offset+y*self.unit))

    # Affichage d'une case
    def reveal(self,x,y):
        box = self.M[x,y]
        if box == -1:
            self.Images[x,y] = 'Exploded'
            self.displayMap()
            self.loose()
        else:
            if self.M[x,y] == 0:
                self.quickReveal(x,y)
            else:
                self.Images[x,y] = str(box)
            self.displayMap()
    def quickReveal(self,x,y):
        self.Images[x,y] = '0'
        for dx in range (-1,2):
            for dy in range (-1,2):
                if 0<=x+dx<self.M.shape[0] and 0<=y+dy<self.M.shape[1] and self.Images[x+dx,y+dy] == 'Unknown':
                    if self.M[x+dx,y+dy] == 0:
                        self.quickReveal(x+dx,y+dy)
                    else:
                        self.Images[x+dx,y+dy] = str(self.M[x+dx,y+dy])

    # Marquage d'une case
    def flag(self,x,y):
        self.Images[x,y] = 'Flag'
        self.displayMap()
        self.checkWin()
    # Démarquage d'une case
    def unflag(self,x,y):
        self.Images[x,y] = 'Unknown'
        self.displayMap()
        self.checkWin()

    # Vérification d'un éventuelle victoire
    def checkWin(self):
        win = True
        for x in range (self.M.shape[0]):
            for y in range (self.M.shape[1]):
                if self.M[x,y] == -1 and self.Images[x,y] != 'Flag' or self.M[x,y] != -1 and self.Images[x,y] == 'Flag' or self.Images[x,y] == 'Unknown':
                    win = False
        if win:
            self.win()

    # Gestion de la défaite
    def loose(self):
        print('Perdu !')
        self.playing = False
        for x in range (self.M.shape[0]):
            for y in range (self.M.shape[1]):
                image = self.Images[x,y]
                value = self.M[x,y]
                if value == -1 and image == 'Unknown':
                    self.Images[x,y] = 'Mine'
                if image == 'Flag' and value != -1:
                    self.Images[x,y] = 'FlagIncorrect'
        self.displayMap()
    # Gestion de la victoire
    def win(self):
        print('Gagné !')
        self.playing = False

    # Actions de l'utilisateur
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                global scene
                scene = 'Quit'
            if self.playing:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    x = (x-self.offset)//self.unit
                    y = (y-self.offset)//self.unit
                    if 0<=x<self.M.shape[0] and 0<=y<self.M.shape[1]:
                        if event.button == 1 and self.Images[x,y] != 'Flag':
                            self.reveal(x,y)
                        elif event.button == 3:
                            if self.Images[x,y] == 'Unknown':
                                self.flag(x,y)
                            elif self.Images[x,y] == 'Flag':
                                self.unflag(x,y)
    # Actualisation
    def update(self):
        pygame.display.set_caption(self.title +' | ' + str(int(self.clock.get_fps())) + ' fps')
    # Affichage graphique
    def draw(self):
        pygame.display.flip()
    # Boucle prinicpale
    def run(self):
        while self.running:
            self.handleEvents()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

# Code prinicpal
if __name__ == '__main__':
    pygame.init()
    scene = 'MainMenu'
    dim = (12, 12)
    while scene != 'Quit':
        if scene == 'MainMenu':
            game = Menu(['NewGame','Options','Quit'])
            game.run()
        if scene == 'Options':
            game = Menu(['8x8','12x12','16x16','20x20','Menu'])
            game.run()
        if scene == 'Game':
            game = Game(dim)
            game.run()
        if scene == 'Quit':
            pygame.quit()