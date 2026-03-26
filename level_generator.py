import random


class LevelGenerator:
    def __init__(self, winwidth=1080, winheight=600):
        self.winwidth = winwidth
        self.winheight = winheight

    def generate_course(self, seed, num_levels=9):
        """Generates a list of levels based on the seed."""
        random.seed(str(seed))

        course = []
        for i in range(num_levels):
            level = self.generate_level(i + 1)
            course.append(level)

        return course

    def generate_level(self, difficulty):
        """Generates a single level. Difficulty 1-9 scales hazard complexity."""
        level_objects = []

        # 1. Base Floor
        floor_y = self.winheight - 8
        level_objects.append([0, floor_y, self.winwidth + 64, 100, 'floor'])

        # 2. Ceiling (keep ball in)
        level_objects.append([0, -8, self.winwidth + 64, 16, 'floor'])

        # 3. Side Walls
        level_objects.append([-8, 0, 16, self.winheight + 100, 'wall'])
        level_objects.append([self.winwidth - 8, 0, 16, self.winheight + 100, 'wall'])

        # 4. Start Position (left side)
        start_x = 50
        start_y = self.winheight - 20
        level_objects.append([start_x - 10, start_y - 2, 80, 16, 'floor'])

        # 5. Flag Position (right side, varies by difficulty)
        if difficulty <= 3:
            flag_x = random.randint(self.winwidth - 200, self.winwidth - 100)
            flag_y = random.randint(350, self.winheight - 100)
        elif difficulty <= 6:
            flag_x = random.randint(self.winwidth - 220, self.winwidth - 100)
            flag_y = random.randint(200, self.winheight - 120)
        else:
            flag_x = random.randint(self.winwidth - 220, self.winwidth - 100)
            flag_y = random.randint(100, self.winheight - 150)

        # Green + platform under flag
        green_width = 128
        green_y = flag_y + 60
        level_objects.append([flag_x - 32, green_y, green_width, 8, 'green'])
        level_objects.append([flag_x - 32, green_y + 8, green_width, 24, 'floor'])

        # 6. Generate obstacles between start and flag
        current_x = start_x + 120
        target_x = flag_x - 80
        coin_count = 0
        max_coins = 1 if difficulty <= 6 else 2

        # Build platform tiers for multi-tier structure
        tier_heights = self._make_tiers(difficulty, flag_y)

        while current_x < target_x:
            remaining = target_x - current_x
            if remaining <= 0:
                break

            choice = self._pick_obstacle(difficulty)

            segment_width = random.randint(64, max(64, min(200, remaining)))

            if choice == 'platform':
                plat_y = random.choice(tier_heights)
                level_objects.append([current_x, plat_y, segment_width, 16, 'floor'])
                # Maybe add an elevated coin on this platform
                if coin_count < max_coins and random.random() < 0.35:
                    cx = current_x + segment_width // 2 - 16
                    level_objects.append([cx, plat_y - 40, 32, 32, 'coin', True])
                    coin_count += 1
                current_x += segment_width + random.randint(20, 60)

            elif choice == 'elevated_platform':
                # Platform at a higher tier, with a connecting lower platform
                high_y = random.randint(100, 250)
                low_y = random.randint(300, 450)
                w1 = random.randint(64, 128)
                w2 = random.randint(64, 128)
                level_objects.append([current_x, low_y, w1, 16, 'floor'])
                level_objects.append([current_x + w1 + 40, high_y, w2, 16, 'floor'])
                if coin_count < max_coins and random.random() < 0.4:
                    level_objects.append([current_x + w1 + 40 + w2 // 2 - 16, high_y - 40, 32, 32, 'coin', True])
                    coin_count += 1
                current_x += w1 + w2 + 80 + random.randint(20, 50)

            elif choice == 'water':
                level_objects.append([current_x, self.winheight - 48, segment_width, 40, 'water'])
                current_x += segment_width + random.randint(20, 50)

            elif choice == 'sand':
                level_objects.append([current_x, self.winheight - 48, segment_width, 40, 'sand'])
                current_x += segment_width + random.randint(20, 50)

            elif choice == 'wall':
                wall_h = random.randint(80, 200)
                wall_y = random.randint(self.winheight - wall_h - 80, self.winheight - 80)
                # Validate: wall must not span full height (leave at least 80px gap at top)
                if wall_y > 80:
                    level_objects.append([current_x, wall_y, 16, wall_h, 'wall'])
                current_x += 16 + random.randint(20, 60)

            elif choice == 'laser':
                laser_h = random.randint(100, 220)
                # Place from floor upward, leaving gap for ball to pass over or below
                laser_y = random.randint(self.winheight - laser_h - 60, self.winheight - 60)
                if laser_y > 80:
                    level_objects.append([current_x, laser_y, 16, laser_h, 'laser'])
                    level_objects.append([current_x, laser_y + laser_h, 16, self.winheight - laser_y - laser_h, 'wall'])
                current_x += 16 + random.randint(40, 80)

            elif choice == 'sticky':
                sticky_h = random.randint(80, 180)
                sticky_y = random.randint(100, self.winheight - sticky_h - 60)
                level_objects.append([current_x, sticky_y, 16, sticky_h, 'sticky'])
                current_x += 16 + random.randint(30, 70)

            elif choice == 'moving':
                plat_y = random.choice(tier_heights)
                plat_w = random.randint(80, 150)
                move_range = random.randint(80, 180)
                speed = random.randint(1, 3) if difficulty <= 6 else random.randint(2, 4)
                level_objects.append([current_x, plat_y, plat_w, 16, 'moving',
                                       {'speed': speed, 'axis': 'x', 'range': move_range}])
                if coin_count < max_coins and random.random() < 0.3:
                    level_objects.append([current_x + plat_w // 2 - 16, plat_y - 40, 32, 32, 'coin', True])
                    coin_count += 1
                current_x += plat_w + move_range + random.randint(30, 60)

            elif choice == 'gap':
                # Just advance — there's a base floor so this creates open space
                current_x += random.randint(60, 120)

        # Ensure at least one coin exists
        if coin_count == 0:
            coin_x = random.randint(start_x + 100, max(start_x + 101, target_x - 50))
            coin_y = self.winheight - 60
            level_objects.append([coin_x, coin_y, 32, 32, 'coin', True])

        # Add Flag
        level_objects.append([flag_x, flag_y, 64, 64, 'flag'])

        # Par calculation: base 3 + obstacles/3 + distance factor
        obstacle_count = sum(1 for o in level_objects if len(o) > 4 and o[4] in ('wall', 'water', 'sand', 'laser', 'sticky', 'moving'))
        distance = flag_x - start_x
        distance_factor = distance / 400
        par = max(3, min(6, round(3 + obstacle_count / 3 + distance_factor)))

        level_objects.append([par, (start_x, start_y - 12)])

        return level_objects

    def _make_tiers(self, difficulty, flag_y):
        """Return a list of Y heights to use for platform tiers based on difficulty."""
        if difficulty <= 3:
            # Simple: one or two heights near floor
            return [self.winheight - 120, self.winheight - 200]
        elif difficulty <= 6:
            # Medium: three tiers
            return [self.winheight - 120, self.winheight - 240, self.winheight - 360]
        else:
            # Hard: four tiers, including high platforms
            return [self.winheight - 100, self.winheight - 220, self.winheight - 340, max(100, flag_y - 50)]

    def _pick_obstacle(self, difficulty):
        """Choose an obstacle type weighted by difficulty tier."""
        if difficulty <= 3:
            # Simple: mostly platforms, gaps, some sand
            return random.choice([
                'platform', 'platform', 'platform',
                'gap', 'gap',
                'sand', 'wall',
            ])
        elif difficulty <= 6:
            # Medium: add water, elevated platforms, moving
            return random.choice([
                'platform', 'platform',
                'elevated_platform',
                'water', 'water',
                'sand',
                'wall', 'wall',
                'gap',
                'moving',
            ])
        else:
            # Hard: add laser, sticky, moving
            return random.choice([
                'platform',
                'elevated_platform',
                'water',
                'sand',
                'wall',
                'laser', 'laser',
                'sticky',
                'moving', 'moving',
                'gap',
            ])

    def _validate_path(self, level_objects, start_x, flag_x):
        """
        Simple horizontal path validation: ensure no wall spans the full window height
        at any x position between start and flag, which would completely block passage.
        Returns True if path seems passable.
        """
        walls = [o for o in level_objects if len(o) >= 5 and o[4] in ('wall', 'laser') and o[2] <= 20]
        for w in walls:
            wx, wy, ww, wh = w[0], w[1], w[2], w[3]
            if wx < start_x or wx > flag_x:
                continue
            # Check if this wall spans from ceiling to floor (full block)
            if wy <= 0 and wy + wh >= self.winheight:
                return False
        return True
