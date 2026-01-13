import subprocess
import sys
import get_pip
import os

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    print("[GAME] Trying to import pygame")
    import pygame
except:
    print("[EXCEPTION] Pygame not installed")

    try:
        print("[GAME] Trying to install pygame via pip")
        import pip
        install("pygame")
        print("[GAME] Pygame has been installed")
    except:
        print("[EXCEPTION] Pip not installed on system")
        print("[GAME] Trying to install pip")
        get_pip.main()
        print("[GAME] Pip has been installed")
        try:
            print("[GAME] Trying to install pygame")
            import pip
            install("pygame")
            print("[GAME] Pygame has been installed")
        except:
            print("[ERROR 1] Pygame could not be installed")

    import pygame

import physics
import math
import courses
import startScreen
import profiles
import os
from time import sleep, time
import tkinter as tk
from tkinter import messagebox
import sys
import ui_style
from ui_style import (Colors, Fonts, HUDCard, draw_ball_shadow, draw_ball_premium, 
                      PremiumBackground, draw_shadow, draw_rounded_rect,
                      ParticleSystem, BallTrail, ParallaxBackground as ParallaxBG,
                      ScreenTransition, CameraShake, ScreenFlash, FlagAnimation, ConfettiSystem,
                      BallPhysicsEffect, AssetManager, Config, draw_ball_squash_stretch, PlatformRenderer)

# INITIALIZATION
pygame.init()

# Load Config
Config.load()
SOUND = Config.get('sfx_enabled', False)

winwidth = Config.get('screen_width', 1080)
winheight = Config.get('screen_height', 600)
pygame.display.set_caption('Super Minigolf')

# Initialize UI Style System
ui_style.init_ui()

# Create premium background
premium_bg = PremiumBackground(winwidth, winheight)

# ETAPA 2 - Particle system and effects
particle_system = ParticleSystem(max_particles=Config.get('particle_count', 150))
ball_trail = BallTrail(max_length=15)
parallax_bg = ParallaxBG(winwidth, winheight)
ball_physics = BallPhysicsEffect() # Squash/Stretch effect

# ETAPA 3 - Screen effects and animations
screen_transition = ScreenTransition(winwidth, winheight)
camera_shake = CameraShake()
screen_flash = ScreenFlash(winwidth, winheight)
flag_anim = FlagAnimation()
confetti = ConfettiSystem(max_particles=80)

# LOAD IMAGES
icon = AssetManager.load_image(os.path.join('img', 'icon.ico'), (32, 32))
background = AssetManager.load_image(os.path.join('img', 'back.png'), alpha=False)
sand = AssetManager.load_image(os.path.join('img', 'sand.png'))
edge = AssetManager.load_image(os.path.join('img', 'sandEdge.png'))
bottom = AssetManager.load_image(os.path.join('img', 'sandBottom.png'))
green = AssetManager.load_image(os.path.join('img', 'green.png'))
flag = AssetManager.load_image(os.path.join('img', 'flag.png'))
water = AssetManager.load_image(os.path.join('img', 'water.png'))
laser = AssetManager.load_image(os.path.join('img', 'laser.png'))
sticky = AssetManager.load_image(os.path.join('img', 'sticky.png'))

# Load coin animation frames
coinPics = [AssetManager.load_image(os.path.join('img', f'coin{i}.png')) for i in range(1, 9)]

powerMeter = AssetManager.load_image(os.path.join('img', 'power.png'), (150, 150))

# SET ICON
pygame.display.set_icon(icon)

# GLOBAL VARIABLES
coinTime = 0
coinIndex = 0
time = 0
rollVel = 0
strokes = 0
par = 0
level = 8
flagx = 0
coins = 0
shootPos = ()
ballColor = (255,255,255)
ballStationary = ()
line = None
power = 0
hole = ()
objects = []
put = False
shoot = False
start = True

# SOUND SETTINGS
MUSIC_VOLUME = Config.get('music_volume', 0.5)
SFX_VOLUME = Config.get('sfx_volume', 0.7)

# LOAD MUSIC AND SOUNDS
if Config.get('sfx_enabled', True):
    try:
        wrong = AssetManager.load_sound(os.path.join('sounds', 'wrong12.wav'))
        puttSound = AssetManager.load_sound(os.path.join('sounds', 'putt.wav'))
        inHole = AssetManager.load_sound(os.path.join('sounds', 'inHole.wav'))
        splash = AssetManager.load_sound(os.path.join('sounds', 'splash.wav'))
        
        # Set sound volumes
        if wrong: wrong.set_volume(SFX_VOLUME)
        if puttSound: puttSound.set_volume(SFX_VOLUME)
        if inHole: inHole.set_volume(SFX_VOLUME)
        if splash: splash.set_volume(SFX_VOLUME)
        
        if Config.get('music_enabled', True):
            # Load and play background music
            pygame.mixer.music.load(os.path.join('sounds', 'music.mp3'))
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
        
        print("[SOUND] Audio system initialized successfully")
    except Exception as e:
        print(f"[SOUND ERROR] Could not load audio: {e}")
        SOUND = False
        SOUND = False

# POWER UP VARS
powerUps = 7
hazard = False
stickyPower = False
mullagain = False
superPower = False
powerUpButtons = [[900, 35, 20, 'P', (255,69,0)],[1000, 35, 20, 'S', (255,0,255)], [950, 35, 20, 'M', (105,105,105)]]

# FONTS - Using modern typography from ui_style
myFont = Fonts.TITLE_MEDIUM  # For big messages
parFont = Fonts.HUD_LARGE    # For HUD elements
smallFont = Fonts.HUD_MEDIUM # For smaller text
controlsFont = Fonts.UI_TINY # For controls hint

win = pygame.display.set_mode((winwidth, winheight))

class scoreSheet():
    def __init__(self, parr):
        self.parList = parr
        self.par = sum(self.parList)
        self.holes = 9
        self.finalScore = None
        self.parScore = 0
        self.strokes = []
        self.win = win
        self.winwidth = winwidth
        self.winheight = winheight
        self.width = 400
        self.height = 510
        self.font = Fonts.UI_MEDIUM
        self.bigFont = Fonts.HUD_LARGE

    def getScore(self):
        return sum(self.strokes) - sum(self.parList[:len(self.strokes)])

    def getPar(self):
        return self.par

    def getStrokes(self):
        return sum(self.strokes)

    def drawSheet(self, score=0, coins_collected=0):
        self.strokes.append(score)
        grey = (220, 220, 220)

        text = self.bigFont.render('Strokes: ' + str(sum(self.strokes)), 1, grey)
        self.win.blit(text, (800, 330))
        
        # Display Coins Collected
        coin_text = self.font.render(f'Coins this level: {coins_collected}', 1, (255, 215, 0)) # Gold color
        self.win.blit(coin_text, (800, 370))
        
        text = self.bigFont.render('Par: ' + str(self.par), 1, grey)
        self.win.blit(text, (240 - (text.get_width()/2), 300 - (text.get_height()/2)))
        text = self.bigFont.render('Score: ', 1, grey)
        self.win.blit(text, (800, 275))

        scorePar = sum(self.strokes) - sum(self.parList[:len(self.strokes)])
        if scorePar < 0:
            color = (0,166,0)
        elif scorePar > 0:
            color = (255,0,0)
        else:
            color = grey

        textt = self.bigFont.render(str(scorePar), 1, color)
        win.blit(textt, (805 + text.get_width(), 275))

        startx = self.winwidth/2 - self.width /2
        starty = self.winheight/2 - self.height/2
        pygame.draw.rect(self.win, grey, (startx, starty, self.width, self.height))

        # Set up grid
        for i in range(1,4):
            # Column Lines
            pygame.draw.line(self.win, (0,0,0), (startx + (i * (self.width/3)), starty), (startx + (i * (self.width/3)), starty + self.height), 2)
        for i in range(1, 11):
            # Rows
            if i == 1:  # Display all headers for rows
                blit = self.font.render('Hole', 2, (0,0,0))
                self.win.blit(blit, (startx + 40, starty + 10))
                blit = self.font.render('Par', 2, (0,0,0))
                self.win.blit(blit, (startx + 184, starty + 10))
                blit = self.font.render('Stroke', 2, (0,0,0))
                self.win.blit(blit, (startx + 295, starty + 10))
                blit = self.font.render('Press the mouse to continue...', 1, (128,128,128))
                self.win.blit(blit, (384, 565))
            else:  # Populate rows accordingly
                blit = self.font.render(str(i - 1), 1, (128,128,128))
                self.win.blit(blit, (startx + 56, starty + 10 + ((i - 1) * (self.height/10))))

                blit = self.font.render(str(self.parList[i - 2]), 1, (128,128,128))
                self.win.blit(blit, (startx + 60 + 133, starty + 10 + ((i - 1) * (self.height/10))))
                try:  # Catch the index out of range error, display the stokes each level
                    if self.strokes[i - 2] < self.parList[i - 2]:
                        color = (0,166,0)
                    elif self.strokes[i - 2] > self.parList[i - 2]:
                        color = (255,0,0)
                    else:
                        color = (0,0,0)

                    blit = self.font.render(str(self.strokes[i - 2]), 1, color)
                    self.win.blit(blit, ((startx + 60 + 266, starty + 10 + ((i - 1) * (self.height/10)))))
                except:
                    blit = self.font.render('-', 1, (128,128,128))
                    self.win.blit(blit, (startx + 62 + 266, starty + 10 + ((i - 1) * (self.height/10))))

            # Draw row lines
            pygame.draw.line(self.win, (0,0,0), (startx, starty + (i * (self.height/10))), (startx + self.width, starty + (i * (self.height / 10))), 2)


def error():
    if SOUND:
        wrong.play()
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showerror('Out of Powerups!', 'You have no more powerups remaining for this course, press ok to continue...')
    try:
        root.destroy()
    except:
        pass


def showAudioSettings():
    """Display audio settings menu"""
    global SOUND, MUSIC_VOLUME, SFX_VOLUME
    
    settings_surface = pygame.Surface((400, 300))
    
    # Fonts
    title_font = pygame.font.SysFont('comicsansms', 30)
    sound_font = pygame.font.SysFont('comicsansms', 20)
    inst_font = pygame.font.SysFont('comicsansms', 14) # Smaller for detailed instructions

    waiting = True
    while waiting:
        settings_surface.fill((220, 220, 220))

        # Title
        title_text = title_font.render('Audio Settings', 1, (64, 64, 64))
        settings_surface.blit(title_text, (200 - title_text.get_width()//2, 20))
        
        # Values
        sound_text = sound_font.render(f'Sound: {"ON" if SOUND else "OFF"}', 1, (64, 64, 64))
        settings_surface.blit(sound_text, (50, 70))
        
        music_text = sound_font.render(f'Music: {int(MUSIC_VOLUME * 100)}%', 1, (64, 64, 64))
        settings_surface.blit(music_text, (50, 110))
        
        sfx_text = sound_font.render(f'SFX: {int(SFX_VOLUME * 100)}%', 1, (64, 64, 64))
        settings_surface.blit(sfx_text, (50, 150))
        
        # Instructions
        # S: Toggle, M/N: Music, F/G: SFX
        y_inst = 190
        inst_lines = [
            "Controls:",
            "[S] Toggle Sound ON/OFF",
            "[M] Increase Music   [N] Decrease Music",
            "[F] Increase SFX     [G] Decrease SFX",
            "[ESC] Close Menu"
        ]
        
        for line in inst_lines:
            t = inst_font.render(line, 1, (100, 100, 100))
            settings_surface.blit(t, (30, y_inst))
            y_inst += 25
        
        # Render to screen
        win.blit(settings_surface, (340, 150))
        pygame.display.update()
        
        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                elif event.key == pygame.K_s:
                    SOUND = not SOUND
                    if SOUND:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
                elif event.key == pygame.K_m:
                    MUSIC_VOLUME = max(0.0, min(1.0, MUSIC_VOLUME + 0.1))
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                elif event.key == pygame.K_n:
                    MUSIC_VOLUME = max(0.0, min(1.0, MUSIC_VOLUME - 0.1))
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                elif event.key == pygame.K_f:
                    SFX_VOLUME = max(0.0, min(1.0, SFX_VOLUME + 0.1))
                    if SOUND:
                        for s in [wrong, puttSound, inHole, splash]:
                            s.set_volume(SFX_VOLUME)
                elif event.key == pygame.K_g:
                    SFX_VOLUME = max(0.0, min(1.0, SFX_VOLUME - 0.1))
                    if SOUND:
                        for s in [wrong, puttSound, inHole, splash]:
                            s.set_volume(SFX_VOLUME)


def endScreen(): # Display this screen when the user completes trhe course
    global start, starting, level, sheet, coins
    starting = True
    start = True
    
    # RE-WRITE TEXT FILE Contaning Scores
    oldscore = 'None'
    oldcoins = 0
    
    # Read old scores
    if os.path.exists('scores.txt'):
        try:
            file = open('scores.txt', 'r')
            for line in file:
                l = line.split()
                if len(l) >= 2:
                    if l[0] == 'score':
                        oldscore = str(l[1]).strip()
                    if l[0] == 'coins':
                        oldcoins = str(l[1]).strip()
            file.close()
        except:
            pass

    # Save new scores
    is_new_best = False
    try:
        file = open('scores.txt', 'w')
        if str(oldscore).lower() != 'none':
            if sheet.getScore() < int(oldscore):
                is_new_best = True
                file.write('score ' + str(sheet.getScore()) + '\n')
                profiles.update_best_score(sheet.getScore())
            else:
                file.write('score ' + str(oldscore) + '\n')
        else:
            is_new_best = True
            file.write('score ' + str(sheet.getScore()) + '\n')
            profiles.update_best_score(sheet.getScore())
        
        # Save coins (Syncing profiles and scores.txt)
        # 'coins' is the total current wealth.
        file.write('coins ' + str(coins) + '\n')
        profiles.set_coins(coins)
        
        file.close()
    except Exception as e:
        print(f"Error saving scores: {e}")

    # Celebration!
    confetti.emit(winwidth//2, winheight//2, count=150)
    if is_new_best:
        screen_flash.flash((255, 215, 0), 150) # Gold flash for new best

    # Fonts
    title_font = AssetManager.get_font('Arial', 50, bold=True)
    info_font = AssetManager.get_font('Arial', 30, bold=False)
    small_font = AssetManager.get_font('Arial', 20, bold=False)

    # Wait / Animation Loop
    loop = True
    clock = pygame.time.Clock()
    
    while loop:
        clock.tick(60)
        
        # 1. Background
        premium_bg.draw(win)
        
        # 2. Confetti
        confetti.update()
        confetti.draw(win)
        
        # 3. Flash
        screen_flash.update()
        screen_flash.draw(win)
        
        # 4. Panel (Dark overlay for readability)
        panel_w, panel_h = 600, 450
        panel_x = (winwidth - panel_w) // 2
        panel_y = (winheight - panel_h) // 2
        
        # Draw panel shadow and background
        draw_shadow(win, (panel_x, panel_y, panel_w, panel_h), 20)
        draw_rounded_rect(win, (0, 0, 0, 200), (panel_x, panel_y, panel_w, panel_h), 20)
        
        # 5. Text Content
        # Title
        title_text = "Course Completed!"
        title_surf = title_font.render(title_text, True, Colors.TEXT_LIGHT)
        win.blit(title_surf, (winwidth//2 - title_surf.get_width()//2, panel_y + 40))
        
        if is_new_best:
            best_surf = info_font.render("New Best Score!", True, (255, 215, 0)) # Gold
            win.blit(best_surf, (winwidth//2 - best_surf.get_width()//2, panel_y + 100))
        
        # Stats
        y_off = 160
        gap = 50
        
        # Par
        par_surf = info_font.render(f"Par: {sheet.getPar()}", True, Colors.TEXT_LIGHT)
        win.blit(par_surf, (winwidth//2 - par_surf.get_width()//2, panel_y + y_off))
        
        # Strokes
        strokes_surf = info_font.render(f"Strokes: {sheet.getStrokes()}", True, Colors.TEXT_LIGHT)
        win.blit(strokes_surf, (winwidth//2 - strokes_surf.get_width()//2, panel_y + y_off + gap))
        
        # Score
        score_surf = info_font.render(f"Score: {sheet.getScore()}", True, Colors.ACCENT_BLUE)
        win.blit(score_surf, (winwidth//2 - score_surf.get_width()//2, panel_y + y_off + gap*2))
        
        # Coins
        coins_surf = info_font.render(f"Coins: {coins}", True, (255, 215, 0))
        win.blit(coins_surf, (winwidth//2 - coins_surf.get_width()//2, panel_y + y_off + gap*3))
        
        # Continue prompt
        prompt_surf = small_font.render("Click anywhere to continue...", True, (150, 150, 150))
        win.blit(prompt_surf, (winwidth//2 - prompt_surf.get_width()//2, panel_y + panel_h - 40))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Fix crash
            if event.type == pygame.MOUSEBUTTONDOWN:
                loop = False
                break
    level = 1
    setup(level)
    list = courses.getPar(1)
    par = list[level - 1]
    sheet = scoreSheet(list)
    starting = True
    hover = False
    while starting:
        pygame.time.delay(10)
        startScreen.mainScreen(hover)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                hover = startScreen.shopClick(pos)
                course = startScreen.click(pos)
                startScreen.mouseOver(course != None)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check Seed Mode
                seed = startScreen.seedClick(pos)
                if seed:
                    courses.set_seed(seed)
                    level = 1
                    setup(level)
                    starting = False
                    break
                
                if startScreen.click(pos) != None:
                    courses.set_seed(None) # Reset to normal
                    starting = False
                    break
                if startScreen.shopClick(pos) == True:
                    surface = startScreen.drawShop()
                    win.blit(surface, (0, 0))
                    pygame.display.update()
                    shop = True
                    while shop:
                        for event in pygame.event.get():
                            pygame.time.delay(10)
                            if event.type == pygame.QUIT:
                                pygame.quit()
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                if pos[0] > 10 and pos[0] < 100 and pos[1] > 560:
                                    shop = False
                                    break
                                surface = startScreen.drawShop(pos, True)
                                win.blit(surface, (0, 0))
                                pygame.display.update()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()




def setup(level):  # Setup objects for the level from module courses
    global line, par, hole, power, ballStationary, objects, ballColor, stickyPower, superPower, mullagain, start_coins, coins
    start_coins = coins
    ballColor = (255,255,255)
    stickyPower = False
    superPower = False
    mullagain = False
    if level >= 10:
        endScreen()  # Completed the course
    else:
        list = courses.getPar(1)
        par = list[level - 1]
        pos = courses.getStart(level, 1)
        ballStationary = pos

        objects = courses.getLvl(level)

        # Create the borders if sand is one of the objects
        for i in objects:
            if i[4] == 'sand':
                objects.append([i[0] - 16, i[1], 16, 64, 'edge'])
                objects.append([i[0] + ((i[2] // 64) * 64), i[1], 16, 64, 'edge'])
                objects.append([i[0], i[1] + 64, i[2], 16, 'bottom'])
            elif i[4] == 'flag':
                # Define the position of the hole
                hole = (i[0] + 2, i[1] + i[3])

        line = None
        power = 1


def fade():  # Fade out screen when player gets ball in hole
    fade = pygame.Surface((winwidth, winheight))
    fade.fill((0,0,0))
    for alpha in range(0, 300):
        fade.set_alpha(alpha)
        redrawWindow(ballStationary, None, False, False)
        win.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(1)


def showScore():  # Display the score from class scoreSheet
    global level, coins, start_coins
    sleep(2)
    level += 1
    
    # Calculate coins collected this level
    coins_collected = coins - start_coins
    if coins_collected < 0: coins_collected = 0
    
    sheet.drawSheet(strokes, coins_collected)
    pygame.display.update()
    go = True
    while go:  # Wait until user clicks until we move to next level
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                go = False
                setup(level)


def holeInOne():  # If player gets a hole in one display special mesage to screen
    # ETAPA 3 - Celebration effects!
    confetti.emit(winwidth // 2, winheight // 2, count=50)
    screen_flash.flash((255, 215, 0), intensity=100)  # Gold flash
    
    # Create text with shadow for readability
    message = 'Hole in One!'
    
    # Shadow text (dark outline)
    shadow_font = pygame.font.SysFont('Arial', 48, bold=True)
    shadow = shadow_font.render(message, True, (0, 0, 0))
    text = shadow_font.render(message, True, (255, 255, 255))
    
    x = (winwidth / 2) - (text.get_width() / 2)
    y = (winheight / 2) - (text.get_height() / 2)
    
    # Draw shadow offset
    win.blit(shadow, (x + 2, y + 2))
    win.blit(shadow, (x - 2, y + 2))
    win.blit(shadow, (x + 2, y - 2))
    win.blit(shadow, (x - 2, y - 2))
    # Draw main text
    win.blit(text, (x, y))
    pygame.display.update()
    showScore()


def displayScore(stroke, par):  # Using proper golf terminology display score
    if stroke == 0:
        message = 'Skipped'
    elif stroke == par - 4:
        message = '-4 !'
    elif stroke == par - 3:
        message = 'Albatross!'
    elif stroke == par - 2:
        message = 'Eagle!'
    elif stroke == par - 1:
        message = 'Birdie!'
    elif stroke == par:
        message = 'Par'
    elif stroke == par + 1:
        message = 'Bogey'
    elif stroke == par + 2:
        message = 'Double Bogey'
    elif stroke == par + 3:
        message = 'Triple Bogey'
    else:
        message = '+' + str(stroke - par)

    # Create text with shadow for readability
    display_font = pygame.font.SysFont('Arial', 48, bold=True)
    shadow = display_font.render(message, True, (0, 0, 0))
    label = display_font.render(message, True, (255, 255, 255))
    
    x = (winwidth // 2) - (label.get_width() // 2)
    y = (winheight // 2) - (label.get_height() // 2)
    
    # Draw shadow (outline effect)
    win.blit(shadow, (x + 2, y + 2))
    win.blit(shadow, (x - 2, y + 2))
    win.blit(shadow, (x + 2, y - 2))
    win.blit(shadow, (x - 2, y - 2))
    # Draw main text
    win.blit(label, (x, y))
    pygame.display.update()

    showScore()


def redrawWindow(ball, line, shoot=False, update=True):
    global water, par, strokes, flagx

    # ========================================
    


    pygame.display.update()
    # PREMIUM BACKGROUND WITH GRADIENT + VIGNETTE
    # ========================================
    premium_bg.draw(win, background)
    
    # ========================================
    # ETAPA 2 - PARALLAX CLOUDS
    # ========================================
    parallax_bg.draw(win)
    
    # ========================================
    # DRAW LEVEL OBJECTS
    # ========================================
    for i in objects:
        if i[4] == 'sand':
            for x in range(i[2]//64):
                win.blit(sand, (i[0] + (x * 64), i[1]))
        elif i[4] == 'water':
            for x in range(i[2] // 64):
                water = water.convert()
                water.set_alpha(170)
                win.blit(water, (i[0] + (x * 64), i[1]))
        elif i[4] == 'edge':
            win.blit(edge, (i[0], i[1]))
        elif i[4] == 'bottom':
            # ETAPA 3 - Procedural Material: Stone
            tex = PlatformRenderer.create_texture(i[2], 64, 'stone')
            win.blit(tex, (i[0], i[1]))
        elif i[4] == 'flag':
            # ETAPA 3 - Animated flag with wind effect
            flag_anim.update()
            wave_offset = flag_anim.get_offset()
            
            # Draw flag shadow
            shadow_surf = pygame.Surface((20, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), (0, 0, 20, 8))
            win.blit(shadow_surf, (i[0] - 8, i[1] + i[3] + 2))
            
            # Draw flag with wave offset
            win.blit(flag, (i[0] + wave_offset, i[1]))
            pygame.draw.circle(win, (0, 0, 0), (i[0] + 2, i[1] + i[3]), 6)
            flagx = i[0]
        elif i[4] == 'floor':
            # ETAPA 3 - Procedural Material: Wood
            tex = PlatformRenderer.create_texture(i[2], 64, 'wood')
            win.blit(tex, (i[0], i[1]))
        elif i[4] == 'green':
            for x in range(i[2] // 64):
                win.blit(green, (i[0] + (64 * x), i[1]))
        elif i[4] == 'wall':
            # ETAPA 3 - Procedural Material: Metal
            tex = PlatformRenderer.create_texture(64, i[3], 'metal')
            win.blit(tex, (i[0], i[1]))
        elif i[4] == 'laser':
            for x in range(i[3] // 64):
                win.blit(laser, (i[0], i[1] + (64 * x)))
        elif i[4] == 'sticky':
            for x in range(i[3]//64):
                win.blit(sticky, (i[0], i[1] + (64 * x)))
        elif i[4] == 'coin':
            if i[5]:
                img = coinImg()
                win.blit(img, (i[0], i[1]))

    # ========================================
    # POWER METER
    # ========================================
    win.blit(powerMeter, (4, 520))

    # ========================================
    # AIMING LINE
    # ========================================
    if line != None and not (shoot):
        pygame.draw.line(win, (0, 0, 0), ballStationary, line, 2)

    # ========================================
    # ETAPA 2 - BALL TRAIL
    # ========================================
    if shoot:
        ball_trail.add_position(ball[0], ball[1])
    ball_trail.draw(win, ballColor)

    # ========================================
    # PREMIUM BALL WITH SHADOW AND HIGHLIGHT + SQUASH/STRETCH
    # ========================================
    draw_ball_shadow(win, ball, 5)
    
    # Calculate velocity for squash/stretch
    # (In a real implementation we would pass velocity properly)
    velocity = (0, 0) # Placeholder
    ball_physics.update(velocity)
    
    scale = ball_physics.get_scale()
    draw_ball_squash_stretch(win, ball, ballColor, 5, scale)
    
    # ========================================
    # ETAPA 2 - PARTICLE EFFECTS
    # ========================================
    particle_system.update()
    particle_system.draw(win)

    # ========================================
    # PREMIUM HUD WITH GLASS CARDS
    # ========================================
    
    # Par Card
    draw_shadow(win, (15, 10, 100, 40), 12, (2, 2), 2)
    draw_rounded_rect(win, (255, 255, 255, 45), (15, 10, 100, 40), 12)
    par_label = Fonts.UI_TINY.render("PAR", True, Colors.ACCENT_GREEN)
    win.blit(par_label, (25, 13))
    par_text = Fonts.HUD_LARGE.render(str(par), True, Colors.TEXT_PRIMARY)
    win.blit(par_text, (65, 12))
    
    # Strokes Card
    draw_shadow(win, (15, 55, 100, 40), 12, (2, 2), 2)
    draw_rounded_rect(win, (255, 255, 255, 45), (15, 55, 100, 40), 12)
    stroke_label = Fonts.UI_TINY.render("HIT", True, Colors.ACCENT_BLUE)
    win.blit(stroke_label, (25, 58))
    strokes_text = Fonts.HUD_LARGE.render(str(strokes), True, Colors.TEXT_PRIMARY)
    win.blit(strokes_text, (65, 57))
    
    # ========================================
    # PREMIUM POWER-UP BUTTONS
    # ========================================
    for x in powerUpButtons:
        # Shadow
        shadow_surf = pygame.Surface((x[2] * 2 + 8, x[2] * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 30), (x[2] + 4, x[2] + 6), x[2])
        win.blit(shadow_surf, (x[0] - x[2] - 4, x[1] - x[2] - 2))
        
        # Button background
        pygame.draw.circle(win, (255, 255, 255), (x[0], x[1]), x[2] + 2)
        pygame.draw.circle(win, x[4], (x[0], x[1]), x[2])
        
        # Highlight
        highlight_surf = pygame.Surface((x[2] * 2, x[2] * 2), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surf, (255, 255, 255, 80), (x[2] - 3, x[2] - 3), x[2] // 2)
        win.blit(highlight_surf, (x[0] - x[2], x[1] - x[2]))
        
        # Text
        text = Fonts.HUD_MEDIUM.render(x[3], True, (255, 255, 255))
        win.blit(text, (x[0] - text.get_width() // 2, x[1] - text.get_height() // 2))
    
    # Power-ups remaining label
    draw_shadow(win, (880, 58, 85, 28), 8, (2, 2), 1)
    draw_rounded_rect(win, (255, 255, 255, 40), (880, 58, 85, 28), 8)
    left_text = Fonts.UI_SMALL.render(f"×{powerUps}", True, Colors.TEXT_SECONDARY)
    win.blit(left_text, (910, 62))
    
    # ========================================
    # CONTROLS HINT (bottom)
    # ========================================
    controls_text = Fonts.UI_TINY.render('A: Audio | ESC: Quit | SPACE: Skip', True, Colors.TEXT_SECONDARY)
    # Subtle background for readability
    hint_bg = pygame.Surface((controls_text.get_width() + 16, controls_text.get_height() + 8), pygame.SRCALPHA)
    draw_rounded_rect(hint_bg, (0, 0, 0, 25), (0, 0, controls_text.get_width() + 16, controls_text.get_height() + 8), 6)
    win.blit(hint_bg, (12, winheight - 28))
    win.blit(controls_text, (20, winheight - 24))
    
    # ========================================
    # ETAPA 3 - CONFETTI (for celebrations)
    # ========================================
    confetti.update()
    confetti.draw(win)
    
    # ========================================
    # ETAPA 3 - CAMERA SHAKE
    # ========================================
    camera_shake.update()
    
    # ========================================
    # ETAPA 3 - SCREEN FLASH
    # ========================================
    screen_flash.update()
    screen_flash.draw(win)
    
    # ========================================
    # ETAPA 3 - SCREEN TRANSITION
    # ========================================
    screen_transition.update()
    screen_transition.draw(win)

    if update:
        # Draw HUD (Moved to end for Z-order)
        if profiles.current_user:
            # Coin HUD - Display TOTAL coins (Global Variable)
            # 'coins' variable tracks total user wealth (loaded at start + collected)
            coin_text = Fonts.HUD_MEDIUM.render(f"Coins: {coins}", True, Colors.ACCENT_GOLD)
            c_rect = coin_text.get_rect(topleft=(130, 20))
            bg_rect = c_rect.inflate(20, 10)
            draw_rounded_rect(win, (0, 0, 0, 100), bg_rect, 10)
            win.blit(coin_text, (130, 20))
            
            # User HUD (x=130, y=50)
            user_text = Fonts.UI_SMALL.render(f"Player: {profiles.current_user}", True, Colors.TEXT_SECONDARY)
            win.blit(user_text, (130, 50))

        powerBar()


def coinImg():  # Animation for spinning coin, coin acts as currency
    global coinTime, coinIndex
    coinTime += 1
    if coinTime == 15:  # We don't want to delay the game so we use a count variable based off the clock speed
        coinIndex += 1
        coinTime = 0
    if coinIndex == 8:
        coinIndex = 0
    return coinPics[coinIndex]


def powerBar(moving=False, angle=0):
    if moving:
        # Move the arm on the power meter if we've locked the angle
        redrawWindow(ballStationary, line, False, False)
        pygame.draw.line(win, (255,255,255), (80, winheight -7), (int(80 + round(math.cos(angle) * 60)), int((winheight - (math.sin(angle) * 60)))), 3)
    pygame.display.update()



# Find the angle that the ball hits the ground at
def findAngle(pos):
    sX = ballStationary[0]
    sY = ballStationary[1]
    try:
        angle = math.atan((sY - pos[1]) / (sX - pos[0]))
    except:
        angle = math.pi / 2

    if pos[1] < sY and pos[0] > sX:
        angle = abs(angle)
    elif pos[1] < sY and pos[0] < sX:
        angle = math.pi - angle
    elif pos[1] > sY and pos[0] < sX:
        angle = math.pi + abs(angle)
    elif pos[1] > sY and pos[0] > sX:
        angle = (math.pi * 2) - angle

    return angle


def onGreen():  # Determine if we are on the green
    global hole

    for i in objects:
        if i[4] == 'green':
            if ballStationary[1] < i[1] + i[3] and ballStationary[1] > i[1] - 20 and ballStationary[0] > i[0] and ballStationary[0] < i[0] + i[2]:
                return True
            else:
                return False


def overHole(x,y):  # Determine if we are over top of the hole
    if x > hole[0] - 6 and x < hole[0] + 6:
        if y > hole[1] - 13 and y < hole[1] + 10:
            return True
        else:
            return False
    else:
        return False


# Login Phase
if not profiles.current_user:
    startScreen.login()
    coins = profiles.get_coins()

list = courses.getPar(1)
par = list[level - 1]
sheet = scoreSheet(list)

pos = courses.getStart(level, 1)
ballStationary = pos
setup(1)


# MAIN GAME LOOP:
# - Collision of ball
# - Locking angle and power
# - Checking if power up buttons are clicked
# - Shooting the ball, uses physics module
# - Keeping track of strokes
# - Calls all functions and uses modules/classes imported and defined above

# Start loop
# Display start screen
hover = False
starting = True
while starting:
    pygame.time.delay(10)
    startScreen.mainScreen(hover)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            hover = startScreen.shopClick(pos)
            course = startScreen.click(pos)
            startScreen.mouseOver(course != None)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            # Check Seed Mode
            seed = startScreen.seedClick(pos)
            if seed:
                courses.set_seed(seed)
                level = 1
                setup(level)
                starting = False
                break
                
            if startScreen.click(pos) != None:
                courses.set_seed(None) # Reset to normal
                starting = False
                break
            if startScreen.shopClick(pos) == True:
                surface = startScreen.drawShop()
                win.blit(surface, (0,0))
                pygame.display.update()
                shop = True
                while shop:
                    for event in pygame.event.get():
                        pygame.time.delay(10)
                        if event.type == pygame.QUIT:
                            pygame.quit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()
                            if pos[0] > 10 and pos[0] < 100 and pos[1] > 560:
                                shop = False
                                break
                            surface = startScreen.drawShop(pos, True)
                            win.blit(surface, (0,0))
                            pygame.display.update()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

# Game Loop for levels and collision
while True:
    if stickyPower == False and superPower == False:
        ballColor = startScreen.getBallColor()
        if ballColor == None:
            ballColor = (255,255,255)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Back to Menu (Restart Game)
                pygame.quit()
                os.execl(sys.executable, sys.executable, *sys.argv)
                sys.exit()
            if event.key == pygame.K_SPACE:
                fade()
                if strokes == 1:
                    holeInOne()
                else:
                    displayScore(strokes, par)

                strokes = 0
            if event.key == pygame.K_a:  # Audio settings
                showAudioSettings()
                redrawWindow(ballStationary, line)  # Redraw the game after settings
        if event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            for x in powerUpButtons:
                if pos[0] < x[0] + x[2] and pos[0] > x[0] - x[2] and pos[1] < x[1] + x[2] and pos[1] > x[1] - x[2]:
                    if x[3] == 'S':
                        x[4] = (255,0,120)
                    elif x[3] == 'M':
                        x[4] = (105,75,75)
                    elif x[3] == 'P':
                        x[4] = (170,69,0)
                else:
                    if x[3] == 'S':
                        x[4] = (255,0,255)
                    elif x[3] == 'M':
                        x[4] = (105,105,105)
                    elif x[3] == 'P':
                        x[4] = (255,69,0)

        if event.type == pygame.MOUSEBUTTONDOWN:
            lock = 0
            pos = pygame.mouse.get_pos()
            # See if power up buttons are clicked
            for x in powerUpButtons:
                # Check collision of mouse and button
                if pos[0] < x[0] + x[2] and pos[0] > x[0] - x[2] and pos[1] < x[1] + x[2] and pos[1] > x[1] - x[2]:
                    lock = -1
                    if powerUps == 0:
                        error()
                        break
                    elif x[3] == 'S':  # Sticky Ball (sticks to any non-hazard)
                        if stickyPower is False and superPower is False and powerUps > 0:
                            stickyPower = True
                            powerUps -= 1
                            ballColor = (255,0,255)
                    elif x[3] == 'M':  # Mullagain, allows you to retry your sot from your previous position, will remove strokes u had on last shot
                        if mullagain is False and powerUps > 0 and strokes >= 1:
                            mullagain = True
                            powerUps -= 1
                            ballStationary = shootPos
                            pos = pygame.mouse.get_pos()
                            angle = findAngle(pos)
                            line = (round(ballStationary[0] + (math.cos(angle) * 50)),
                                    round(ballStationary[1] - (math.sin(angle) * 50)))
                            if hazard:
                                strokes -= 2
                            else:
                                strokes -= 1
                            hazard = False
                    elif x[3] == 'P':  # Power ball, power is multiplied by 1.5x
                        if superPower is False and stickyPower is False and powerUps > 0:
                            superPower = True
                            powerUps -= 1
                            ballColor = (255,69,0)

            # If you click the power up button don't lock angle
            if lock == 0:
                powerAngle = math.pi
                neg = 1
                powerLock = False
                loopTime = 0

                while not powerLock:  # If we haven't locked power stay in this loop until we do
                    loopTime += 1
                    if loopTime == 6:
                        powerAngle -= 0.1 * neg
                        powerBar(True, powerAngle)
                        loopTime = 0
                        if powerAngle < 0 or powerAngle > math.pi:
                            neg = neg * -1
                    else:
                        redrawWindow(ballStationary, line, False, False)


                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            strokes += 1
                            hazard = False
                            if not onGreen():
                                shoot = True
                            else:
                                put = True
                                if SOUND:
                                    puttSound.play()
                            if put:
                                power = (math.pi - powerAngle) * 5
                                rollVel = power
                            else:
                                if not superPower:  # Change power if we selected power ball
                                    power = (math.pi - powerAngle) * 30
                                else:
                                    power = (math.pi - powerAngle) * 40
                            
                            # Trigger ball stretch effect
                            ball_physics.on_launch(power / 30) # Normalize power roughly
                            ball_trail.clear()
                            particle_system.emit_dust(ballStationary[0], ballStationary[1], count=8)
                            if SOUND and not put:
                                puttSound.play()

                            shootPos = ballStationary
                            powerLock = True
                            break

        if event.type == pygame.MOUSEMOTION:  # Change the position of the angle line
            pos = pygame.mouse.get_pos()
            angle = findAngle(pos)
            line = (round(ballStationary[0] + (math.cos(angle) * 50)), round(ballStationary[1] - (math.sin(angle) * 50)))

            if onGreen():  # If we are on green have the angle lin point towards the hole, bc putter cannot chip
                if ballStationary[0] > flagx:
                    angle = math.pi
                    line = (ballStationary[0] - 30, ballStationary[1])
                else:
                    angle = 0
                    line = (ballStationary[0] + 30, ballStationary[1])

    if pygame.get_init():
        redrawWindow(ballStationary, line)
    hitting = False

    while put and not shoot:  # If we are putting
        # If we aren't in the hole
        if not(overHole(ballStationary[0], ballStationary[1])):
            pygame.time.delay(20)
            rollVel -= 0.5  # Slow down the ball gradually
            if angle == math.pi:
                ballStationary = (round(ballStationary[0] - rollVel), ballStationary[1])
            else:
                ballStationary = (round(ballStationary[0] + rollVel), ballStationary[1])
            redrawWindow(ballStationary, None, True)

            if rollVel < 0.5:  # Stop moving ball if power is low enough
                time = 0
                put = False
                pos = pygame.mouse.get_pos()
                angle = findAngle(pos)
                line = (round(ballStationary[0] + (math.cos(angle) * 50)), round(ballStationary[1] - (math.sin(angle) * 50)))

                #Determine what way to point the angle line
                if onGreen():
                    if ballStationary[0] > flagx:
                        angle = math.pi
                        line = (ballStationary[0] - 30, ballStationary[1])
                    else:
                        angle = 0
                        line = (ballStationary[0] + 30, ballStationary[1])
        else:
            # We have got the ball in the hole
            if SOUND:
                inHole.play()
            while True:  # Move ball so it looks like it goes into the hole (increase y value)
                pygame.time.delay(20)
                redrawWindow(ballStationary, None, True)
                ballStationary = (ballStationary[0], ballStationary[1] + 1)
                if ballStationary[0] > hole[0]:
                    ballStationary = (ballStationary[0] - 1, ballStationary[1])
                else:
                    ballStationary = (ballStationary[0] + 1, ballStationary[1])

                if ballStationary[1] > hole[1] + 5:
                    put = False
                    break

            # Advance to score board
            fade()
            if strokes == 1:
                holeInOne()
            else:
                displayScore(strokes, par)

            strokes = 0

    while shoot:  # If we are shooting the ball
        if not(overHole(ballStationary[0], ballStationary[1])):  # If we aren't in the hole
            maxT = physics.maxTime(power, angle)
            time += 0.085
            ballCords = physics.ballPath(ballStationary[0], ballStationary[1], power, angle, time)
            redrawWindow(ballCords, None, True)

            # TO FIX GLITCH WHERE YOU GO THROUGH WALLS AND FLOORS
            if ballCords[1] > 650:
                var = True
                while var:
                    fade()
                    if strokes == 1:
                        holeInOne()
                    else:
                        displayScore(strokes, par)

                    strokes = 0

            # COLLISION LOOP, VERY COMPLEX,
            # - All angles are in radians
            # - Physics are in general real and correct

            for i in objects:  # for every object in the level
                if i[4] == 'coin':  # If the ball hits a coin
                    if len(i) > 5 and i[5]:  # Check if coin exists and is visible
                        # Larger hitbox for easier collection (coin is 32x32)
                        coin_x, coin_y = i[0], i[1]
                        coin_w, coin_h = i[2], i[3]
                        ball_x, ball_y = ballCords[0], ballCords[1]
                        
                        # Expanded collision area for easier pickup
                        if (ball_x > coin_x - 10 and ball_x < coin_x + coin_w + 10 and 
                            ball_y > coin_y - 10 and ball_y < coin_y + coin_h + 10):
                            if SOUND:
                                puttSound.play()  # Use putt sound for coin collection
                            i[5] = False  # Directly disable the coin
                            # courses.coinHit(level - 1) - Removed to fix bug where all coins disappear
                            coins += 1
                            # ETAPA 2 - Sparkle effect on coin collect
                            particle_system.emit_sparkle(coin_x + 16, coin_y + 16)

                if i[4] == 'laser':  # if the ball hits the laser hazard
                    if ballCords[0] > i[0] and ballCords[0] < i[0] + i[2] and ballCords[1] > i[1] and ballCords[1] < i[1] + i[3]:
                        ballCords = shootPos
                        hazard = True
                        subtract = 0
                        ballStationary = ballCords
                        time = 0
                        pos = pygame.mouse.get_pos()
                        angle = findAngle(pos)
                        line = (round(ballStationary[0] + (math.cos(angle) * 50)),
                                round(ballStationary[1] - (math.sin(angle) * 50)))
                        power = 1
                        powerAngle = math.pi
                        shoot = False
                        strokes += 1

                        # Display message with shadow for readability
                        hazard_font = pygame.font.SysFont('Arial', 36, bold=True)
                        msg = 'Laser Hazard +1'
                        shadow = hazard_font.render(msg, True, (0, 0, 0))
                        label = hazard_font.render(msg, True, (255, 255, 255))
                        x = winwidth / 2 - label.get_width() / 2
                        y = winheight / 2 - label.get_height() / 2
                        win.blit(shadow, (x + 2, y + 2))
                        win.blit(shadow, (x - 2, y + 2))
                        win.blit(shadow, (x + 2, y - 2))
                        win.blit(shadow, (x - 2, y - 2))
                        win.blit(label, (x, y))
                        pygame.display.update()
                        pygame.time.delay(1000)
                        ballColor = (255,255,255)
                        stickyPower = False
                        superPower = False
                        mullagain = False
                        break

                elif i[4] == 'water':
                    if ballCords[1] > i[1] - 6 and ballCords[1] < i[1] + 8 and ballCords[0] < i[0] + i[2] and ballCords[0] > i[0] + 2:
                        # ETAPA 2 - Water splash particles
                        particle_system.emit_splash(ballCords[0], ballCords[1])
                        ball_trail.clear()
                        
                        ballCords = shootPos
                        subtract = 0
                        hazard = True
                        ballStationary = ballCords
                        time = 0
                        pos = pygame.mouse.get_pos()
                        angle = findAngle(pos)
                        line = (round(ballStationary[0] + (math.cos(angle) * 50)), round(ballStationary[1] - (math.sin(angle) * 50)))
                        power = 1
                        powerAngle = math.pi
                        shoot = False
                        strokes += 1

                        # Display message with shadow for readability
                        hazard_font = pygame.font.SysFont('Arial', 36, bold=True)
                        msg = 'Water Hazard +1'
                        shadow = hazard_font.render(msg, True, (0, 0, 0))
                        label = hazard_font.render(msg, True, (255, 255, 255))
                        if SOUND:
                            splash.play()
                        x = winwidth / 2 - label.get_width() / 2
                        y = winheight / 2 - label.get_height() / 2
                        win.blit(shadow, (x + 2, y + 2))
                        win.blit(shadow, (x - 2, y + 2))
                        win.blit(shadow, (x + 2, y - 2))
                        win.blit(shadow, (x - 2, y - 2))
                        win.blit(label, (x, y))
                        pygame.display.update()
                        pygame.time.delay(1500)
                        ballColor = (255,255,255)
                        stickyPower = False
                        mullagain = False
                        superPower = False
                        break

                elif i[4] != 'flag' and i[4] != 'coin':
                    if ballCords[1] > i[1] - 2 and ballCords[1] < i[1] + 7 and ballCords[0] < i[0] + i[2] and ballCords[0] > i[0]:
                        hitting = False
                        power = physics.findPower(power, angle, time)
                        if angle > math.pi * (1/2) and angle < math.pi:
                            x = physics.findAngle(power, angle)
                            angle = math.pi - x
                        elif angle < math.pi / 2:
                            angle = physics.findAngle(power, angle)
                        elif angle > math.pi and angle < math.pi * (3/2):
                            x = physics.findAngle(power, angle)
                            angle = math.pi - x
                        else:
                            x = physics.findAngle(power, angle)
                            angle = x

                        power = power * 0.5
                        if time > 0.15:
                            time = 0
                        subtract = 0
                        while True:
                            subtract += 1
                            if ballCords[1] - subtract < i[1]:
                                ballCords = (ballCords[0], ballCords[1] - subtract)
                                break
                        ballStationary = ballCords
                        
                        # ETAPA 3 - Visual Feedback
                        ball_physics.on_collision('vertical')
                        particle_system.emit_dust(ballCords[0], ballCords[1], count=5)
                        if power > 5:
                            camera_shake.shake(intensity=min(5, int(power/3)))

                        if i[4] == 'sand':
                            if SOUND and power > 5:  # Only play sound if ball has significant power
                                wrong.play()  # Use wrong sound for sand collision
                            subtract = 0
                            while True:
                                subtract += 1
                                if ballCords[1] - subtract < i[1] - 4:
                                    ballCords = (ballCords[0], ballCords[1] - subtract)
                                    power = 0
                                    break

                        if i[4] == 'sticky' or stickyPower:
                            subtract = 0
                            while True:
                                subtract += 1
                                if ballCords[1] - subtract < i[1] - 4:
                                    ballCords = (ballCords[0], ballCords[1] - subtract)
                                    power = 0
                                    break


                            ballStationary = ballCords
                            shoot = False
                            time = 0
                            pos = pygame.mouse.get_pos()
                            angle = findAngle(pos)
                            line = (round(ballStationary[0] + (math.cos(angle) * 50)),
                                    round(ballStationary[1] - (math.sin(angle) * 50)))
                            power = 1
                            powerAngle = math.pi


                    elif ballCords[1] < i[1] + i[3] and ballCords[1] > i[1] and ballCords[0] > i[0] - 2 and ballCords[0] < i[0] + 10:
                        hitting = False
                        power = physics.findPower(power, angle, time)
                        if angle < math.pi / 2:
                            if not(time > maxT):
                                x = physics.findAngle(power, angle)
                                angle = math.pi - x
                            else:
                                x = physics.findAngle(power, angle)
                                angle = math.pi + x
                        else:
                            x = physics.findAngle(power, angle)
                            angle = math.pi + x


                        power = power * 0.5

                        if time > 0.15:
                            time = 0
                        subtract = 0

                        while True:
                            subtract += 1
                            if ballCords[0] - subtract < i[0] - 3:
                                ballCords = (ballCords[0] - subtract, ballCords[1])
                                break
                        ballStationary = ballCords
                        
                        # ETAPA 3 - Visual Feedback
                        ball_physics.on_collision('horizontal')
                        particle_system.emit_dust(ballCords[0], ballCords[1], count=5)
                        if power > 5:
                            camera_shake.shake(intensity=min(5, int(power/3)))

                        if i[4] == 'sticky' or stickyPower:
                            subtract = 0
                            while True:
                                subtract += 1
                                if ballCords[0] - subtract < i[0] - 3:
                                    ballCords = (ballCords[0] - subtract, ballCords[1])
                                    power = 0
                                    break

                    elif ballCords[1] < i[1] + i[3] and ballCords[1] > i[1] and ballCords[0] > i[0] + i[2] - 16 and ballCords[0] < i[0] + i[2]:
                        hitting = False

                        power = physics.findPower(power, angle, time)
                        if angle < math.pi:
                            if not (time > maxT):
                                angle = physics.findAngle(power, angle)
                            else:
                                x = physics.findAngle(power, angle)
                                angle = math.pi * 2 - x
                        else:
                            x = physics.findAngle(power, angle)
                            angle = math.pi * 2 - x

                        power = power * 0.5

                        if time > 0.15:
                            time = 0
                        subtract = 0

                        while True:
                            subtract += 1
                            if ballCords[0] + subtract > i[0] + i[2] + 4:
                                ballCords = (ballCords[0] + subtract, ballCords[1])
                                break
                        ballStationary = ballCords
                        
                        # ETAPA 3 - Visual Feedback
                        ball_physics.on_collision('horizontal')
                        particle_system.emit_dust(ballCords[0], ballCords[1], count=5)
                        if power > 5:
                            camera_shake.shake(intensity=min(5, int(power/3)))

                        if i[4] == 'sticky' or stickyPower:
                            subtract = 0
                            while True:
                                subtract += 1
                                if ballCords[0] + subtract > i[0] + i[2] + 4:
                                    ballCords = (ballCords[0] + subtract, ballCords[1])
                                    power = 0
                                    break



                    elif ballCords[1] > i[1] + i[3]and ballCords[0] + 2 > i[0] and ballCords[1] < i[1] + i[3] + 10 and ballCords[0] < i[0] + i[2] + 2:
                        power = physics.findPower(power, angle, time)
                        if not(hitting):
                            hitting = True
                            if angle > math.pi / 2:
                                x = physics.findAngle(power, angle)
                                angle = math.pi + x
                            else:
                                x = physics.findAngle(power, angle)
                                angle = 2 * math.pi - x

                        power = power * 0.5
                        if time > 0.04:
                            time = 0

                        subtract = 0
                        while True:
                            subtract += 1
                            if ballCords[1] + subtract > i[1] + i[3] + 8:
                                ballCords = (ballCords[0], ballCords[1] + subtract)
                                break


                        if i[4] == 'sticky' or stickyPower:
                            subtract = 0
                            while True:
                                subtract += 1
                                if ballCords[0] + subtract > i[1] + i[3] + 4:
                                    ballCords = (ballCords[0], ballCords[1] + subtract)
                                    power = 0
                                    break
                        ballStationary = ballCords

                    if power < 2.5:
                        subtract = 0
                        pygame.display.update()
                        ballStationary = ballCords
                        shoot = False
                        time = 0
                        pos = pygame.mouse.get_pos()
                        angle = findAngle(pos)
                        line = (round(ballStationary[0] + (math.cos(angle) * 50)), round(ballStationary[1] - (math.sin(angle) * 50)))
                        power = 1
                        powerAngle = math.pi
                        ballColor = (255,255,255)
                        stickyPower = False
                        mullagain = False
                        superPower = False
                        break

        else:
            if SOUND:
                inHole.play()
                # Add a small delay to make the sound more impactful
                pygame.time.delay(200)
            var = True
            while var:
                pygame.time.delay(20)
                redrawWindow(ballStationary, None, True)
                ballStationary = (ballStationary[0], ballStationary[1] + 1)
                if ballStationary[0] > hole[0]:
                    ballStationary = (ballStationary[0] - 1, ballStationary[1])
                else:
                    ballStationary = (ballStationary[0] + 1, ballStationary[1])

                if ballStationary[1] > hole[1] + 5:
                    shoot = False
                    var = False

            fade()
            if strokes == 1:
                holeInOne()
            else:
                displayScore(strokes, par)

            strokes = 0

    if onGreen():
        if ballStationary[0] > flagx:
            angle = math.pi
            line = (ballStationary[0] - 30, ballStationary[1])
        else:
            angle = 0
            line = (ballStationary[0] + 30, ballStationary[1])


pygame.quit()
