import pygame
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import profiles
import ui_style
from ui_style import Colors, Fonts, draw_rounded_rect, draw_shadow, create_gradient_surface, create_vignette

pygame.init()

# Initialize UI Style System
ui_style.init_ui()

win = pygame.display.set_mode((1080, 600))
title = pygame.image.load(os.path.join('img', 'title.png'))
back = pygame.image.load(os.path.join('img', 'back.png'))
course = pygame.image.load(os.path.join('img', 'course1.png'))
course1 = pygame.transform.scale(course, (200, 200))

# Premium background layers
gradient_bg = create_gradient_surface(1080, 600, Colors.SKY_TOP, Colors.SKY_BOTTOM)
vignette_overlay = create_vignette(1080, 600, intensity=50, radius_factor=0.65)

# Modern fonts
font = Fonts.UI_MEDIUM
font_large = Fonts.TITLE_SMALL
font_small = Fonts.UI_SMALL

buttons = [[440, 240, 200, 200, 'Grassy Land']]  # [x, y, width, height, name]
shopButton = [15, 525, 200, 60]
seedButton = [15, 60, 200, 50]
logoutButton = [900, 20, 160, 40] # Top Right
ballObjects = []
surfaces = []

class ball():
    def __init__(self, color, locked, org):
        self.color = color
        self.locked = locked
        self.original = org
        self.price = 10
        self.equipped = False
        self.font = Fonts.UI_SMALL

    def unlock(self):
        profiles.unlock_ball(self.original)
        self.locked = False

    def getLocked(self):
        return self.locked

    def equip(self):
        profiles.equip_ball(self.original)
        self.equipped = True

    def getEquip(self):
        return self.equipped
    
    def getSurf(self, hover=False):
        surf = pygame.Surface((160, 140), pygame.SRCALPHA, 32)
        surf = surf.convert_alpha()
        
        # Glass card background
        draw_rounded_rect(surf, (255, 255, 255, 50), (5, 5, 150, 130), 16)
        
        # Ball with shadow and highlight
        # Shadow
        shadow_surf = pygame.Surface((50, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 30), (0, 0, 50, 15))
        surf.blit(shadow_surf, (55, 45))
        
        # Ball outer ring
        pygame.draw.circle(surf, (0, 0, 0), (80, 30), 24)
        pygame.draw.circle(surf, self.color, (80, 30), 22)
        
        # Ball highlight
        highlight = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(highlight, (255, 255, 255, 100), (15, 15), 8)
        surf.blit(highlight, (62, 12))
        
        if self.locked:
            # Lock icon (text instead of emoji)
            lock_text = self.font.render('[X]', True, Colors.TEXT_SECONDARY)
            surf.blit(lock_text, (68, 55))
            
            # Price label
            price_text = self.font.render('10 coins', True, Colors.TEXT_PRIMARY)
            surf.blit(price_text, (80 - price_text.get_width() // 2, 78))
            
            # Buy button
            btn_color = Colors.ACCENT_ORANGE if hover else Colors.ACCENT_BLUE
            draw_rounded_rect(surf, btn_color, (30, 105, 100, 26), 13)
            buy_text = Fonts.UI_TINY.render('BUY', True, (255, 255, 255))
            surf.blit(buy_text, (80 - buy_text.get_width() // 2, 109))
        else:
            # Checkmark for unlocked (text instead of emoji)
            check_text = self.font.render('[OK]', True, Colors.ACCENT_GREEN)
            surf.blit(check_text, (65, 55))
            
            if self.equipped:
                # Equipped badge
                draw_rounded_rect(surf, Colors.ACCENT_GREEN, (25, 105, 110, 26), 13)
                equip_text = Fonts.UI_TINY.render('EQUIPPED', True, (255, 255, 255))
                surf.blit(equip_text, (80 - equip_text.get_width() // 2, 109))
            else:
                # Equip button
                btn_color = (100, 116, 139) if not hover else Colors.ACCENT_BLUE
                draw_rounded_rect(surf, btn_color, (35, 105, 90, 26), 13)
                equip_text = Fonts.UI_TINY.render('EQUIP', True, (255, 255, 255))
                surf.blit(equip_text, (80 - equip_text.get_width() // 2, 109))

        return surf


def getBest():
    return profiles.get_best_score()

def getCoins():
    return profiles.get_coins()

def change_user():
     profiles.logout()
     login()

    
def drawShop(pos=None, click=False):
    global ballObjects
    pygame.time.delay(20)

    if pos != None:
        c = 0
        for i in surfaces:
            if pos[0] > i[0] and pos[0] < i[0] + i[2]:
                if pos[1] > i[1] + 80 and pos[1] < i[1] + i[3]:
                    if click == True:
                        root = tk.Tk()
                        root.attributes("-topmost", True)
                        root.withdraw()
                        if ballObjects[c].locked == True:
                            if messagebox.askyesno('Confirm Purchase?', 'Are you sure you would like to purchase this new ball for 10 coins?'):
                                if int(getCoins()) >= 10:
                                    ballObjects[c].unlock()
                                    ballObjects[c].unlock()
                                    profiles.add_coins(-10) # Deduct coins
                                    # oldCoins = int(getCoins())
                                else:
                                    messagebox.showerror('Not enough coins!', 'You do not have enough coins to purchase this item!')
                
                                try:
                                    root.destroy()
                                    break
                                except:
                                    break
                            else:
                                break
                        else:
                            for balls in ballObjects:
                                balls.equipped = False
                                
                            ballObjects[c].equip()
                            ballObjects[c].equipped = True
            c = c + 1
    
    surf = pygame.Surface((1080, 600))
    # Premium background
    surf.blit(gradient_bg, (0, 0))
    back_copy = back.copy()
    back_copy.set_alpha(160)
    surf.blit(back_copy, (0, 0))
    surf.blit(vignette_overlay, (0, 0))
    
    # Title
    shop_title = Fonts.UI_LARGE.render('BALL SHOP', True, Colors.TEXT_PRIMARY)
    surf.blit(shop_title, (540 - shop_title.get_width() // 2, 15))
    
    # Back button (pill style)
    draw_rounded_rect(surf, (100, 116, 139), (15, 555, 100, 35), 17)
    backButton = font_small.render('← Back', True, (255, 255, 255))
    surf.blit(backButton, (40, 562))
    
    # Coins display card
    coins_val = getCoins()
    draw_shadow(surf, (900, 10, 160, 40), 12, (2, 2), 2)
    draw_rounded_rect(surf, (255, 255, 255, 50), (900, 10, 160, 40), 12)
    coin_label = Fonts.UI_TINY.render('COINS', True, Colors.ACCENT_GOLD)
    surf.blit(coin_label, (915, 14))
    coin_text = Fonts.HUD_MEDIUM.render(str(coins_val), True, Colors.TEXT_PRIMARY)
    surf.blit(coin_text, (970, 14))
    count = 0
    c = 0
    xVal = 0
    count = 0
    c = 0
    xVal = 0
    
    # Use profiles to get ball list
    ball_data = profiles.get_balls()
    ballObjects = [] # Rebuild locally
    
    for b_info in ball_data:
        color_str = b_info["color"]
        is_locked = b_info["locked"]
        is_equipped = b_info["equipped"]
        
        # Convert "r,g,b" to tuple
        parts = color_str.split(',')
        color_tuple = tuple(map(int, parts))
        
        # Create ball object
        obj = ball(color_tuple, is_locked, color_str)
        if is_equipped:
            obj.equipped = True
            
        if len(ballObjects) <= 15:
             # Just safety cap
             pass
             
        s = obj.getSurf()
        surf.blit(s, ((200 * count) - 150, 50 + (xVal * 160)))
        surfaces.append([(200 * count) - 150, 50 + (xVal * 160), 160, 125])
        ballObjects.append(obj)
        
        count += 1
        if count % 5 == 0:
            xVal = xVal + 1
            count = 0
        c = c + 1


    
    pygame.display.update()
    return surf


def getBallColor():
    global ballObjects
    for balls in ballObjects:
        if balls.equipped == True:
            return balls.color
    return None


def mainScreen(hover=False):
    global shopButton, seedButton
    # Ensure shopButton is correct
    shopButton = [15, 525, 200, 60]
    
    surf = pygame.Surface((1080, 600))
    w = title.get_width()
    h = title.get_height()
    
    # Premium background
    surf.blit(gradient_bg, (0, 0))
    back_copy = back.copy()
    back_copy.set_alpha(160)
    surf.blit(back_copy, (0, 0))
    surf.blit(vignette_overlay, (0, 0))
    
    # Title
    surf.blit(title, ((1080/2 - (w/2)), 50))
    
    # Shop Button (Bottom Left)
    # Using a modern pill button
    shop_btn_color = Colors.ACCENT_PURPLE if hover else Colors.ACCENT_BLUE
    # Coords: (15, 525, 200, 60) matching hitbox
    draw_shadow(surf, (15, 525, 200, 60), 18, (2, 2), 2)
    draw_rounded_rect(surf, shop_btn_color, (15, 525, 200, 60), 18)
    shop_text = font_small.render('SHOP', True, (255, 255, 255))
    text_rect = shop_text.get_rect(center=(15 + 100, 525 + 30))
    surf.blit(shop_text, text_rect)
    # shopButton = [15, 525, 200, 60] # Managed by global/local fix

    # LOGOUT Button (Top Right)
    # Coords: (900, 20, 160, 40) matching hitbox
    logout_btn_color = (220, 38, 38) # Red
    draw_shadow(surf, (900, 20, 160, 40), 12, (2, 2), 2)
    draw_rounded_rect(surf, logout_btn_color, (900, 20, 160, 40), 12)
    logout_text = font_small.render('LOGOUT', True, (255, 255, 255))
    l_rect = logout_text.get_rect(center=(900 + 80, 20 + 20))
    surf.blit(logout_text, l_rect)
    
    # SEED MODE Button (top left)
    # Using a modern pill button
    seed_btn_color = Colors.ACCENT_GREEN
    draw_shadow(surf, (15, 60, 140, 36), 18, (2, 2), 2)
    draw_rounded_rect(surf, seed_btn_color, (15, 60, 140, 36), 18)
    seed_text = font_small.render('SEED MODE', True, (255, 255, 255))
    text_rect = seed_text.get_rect(center=(15 + 70, 60 + 18))
    surf.blit(seed_text, text_rect)
    seedButton = pygame.Rect(15, 60, 140, 36)
    
    # Course Card with glass effect
    i = buttons[0]
    draw_shadow(surf, (i[0] - 15, i[1] - 10, i[2] + 30, i[3] + 90), 20, (4, 4), 3)
    draw_rounded_rect(surf, (255, 255, 255, 40), (i[0] - 15, i[1] - 10, i[2] + 30, i[3] + 90), 20)
    
    surf.blit(course1, (i[0], i[1]))
    
    # Course name
    name_text = font.render(i[4], True, Colors.TEXT_PRIMARY)
    surf.blit(name_text, (i[0] + (i[2] - name_text.get_width()) // 2, i[1] + i[3] + 10))
    
    # Best score
    best_text = font_small.render('Best: ' + str(getBest()), True, Colors.TEXT_SECONDARY)
    surf.blit(best_text, (i[0] + (i[2] - best_text.get_width()) // 2, i[1] + i[3] + 40))
    
    # Coins display card (top left)
    coins_val = getCoins()
    draw_shadow(surf, (15, 10, 130, 36), 12, (2, 2), 2)
    draw_rounded_rect(surf, (255, 255, 255, 50), (15, 10, 130, 36), 12)
    coin_label = Fonts.UI_TINY.render('COINS', True, Colors.ACCENT_GOLD)
    surf.blit(coin_label, (25, 12))
    coin_text = font_small.render(str(coins_val), True, Colors.TEXT_PRIMARY)
    surf.blit(coin_text, (85, 14))
    
    # Play hint at bottom
    hint_text = Fonts.UI_TINY.render('Click the course to play!', True, Colors.TEXT_SECONDARY)
    hint_bg = pygame.Surface((hint_text.get_width() + 20, hint_text.get_height() + 10), pygame.SRCALPHA)
    draw_rounded_rect(hint_bg, (0, 0, 0, 30), (0, 0, hint_text.get_width() + 20, hint_text.get_height() + 10), 8)
    surf.blit(hint_bg, (540 - hint_text.get_width() // 2 - 10, 565))
    surf.blit(hint_text, (540 - hint_text.get_width() // 2, 570))
    
    win.blit(surf, (0,0))
    pygame.display.update()


def mouseOver(larger=False):
    global course1
    if larger:
        buttons[0][0] = 415
        buttons[0][1] = 220
        buttons[0][2] = 250
        buttons[0][3] = 250
        course1 = pygame.transform.scale(course, (250, 250))
    else:
        buttons[0][1] = 240
        buttons[0][0] = 440
        buttons[0][2] = 200
        buttons[0][3] = 200
        course1 = pygame.transform.scale(course, (200, 200))
    mainScreen()


def shopClick(pos):
    # FORCE CORRECT COORDINATES (Bottom Left)
    # [15, 525, 200, 60]
    shop_rect = [15, 525, 200, 60] 
    
    # print(f"[DEBUG] shopClick checking pos={pos} against shop_rect={shop_rect}")
    if pos[0] > shop_rect[0] and pos[0] < shop_rect[0] + shop_rect[2]:
        if pos[1] > shop_rect[1] and pos[1] < shop_rect[1] + shop_rect[3]:
            return True
    return False


def seedClick(pos):
    global seedButton
    i = seedButton
    if i: # Ensure it is initialized
        if pos[0] > i[0] and pos[0] < i[0] + i[2]:
            if pos[1] > i[1] and pos[1] < i[1] + i[3]:
                # Ask for seed
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                seed = simpledialog.askstring("Seed Mode", "Enter a seed for procedural generation:\n(Leave empty to cancel)")
                root.destroy()
                return seed
    return False

def logoutClick(pos):
    # FORCE CORRECT COORDINATES (Top Right)
    # [900, 20, 160, 40]
    logout_rect = [900, 20, 160, 40]
    
    # print(f"[DEBUG] logoutClick checking pos={pos} against logout_rect={logout_rect}")
    if pos[0] > logout_rect[0] and pos[0] < logout_rect[0] + logout_rect[2]:
        if pos[1] > logout_rect[1] and pos[1] < logout_rect[1] + logout_rect[3]:
            return True
    return False


def login():
    """Prompt user for login name"""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    
    # Custom dialog style could be better, but simpledialog is robust
    name = simpledialog.askstring("Welcome to Golf Game", "Enter your Player Name:")
    
    root.destroy()
    
    if not name or name.strip() == "":
        name = "Player"
        
    profiles.login(name)
    return name


def init_shop_defaults():
    """Initialize default balls if scores.txt is missing/empty"""
    defaults = [
        "255,255,255-True", # White (Unlocked)
        "255,0,0-False",
        "0,255,0-False",
        "0,0,255-False",
        "255,255,0-False",
        "255,0,255-False",
        "0,255,255-False",
        "192,192,192-False",
        "128,128,128-False",
        "128,0,0-False",
        "128,128,0-False",
        "0,128,0-False",
        "128,0,128-False",
        "0,128,128-False",
        "0,0,128-False",
        "255,165,0-False"
    ]
    
    existing = ""
    if os.path.exists('scores.txt'):
         try:
             with open('scores.txt', 'r') as f:
                 existing = f.read()
         except:
             pass
             
    if 'True' not in existing and 'False' not in existing:
        try:
            with open('scores.txt', 'a') as f:
                if len(existing) > 0 and not existing.endswith('\n'):
                    f.write('\n')
                for d in defaults:
                    f.write(d + '\n')
        except:
            pass

# Initialize defaults on load
init_shop_defaults()

def click(pos):
    for i in buttons:
        if pos[0] > i[0] and pos[0] < i[0] + i[2]:
            if pos[1] > i[1] and pos[1] < i[1] + i[3]:
                return i[4]
                break
    return None
