# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Super Minigolf - a 2D minigolf game built with Python 3.6+ and Pygame 2.0+. Portuguese-language project (README, comments, UI strings are in Portuguese).

## Running the Game

```bash
python main.py
```

Pygame is auto-installed if missing (via `get_pip.py` fallback). No other dependencies required.

## Architecture

**Entry point:** `main.py` contains the full game loop with three phases:
1. **Login** - tkinter dialog via `startScreen.login()` -> `profiles.login(username)`
2. **Menu** - `run_menu()` handles course selection, shop, seed mode, logout
3. **Gameplay** - `run_game()` runs 9-hole loop with physics, collision, scoring

**Module responsibilities:**

- `main.py` - Game loop, rendering (`redrawWindow`), collision, HUD, effects, scoring (`scoreSheet` class)
- `physics.py` - Trajectory math: `ballPath()`, `maxTime()`, `findPower()`, `findAngle()`. Gravity = -9.8
- `courses.py` - 9 handcrafted levels as object lists. Each object: `[x, y, w, h, type, optional_data]`. Types: floor, wall, green, water, sand, laser, sticky, coin, flag
- `startScreen.py` - Login UI, main menu rendering, shop interface (`drawShop`). `ball` class represents purchasable balls
- `ui_style.py` - Visual system (~1300 lines): `Colors`, `Fonts`, drawing utilities (rounded rects, gradients, shadows), visual effects classes (`ParticleSystem`, `BallTrail`, `ParallaxBackground`, `ScreenTransition`, `CameraShake`, `ScreenFlash`, `FlagAnimation`, `ConfettiSystem`, `BallPhysicsEffect`), `AssetManager` (cached loading), `Config` (settings persistence), `PlatformRenderer` (cached textures)
- `profiles.py` - JSON-based user persistence (`profiles.json`): coins, best score, unlocked/equipped balls
- `level_generator.py` - Procedural level generation from seed. Deterministic (same seed = same level)

**Key data flow:**
- Levels are lists of object definitions fetched via `courses.getLvl(n)` / `courses.getPar(1)`
- Ball trajectory computed by `physics.ballPath(x, y, power, angle, time)`
- Collision is AABB-based, checked per-frame against level objects
- Profile data (coins, balls, scores) persisted to `profiles.json` via `profiles.py` functions

## Game Systems

- **Hazards:** Water (reset + penalty), Sand (friction), Laser (instant reset), Sticky (velocity = 0)
- **Power-ups:** Power Ball (P, 1.5x force), Sticky Ball (S), Mullagain (M, undo shot). Max 3 per course
- **Scoring:** Golf terminology (Hole in One through Triple Bogey). Best score saved per profile
- **Shop:** 16 ball colors, purchased with coins (10 coins each). State persisted per user
- **Audio:** Music (MP3 loop) + SFX (WAV). Toggle with A key. Independent volume controls

## Window and Display

Fixed resolution: 1080x600 pixels. No resizing support.

## Assets

- `img/` - PNG sprites (background, flag, coin animation frames 1-8, obstacle textures, power meter)
- `sounds/` - music.mp3 (background), putt.wav, splash.wav, inHole.wav, wrong12.wav

## No Build/Test/Lint

No test framework, linter config, or CI pipeline. The project runs directly via `python main.py`.

## Notable Quirks

- `scores.txt` is legacy — `profiles.json` via `profiles.py` is the actual persistence system now
- `main_new_logic.py` is an experimental/unused refactor of `main.py` — not loaded anywhere
- `get_pip.py` is a 1.7MB standalone pip installer used as fallback if pip is missing
- `courses.py` `coinHit()` mutates level data in-place (sets coin visible flag to `False`)
- Shop in `startScreen.py` rebuilds `ballObjects` and `surfaces` globals on every `drawShop()` call
- Login system uses `tkinter` dialogs (`simpledialog`, `messagebox`) which block the Pygame event loop
- Seed mode: `courses.set_seed(seed)` switches to procedural generation via `level_generator.py`. Set to `None` to revert to handcrafted levels
