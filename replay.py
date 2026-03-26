"""
Replay System - Records ball shots and plays them back as a ghost ball.
Press R (handled in main.py) to trigger replay of the last shot.
"""

import pygame


class ReplaySystem:
    """
    Records up to MAX_SHOTS shots per hole and replays them as a ghost ball.

    Usage:
        replay = ReplaySystem()
        replay.start_recording(start_pos)      # when shot begins
        replay.record_frame(x, y)              # each game frame while ball moves
        replay.stop_recording()                # when ball comes to rest

        replay.play_last_shot()                # trigger replay (e.g. on R key)
        # In game loop:
        replay.update()
        replay.draw(surface)
    """

    MAX_SHOTS = 3
    TRAIL_LENGTH = 6       # ghost trail dots
    GHOST_RADIUS = 6
    GHOST_COLOR  = (200, 200, 200)
    TRAIL_COLOR  = (180, 180, 180)

    def __init__(self):
        self._shots = []          # list of completed shot frame lists
        self._current = None      # list being recorded right now
        self._replay_shot = None  # shot currently being replayed (list of (x,y))
        self._frame_idx = 0       # current frame index during replay
        self._trail = []          # recent positions shown during replay

    # ------------------------------------------------------------------
    # Recording API
    # ------------------------------------------------------------------

    def start_recording(self, start_pos):
        """Begin recording a new shot starting at start_pos (x, y)."""
        self._current = [tuple(start_pos)]

    def record_frame(self, x, y):
        """Append the current ball position to the active recording."""
        if self._current is not None:
            self._current.append((x, y))

    def stop_recording(self):
        """Finalise the active recording and store it (max MAX_SHOTS kept)."""
        if self._current is not None and len(self._current) > 1:
            self._shots.append(self._current)
            if len(self._shots) > self.MAX_SHOTS:
                self._shots.pop(0)
        self._current = None

    # ------------------------------------------------------------------
    # Playback API
    # ------------------------------------------------------------------

    def play_last_shot(self):
        """Start replaying the most recently recorded shot."""
        if not self._shots:
            return
        self._replay_shot = self._shots[-1]
        self._frame_idx = 0
        self._trail = []

    def update(self):
        """Advance replay by one frame. Call once per game loop tick."""
        if self._replay_shot is None:
            return
        self._frame_idx += 1
        if self._frame_idx >= len(self._replay_shot):
            # Replay finished
            self._replay_shot = None
            self._trail = []

    def draw(self, surface, color=None):
        """
        Draw the ghost ball at the current replay position with a short trail.

        Args:
            surface: Pygame surface to draw on
            color:   RGB colour for the ghost ball (default grey)
        """
        if self._replay_shot is None:
            return

        if color is None:
            color = self.GHOST_COLOR

        idx = min(self._frame_idx, len(self._replay_shot) - 1)
        pos = self._replay_shot[idx]

        # Build trail from recent frames
        trail_start = max(0, idx - self.TRAIL_LENGTH)
        trail_positions = self._replay_shot[trail_start:idx]

        # Draw trail dots (oldest = most transparent)
        for i, tp in enumerate(trail_positions):
            fade = (i + 1) / (len(trail_positions) + 1)
            alpha = int(80 * fade)
            radius = max(2, int(self.GHOST_RADIUS * 0.6 * fade))
            dot_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, (*self.TRAIL_COLOR, alpha), (radius, radius), radius)
            surface.blit(dot_surf, (int(tp[0]) - radius, int(tp[1]) - radius))

        # Draw ghost ball at current position (50% alpha)
        r = self.GHOST_RADIUS
        ghost_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surf, (*color, 128), (r, r), r)
        # Subtle highlight
        pygame.draw.circle(ghost_surf, (255, 255, 255, 60), (r - 2, r - 2), r // 2)
        surface.blit(ghost_surf, (int(pos[0]) - r, int(pos[1]) - r))

    def is_replaying(self):
        """Return True if a replay is currently active."""
        return self._replay_shot is not None

    def clear(self):
        """Clear all recorded shots and stop any active replay."""
        self._shots = []
        self._current = None
        self._replay_shot = None
        self._frame_idx = 0
        self._trail = []

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def shot_count(self):
        """Number of recorded shots available for replay."""
        return len(self._shots)
