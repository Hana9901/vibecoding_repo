"""
俄罗斯方块 — 使用 pygame。运行前激活 venv 后执行: python main.py
"""
from __future__ import annotations

import random
import sys
from typing import List, Tuple

import pygame

# 窗口与网格
COLS, ROWS = 10, 20
CELL = 32
SIDEBAR = 180
WIDTH = COLS * CELL + SIDEBAR
HEIGHT = ROWS * CELL
FPS = 60

# 颜色
BLACK = (15, 15, 20)
GRID_LINE = (40, 40, 55)
COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 80, 240),
    "L": (240, 140, 0),
}

SHAPES: dict[str, List[List[Tuple[int, int]]]] = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    "O": [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (0, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(2, 0), (1, 0), (1, 1), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}


def new_bag() -> List[str]:
    pieces = list(SHAPES.keys())
    random.shuffle(pieces)
    return pieces


class Tetris:
    def __init__(self) -> None:
        self.grid: List[List[str | None]] = [[None] * COLS for _ in range(ROWS)]
        self.bag = new_bag()
        self.next_kind = self.bag.pop()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.piece_kind: str | None = None
        self.rotation_idx = 0
        self.px = 0
        self.py = 0
        self.game_over = False
        self._spawn_piece()

    def _spawn_piece(self) -> None:
        self.piece_kind = self.next_kind
        if not self.bag:
            self.bag = new_bag()
        self.next_kind = self.bag.pop()
        self.rotation_idx = 0
        self.px = COLS // 2 - 2
        self.py = 0
        if self._collision(self._cells()):
            self.game_over = True

    def _cells(self) -> List[Tuple[int, int]]:
        assert self.piece_kind is not None
        rotations = SHAPES[self.piece_kind]
        base = rotations[self.rotation_idx % len(rotations)]
        return [(self.px + x, self.py + y) for x, y in base]

    def _collision(self, cells: List[Tuple[int, int]]) -> bool:
        for x, y in cells:
            if x < 0 or x >= COLS or y >= ROWS:
                return True
            if y >= 0 and self.grid[y][x] is not None:
                return True
        return False

    def try_move(self, dx: int, dy: int) -> bool:
        if self.game_over or self.piece_kind is None:
            return False
        self.px += dx
        self.py += dy
        if self._collision(self._cells()):
            self.px -= dx
            self.py -= dy
            return False
        return True

    def rotate(self) -> None:
        if self.game_over or self.piece_kind is None:
            return
        rotations = SHAPES[self.piece_kind]
        old = self.rotation_idx
        self.rotation_idx = (self.rotation_idx + 1) % len(rotations)
        if self._collision(self._cells()):
            for kick in (-1, 1, -2, 2):
                self.px += kick
                if not self._collision(self._cells()):
                    return
                self.px -= kick
            self.rotation_idx = old

    def lock_and_clear(self) -> None:
        assert self.piece_kind is not None
        color = self.piece_kind
        for x, y in self._cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.grid[y][x] = color

        cleared = 0
        new_grid: List[List[str | None]] = []
        for row in self.grid:
            if all(c is not None for c in row):
                cleared += 1
            else:
                new_grid.append(row)
        while len(new_grid) < ROWS:
            new_grid.insert(0, [None] * COLS)
        self.grid = new_grid

        if cleared:
            self.lines_cleared += cleared
            points = {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 800)
            self.score += points * self.level
            self.level = 1 + self.lines_cleared // 10

        self._spawn_piece()

    def soft_drop_tick(self, frames: int) -> None:
        if self.game_over:
            return
        speed = max(1, 48 - min(self.level, 35) * 2)
        if frames % speed == 0:
            if not self.try_move(0, 1):
                self.lock_and_clear()

    def hard_drop(self) -> None:
        if self.game_over:
            return
        while self.try_move(0, 1):
            self.score += 2
        self.lock_and_clear()


def draw_cell(
    surf: pygame.Surface,
    gx: int,
    gy: int,
    kind: str,
    alpha: float = 1.0,
) -> None:
    color = COLORS[kind]
    if alpha < 1.0:
        c = pygame.Color(*color)
        c.a = int(255 * alpha)
        tile = pygame.Surface((CELL - 2, CELL - 2), pygame.SRCALPHA)
        tile.fill(c)
        surf.blit(tile, (gx * CELL + 1, gy * CELL + 1))
    else:
        r = pygame.Rect(gx * CELL + 1, gy * CELL + 1, CELL - 2, CELL - 2)
        pygame.draw.rect(surf, color, r)
        pygame.draw.rect(surf, (255, 255, 255), r, 1)


def draw_game(
    surf: pygame.Surface,
    game: Tetris,
    font: pygame.font.Font,
    small: pygame.font.Font,
) -> None:
    surf.fill(BLACK)
    # 主游戏区网格
    for x in range(COLS + 1):
        pygame.draw.line(
            surf, GRID_LINE, (x * CELL, 0), (x * CELL, HEIGHT)
        )
    for y in range(ROWS + 1):
        pygame.draw.line(
            surf, GRID_LINE, (0, y * CELL), (COLS * CELL, y * CELL)
        )

    for gy in range(ROWS):
        for gx in range(COLS):
            c = game.grid[gy][gx]
            if c:
                draw_cell(surf, gx, gy, c)

    if not game.game_over and game.piece_kind:
        for gx, gy in game._cells():
            if gy >= 0:
                draw_cell(surf, gx, gy, game.piece_kind)

    # 幽灵落点
    if not game.game_over and game.piece_kind:
        saved_py = game.py
        ghost_drop = 0
        while True:
            game.py += 1
            if game._collision(game._cells()):
                game.py -= 1
                break
            ghost_drop += 1
        game.py = saved_py
        if ghost_drop > 0:
            for gx, gy in game._cells():
                gy2 = gy + ghost_drop
                if gy2 >= 0:
                    draw_cell(surf, gx, gy2, game.piece_kind, 0.25)

    # 侧边栏
    sx = COLS * CELL + 12
    surf.blit(font.render("俄罗斯方块", True, (220, 220, 230)), (sx, 16))
    surf.blit(small.render(f"分数: {game.score}", True, (180, 180, 200)), (sx, 56))
    surf.blit(small.render(f"等级: {game.level}", True, (180, 180, 200)), (sx, 78))
    surf.blit(small.render(f"消行: {game.lines_cleared}", True, (180, 180, 200)), (sx, 100))
    surf.blit(small.render("操作说明", True, (200, 200, 220)), (sx, 140))
    hints = [
        "← →  左右",
        "↑     旋转",
        "↓     加速",
        "空格  直落",
        "R    重新开始",
        "ESC  退出",
    ]
    yy = 165
    for line in hints:
        surf.blit(small.render(line, True, (140, 140, 160)), (sx, yy))
        yy += 22

    surf.blit(small.render("下一个", True, (200, 200, 220)), (sx, 300))
    preview_x = sx
    preview_y = 328
    preview_cell = 22
    rotations = SHAPES[game.next_kind]
    cells = rotations[0]
    min_x = min(c[0] for c in cells)
    min_y = min(c[1] for c in cells)
    for x, y in cells:
        px = preview_x + (x - min_x) * preview_cell
        py = preview_y + (y - min_y) * preview_cell
        r = pygame.Rect(px, py, preview_cell - 2, preview_cell - 2)
        pygame.draw.rect(surf, COLORS[game.next_kind], r)
        pygame.draw.rect(surf, (255, 255, 255), r, 1)

    if game.game_over:
        overlay = pygame.Surface((COLS * CELL, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))
        msg = font.render("游戏结束", True, (255, 80, 80))
        surf.blit(msg, msg.get_rect(center=(COLS * CELL // 2, HEIGHT // 2 - 20)))
        m2 = small.render("按 R 重新开始", True, (220, 220, 230))
        surf.blit(m2, m2.get_rect(center=(COLS * CELL // 2, HEIGHT // 2 + 18)))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("俄罗斯方块 Tetris")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    try:
        font = pygame.font.SysFont("microsoftyahei", 22, bold=True)
        small = pygame.font.SysFont("microsoftyahei", 16)
    except Exception:
        font = pygame.font.Font(None, 28)
        small = pygame.font.Font(None, 22)

    game = Tetris()
    frame = 0
    soft_repeat = 0

    while True:
        frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    game = Tetris()
                    frame = 0
                    continue
                if game.game_over:
                    continue
                if event.key == pygame.K_LEFT:
                    game.try_move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.try_move(1, 0)
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_DOWN:
                    game.try_move(0, 1)
                    game.score += 1
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()

        keys = pygame.key.get_pressed()
        if not game.game_over and keys[pygame.K_DOWN]:
            soft_repeat += 1
            if soft_repeat >= 4:
                soft_repeat = 0
                if game.try_move(0, 1):
                    game.score += 1
        else:
            soft_repeat = 0

        game.soft_drop_tick(frame)
        draw_game(screen, game, font, small)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
