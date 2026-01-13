import random

class LevelGenerator:
    def __init__(self, winwidth=1080, winheight=600):
        self.winwidth = winwidth
        self.winheight = winheight
        
    def generate_course(self, seed, num_levels=9):
        """Generates a list of levels based on the seed."""
        # Clean seed and convert to hashable if needed, though random.seed handles strings
        random.seed(str(seed))
        
        course = []
        for i in range(num_levels):
            level = self.generate_level(i + 1)
            course.append(level)
            
        return course

    def generate_level(self, difficulty):
        """Generates a single level list."""
        level_objects = []
        
        # 1. Base Floor (Always present to catch falling balls)
        # Position slightly off-screen to cover edges
        floor_y = self.winheight - 8
        level_objects.append([0, floor_y, self.winwidth + 64, 100, 'floor'])
        
        # 2. Side Walls (To keep ball in play)
        level_objects.append([-8, 0, 16, self.winheight + 100, 'wall'])
        level_objects.append([self.winwidth - 8, 0, 16, self.winheight + 100, 'wall'])
        
        # 3. Start Position
        start_x = 50
        start_y = self.winheight - 20
        # Start pad
        level_objects.append([start_x - 10, start_y - 2, 64, 16, 'floor'])
        
        # 4. Target (Flag) Position
        # Randomly place flag on the right side
        flag_x = random.randint(self.winwidth - 200, self.winwidth - 80)
        flag_y = random.randint(200, self.winheight - 80)
        
        # Ensure flag has a platform (Green)
        green_width = 128
        green_y = flag_y + 60
        level_objects.append([flag_x - 32, green_y, green_width, 16, 'green'])
        level_objects.append([flag_x - 32, green_y + 8, green_width, 32, 'floor'])
        
        # 5. Generate Obstacles & Platforms between Start and Flag
        current_x = start_x + 100
        target_x = flag_x - 50
        
        while current_x < target_x:
            # Decide what to place: Platform, Water, Sand, Wall, Nothing
            choice = random.choice(['platform', 'platform', 'water', 'sand', 'wall', 'gap'])
            
            segment_width = random.randint(64, 200)
            if current_x + segment_width > target_x:
                segment_width = target_x - current_x
            
            if choice == 'platform':
                # Floating platform
                plat_y = random.randint(200, self.winheight - 100)
                level_objects.append([current_x, plat_y, segment_width, 16, 'floor'])
                
                # Maybe add a coin
                if random.random() < 0.3:
                    level_objects.append([current_x + segment_width//2 - 16, plat_y - 40, 32, 32, 'coin', True])
                    
            elif choice == 'water':
                # Water hazard on floor
                level_objects.append([current_x, self.winheight - 40, segment_width, 32, 'water'])
                
            elif choice == 'sand':
                # Sand trap on floor
                # Needs a floor underneath usually, or just replace floor?
                # In this game, sand sits on top or is the block
                level_objects.append([current_x, self.winheight - 30, segment_width, 32, 'sand'])
                
            elif choice == 'wall':
                # Vertical wall obstacle
                wall_h = random.randint(64, 200)
                wall_y = random.randint(100, self.winheight - wall_h)
                level_objects.append([current_x, wall_y, 16, wall_h, 'wall'])
                current_x += 16 # Wall is thin
                continue # Skip adding width
                
            elif choice == 'gap':
                # Empty space (gap in floor would need multiple floor objs, currently we abuse one big floor)
                # Since we have a big base floor, "gap" is meaningless unless we remove the base floor segments.
                # For simplicity, we just add obstacles ON TOP of the base floor or floating.
                pass
            
            current_x += segment_width + random.randint(20, 50)

        # Add Flag Object
        level_objects.append([flag_x, flag_y, 64, 64, 'flag'])
        
        # Calculate Par (Simple heuristic based on distance/obstacles)
        par = 3 + (difficulty // 3)
        
        # Add End Tuple
        level_objects.append([par, (start_x, start_y - 12)])
        
        return level_objects
