# -*- coding: utf-8 -*-
#
# ONE-FILE MOBILE MINI-GAMES
# Python + Kivy
#
# Запуск:
#     pip install kivy
#     python main.py
#
# Для Android позже можно собрать через Buildozer.
#

import json
import os
import random
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget


# ============================================================
# SAVE SYSTEM
# ============================================================

SAVE_FILE = "mini_games_save.json"


DEFAULT_SAVE = {
    "coins": 0,
    "best": {
        "red": 0,
        "reaction": 9999,
        "snake": 0,
        "pong": 0,
        "mines": 0,
        "2048": 0,
        "target": 0,
        "math": 0
    }
}


def load_save():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            result = DEFAULT_SAVE.copy()
            result["best"] = DEFAULT_SAVE["best"].copy()

            if isinstance(data, dict):
                result["coins"] = int(data.get("coins", 0))
                if isinstance(data.get("best"), dict):
                    result["best"].update(data["best"])

            return result
    except Exception:
        pass

    return {
        "coins": 0,
        "best": DEFAULT_SAVE["best"].copy()
    }


def save_data(data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


SAVE = load_save()


# ============================================================
# COLORS
# ============================================================

BG = (0.055, 0.065, 0.09, 1)
PANEL = (0.10, 0.12, 0.17, 1)
PANEL2 = (0.13, 0.15, 0.21, 1)
WHITE = (0.95, 0.95, 0.98, 1)
GRAY = (0.62, 0.65, 0.72, 1)
GREEN = (0.25, 0.85, 0.45, 1)
RED = (0.95, 0.25, 0.25, 1)
BLUE = (0.25, 0.55, 1, 1)
YELLOW = (1, 0.78, 0.15, 1)
ORANGE = (1, 0.45, 0.12, 1)
PURPLE = (0.65, 0.35, 1, 1)


# ============================================================
# COMMON WIDGETS
# ============================================================

class BGWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            Color(*BG)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class GameButton(Button):

    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color", PANEL2)
        kwargs.setdefault("color", WHITE)
        kwargs.setdefault("font_size", dp(18))
        super().__init__(**kwargs)


class Title(Label):

    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", dp(28))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("color", WHITE)
        super().__init__(**kwargs)


class BaseScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = FloatLayout()
        self.bg = BGWidget()
        self.root_layout.add_widget(self.bg)
        self.add_widget(self.root_layout)

    def add_back_button(self):
        b = GameButton(
            text="← МЕНЮ",
            size_hint=(None, None),
            size=(dp(110), dp(48)),
            pos=(dp(10), dp(10))
        )
        b.bind(on_release=lambda *_: self.go_menu())
        self.root_layout.add_widget(b)

    def go_menu(self):
        App.get_running_app().sm.current = "menu"

    def on_enter(self):
        pass

    def on_leave(self):
        pass


def add_top_label(layout, text):
    label = Label(
        text=text,
        size_hint=(1, None),
        height=dp(55),
        pos_hint={"top": 1},
        color=WHITE,
        font_size=dp(22),
        bold=True
    )
    layout.add_widget(label)
    return label


# ============================================================
# MENU
# ============================================================

class MenuScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        title = Title(
            text="🎮 MINI GAME COMBINE",
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"top": 0.96}
        )
        self.root_layout.add_widget(title)

        self.coins_label = Label(
            text="",
            size_hint=(1, None),
            height=dp(40),
            pos_hint={"top": 0.86},
            color=YELLOW,
            font_size=dp(19)
        )
        self.root_layout.add_widget(self.coins_label)

        games = GridLayout(
            cols=2,
            spacing=dp(10),
            padding=dp(15),
            size_hint=(0.94, 0.62),
            pos_hint={"center_x": 0.5, "center_y": 0.49}
        )

        buttons = [
            ("🟥 НЕ НАЖМИ КРАСНУЮ", "red"),
            ("⚡ РЕАКЦИЯ", "reaction"),
            ("🐍 ЗМЕЙКА", "snake"),
            ("🏓 PONG", "pong"),
            ("💣 САПЁР", "mines"),
            ("🧱 2048", "2048"),
            ("🎯 ТИР", "target"),
            ("🧠 МАТЕМАТИКА", "math"),
        ]

        for text, screen_name in buttons:
            b = GameButton(text=text)
            b.bind(
                on_release=lambda btn, name=screen_name:
                self.open_game(name)
            )
            games.add_widget(b)

        self.root_layout.add_widget(games)

        stats = GameButton(
            text="🏆 РЕКОРДЫ / СТАТИСТИКА",
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={"center_x": 0.5, "y": 0.08}
        )
        stats.bind(on_release=self.open_stats)
        self.root_layout.add_widget(stats)

        Clock.schedule_once(lambda *_: self.refresh(), 0)

    def refresh(self):
        self.coins_label.text = f"💰 Монеты: {SAVE['coins']}"

    def on_enter(self):
        self.refresh()

    def open_game(self, name):
        App.get_running_app().sm.current = name

    def open_stats(self, *_):
        App.get_running_app().sm.current = "stats"


# ============================================================
# STATS
# ============================================================

class StatsScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🏆 СТАТИСТИКА")

        self.text = Label(
            text="",
            color=WHITE,
            font_size=dp(18),
            halign="left",
            valign="middle",
            size_hint=(0.9, 0.65),
            pos_hint={"center_x": 0.5, "center_y": 0.52}
        )

        self.root_layout.add_widget(self.text)
        self.add_back_button()

    def on_enter(self):
        b = SAVE["best"]

        self.text.text = (
            f"💰 Монеты: {SAVE['coins']}\n\n"
            f"🟥 Красная: {b['red']}\n"
            f"⚡ Реакция: {b['reaction']} мс\n"
            f"🐍 Змейка: {b['snake']}\n"
            f"🏓 Pong: {b['pong']}\n"
            f"💣 Сапёр: {b['mines']}\n"
            f"🧱 2048: {b['2048']}\n"
            f"🎯 Тир: {b['target']}\n"
            f"🧠 Математика: {b['math']}"
        )


# ============================================================
# RED GAME
# ============================================================

class RedScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🟥 НЕ НАЖМИ КРАСНУЮ")

        self.info = Label(
            text="Нажимай на зелёные кнопки.\nКрасная — проигрыш!",
            color=WHITE,
            font_size=dp(19),
            size_hint=(1, None),
            height=dp(80),
            pos_hint={"center_y": 0.82}
        )
        self.root_layout.add_widget(self.info)

        self.area = FloatLayout(
            size_hint=(0.9, 0.55),
            pos_hint={"center_x": 0.5, "center_y": 0.45}
        )

        self.root_layout.add_widget(self.area)

        self.score = 0
        self.red_button = None

        self.start_button = GameButton(
            text="СТАРТ",
            size_hint=(None, None),
            size=(dp(150), dp(55)),
            pos_hint={"center_x": 0.5, "center_y": 0.15}
        )
        self.start_button.bind(on_release=self.start)
        self.root_layout.add_widget(self.start_button)

        self.add_back_button()

    def start(self, *_):
        self.score = 0
        self.start_button.disabled = True
        self.spawn()

    def spawn(self):
        self.area.clear_widgets()

        count = min(12, 4 + self.score // 3)

        red_index = random.randrange(count)

        for i in range(count):
            b = GameButton(
                text="●",
                font_size=dp(28),
                background_color=RED if i == red_index else GREEN,
                size_hint=(None, None),
                size=(dp(58), dp(58))
            )

            b.pos = (
                random.uniform(dp(5), max(dp(6), self.area.width - dp(65))),
                random.uniform(dp(5), max(dp(6), self.area.height - dp(65)))
            )

            if i == red_index:
                b.bind(on_release=self.red_hit)
            else:
                b.bind(on_release=self.green_hit)

            self.area.add_widget(b)

    def green_hit(self, *_):
        self.score += 1
        SAVE["coins"] += 1

        if self.score > SAVE["best"]["red"]:
            SAVE["best"]["red"] = self.score

        save_data(SAVE)

        self.info.text = f"Счёт: {self.score}"
        self.spawn()

    def red_hit(self, *_):
        self.info.text = f"💥 Проигрыш!\nРезультат: {self.score}"
        self.start_button.disabled = False
        self.area.clear_widgets()


# ============================================================
# REACTION
# ============================================================

class ReactionScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "⚡ РЕАКЦИЯ")

        self.info = Label(
            text="Нажми СТАРТ и жди зелёного.",
            color=WHITE,
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(90),
            pos_hint={"center_y": 0.8}
        )
        self.root_layout.add_widget(self.info)

        self.box = GameButton(
            text="СТАРТ",
            size_hint=(0.7, 0.35),
            pos_hint={"center_x": 0.5, "center_y": 0.47},
            font_size=dp(30)
        )

        self.box.bind(on_release=self.click)
        self.root_layout.add_widget(self.box)

        self.state = "idle"
        self.start_time = 0
        self.timer_event = None

        self.add_back_button()

    def click(self, *_):

        if self.state == "idle":
            self.state = "waiting"
            self.box.text = "ЖДИ..."
            self.box.background_color = ORANGE

            delay = random.uniform(1.5, 4.0)
            self.timer_event = Clock.schedule_once(self.go_green, delay)

        elif self.state == "waiting":
            self.state = "idle"
            if self.timer_event:
                self.timer_event.cancel()

            self.box.text = "РАНО!"
            self.box.background_color = RED

        elif self.state == "green":
            reaction = int((time.time() - self.start_time) * 1000)

            self.state = "idle"

            self.info.text = f"⚡ {reaction} мс"

            self.box.text = "ЕЩЁ РАЗ"
            self.box.background_color = BLUE

            if reaction < SAVE["best"]["reaction"]:
                SAVE["best"]["reaction"] = reaction

            SAVE["coins"] += max(1, 100 - reaction // 10)

            save_data(SAVE)

    def go_green(self, *_):
        self.state = "green"
        self.start_time = time.time()

        self.box.text = "НАЖМИ!"
        self.box.background_color = GREEN


# ============================================================
# SNAKE
# ============================================================

class SnakeGame(Widget):

    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)

        self.screen = screen

        self.cols = 18
        self.rows = 24

        self.snake = []
        self.food = (5, 5)

        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.running = False
        self.score = 0

        self.bind(size=self.redraw, pos=self.redraw)

        Window.bind(on_key_down=self.key_down)

    def start(self):
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.running = True

        self.spawn_food()

        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 0.12)

        self.redraw()

    def spawn_food(self):
        while True:
            p = (
                random.randrange(self.cols),
                random.randrange(self.rows)
            )

            if p not in self.snake:
                self.food = p
                return

    def key_down(self, window, key, scancode, codepoint, modifiers):

        keys = {
            273: (0, 1),
            274: (0, -1),
            275: (1, 0),
            276: (-1, 0)
        }

        if key in keys:
            self.set_direction(keys[key])

    def set_direction(self, d):
        if (-d[0], -d[1]) != self.direction:
            self.next_direction = d

    def on_touch_down(self, touch):

        if not self.collide_point(*touch.pos):
            return False

        x = touch.x - self.x
        y = touch.y - self.y

        if abs(x) > abs(y):
            self.set_direction((1, 0) if x > 0 else (-1, 0))
        else:
            self.set_direction((0, 1) if y > 0 else (0, -1))

        return True

    def update(self, dt):

        if not self.running:
            return

        self.direction = self.next_direction

        head = self.snake[0]

        new_head = (
            head[0] + self.direction[0],
            head[1] + self.direction[1]
        )

        if (
            new_head[0] < 0
            or new_head[0] >= self.cols
            or new_head[1] < 0
            or new_head[1] >= self.rows
            or new_head in self.snake
        ):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            SAVE["coins"] += 2

            if self.score > SAVE["best"]["snake"]:
                SAVE["best"]["snake"] = self.score

            save_data(SAVE)

            self.spawn_food()
        else:
            self.snake.pop()

        self.redraw()

    def game_over(self):
        self.running = False
        Clock.unschedule(self.update)

        self.screen.info.text = (
            f"💥 Змейка проиграла!\n"
            f"Счёт: {self.score}"
        )

        self.redraw()

    def redraw(self, *args):

        self.canvas.clear()

        if self.width <= 0 or self.height <= 0:
            return

        cw = self.width / self.cols
        ch = self.height / self.rows

        with self.canvas:

            Color(*PANEL)
            Rectangle(pos=self.pos, size=self.size)

            Color(*RED)

            fx, fy = self.food

            Ellipse(
                pos=(
                    self.x + fx * cw + cw * 0.1,
                    self.y + fy * ch + ch * 0.1
                ),
                size=(cw * 0.8, ch * 0.8)
            )

            for i, (sx, sy) in enumerate(self.snake):

                Color(*(GREEN if i == 0 else BLUE))

                Rectangle(
                    pos=(
                        self.x + sx * cw + 1,
                        self.y + sy * ch + 1
                    ),
                    size=(cw - 2, ch - 2)
                )


class SnakeScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🐍 ЗМЕЙКА")

        self.info = Label(
            text="Стрелки на ПК или свайпы на телефоне.",
            color=WHITE,
            size_hint=(1, None),
            height=dp(55),
            pos_hint={"top": 0.9}
        )
        self.root_layout.add_widget(self.info)

        self.game = SnakeGame(
            self,
            size_hint=(0.9, 0.68),
            pos_hint={"center_x": 0.5, "center_y": 0.49}
        )

        self.root_layout.add_widget(self.game)

        start = GameButton(
            text="СТАРТ / ЗАНОВО",
            size_hint=(0.5, None),
            height=dp(50),
            pos_hint={"center_x": 0.5, "y": 0.09}
        )

        start.bind(on_release=lambda *_: self.game.start())

        self.root_layout.add_widget(start)

        self.add_back_button()

    def on_leave(self):
        self.game.running = False
        Clock.unschedule(self.game.update)


# ============================================================
# PONG
# ============================================================

class PongGame(Widget):

    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)

        self.screen = screen

        self.ball = [0, 0]
        self.velocity = [0, 0]

        self.player_y = 0
        self.enemy_y = 0

        self.player_score = 0
        self.enemy_score = 0

        self.running = False

        self.bind(size=self.reset_positions, pos=self.reset_positions)

    def start(self):
        self.player_score = 0
        self.enemy_score = 0
        self.running = True

        self.reset_ball(random.choice([-1, 1]))

        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1 / 60)

    def reset_positions(self, *args):
        self.player_y = self.height / 2
        self.enemy_y = self.height / 2

        if self.width > 0:
            self.reset_ball(random.choice([-1, 1]))

        self.redraw()

    def reset_ball(self, direction):
        self.ball = [self.width / 2, self.height / 2]

        self.velocity = [
            direction * max(dp(3), self.width * 0.006),
            random.choice([-1, 1]) * max(dp(2), self.height * 0.004)
        ]

    def on_touch_down(self, touch):
        self.move_player(touch.y)
        return True

    def on_touch_move(self, touch):
        self.move_player(touch.y)
        return True

    def move_player(self, y):
        self.player_y = max(dp(35), min(self.height - dp(35), y - self.y))

    def update(self, dt):

        if not self.running:
            return

        self.ball[0] += self.velocity[0]
        self.ball[1] += self.velocity[1]

        if self.ball[1] <= dp(10) or self.ball[1] >= self.height - dp(10):
            self.velocity[1] *= -1

        # AI
        if self.enemy_y < self.ball[1]:
            self.enemy_y += dp(2.7)
        else:
            self.enemy_y -= dp(2.7)

        self.enemy_y = max(dp(35), min(self.height - dp(35), self.enemy_y))

        # Player paddle
        if (
            self.ball[0] <= dp(35)
            and abs(self.ball[1] - self.player_y) < dp(45)
            and self.velocity[0] < 0
        ):
            self.velocity[0] *= -1.05

        # Enemy paddle
        if (
            self.ball[0] >= self.width - dp(35)
            and abs(self.ball[1] - self.enemy_y) < dp(45)
            and self.velocity[0] > 0
        ):
            self.velocity[0] *= -1.05

        if self.ball[0] < -dp(20):
            self.enemy_score += 1
            self.reset_ball(1)

        if self.ball[0] > self.width + dp(20):
            self.player_score += 1

            if self.player_score > SAVE["best"]["pong"]:
                SAVE["best"]["pong"] = self.player_score

            SAVE["coins"] += 5
            save_data(SAVE)

            self.reset_ball(-1)

        self.screen.info.text = (
            f"{self.player_score} : {self.enemy_score}"
        )

        self.redraw()

    def redraw(self, *args):

        self.canvas.clear()

        with self.canvas:

            Color(*PANEL)
            Rectangle(pos=self.pos, size=self.size)

            Color(*GRAY)

            Line(
                points=[
                    self.center_x,
                    self.y,
                    self.center_x,
                    self.top
                ],
                width=1,
                dash_offset=3,
                dash_length=5
            )

            Color(*GREEN)

            Rectangle(
                pos=(self.x + dp(15), self.y + self.player_y - dp(35)),
                size=(dp(12), dp(70))
            )

            Color(*RED)

            Rectangle(
                pos=(
                    self.right - dp(27),
                    self.y + self.enemy_y - dp(35)
                ),
                size=(dp(12), dp(70))
            )

            Color(*WHITE)

            Ellipse(
                pos=(
                    self.x + self.ball[0] - dp(9),
                    self.y + self.ball[1] - dp(9)
                ),
                size=(dp(18), dp(18))
            )


class PongScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🏓 PONG")

        self.info = Label(
            text="0 : 0",
            color=WHITE,
            font_size=dp(24),
            size_hint=(1, None),
            height=dp(50),
            pos_hint={"top": 0.9}
        )

        self.root_layout.add_widget(self.info)

        self.game = PongGame(
            self,
            size_hint=(0.9, 0.68),
            pos_hint={"center_x": 0.5, "center_y": 0.47}
        )

        self.root_layout.add_widget(self.game)

        b = GameButton(
            text="СТАРТ",
            size_hint=(0.45, None),
            height=dp(50),
            pos_hint={"center_x": 0.5, "y": 0.09}
        )

        b.bind(on_release=lambda *_: self.game.start())

        self.root_layout.add_widget(b)

        self.add_back_button()

    def on_leave(self):
        self.game.running = False
        Clock.unschedule(self.game.update)


# ============================================================
# MINESWEEPER
# ============================================================

class MinesScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "💣 САПЁР")

        self.info = Label(
            text="Открой все безопасные клетки.",
            color=WHITE,
            font_size=dp(18),
            size_hint=(1, None),
            height=dp(50),
            pos_hint={"top": 0.9}
        )

        self.root_layout.add_widget(self.info)

        self.grid = GridLayout(
            cols=8,
            rows=8,
            spacing=dp(2),
            padding=dp(3),
            size_hint=(0.9, 0.65),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        self.root_layout.add_widget(self.grid)

        self.cells = []
        self.mines = set()
        self.opened = set()

        restart = GameButton(
            text="НОВАЯ ИГРА",
            size_hint=(0.45, None),
            height=dp(50),
            pos_hint={"center_x": 0.5, "y": 0.09}
        )

        restart.bind(on_release=lambda *_: self.new_game())

        self.root_layout.add_widget(restart)

        self.add_back_button()

        self.new_game()

    def new_game(self):
        self.grid.clear_widgets()
        self.cells = []
        self.opened = set()

        self.mines = set(
            random.sample(range(64), 10)
        )

        for i in range(64):

            b = GameButton(
                text="",
                font_size=dp(15),
                background_color=PANEL2
            )

            b.bind(
                on_release=lambda btn, idx=i:
                self.open_cell(idx)
            )

            self.cells.append(b)
            self.grid.add_widget(b)

        self.info.text = "💣 10 мин"

    def neighbours(self, idx):
        x = idx % 8
        y = idx // 8

        result = []

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):

                if dx == 0 and dy == 0:
                    continue

                nx = x + dx
                ny = y + dy

                if 0 <= nx < 8 and 0 <= ny < 8:
                    result.append(ny * 8 + nx)

        return result

    def count_mines(self, idx):
        return sum(
            1 for n in self.neighbours(idx)
            if n in self.mines
        )

    def open_cell(self, idx):

        if idx in self.opened:
            return

        if idx in self.mines:

            for m in self.mines:
                self.cells[m].text = "💣"

            self.info.text = "💥 БУМ! Ты проиграл."

            return

        self.reveal(idx)

        safe = 64 - len(self.mines)

        if len(self.opened) >= safe:

            self.info.text = "🏆 САПЁР ПРОЙДЕН!"

            SAVE["coins"] += 30
            SAVE["best"]["mines"] += 1

            save_data(SAVE)

    def reveal(self, idx):

        if idx in self.opened or idx in self.mines:
            return

        self.opened.add(idx)

        count = self.count_mines(idx)

        self.cells[idx].text = str(count) if count else "·"
        self.cells[idx].background_color = PANEL

        if count == 0:
            for n in self.neighbours(idx):
                self.reveal(n)


# ============================================================
# 2048
# ============================================================

class Game2048Screen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🧱 2048")

        self.info = Label(
            text="Свайпай в любую сторону.",
            color=WHITE,
            font_size=dp(17),
            size_hint=(1, None),
            height=dp(50),
            pos_hint={"top": 0.9}
        )

        self.root_layout.add_widget(self.info)

        self.grid = GridLayout(
            cols=4,
            rows=4,
            spacing=dp(5),
            padding=dp(5),
            size_hint=(0.88, 0.58),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        self.root_layout.add_widget(self.grid)

        self.buttons = []

        for _ in range(16):

            b = GameButton(
                text="",
                font_size=dp(23),
                background_color=PANEL2
            )

            self.buttons.append(b)
            self.grid.add_widget(b)

        self.board = [0] * 16
        self.start_touch = None

        restart = GameButton(
            text="НОВАЯ ИГРА",
            size_hint=(0.45, None),
            height=dp(50),
            pos_hint={"center_x": 0.5, "y": 0.09}
        )

        restart.bind(on_release=lambda *_: self.new_game())

        self.root_layout.add_widget(restart)

        self.add_back_button()

        Window.bind(on_key_down=self.key_down)

        self.new_game()

    def new_game(self):
        self.board = [0] * 16
        self.add_tile()
        self.add_tile()
        self.update_view()

    def add_tile(self):

        free = [
            i for i, v in enumerate(self.board)
            if v == 0
        ]

        if free:
            self.board[random.choice(free)] = (
                4 if random.random() < 0.1 else 2
            )

    def key_down(self, window, key, scancode, codepoint, modifiers):

        directions = {
            273: "up",
            274: "down",
            275: "right",
            276: "left"
        }

        if key in directions:
            self.move(directions[key])

    def on_touch_down(self, touch):

        self.start_touch = touch.pos
        return True

    def on_touch_up(self, touch):

        if not self.start_touch:
            return True

        dx = touch.x - self.start_touch[0]
        dy = touch.y - self.start_touch[1]

        if abs(dx) < dp(20) and abs(dy) < dp(20):
            return True

        if abs(dx) > abs(dy):
            self.move("right" if dx > 0 else "left")
        else:
            self.move("up" if dy > 0 else "down")

        self.start_touch = None

        return True

    def move_line(self, line):

        original = line[:]

        values = [x for x in line if x != 0]

        result = []
        i = 0

        while i < len(values):

            if i + 1 < len(values) and values[i] == values[i + 1]:

                result.append(values[i] * 2)

                SAVE["coins"] += 1

                i += 2

            else:

                result.append(values[i])

                i += 1

        result += [0] * (4 - len(result))

        return result, result != original

    def move(self, direction):

        old = self.board[:]
        changed = False

        if direction == "left":

            for y in range(4):

                line = [
                    self.board[y * 4 + x]
                    for x in range(4)
                ]

                line, c = self.move_line(line)
                changed |= c

                for x in range(4):
                    self.board[y * 4 + x] = line[x]

        elif direction == "right":

            for y in range(4):

                line = [
                    self.board[y * 4 + x]
                    for x in reversed(range(4))
                ]

                line, c = self.move_line(line)
                changed |= c

                for x in range(4):
                    self.board[y * 4 + x] = line[3 - x]

        elif direction == "up":

            for x in range(4):

                line = [
                    self.board[y * 4 + x]
                    for y in range(4)
                ]

                line, c = self.move_line(line)
                changed |= c

                for y in range(4):
                    self.board[y * 4 + x] = line[y]

        elif direction == "down":

            for x in range(4):

                line = [
                    self.board[y * 4 + x]
                    for y in reversed(range(4))
                ]

                line, c = self.move_line(line)
                changed |= c

                for y in range(4):
                    self.board[y * 4 + x] = line[3 - y]

        if changed:
            self.add_tile()
            self.update_view()

        if 2048 in self.board:
            self.info.text = "🏆 2048 ДОСТИГНУТО!"

            if SAVE["best"]["2048"] < 2048:
                SAVE["best"]["2048"] = 2048

            save_data(SAVE)

        elif not self.can_move():
            self.info.text = "💀 ИГРА ОКОНЧЕНА"

    def can_move(self):

        if 0 in self.board:
            return True

        for y in range(4):
            for x in range(4):

                i = y * 4 + x

                if x < 3 and self.board[i] == self.board[i + 1]:
                    return True

                if y < 3 and self.board[i] == self.board[i + 4]:
                    return True

        return False

    def update_view(self):

        score = sum(self.board)

        self.info.text = f"Сумма: {score}"

        for i, value in enumerate(self.board):

            self.buttons[i].text = str(value) if value else ""


# ============================================================
# TARGET SHOOTER
# ============================================================

class TargetScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🎯 ТИР")

        self.info = Label(
            text="Попади по цели как можно быстрее.",
            color=WHITE,
            font_size=dp(18),
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"top": 0.9}
        )

        self.root_layout.add_widget(self.info)

        self.area = FloatLayout(
            size_hint=(0.9, 0.65),
            pos_hint={"center_x": 0.5, "center_y": 0.48}
        )

        self.root_layout.add_widget(self.area)

        self.score = 0
        self.start_time = 0
        self.running = False
        self.target = None

        start = GameButton(
            text="СТАРТ",
            size_hint=(0.45, None),
            height=dp(50),
            pos_hint={"center_x": 0.5, "y": 0.09}
        )

        start.bind(on_release=self.start)

        self.root_layout.add_widget(start)

        self.add_back_button()

    def start(self, *_):

        self.score = 0
        self.running = True
        self.start_time = time.time()

        self.spawn()

    def spawn(self):

        self.area.clear_widgets()

        target = GameButton(
            text="🎯",
            font_size=dp(30),
            size_hint=(None, None),
            size=(dp(70), dp(70)),
            background_color=RED
        )

        target.pos = (
            random.uniform(
                dp(5),
                max(dp(6), self.area.width - dp(75))
            ),
            random.uniform(
                dp(5),
                max(dp(6), self.area.height - dp(75))
            )
        )

        target.bind(on_release=self.hit)

        self.area.add_widget(target)

        self.target = target

    def hit(self, *_):

        if not self.running:
            return

        self.score += 1
        SAVE["coins"] += 2

        elapsed = int((time.time() - self.start_time) * 1000)

        self.info.text = (
            f"Попаданий: {self.score} | {elapsed} мс"
        )

        if self.score > SAVE["best"]["target"]:
            SAVE["best"]["target"] = self.score

        save_data(SAVE)

        if self.score >= 20:

            self.running = False
            self.area.clear_widgets()

            self.info.text = (
                f"🏆 ТИР ПРОЙДЕН!\n"
                f"Попаданий: {self.score}"
            )

        else:
            self.spawn()


# ============================================================
# CLICKER
# ============================================================

class ClickerScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🪙 КЛИКЕР")

        self.coins = 0
        self.power = 1
        self.cost = 50

        self.info = Label(
            text="",
            color=WHITE,
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(80),
            pos_hint={"top": 0.85}
        )

        self.root_layout.add_widget(self.info)

        click = GameButton(
            text="💰\nКЛИК",
            font_size=dp(30),
            size_hint=(0.7, 0.38),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        click.bind(on_release=self.click)

        self.root_layout.add_widget(click)

        upgrade = GameButton(
            text="⬆ УЛУЧШИТЬ",
            size_hint=(0.55, None),
            height=dp(55),
            pos_hint={"center_x": 0.5, "y": 0.17}
        )

        upgrade.bind(on_release=self.upgrade)

        self.root_layout.add_widget(upgrade)

        self.add_back_button()

        self.update()

    def click(self, *_):
        self.coins += self.power
        self.update()

    def upgrade(self, *_):

        if self.coins >= self.cost:

            self.coins -= self.cost
            self.power += 1

            self.cost = int(self.cost * 1.6)

            self.update()

    def update(self):

        self.info.text = (
            f"Монеты: {self.coins}\n"
            f"Сила клика: {self.power}\n"
            f"Цена улучшения: {self.cost}"
        )


# ============================================================
# MATH
# ============================================================

class MathScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_top_label(self.root_layout, "🧠 МАТЕМАТИКА")

        self.info = Label(
            text="",
            color=WHITE,
            font_size=dp(23),
            size_hint=(1, None),
            height=dp(80),
            pos_hint={"top": 0.85}
        )

        self.root_layout.add_widget(self.info)

        self.buttons = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint=(0.85, 0.4),
            pos_hint={"center_x": 0.5, "center_y": 0.48}
        )

        self.root_layout.add_widget(self.buttons)

        self.score = 0
        self.answer = 0

        self.add_back_button()

        self.new_question()

    def new_question(self):

        a = random.randint(1, 20)
        b = random.randint(1, 20)

        op = random.choice(["+", "-", "*"])

        if op == "+":
            self.answer = a + b

        elif op == "-":
            self.answer = a - b

        else:
            self.answer = a * b

        self.info.text = f"{a} {op} {b} = ?"

        answers = {self.answer}

        while len(answers) < 4:

            fake = self.answer + random.randint(-15, 15)

            if fake != self.answer:
                answers.add(fake)

        answers = list(answers)
        random.shuffle(answers)

        self.buttons.clear_widgets()

        for value in answers:

            b = GameButton(
                text=str(value),
                font_size=dp(24)
            )

            b.bind(
                on_release=lambda btn, v=value:
                self.answer_click(v)
            )

            self.buttons.add_widget(b)

    def answer_click(self, value):

        if value == self.answer:

            self.score += 1
            SAVE["coins"] += 3

            if self.score > SAVE["best"]["math"]:
                SAVE["best"]["math"] = self.score

            self.info.text = f"✅ Верно! Счёт: {self.score}"

            save_data(SAVE)

        else:

            self.score = 0
            self.info.text = "❌ Неверно!"

        Clock.schedule_once(
            lambda *_: self.new_question(),
            0.35
        )


# ============================================================
# APP
# ============================================================

class MiniGamesApp(App):

    def build(self):

        Window.clearcolor = BG

        self.sm = ScreenManager()

        self.sm.add_widget(
            MenuScreen(name="menu")
        )

        self.sm.add_widget(
            RedScreen(name="red")
        )

        self.sm.add_widget(
            ReactionScreen(name="reaction")
        )

        self.sm.add_widget(
            SnakeScreen(name="snake")
        )

        self.sm.add_widget(
            PongScreen(name="pong")
        )

        self.sm.add_widget(
            MinesScreen(name="mines")
        )

        self.sm.add_widget(
            Game2048Screen(name="2048")
        )

        self.sm.add_widget(
            TargetScreen(name="target")
        )

        self.sm.add_widget(
            ClickerScreen(name="clicker")
        )

        self.sm.add_widget(
            MathScreen(name="math")
        )

        self.sm.add_widget(
            StatsScreen(name="stats")
        )

        return self.sm


if __name__ == "__main__":
    MiniGamesApp().run()