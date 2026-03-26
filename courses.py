winheight = 600
winwidth = 1080

from level_generator import LevelGenerator

# Global state for Seed Mode
current_seed = None
generated_course_data = []

def set_seed(seed):
    global current_seed, generated_course_data
    if seed:
        current_seed = seed
        gen = LevelGenerator(winwidth, winheight)
        generated_course_data = gen.generate_course(seed)
        print(f"[COURSES] Seed Mode Active: {seed}")
    else:
        current_seed = None
        generated_course_data = []
        print("[COURSES] Seed Mode Disabled")

lvl1 = [[0, -8, 1200, 24, 'floor'], [100, 100, 32, 32, 'coin', True],[952, winheight - 8, 128, 8, 'green'], [0, winheight - 8, winwidth - 128, 100, 'floor'], [-8, 0, 16, winheight + 100, 'wall'], [280, 350, 64, 64, 'sand'], [520, 350, 256, 16, 'floor'], [0, 152, 128, 16, 'floor'], [344, 152, 16, 448, 'wall'], [winwidth - 8, 0, 16, winheight + 100, 'wall'], [936, 320, 16, 320, 'wall'], [880, winheight - 8, 64, 8, 'floor'], [360, 560, 576, 32, 'water'],[1006, winheight - 68, 64, 64, 'flag'], [5, (180, winheight - 12)]]
lvl2 = [[0, -8, 1200, 24, 'floor'], [968, winheight - 8, 300, 16, 'floor'], [-8, 0, 16, winheight + 100, 'wall'], [-40, winheight - 8, 900, 16, 'floor'], [128, winheight - 128, 16, 128, 'wall'], [144, winheight - 38, 704, 32, 'water'], [420, 350, 128, 64, 'sand'], [470, 300, 32, 32, 'coin', True], [winwidth - 8, 0, 16, winheight + 100, 'wall'], [848, 300, 16, 500, 'wall'], [864, 364, 128, 16, 'floor'], [992, 300, 16, 192, 'wall'], [864, 332, 128, 32, 'water'], [860, winheight - 8, 128, 8, 'green'], [900, winheight - 68, 64, 64, 'flag'],[4, (50, winheight - 12)]]
lvl3 = [[0, 100, 128, 16, 'floor'], [500, winheight - 8, 192, 8, 'green'], [600, winheight-68, 64, 64, 'flag'], [590, 400, 32, 32, 'coin', True], [-8, -400, 16, winheight + 500, 'wall'],[484, winheight - 128, 16, 128, 'wall'], [692, winheight - 128, 16, 128, 'wall'], [708, winheight - 38, 128, 32, 'water'], [winwidth - 8, 0, 16, winheight + 100, 'wall'], [356, winheight - 38, 128, 32, 'water'], [-12, winheight-8, 512, 16, 'floor'], [708, winheight - 8, 600, 32, 'floor'], [836, winheight-64, 500, 64, 'sand'], [-28, winheight-64, 400, 64, 'sand'], [3, (50, 95)]]
lvl4 = [[0, winheight - 8, winwidth + 64, 100, 'floor'], [550, 300, 32, 32, 'coin', True], [0, winheight - 40, 1200, 32, 'water'], [50, 450, 128, 16, 'floor'], [-8, 0, 16, winheight + 100, 'wall'], [winwidth - 128, 450, 128, 8, "green"], [winwidth - 128, 458, 128, 16, "floor"], [winwidth-80, 388, 64, 64, 'flag'], [winwidth - 8, 0, 16, winheight + 100, 'wall'], [3, (120, 446)]]
lvl5 = [[800, 400, 32, 32, 'coin', True], [0, winheight - 8, winwidth + 64, 100, 'floor'], [-8, 0, 16, winheight + 100, 'wall'],  [winwidth - 8, 0, 16, winheight + 100, 'wall'], [0, 400, 128, 16, 'floor'], [128, 118, 16, 600, 'wall'], [144, 152, 128, 32, 'water'], [144, 184, 192, 16, 'floor'], [256, 120, 64, 64, 'sand'], [winwidth-200, 164, 192, 8, 'green'], [winwidth-216, 164, 16, 64, 'wall'], [752, 528, 320, 64, 'sand'], [736, 0, 16, 270, 'wall'], [winwidth-200, 172, 192, 16, 'floor'], [0, -8, 1200, 16, 'floor'], [8, 200, 64, 64, 'sand'], [winwidth-108, 104, 64, 64, 'flag'], [5, (50, 395)]]
lvl6 = [[200, 136, 1000, 32, 'water'], [475, 284, 64, 16, 'floor'],[523, 300, 16, 500, 'wall'],[500, 300, 15, 500, 'laser'], [490, 250, 32, 32, 'coin', True], [0, 120, 64, 64 ,'sand'], [0, 450, 200, 16, 'floor'], [184, 120, 16, 64, 'wall'],[0, winheight - 8, winwidth + 64, 100, 'floor'], [-8, 0, 16, winheight + 100, 'wall'], [814, 124, 400, 16, 'floor'],[winwidth - 8, 0, 16, winheight + 100, 'wall'], [winwidth-13, 340, 16, 128, 'sticky'], [winwidth-250, 400, 128, 16, 'green'], [winwidth-250, 408, 128, 16, 'floor'], [winwidth -200, 338, 64, 64, 'flag'], [200, 168, 1000, 16, 'floor'],[winwidth-266, 168, 16, 260, 'wall'], [winwidth-266, 128, 16, 64, 'wall'], [5, (920, 120)]]
lvl7 = [[0, 560, 1200, 32, 'water'], [0, 300, 128, 16, 'floor'], [0, 490, 192, 16, 'floor'], [128, 450, 192, 16, 'floor'], [344, 268, 16, 192, 'wall'], [360, 380, 192, 64, 'sand'], [0, winheight - 8, winwidth + 64, 100, 'floor'], [0, -8, 1200, 16, 'floor'], [-8, 0, 16, 700, 'wall'], [winwidth - 8, 0, 16, 700, 'wall'], [700, 150, 192, 16, 'floor'], [780, 110, 32, 32, 'coin', True], [winwidth-200, 500, 128, 16, 'green'], [winwidth-200, 508, 128, 16, 'floor'], [winwidth-13, 300, 16, 192, 'sticky'], [winwidth - 140, 438, 64, 64, 'flag'],(4, (50, 485))]
lvl8 = [[400, 560, 800, 32, 'water'], [0, winheight - 8, winwidth + 64, 100, 'floor'], [-8, 0, 16, winheight + 100, 'wall'],  [winwidth - 8, 0, 16, winheight + 100, 'wall'], [0,-8, 1200, 16, 'floor'], [winwidth - 134, 200, 128, 8, 'green'], [winwidth - 134, 208, 128, 16, 'floor'], [winwidth - 326, 200, 192, 32, 'water'], [winwidth - 340, 176, 16, 64, 'wall'], [winwidth - 326, -32, 16, 128, 'wall'], [400, 200, 16, 550, 'wall'], [150, 300, 64, 64, 'sand'], [540, 190, 128, 64, 'sand'], [574, 150, 32, 32, 'coin', True], [370, 184, 64, 16, 'floor'],[390, 200, 16, 550, 'laser'], [0, 500, 64, 16, 'floor'],[272, 440, 128, 16, 'floor'], [winwidth - 326, 224, 400, 16, 'floor'],[winwidth - 68, 140, 64, 64, 'flag'], [6, (200, 588)]]
lvl9 = [[0, winheight-36, 1200, 32, 'water'], [-8,0,16, 700, 'wall'], [winwidth-8, 0, 16, 700, 'wall'], [0, -8, 1200, 16, 'floor'], [0,winheight-8,1200, 16, 'floor'], [0, 500, 128, 16, 'floor'], [350, 375, 128, 64, 'sand'],[700, 250, 64, 64, 'sand'], [winwidth -198, 150, 200, 8, 'green'], [winwidth -198, 158, 200, 8, 'floor'],[550, 230, 32, 32, 'coin', True],[winwidth-80, 90, 64, 64, 'flag'], [5, (64, 496)]]

# Level 10 - Vertical Maze: navigate up through a series of ledges
lvl10 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Maze ledges alternating left/right
    [0, 480, 700, 16, 'floor'],
    [380, 380, 700, 16, 'floor'],
    [0, 280, 700, 16, 'floor'],
    [380, 180, 700, 16, 'floor'],
    # Hazards between ledges
    [0, 496, 700, 32, 'water'],
    [380, 296, 64, 64, 'sand'],
    # Coin on third ledge
    [300, 248, 32, 32, 'coin', True],
    # Green and flag at top right
    [winwidth - 200, 128, 192, 8, 'green'],
    [winwidth - 200, 136, 192, 16, 'floor'],
    [winwidth - 136, 64, 64, 64, 'flag'],
    [4, (50, winheight - 12)],
]

# Level 11 - Water Bridge: narrow walkways over a giant water pit
lvl11 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Massive water below
    [0, 400, winwidth, 200, 'water'],
    # Narrow bridges over the water
    [0, 396, 128, 16, 'floor'],
    [200, 340, 128, 16, 'floor'],
    [400, 396, 128, 16, 'floor'],
    [600, 300, 128, 16, 'floor'],
    [800, 340, 128, 16, 'floor'],
    # Coin on middle bridge
    [616, 268, 32, 32, 'coin', True],
    # Sand near flag
    [900, 396, 64, 64, 'sand'],
    # Green and flag
    [winwidth - 200, 260, 192, 8, 'green'],
    [winwidth - 200, 268, 192, 16, 'floor'],
    [winwidth - 136, 196, 64, 64, 'flag'],
    [4, (50, 388)],
]

# Level 12 - Laser Corridor: multiple laser beams to navigate around
lvl12 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Main floor corridor
    [0, winheight - 80, winwidth, 16, 'floor'],
    # Laser walls with gaps
    [200, winheight - 320, 16, 256, 'laser'],
    [200, winheight - 80, 16, 80, 'wall'],
    [430, winheight - 80, 16, 200, 'wall'],
    [430, winheight - 380, 16, 200, 'laser'],
    [660, winheight - 300, 16, 236, 'laser'],
    [660, winheight - 80, 16, 80, 'wall'],
    # Coin in middle safe zone
    [530, winheight - 120, 32, 32, 'coin', True],
    # Sand traps
    [300, winheight - 96, 128, 32, 'sand'],
    # Green and flag on elevated platform
    [winwidth - 220, 200, 192, 8, 'green'],
    [winwidth - 220, 208, 192, 16, 'floor'],
    [winwidth - 220, 200, 16, 400, 'wall'],
    [winwidth - 156, 136, 64, 64, 'flag'],
    [5, (50, winheight - 84)],
]

# Level 13 - Sand Pit Gauntlet: deep sand everywhere, precision shots needed
lvl13 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Sand covering the ground
    [0, winheight - 80, 240, 80, 'sand'],
    [256, winheight - 80, 240, 80, 'sand'],
    [512, winheight - 80, 240, 80, 'sand'],
    [768, winheight - 80, 240, 80, 'sand'],
    # Narrow floor strips to navigate
    [240, winheight - 80, 16, 80, 'floor'],
    [496, winheight - 80, 16, 80, 'floor'],
    [752, winheight - 80, 16, 80, 'floor'],
    # Elevated platforms with sand
    [128, 350, 256, 16, 'floor'],
    [128, 334, 256, 32, 'sand'],
    [500, 300, 256, 16, 'floor'],
    [500, 284, 256, 32, 'sand'],
    # Coin on elevated sand platform
    [596, 252, 32, 32, 'coin', True],
    # Ramp walls
    [384, 350, 16, 250, 'wall'],
    [756, 300, 16, 300, 'wall'],
    # Green and flag
    [winwidth - 200, 200, 192, 8, 'green'],
    [winwidth - 200, 208, 192, 16, 'floor'],
    [winwidth - 136, 136, 64, 64, 'flag'],
    [5, (50, winheight - 12)],
]

# Level 14 - Multi-Platform Jumper: elevated stepping-stone platforms
lvl14 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Water pit below
    [0, winheight - 40, winwidth, 40, 'water'],
    # Stepping stone platforms at varying heights
    [0, 500, 100, 16, 'floor'],
    [180, 440, 100, 16, 'floor'],
    [360, 380, 100, 16, 'floor'],
    [540, 320, 100, 16, 'floor'],
    [720, 260, 100, 16, 'floor'],
    [900, 200, 100, 16, 'floor'],
    # Hazards on some platforms
    [180, 408, 64, 32, 'sand'],
    [540, 288, 64, 32, 'sand'],
    # Coin on high platform
    [756, 228, 32, 32, 'coin', True],
    # Wall obstacles
    [280, 200, 16, 300, 'wall'],
    [640, 150, 16, 250, 'wall'],
    # Green and flag at the top
    [winwidth - 180, 148, 164, 8, 'green'],
    [winwidth - 180, 156, 164, 16, 'floor'],
    [winwidth - 116, 84, 64, 64, 'flag'],
    [5, (40, 492)],
]

# Level 15 - Sticky Walls Puzzle: use sticky walls to slow and redirect ball
lvl15 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Sticky wall sections
    [300, 100, 16, 300, 'sticky'],
    [600, 200, 16, 300, 'sticky'],
    [800, 100, 16, 250, 'sticky'],
    # Floor platforms
    [0, winheight - 80, 300, 16, 'floor'],
    [316, 400, 284, 16, 'floor'],
    [616, 500, 184, 16, 'floor'],
    [816, 350, 200, 16, 'floor'],
    # Water hazard
    [300, winheight - 40, 316, 40, 'water'],
    [616, winheight - 40, 200, 40, 'water'],
    # Sand
    [820, 334, 128, 32, 'sand'],
    # Coin
    [660, 468, 32, 32, 'coin', True],
    # Green and flag
    [winwidth - 200, 200, 192, 8, 'green'],
    [winwidth - 200, 208, 192, 16, 'floor'],
    [winwidth - 136, 136, 64, 64, 'flag'],
    [5, (50, winheight - 84)],
]

# Level 16 - Long Distance Shot: wide open with long diagonal path and moving platform
lvl16 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Long water hazard spanning most of screen
    [128, winheight - 60, 800, 60, 'water'],
    # Start platform
    [0, winheight - 80, 140, 16, 'floor'],
    # Moving platform in middle
    [400, 350, 150, 16, 'moving', {'speed': 2, 'axis': 'x', 'range': 200}],
    # Landing platforms
    [640, 250, 128, 16, 'floor'],
    [820, 180, 128, 16, 'floor'],
    # Coin on middle platform
    [670, 218, 32, 32, 'coin', True],
    # Sand near flag
    [860, 164, 80, 32, 'sand'],
    # Second coin on end platform
    [840, 148, 32, 32, 'coin', True],
    # Green and flag
    [winwidth - 200, 120, 192, 8, 'green'],
    [winwidth - 200, 128, 192, 16, 'floor'],
    [winwidth - 136, 56, 64, 64, 'flag'],
    [5, (50, winheight - 84)],
]

# Level 17 - Obstacle Course: packed with everything
lvl17 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Main elevated corridor with gaps
    [0, 400, 200, 16, 'floor'],
    [260, 340, 200, 16, 'floor'],
    [520, 280, 200, 16, 'floor'],
    [780, 220, 200, 16, 'floor'],
    # Walls to force navigation
    [200, 200, 16, 216, 'wall'],
    [460, 140, 16, 216, 'wall'],
    [720, 80, 16, 216, 'wall'],
    # Hazards on platforms
    [0, 368, 128, 32, 'sand'],
    [270, 308, 64, 32, 'water'],
    [530, 248, 64, 32, 'sand'],
    # Laser blocking path
    [460, 340, 16, 240, 'laser'],
    # Sticky section
    [720, 80, 60, 16, 'sticky'],
    # Coins
    [300, 308, 32, 32, 'coin', True],
    [560, 248, 32, 32, 'coin', True],
    # Green and flag
    [winwidth - 200, 140, 192, 8, 'green'],
    [winwidth - 200, 148, 192, 16, 'floor'],
    [winwidth - 136, 76, 64, 64, 'flag'],
    [6, (50, 388)],
]

# Level 18 - Final Challenge: all hazard types, moving platform, tight corridors
lvl18 = [
    [-8, 0, 16, winheight + 100, 'wall'],
    [winwidth - 8, 0, 16, winheight + 100, 'wall'],
    [0, -8, 1200, 16, 'floor'],
    [0, winheight - 8, winwidth + 64, 100, 'floor'],
    # Base with gaps replaced by water
    [128, winheight - 60, 300, 60, 'water'],
    [500, winheight - 60, 300, 60, 'water'],
    [0, winheight - 80, 140, 16, 'floor'],
    [440, winheight - 80, 60, 16, 'floor'],
    [808, winheight - 80, 140, 16, 'floor'],
    # Mid-section: laser corridor
    [300, 300, 16, 300, 'laser'],
    [480, 200, 16, 400, 'laser'],
    # Sticky walls
    [660, 150, 16, 250, 'sticky'],
    # Sand traps on platforms
    [0, 400, 128, 16, 'floor'],
    [0, 368, 128, 32, 'sand'],
    [180, 320, 120, 16, 'floor'],
    [180, 288, 60, 32, 'sand'],
    [500, 280, 120, 16, 'floor'],
    [676, 280, 120, 16, 'floor'],
    # Moving platform bridging dangerous gap
    [316, 260, 150, 16, 'moving', {'speed': 3, 'axis': 'x', 'range': 150}],
    # Wall maze
    [840, 100, 16, 280, 'wall'],
    [840, 380, 16, 280, 'wall'],
    # Coins
    [200, 288, 32, 32, 'coin', True],
    [520, 248, 32, 32, 'coin', True],
    # Green and flag
    [winwidth - 200, 100, 192, 8, 'green'],
    [winwidth - 200, 108, 192, 16, 'floor'],
    [winwidth - 136, 36, 64, 64, 'flag'],
    [6, (50, winheight - 84)],
]

course1 = [lvl1, lvl2, lvl3, lvl4, lvl5, lvl6, lvl7, lvl8, lvl9, lvl10, lvl11, lvl12, lvl13, lvl14, lvl15, lvl16, lvl17, lvl18]



def getLvl(n=1):
    if current_seed and generated_course_data:
        if n <= len(generated_course_data):
            return generated_course_data[n - 1][:-1]
        return generated_course_data[-1][:-1] # Fallback
    return course1[n - 1][:-1]


def getPar(course=1):
    if current_seed and generated_course_data:
        count = []
        for x in generated_course_data:
            l = x[-1]
            count.append(l[0])
        return count

    if course == 1:
        count = []
        for x in range(len(course1)):
            l = course1[x][-1]
            par = l[0]
            count.append(par)
    return count


def getStart(lvl, course=1):
    if current_seed and generated_course_data:
        if lvl <= len(generated_course_data):
            pos = generated_course_data[lvl - 1][-1]
            nPos = pos[-1]
            return nPos
            
    if course == 1:
        pos = course1[lvl - 1][-1]
        nPos = pos[-1]
    return nPos


def coinHit(lvl):
    if current_seed and generated_course_data:
        target = generated_course_data
    else:
        target = course1

    if lvl < len(target):
        for x in target[lvl]:
            if len(x) > 4:
                if x[4] == 'coin':
                    x[5] = False

