
# ========================================
# GAME STATE MANAGEMENT
# ========================================

def run_menu():
    global level, ballColor, coins, ballStationary, shop
    running = True
    hover = False
    
    # Ensure music is playing if enabled
    if Config.get('music_enabled', True):
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        except:
             pass

    while running:
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
                
                # Check Logout
                if startScreen.logoutClick(pos):
                    return 'logout'

                # Check Seed Mode
                seed = startScreen.seedClick(pos)
                if seed:
                    courses.set_seed(seed)
                    level = 1
                    return 'play'
                    
                if startScreen.click(pos) != None:
                    courses.set_seed(None) # Reset to normal
                    return 'play'

                if startScreen.shopClick(pos) == True:
                    # Enter Shop Loop
                    surface = startScreen.drawShop()
                    win.blit(surface, (0,0))
                    pygame.display.update()
                    shop_open = True
                    while shop_open:
                        for event in pygame.event.get():
                            pygame.time.delay(10)
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                if pos[0] > 10 and pos[0] < 100 and pos[1] > 560: # Back button area (approx)
                                    shop_open = False
                                    break
                                # Redraw shop with click
                                surface = startScreen.drawShop(pos, True)
                                win.blit(surface, (0,0))
                                pygame.display.update()
                                # Sync coins if changed
                                coins = profiles.get_coins()

            if event.type == pygame.QUIT:
                return 'quit'
    return 'quit'

def run_game():
    global level, strokes, par, sheet, ballStationary, shootPos, powerUps, ballColor, stickyPower, superPower, mullagain, hazard, shoot, put, coins, power, loopTime, powerLock, powerAngle, neg
    
    # Initialization for Game Loop
    list = courses.getPar(1)
    par = list[level - 1]
    sheet = scoreSheet(list)
    pos = courses.getStart(level, 1)
    ballStationary = pos
    setup(level)

    # Reset Power Ups
    stickyPower = False
    superPower = False
    mullagain = False
    powerUps = 3
    
    # Physics Vars
    time = 0
    power = 0
    angle = 0
    shoot = False
    put = False
    hitting = False
    
    # Initial Draw
    redrawWindow(ballStationary, None, False, False)
    
    running = True
    while running:
        # Sync Ball Color from Profile (ensure texture loaded)
        keys = profiles.get_equipped_ball()
        if keys:
            try:
                # Convert "r,g,b" to tuple
                ballColor = tuple(map(int, keys.split(',')))
            except:
                ballColor = (255, 255, 255)
        
        # Override if powerup active
        if stickyPower: ballColor = (255,0,255)
        if superPower: ballColor = (255,69,0)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to Menu
                    return 'menu'
                    
                if event.key == pygame.K_SPACE:
                    fade()
                    if strokes == 1:
                        holeInOne()
                    else:
                        displayScore(strokes, par)
                    strokes = 0
                    
                if event.key == pygame.K_a:  # Audio settings
                    showAudioSettings()
                    redrawWindow(ballStationary, line)

            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                for x in powerUpButtons:
                    if pos[0] < x[0] + x[2] and pos[0] > x[0] - x[2] and pos[1] < x[1] + x[2] and pos[1] > x[1] - x[2]:
                        if x[3] == 'S': x[4] = (255,0,120)
                        elif x[3] == 'M': x[4] = (105,75,75)
                        elif x[3] == 'P': x[4] = (170,69,0)
                    else:
                        if x[3] == 'S': x[4] = (255,0,255)
                        elif x[3] == 'M': x[4] = (105,105,105)
                        elif x[3] == 'P': x[4] = (255,69,0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                lock = 0
                pos = pygame.mouse.get_pos()
                for x in powerUpButtons:
                    if pos[0] < x[0] + x[2] and pos[0] > x[0] - x[2] and pos[1] < x[1] + x[2] and pos[1] > x[1] - x[2]:
                        lock = -1
                        if powerUps == 0:
                            error()
                            break
                        elif x[3] == 'S':
                            if stickyPower is False and superPower is False and powerUps > 0:
                                stickyPower = True
                                powerUps -= 1
                        elif x[3] == 'M':
                            if mullagain is False and powerUps > 0 and strokes >= 1:
                                mullagain = True
                                powerUps -= 1
                                ballStationary = shootPos
                                pos = pygame.mouse.get_pos()
                                angle = findAngle(pos)
                                if hazard: strokes -= 2
                                else: strokes -= 1
                                hazard = False
                        elif x[3] == 'P':
                            if superPower is False and stickyPower is False and powerUps > 0:
                                superPower = True
                                powerUps -= 1

                if lock == 0:
                    powerAngle = math.pi
                    neg = 1
                    powerLock = False
                    loopTime = 0

                    while not powerLock:
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
                                return 'quit'
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                strokes += 1
                                hazard = False
                                if not onGreen():
                                    shoot = True
                                else:
                                    put = True
                                    if SOUND: puttSound.play()
                                if put:
                                    power = (math.pi - powerAngle) * 5
                                    rollVel = power
                                else:
                                    if not superPower: power = (math.pi - powerAngle) * 30
                                    else: power = (math.pi - powerAngle) * 40
                                
                                ball_physics.on_launch(power / 30)
                                ball_trail.clear()
                                particle_system.emit_dust(ballStationary[0], ballStationary[1], count=8)
                                if SOUND and not put: puttSound.play()

                                shootPos = ballStationary
                                powerLock = True
                                break

            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                angle = findAngle(pos)
                line = (round(ballStationary[0] + (math.cos(angle) * 50)), round(ballStationary[1] - (math.sin(angle) * 50)))
                if onGreen():
                    if ballStationary[0] > flagx:
                        angle = math.pi
                        line = (ballStationary[0] - 30, ballStationary[1])
                    else:
                        angle = 0
                        line = (ballStationary[0] + 30, ballStationary[1])

        if pygame.get_init():
            redrawWindow(ballStationary, line)
        hitting = False

        while put and not shoot:
            if not(overHole(ballStationary[0], ballStationary[1])):
                pygame.time.delay(20)
                rollVel -= 0.5
                if angle == math.pi: ballStationary = (round(ballStationary[0] - rollVel), ballStationary[1])
                else: ballStationary = (round(ballStationary[0] + rollVel), ballStationary[1])
                redrawWindow(ballStationary, None, True)

                if rollVel < 0.5:
                    put = False
                    pos = pygame.mouse.get_pos()
                    angle = findAngle(pos)
                    line = (round(ballStationary[0] + (math.cos(angle) * 50)), round(ballStationary[1] - (math.sin(angle) * 50)))
                    if onGreen():
                        if ballStationary[0] > flagx:
                            angle = math.pi
                            line = (ballStationary[0] - 30, ballStationary[1])
                        else:
                            angle = 0
                            line = (ballStationary[0] + 30, ballStationary[1])
            else:
                if SOUND: 
                    inHole.play()
                    pygame.time.delay(200)
                var = True
                while var:
                    pygame.time.delay(20)
                    redrawWindow(ballStationary, None, True)
                    ballStationary = (ballStationary[0], ballStationary[1] + 1)
                    if ballStationary[0] > hole[0]: ballStationary = (ballStationary[0] - 1, ballStationary[1])
                    else: ballStationary = (ballStationary[0] + 1, ballStationary[1])
                    if ballStationary[1] > hole[1] + 5: shoot = False; var = False
                fade()
                if strokes == 1: holeInOne()
                else: displayScore(strokes, par)
                strokes = 0
                # Re-sync after score screen
                coins = profiles.get_coins()

        while shoot:
            if not(overHole(ballStationary[0], ballStationary[1])):
                maxT = physics.maxTime(power, angle)
                time += 0.085
                ballCords = physics.ballPath(ballStationary[0], ballStationary[1], power, angle, time)
                redrawWindow(ballCords, None, True)

                if ballCords[1] > 650:
                    var = True
                    while var:
                        fade()
                        if strokes == 1: holeInOne()
                        else: displayScore(strokes, par)
                        strokes = 0
                        var = False

                for i in objects:
                    if i[4] == 'coin':
                        if len(i) > 5 and i[5]:
                            coin_x, coin_y = i[0], i[1]
                            coin_w, coin_h = i[2], i[3]
                            ball_x, ball_y = ballCords[0], ballCords[1]
                            
                            if (ball_x > coin_x - 10 and ball_x < coin_x + coin_w + 10 and 
                                ball_y > coin_y - 10 and ball_y < coin_y + coin_h + 10):
                                if SOUND: puttSound.play()
                                i[5] = False
                                coins += 1
                                particle_system.emit_sparkle(coin_x + 16, coin_y + 16)

                    if i[4] == 'laser':
                        if ballCords[0] > i[0] and ballCords[0] < i[0] + i[2] and ballCords[1] > i[1] and ballCords[1] < i[1] + i[3]:
                            ballCords = shootPos
                            hazard = True
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
                            if SOUND: wrong.play()
                            pygame.time.delay(1000)
                            ballColor = (255,255,255)
                            stickyPower = False
                            superPower = False
                            mullagain = False
                            break

                    elif i[4] == 'water':
                        if ballCords[1] > i[1] - 6 and ballCords[1] < i[1] + 8 and ballCords[0] < i[0] + i[2] and ballCords[0] > i[0] + 2:
                            particle_system.emit_splash(ballCords[0], ballCords[1])
                            ball_trail.clear()
                            ballCords = shootPos
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
                            if SOUND: splash.play()
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
                             if angle > math.pi * 0.5 and angle < math.pi: x = physics.findAngle(power, angle); angle = math.pi - x
                             elif angle < math.pi * 0.5: angle = physics.findAngle(power, angle)
                             elif angle > math.pi and angle < math.pi * 1.5: x = physics.findAngle(power, angle); angle = math.pi - x
                             else: x = physics.findAngle(power, angle); angle = x
                             
                             power = power * 0.5
                             if time > 0.15: time = 0
                             subtract = 0
                             while True:
                                 subtract += 1
                                 if ballCords[1] - subtract < i[1]: ballCords = (ballCords[0], ballCords[1] - subtract); break
                             ballStationary = ballCords
                             ball_physics.on_collision('vertical')
                             particle_system.emit_dust(ballCords[0], ballCords[1], count=5)
                             if i[4] == 'sand':
                                 if SOUND and power > 5: wrong.play()
                                 power = 0
                             if i[4] == 'sticky' or stickyPower: power = 0
                             ballStationary = ballCords
                             shoot = False
                             time = 0; pos = pygame.mouse.get_pos(); angle = findAngle(pos)
                             line = (round(ballStationary[0] + (math.cos(angle) * 50)), round(ballStationary[1] - (math.sin(angle) * 50)))
                         
                         elif ballCords[1] < i[1] + i[3] and ballCords[1] > i[1] and ballCords[0] > i[0] - 2 and ballCords[0] < i[0] + 10:
                             hitting = False
                             power = physics.findPower(power, angle, time)
                             if angle < math.pi / 2:
                                 if not(time > maxT): x = physics.findAngle(power, angle); angle = math.pi - x
                                 else: x = physics.findAngle(power, angle); angle = math.pi + x
                             else: x = physics.findAngle(power, angle); angle = math.pi + x
                             power *= 0.5
                             if time > 0.15: time = 0
                             subtract = 0
                             while True:
                                 subtract += 1
                                 if ballCords[0] - subtract < i[0] - 3: ballCords = (ballCords[0] - subtract, ballCords[1]); break
                             ballStationary = ballCords
                             ball_physics.on_collision('horizontal')
                             particle_system.emit_dust(ballCords[0], ballCords[1], count=5)
                             if i[4] == 'sticky' or stickyPower: power = 0

                         elif ballCords[1] < i[1] + i[3] and ballCords[1] > i[1] and ballCords[0] > i[0] + i[2] - 16 and ballCords[0] < i[0] + i[2]:
                             hitting = False
                             power = physics.findPower(power, angle, time)
                             if angle < math.pi:
                                 if not (time > maxT): angle = physics.findAngle(power, angle)
                                 else: x = physics.findAngle(power, angle); angle = math.pi * 2 - x
                             else: x = physics.findAngle(power, angle); angle = math.pi * 2 - x
                             power *= 0.5
                             if time > 0.15: time = 0
                             subtract = 0
                             while True:
                                 subtract += 1
                                 if ballCords[0] + subtract > i[0] + i[2] + 4: ballCords = (ballCords[0] + subtract, ballCords[1]); break
                             ballStationary = ballCords
                             ball_physics.on_collision('horizontal')
                             particle_system.emit_dust(ballCords[0], ballCords[1], count=5)
                             if i[4] == 'sticky' or stickyPower: power = 0

                         elif ballCords[1] > i[1] + i[3]and ballCords[0] + 2 > i[0] and ballCords[1] < i[1] + i[3] + 10 and ballCords[0] < i[0] + i[2] + 2:
                             power = physics.findPower(power, angle, time)
                             if not(hitting):
                                 hitting = True
                                 if angle > math.pi / 2: x = physics.findAngle(power, angle); angle = math.pi + x
                                 else: x = physics.findAngle(power, angle); angle = 2 * math.pi - x
                             power *= 0.5
                             if time > 0.04: time = 0
                             subtract = 0
                             while True:
                                 subtract += 1
                                 if ballCords[1] + subtract > i[1] + i[3] + 8: ballCords = (ballCords[0], ballCords[1] + subtract); break
                             if i[4] == 'sticky' or stickyPower:
                                 subtract = 0
                                 while True:
                                     subtract += 1
                                     if ballCords[0] + subtract > i[1] + i[3] + 4: ballCords = (ballCords[0], ballCords[1] + subtract); power = 0; break
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
                         stickyPower = False
                         mullagain = False
                         superPower = False
                         break
            else:
                 if SOUND: 
                     inHole.play()
                     pygame.time.delay(200)
                 var = True
                 while var:
                     pygame.time.delay(20)
                     redrawWindow(ballStationary, None, True)
                     ballStationary = (ballStationary[0], ballStationary[1] + 1)
                     if ballStationary[0] > hole[0]: ballStationary = (ballStationary[0] - 1, ballStationary[1])
                     else: ballStationary = (ballStationary[0] + 1, ballStationary[1])
                     if ballStationary[1] > hole[1] + 5: shoot = False; var = False
                 fade()
                 if strokes == 1: holeInOne()
                 else: displayScore(strokes, par)
                 strokes = 0
                 coins = profiles.get_coins()

        if onGreen():
            if ballStationary[0] > flagx: angle = math.pi; line = (ballStationary[0] - 30, ballStationary[1])
            else: angle = 0; line = (ballStationary[0] + 30, ballStationary[1])


def main():
    global coins, level, par, sheet, ballStationary, shooting
    
    # APP LOOP
    while True:
        # 1. Login Phase
        if not profiles.current_user:
            startScreen.login()
            
        # Sync Initial Data - IMPORTANT
        coins = profiles.get_coins()
        
        # 2. Main Menu Phase
        action = run_menu()
        
        # 3. Handle Menu Action
        if action == 'quit':
            pygame.quit()
            sys.exit()
            
        elif action == 'logout':
            profiles.logout()
            # Loop continues, sees no user, triggers login()
            continue
            
        elif action == 'play':
            # 4. Game Phase
            game_action = run_game()
            
            if game_action == 'menu':
                # User pressed ESC, go back to top (Menu)
                continue
            elif game_action == 'quit':
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
