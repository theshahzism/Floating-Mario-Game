import tkinter as tk
from PIL import Image, ImageTk
from time import sleep
import random # For generating random numbers
import sys # We will use sys.exit to exit the program
import pygame
from pygame.locals import * # Basic pygame imports

# Global Variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/maryo.png'
BACKGROUND = 'gallery/sprites/bg.jpg'
PIPE = 'gallery/sprites/pipe.png'
score = 0
#colors
red=(255,0,0)
black=(0,0,0)


def easy_game():
    root.destroy()
                
    def ScreenText(text,color,x,y,size,style,bold=False,italic=False):
        font=pygame.font.SysFont(style,size,bold=bold,italic=italic)
        screen_text=font.render(text,True,color)
        SCREEN.blit(screen_text,(x,y))

    def HighestScore():
        with open('highest score.txt','r') as f:
            return f.read()
    def mainGame():
        score = 0
        playerx = int(SCREENWIDTH/5)
        playery = int(SCREENWIDTH/2)
        basex = 0

        # Create 2 pipes for blitting on the screen
        newPipe1 = getRandomPipe()
        newPipe2 = getRandomPipe()

        # my List of upper pipes
        upperPipes = [
            {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
            {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
        ]
        # my List of lower pipes
        lowerPipes = [
            {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
            {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
        ]
        highestscore=0
        pipeVelX = -4
        playerVelY = -7
        playerMaxVelY = 10
        playerMinVelY = -8
        playerAccY = 1
        playerFlapAccv = -10 # velocity while flapping
        playerFlapped = False # It is true only when the bird is flapping
        try:
            highestscore=int(HighestScore())
        except:
            highestscore=0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery > 0:
                        playerVelY = playerFlapAccv
                        playerFlapped = True
                        GAME_SOUNDS['wing'].play()

            crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
            if crashTest:
                return     

            #check for score
            playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
                if pipeMidPos<= playerMidPos < pipeMidPos +4:
                    score +=1
                    print(f"Your score is {score}") 
                    GAME_SOUNDS['point'].play()
            ScreenText(f"score{score}",black,10,40,size=20,style="Calibri")
            if (highestscore<score):
                highestscore=score
            with open('highest score.txt','w+') as f:
                f.write(str(highestscore))

            if playerVelY <playerMaxVelY and not playerFlapped:
                playerVelY += playerAccY

            if playerFlapped:
                playerFlapped = False            
            playerHeight = GAME_SPRITES['player'].get_height()
            playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

            # move pipes to the left
            for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
                upperPipe['x'] += pipeVelX
                lowerPipe['x'] += pipeVelX

            # Add a new pipe when the first is about to cross the leftmost part of the screen
            if 0<upperPipes[0]['x']<5:
                newpipe = getRandomPipe()
                upperPipes.append(newpipe[0])
                lowerPipes.append(newpipe[1])

            # if the pipe is out of the screen, remove it
            if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
                upperPipes.pop(0)
                lowerPipes.pop(0)
            
            # Lets blit our sprites now
            SCREEN.blit(GAME_SPRITES['background'], (0, 0))
            for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
                SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

            SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
            SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
            myDigits = [int(x) for x in list(str(score))]
            width = 0
            for digit in myDigits:
                width += GAME_SPRITES['numbers'][digit].get_width()
            Xoffset = (SCREENWIDTH - width)/2

            for digit in myDigits:
                SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
                Xoffset += GAME_SPRITES['numbers'][digit].get_width()
            ScreenText(f"Highest Score: {highestscore}",black,SCREENWIDTH-145,10,size=25,style='Calibri Bold')
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def isCollide(playerx, playery, upperPipes, lowerPipes):
        for pipe in upperPipes:
            pipeHeight = GAME_SPRITES['pipe'][0].get_height()
            if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
                GAME_SOUNDS['hit'].play()
                return True

        for pipe in lowerPipes:
            if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
                GAME_SOUNDS['hit'].play()
                return True


        return False

    def getRandomPipe():
        """
        Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
        """
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        offset = SCREENHEIGHT/3
        y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
        pipeX = SCREENWIDTH + 10
        y1 = pipeHeight - y2 + offset
        pipe = [
            {'x': pipeX, 'y': -y1}, #upper Pipe
            {'x': pipeX, 'y': y2} #lower Pipe
        ]
        return pipe

    if __name__ == "__main__":
        # This will be the main point from where our game will start
        pygame.init() # Initialize all pygame's modules
        FPSCLOCK = pygame.time.Clock()
        pygame.display.set_caption('Floating Mario')
        GAME_SPRITES['numbers'] = ( 
            pygame.image.load('gallery/sprites/0.png').convert_alpha(),
            pygame.image.load('gallery/sprites/1.png').convert_alpha(),
            pygame.image.load('gallery/sprites/2.png').convert_alpha(),
            pygame.image.load('gallery/sprites/3.png').convert_alpha(),
            pygame.image.load('gallery/sprites/4.png').convert_alpha(),
            pygame.image.load('gallery/sprites/5.png').convert_alpha(),
            pygame.image.load('gallery/sprites/6.png').convert_alpha(),
            pygame.image.load('gallery/sprites/7.png').convert_alpha(),
            pygame.image.load('gallery/sprites/8.png').convert_alpha(),
            pygame.image.load('gallery/sprites/9.png').convert_alpha(),
        )

        GAME_SPRITES['base'] =pygame.image.load('gallery/sprites/base.png').convert_alpha()
        GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
        pygame.image.load(PIPE).convert_alpha()
        )

        # Game sounds

        GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/mario_dies.wav')
        GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
        GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
        GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')
        GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
        GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    def game_over():
        game_over_img = pygame.image.load('gallery/sprites/endo.png')
        game_over_img_rect = game_over_img.get_rect()
        game_over_img_rect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)
        SCREEN.blit(game_over_img, game_over_img_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    SCREEN.blit(game_over_img, game_over_img_rect)
                pygame.display.update()
                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                            pygame.quit()
                            sys.exit()
                        elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                            return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        SCREEN.blit(game_over_img, game_over_img_rect)
    while True:
        mainGame() 
        game_over()


def hard_game():
    root.destroy()
    def ScreenText(text,color,x,y,size,style,bold=False,italic=False):
        font=pygame.font.SysFont(style,size,bold=bold,italic=italic)
        screen_text=font.render(text,True,color)
        SCREEN.blit(screen_text,(x,y))

    def HighestScore():
        with open('highest score.txt','r') as f:
            return f.read()
    def mainGame():
        score = 0
        playerx = int(SCREENWIDTH/5)
        playery = int(SCREENWIDTH/2)
        basex = 0

        # Create 2 pipes for blitting on the screen
        newPipe1 = getRandomPipe()
        newPipe2 = getRandomPipe()

        # my List of upper pipes
        upperPipes = [
            {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
            {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
        ]
        # my List of lower pipes
        lowerPipes = [
            {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
            {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
        ]
        pipeVelX = -6
        playerVelY = -16
        playerMaxVelY = 17
        playerMinVelY = -9
        playerAccY = 1
        playerFlapAccv = -13 # velocity while flapping
        playerFlapped = False # It is true only when the bird is flapping
        try:
            highestscore=int(HighestScore())
        except:
            highestscore=0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery > 0:
                        playerVelY = playerFlapAccv
                        playerFlapped = True
                        GAME_SOUNDS['wing'].play()

            crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
            if crashTest:
                return     

            #check for score
            playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
                if pipeMidPos<= playerMidPos < pipeMidPos +4:
                    score +=1
                    print(f"Your score is {score}") 
                    GAME_SOUNDS['point'].play()
            ScreenText(f"score{score}",black,10,40,size=20,style="Calibri")
            if (highestscore<score):
                highestscore=score
            with open('hardest_highest score.txt','w+') as f:
                f.write(str(highestscore))

            if playerVelY <playerMaxVelY and not playerFlapped:
                playerVelY += playerAccY

            if playerFlapped:
                playerFlapped = False            
            playerHeight = GAME_SPRITES['player'].get_height()
            playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

            # move pipes to the left
            for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
                upperPipe['x'] += pipeVelX
                lowerPipe['x'] += pipeVelX

            # Add a new pipe when the first is about to cross the leftmost part of the screen
            if 0<upperPipes[0]['x']<6:
                newpipe = getRandomPipe()
                upperPipes.append(newpipe[0])
                lowerPipes.append(newpipe[1])

            # if the pipe is out of the screen, remove it
            if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
                upperPipes.pop(0)
                lowerPipes.pop(0)
            
            # Lets blit our sprites now
            SCREEN.blit(GAME_SPRITES['background'], (0, 0))
            for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
                SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

            SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
            SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
            myDigits = [int(x) for x in list(str(score))]
            width = 0
            for digit in myDigits:
                width += GAME_SPRITES['numbers'][digit].get_width()
            Xoffset = (SCREENWIDTH - width)/2

            for digit in myDigits:
                SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
                Xoffset += GAME_SPRITES['numbers'][digit].get_width()
            ScreenText(f"Highest Score: {highestscore}",black,SCREENWIDTH-145,10,size=25,style='Calibri Bold')
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def isCollide(playerx, playery, upperPipes, lowerPipes):
        if playery<=0 or playery>GROUNDY-25:
            GAME_SOUNDS['hit'].play()
            return True
        for pipe in upperPipes:
            pipeHeight = GAME_SPRITES['pipe'][0].get_height()
            if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
                GAME_SOUNDS['hit'].play()
                return True

        for pipe in lowerPipes:
            if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
                GAME_SOUNDS['hit'].play()
                return True


        return False

    def getRandomPipe():
        """
        Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
        """
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        offset = SCREENHEIGHT/3
        y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
        pipeX = SCREENWIDTH + 10
        y1 = pipeHeight - y2 + offset
        pipe = [
            {'x': pipeX, 'y': -y1}, #upper Pipe
            {'x': pipeX, 'y': y2} #lower Pipe
        ]
        return pipe

    if __name__ == "__main__":
        # This will be the main point from where our game will start
        pygame.init() # Initialize all pygame's modules
        FPSCLOCK = pygame.time.Clock()
        pygame.display.set_caption('Floating Mario')
        GAME_SPRITES['numbers'] = ( 
            pygame.image.load('gallery/sprites/0.png').convert_alpha(),
            pygame.image.load('gallery/sprites/1.png').convert_alpha(),
            pygame.image.load('gallery/sprites/2.png').convert_alpha(),
            pygame.image.load('gallery/sprites/3.png').convert_alpha(),
            pygame.image.load('gallery/sprites/4.png').convert_alpha(),
            pygame.image.load('gallery/sprites/5.png').convert_alpha(),
            pygame.image.load('gallery/sprites/6.png').convert_alpha(),
            pygame.image.load('gallery/sprites/7.png').convert_alpha(),
            pygame.image.load('gallery/sprites/8.png').convert_alpha(),
            pygame.image.load('gallery/sprites/9.png').convert_alpha(),
        )

        GAME_SPRITES['base'] =pygame.image.load('gallery/sprites/base.png').convert_alpha()
        GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
        pygame.image.load(PIPE).convert_alpha()
        )

        # Game sounds

        GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/mario_dies.wav')
        GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
        GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
        GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')
        GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
        GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    def game_over():
        game_over_img = pygame.image.load('gallery/sprites/endo.png')
        game_over_img_rect = game_over_img.get_rect()
        game_over_img_rect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)
        SCREEN.blit(game_over_img, game_over_img_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    SCREEN.blit(game_over_img, game_over_img_rect)
                pygame.display.update()
                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                            pygame.quit()
                            sys.exit()
                        elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                            return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        SCREEN.blit(game_over_img, game_over_img_rect)

    while True:
      mainGame()
      game_over()
        

def medium_game():
    root.destroy()
    def ScreenText(text,color,x,y,size,style,bold=False,italic=False):
        font=pygame.font.SysFont(style,size,bold=bold,italic=italic)
        screen_text=font.render(text,True,color)
        SCREEN.blit(screen_text,(x,y))

    def HighestScore():
        with open('highest score.txt','r') as f:
            return f.read()
    def mainGame():
        score = 0
        playerx = int(SCREENWIDTH/5)
        playery = int(SCREENWIDTH/2)
        basex = 0

        # Create 2 pipes for blitting on the screen
        newPipe1 = getRandomPipe()
        newPipe2 = getRandomPipe()

        # my List of upper pipes
        upperPipes = [
            {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
            {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
        ]
        # my List of lower pipes
        lowerPipes = [
            {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
            {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
        ]
        highestscore=0
        pipeVelX = -4
        playerVelY = -11
        playerMaxVelY = 15
        playerMinVelY = -8
        playerAccY = 1
        playerFlapAccv = -10 # velocity while flapping
        playerFlapped = False # It is true only when the bird is flapping
        try:
            highestscore=int(HighestScore())
        except:
            highestscore=0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery > 0:
                        playerVelY = playerFlapAccv
                        playerFlapped = True
                        GAME_SOUNDS['wing'].play()

            crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
            if crashTest:
                return     

            #check for score
            playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
                if pipeMidPos<= playerMidPos < pipeMidPos +4:
                    score +=1
                    print(f"Your score is {score}") 
                    GAME_SOUNDS['point'].play()
            ScreenText(f"score{score}",black,10,40,size=20,style="Calibri")
            if (highestscore<score):
                highestscore=score
            with open('medium_highest score.txt','w+') as f:
                f.write(str(highestscore))

            if playerVelY <playerMaxVelY and not playerFlapped:
                playerVelY += playerAccY

            if playerFlapped:
                playerFlapped = False            
            playerHeight = GAME_SPRITES['player'].get_height()
            playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

            # move pipes to the left
            for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
                upperPipe['x'] += pipeVelX
                lowerPipe['x'] += pipeVelX

            # Add a new pipe when the first is about to cross the leftmost part of the screen
            if 0<upperPipes[0]['x']<5:
                newpipe = getRandomPipe()
                upperPipes.append(newpipe[0])
                lowerPipes.append(newpipe[1])

            # if the pipe is out of the screen, remove it
            if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
                upperPipes.pop(0)
                lowerPipes.pop(0)
            
            # Lets blit our sprites now
            SCREEN.blit(GAME_SPRITES['background'], (0, 0))
            for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
                SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

            SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
            SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
            myDigits = [int(x) for x in list(str(score))]
            width = 0
            for digit in myDigits:
                width += GAME_SPRITES['numbers'][digit].get_width()
            Xoffset = (SCREENWIDTH - width)/2

            for digit in myDigits:
                SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
                Xoffset += GAME_SPRITES['numbers'][digit].get_width()
            ScreenText(f"Highest Score: {highestscore}",black,SCREENWIDTH-145,10,size=25,style='Calibri Bold')
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def isCollide(playerx, playery, upperPipes, lowerPipes):
        if playery<=0 or playery>GROUNDY-25:
            GAME_SOUNDS['hit'].play()
            return True
        for pipe in upperPipes:
            pipeHeight = GAME_SPRITES['pipe'][0].get_height()
            if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
                GAME_SOUNDS['hit'].play()
                return True

        for pipe in lowerPipes:
            if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
                GAME_SOUNDS['hit'].play()
                return True


        return False

    def getRandomPipe():
        """
        Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
        """
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        offset = SCREENHEIGHT/3
        y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
        pipeX = SCREENWIDTH + 10
        y1 = pipeHeight - y2 + offset
        pipe = [
            {'x': pipeX, 'y': -y1}, #upper Pipe
            {'x': pipeX, 'y': y2} #lower Pipe
        ]
        return pipe

    if __name__ == "__main__":
        # This will be the main point from where our game will start
        pygame.init() # Initialize all pygame's modules
        FPSCLOCK = pygame.time.Clock()
        pygame.display.set_caption('Floating Mario')
        GAME_SPRITES['numbers'] = ( 
            pygame.image.load('gallery/sprites/0.png').convert_alpha(),
            pygame.image.load('gallery/sprites/1.png').convert_alpha(),
            pygame.image.load('gallery/sprites/2.png').convert_alpha(),
            pygame.image.load('gallery/sprites/3.png').convert_alpha(),
            pygame.image.load('gallery/sprites/4.png').convert_alpha(),
            pygame.image.load('gallery/sprites/5.png').convert_alpha(),
            pygame.image.load('gallery/sprites/6.png').convert_alpha(),
            pygame.image.load('gallery/sprites/7.png').convert_alpha(),
            pygame.image.load('gallery/sprites/8.png').convert_alpha(),
            pygame.image.load('gallery/sprites/9.png').convert_alpha(),
        )

        GAME_SPRITES['base'] =pygame.image.load('gallery/sprites/base.png').convert_alpha()
        GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
        pygame.image.load(PIPE).convert_alpha()
        )

        # Game sounds

        GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/mario_dies.wav')
        GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
        GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
        GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')
        GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
        GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    def game_over():
        game_over_img = pygame.image.load('gallery/sprites/endo.png')
        game_over_img_rect = game_over_img.get_rect()
        game_over_img_rect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)
        SCREEN.blit(game_over_img, game_over_img_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    SCREEN.blit(game_over_img, game_over_img_rect)
                pygame.display.update()
                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                            pygame.quit()
                            sys.exit()
                        elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                            return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        SCREEN.blit(game_over_img, game_over_img_rect)
    while True:
        mainGame() 
        game_over()
# For starting label
def destroy_label():
    label.destroy()
    root.destroy()

root = tk.Tk()

label = tk.Label(root, text="Starting the game...")
label.pack()

root.after(2000, destroy_label)
root.mainloop()
    
root = tk.Tk()
root.title("FLOATING MARIO")
root.geometry("800x600")
root.iconbitmap(r'biticon.ico')

heading = tk.Label(root, text="FLOATING MARIO", font=("Arial", 24))
heading.pack()

instructions = tk.Label(root, text="""Greetings Player!
Press start to play the FLOATING MARIO GAME.
The game has three level. Each level will have pipe.Hiting them, will end the game.
If you hit the ceiling and bottom in easy mode, it's okay, but; will end the game in other modes.
In hard mode, score will be delayed.
Press up arrow or space key to handle your MARIO. Good Luck!""")
instructions.pack()

# create a frame for the logo
logo_frame = tk.Frame(root, bg="white", width=30, height=10)
logo_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# insert the logo image
logo_img = Image.open("gallery/sprites/mainlogo.png")
logo = ImageTk.PhotoImage(logo_img)
logo_label = tk.Label(logo_frame, image=logo, width=500 , height=300)
logo_label.pack()

start_button = tk.Button(root, text="Play in Easy mode", command=easy_game)
start_button.place(relx=0.3, rely=0.8, anchor=tk.CENTER)
start_button = tk.Button(root, text="Play in Medium mode", command=medium_game)
start_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
start_button = tk.Button(root, text="Play in Hard mode", command=hard_game)
start_button.place(relx=0.7, rely=0.8, anchor=tk.CENTER)

root.mainloop()
