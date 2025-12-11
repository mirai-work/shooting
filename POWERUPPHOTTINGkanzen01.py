# complete_hyper_shooter_v6_ui_cleaned.py

import pyxel
import random
import math

# --- 定数 ---
SCREEN_W = 160
SCREEN_H = 120
PLAYER_BULLET_W = 6
PLAYER_BULLET_H = 2

# UIエリア設定
UI_HEIGHT = 16
UI_Y_START = SCREEN_H - UI_HEIGHT
TOP_UI_HEIGHT = 20
PLAYABLE_AREA_TOP = TOP_UI_HEIGHT
PLAYABLE_AREA_BOTTOM = UI_Y_START
PLAYABLE_H_EFFECTIVE = PLAYABLE_AREA_BOTTOM - PLAYABLE_AREA_TOP

# グラフィック/ゲームプレイ関連
LIFE_ICON_SIZE = 6  # ハートアイコンのサイズ
POWER_UP_NAMES = ["SPEED", "MSL", "DUAL", "LASER", "OPTION", "SHIELD"]
METER_ITEM_WIDTH = 25
MAX_POWER_LEVEL = 3
OPTION_DISTANCE = 14

# ボスHPゲージの位置
HP_BAR_W = 50 
BOSS_LABEL_X = 95
BOSS_HP_X = 90
BOSS_HP_Y = 10 

# UI表示位置 
SCORE_Y = 2    # SCORE/LIFE/STAGE/BOSS HP ラベル (上段)
LIFE_Y = 10    # スコア値/ライフハート/ステージ番号/HPゲージ (下段)
STAGE_Y = 2 
LOOP_Y = 10
# CAPSULE_REQUIRED_Y = UI_Y_START + 6  # 削除対象

# スコア定数 
SCORE_FIGHTER = 10
SCORE_WAVER = 30
SCORE_TURRET = 50
SCORE_BOSS = 500

# ステージ情報
STAGE_BG = [0, 1, 5, 6, 3, 2]
STAGE_DURATION = 600
BOSS_APPEARANCE_TIME = 600
STAGE_CLEAR_WAIT = 60
END_CREDIT_TIME = 180


# -------------------- 爆発エフェクト (Explosion) --------------------
class Explosion:
    def __init__(self, x, y, size_mult=1):
        self.particles = []
        num_particles = int(20 * size_mult)
        for _ in range(num_particles):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(1, 3) * size_mult * 0.5
            self.particles.append({
                'x': float(x),
                'y': float(y),
                'dx': math.cos(angle)*speed,
                'dy': math.sin(angle)*speed,
                'color': random.randint(8,11),
                'life': random.randint(15,30)
            })
        self.active = True

    def update(self):
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life']>0]
        if not self.particles:
            self.active = False

    def draw(self):
        for p in self.particles:
            pyxel.pset(int(p['x']), int(p['y']), p['color'])


# -------------------- 弾 (Bullet) --------------------
class Bullet:
    def __init__(self, x, y, type="NORMAL", dx=2, dy=0, color=7, is_player=False):
        self.x = float(x)
        self.y = float(y)
        self.type = type
        self.dx = float(dx)
        self.dy = float(dy)

        if not is_player:
            self.color = 9  # オレンジ (ボス/敵弾)
            self.size = 2
        else:
            self.color = color
            self.size = 1

        self.active = True
        self.is_player = is_player
        self.is_piercing = (type == "LASER")

    def update(self):
        if self.type == "MSL": 
            self.dy = min(self.dy + 0.15, 3)

        self.x += self.dx
        self.y += self.dy

        if self.x < -10 or self.x > SCREEN_W + 10 or self.y < -10 or self.y > SCREEN_H + 10:
            self.active = False

    def draw(self):
        xi = int(self.x)
        yi = int(self.y)
        if self.is_player:
            if self.type == "MSL": 
                pyxel.rect(xi, yi - 1, 4, 3, 8)
                pyxel.pset(xi + 4, yi + 1, 10)
            elif self.type == "LASER":
                laser_length = 30
                pyxel.line(xi, yi - 1, xi + laser_length, yi - 1, 14)
                pyxel.line(xi, yi, xi + laser_length, yi, 12)
                pyxel.line(xi, yi + 1, xi + laser_length, yi + 1, 14)
            elif self.type == "NORMAL" or self.type == "DUAL": 
                pyxel.rect(xi, yi - 1, 6, 3, self.color)
                pyxel.pset(xi + 5, yi, 7)
        else:
            pyxel.circ(xi, yi, int(self.size), self.color)


# -------------------- パワーアップカプセル (PowerUp) --------------------
class PowerUp:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.active = True
        self.anim = 0

    def update(self):
        self.x -= 1
        self.anim = (self.anim + 1) % 10
        if self.x < -5:
            self.active = False

    def draw(self):
        x = int(self.x)
        y = int(self.y)
        color_bright = 10 if self.anim < 5 else 9
        color_dark = 8 if self.anim < 5 else 7

        pyxel.rect(x - 3, y - 3, 6, 6, color_dark)
        pyxel.rect(x - 2, y - 2, 4, 4, color_bright)
        pyxel.pset(x, y, 7)


# -------------------- プレイヤー (Player) --------------------
class Player:
    SIZE = 8
    SHIP_COLOR = 12

    def __init__(self):
        self.x = 20.0
        self.y = PLAYABLE_AREA_TOP + PLAYABLE_H_EFFECTIVE//2
        self.life = 3
        self.bullets = []
        self.anim = 0
        self.exhaust = []

        self.meter_index = -1
        self.power_levels = {
            "SPEED": 0, "MSL": 0, "DUAL": 0,
            "LASER": 0, "OPTION": 0, "SHIELD": 0
        }
        self.options = []
        self.shot_cooldown = 0

    def update(self):
        self.anim = (self.anim + 1) % 20
        self.shot_cooldown = max(0, self.shot_cooldown - 1)

        base_speed = 1.0 + self.power_levels["SPEED"] * 0.5
        dx, dy = 0.0, 0.0
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP): dy = -base_speed
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): dy = base_speed
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): dx = -base_speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): dx = base_speed

        self.x = max(Player.SIZE, min(SCREEN_W - Player.SIZE, self.x + dx))

        min_y = PLAYABLE_AREA_TOP + Player.SIZE
        max_y = PLAYABLE_AREA_BOTTOM - Player.SIZE
        self.y = max(min_y, min(max_y, self.y + dy))

        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)) and self.meter_index != -1:
            self.activate_power_up(self.meter_index)
            self.meter_index = -1
            try:
                pyxel.play(0, 5)
            except Exception:
                pass

        if (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_Y)) and self.shot_cooldown == 0:
            self.fire_shots()

        self.update_options()
        for b in self.bullets: b.update()
        self.bullets = [b for b in self.bullets if b.active]

        self.exhaust.append({'x': self.x-8, 'y': self.y, 'life': 8})
        for e in self.exhaust:
            e['x'] -= 1 + random.uniform(0, 0.5)
            e['y'] += random.uniform(-0.5, 0.5)
            e['life'] -= 1
        self.exhaust = [e for e in self.exhaust if e['life']>0]

    def acquire_capsule(self):
        if self.meter_index == -1:
            self.meter_index = 0
        else:
            self.meter_index = (self.meter_index + 1) % len(POWER_UP_NAMES)
            
        try:
            pyxel.play(0, 1)
        except Exception:
            pass

    def update_options(self):
        current_options = self.power_levels["OPTION"]

        if len(self.options) < current_options:
            new_option_x = self.x - OPTION_DISTANCE * (len(self.options) + 1)
            self.options.append((float(new_option_x), float(self.y)))
        elif len(self.options) > current_options:
            self.options = self.options[:current_options]

        if self.options:
            positions = [(self.x - OPTION_DISTANCE, self.y)] + self.options[:-1]

            new_options = []
            for i, (ox, oy) in enumerate(self.options):
                target_x, target_y = positions[i]
                ox += (target_x - ox) * 0.2
                oy += (target_y - oy) * 0.2
                new_options.append((ox, oy))
            self.options = new_options

    def fire_shots(self):
        if self.power_levels["LASER"] > 0 or self.power_levels["DUAL"] > 0:
            self.shot_cooldown = 10
        else:
            self.shot_cooldown = 5

        fire_points = [(self.x + 6, self.y)] + self.options

        for fx, fy in fire_points:
            if self.power_levels["MSL"] > 0: 
                self.bullets.append(Bullet(fx, fy, type="MSL", dx=3, dy=0, color=8, is_player=True))

            if self.power_levels["LASER"] > 0:
                self.bullets.append(Bullet(fx, fy, type="LASER", dx=4, color=10, is_player=True))
            elif self.power_levels["DUAL"] > 0:
                self.bullets.append(Bullet(fx, fy, type="DUAL", dx=4, dy=-1, color=11, is_player=True))
                self.bullets.append(Bullet(fx, fy, type="DUAL", dx=4, dy=1, color=11, is_player=True))
            else:
                self.bullets.append(Bullet(fx, fy, type="NORMAL", dx=4, color=11, is_player=True))
            
        try:
            pyxel.play(0, 0)
        except Exception:
            pass

    def activate_power_up(self, index):
        name = POWER_UP_NAMES[index]
        if name == "SPEED":
            if self.power_levels["SPEED"] < MAX_POWER_LEVEL:
                self.power_levels["SPEED"] += 1
        elif name == "MSL": 
            self.power_levels["MSL"] = 1
        elif name == "DUAL":
            self.power_levels["DUAL"] = 1
            self.power_levels["LASER"] = 0
        elif name == "LASER":
            self.power_levels["LASER"] = 1
            self.power_levels["DUAL"] = 0
        elif name == "OPTION":
            if self.power_levels["OPTION"] < 2:
                self.power_levels["OPTION"] += 1
        elif name == "SHIELD":
            self.power_levels["SHIELD"] = 3
            
    def draw_icon(self, x, y, size=8):
        xi = int(x)
        yi = int(y)
        scale = float(size) / Player.SIZE
        
        try:
            # 翼
            pyxel.tri(int(xi - 4*scale), int(yi - 2*scale), int(xi - 6*scale), int(yi - 5*scale),
                      int(xi - 2*scale), int(yi - 2*scale), 6)
            pyxel.tri(int(xi - 4*scale), int(yi + 2*scale), int(xi - 6*scale), int(yi + 5*scale),
                      int(xi - 2*scale), int(yi + 2*scale), 6)
        except Exception:
            pass 

        # ノズル
        pyxel.pset(int(xi - 5*scale), int(yi - 3*scale), 7)
        pyxel.pset(int(xi - 5*scale), int(yi + 3*scale), 7)

        # 本体
        pyxel.line(int(xi - 5*scale), int(yi), int(xi + 4*scale), int(yi), 7)
        pyxel.rect(int(xi - 6*scale), int(yi - 1*scale), int(9*scale), int(3*scale), 1)
        pyxel.rect(int(xi - 4*scale), int(yi - 1*scale), int(7*scale), int(3*scale), 12)

        # コックピット
        pyxel.pset(int(xi + 3*scale), int(yi + 1*scale), 8)
        pyxel.pset(int(xi + 5*scale), int(yi), 8)
        pyxel.line(int(xi + 4*scale), int(yi - 1*scale), int(xi + 5*scale), int(yi - 1*scale), 8)

    def draw(self):
        for e in self.exhaust:
            color = 8 if e['life']>5 else 10 if e['life']>2 else 9
            r = 1 + e['life'] * 0.1
            pyxel.circ(int(e['x']), int(e['y']), max(1,int(r)), color)

        x, y = self.x, self.y

        self.draw_icon(x, y)

        for ox, oy in self.options:
            self.draw_icon(ox, oy, size=4) 

        if self.power_levels["SHIELD"] > 0:
            color = 12 if pyxel.frame_count % 4 < 2 else 5
            pyxel.circb(int(self.x), int(self.y), Player.SIZE + 2, color)

        for b in self.bullets: b.draw()


# -------------------- 敵 (Enemy) --------------------
class Enemy:
    SIZE = 6
    def __init__(self, x, y, loop_count, stage, type="FIGHTER"):
        self.x = float(x)
        self.y = float(y)
        self.initial_y = float(y)
        self.type = type
        enemy_color_offset = stage % 5
        self.color = 8 + enemy_color_offset
        self.active = True
        self.wave_timer = 0
        self.shot_cooldown = 0

        if type == "FIGHTER":
            self.base_hp = 1
            self.score_value = SCORE_FIGHTER
            self.speed_multiplier = 1.0 + loop_count * 0.1
        elif type == "WAVER":
            self.base_hp = 1.5
            self.score_value = SCORE_WAVER
            self.speed_multiplier = 1.2 + loop_count * 0.1
        elif type == "TURRET":
            self.base_hp = 2
            self.score_value = SCORE_TURRET
            self.speed_multiplier = 0.5 + loop_count * 0.05

        self.hp = self.base_hp + loop_count * 0.5
        self.anim = 0

    def update(self, player_x, player_y):
        self.anim = (self.anim + 1) % 20
        self.wave_timer += 1
        self.shot_cooldown = max(0, self.shot_cooldown - 1)

        bullet_to_fire = None

        if self.type == "WAVER":
            self.x -= 1.2 * self.speed_multiplier
            self.y = self.initial_y + math.sin(self.wave_timer * 0.15) * 15
        elif self.type == "FIGHTER":
            self.x -= 1 * self.speed_multiplier
        elif self.type == "TURRET":
            self.x -= 0.5 * self.speed_multiplier
            if self.shot_cooldown == 0 and self.x < SCREEN_W - 30:
                bullet_to_fire = self.fire_to_player(player_x, player_y)
                self.shot_cooldown = 90

        if self.x < -Enemy.SIZE:
            self.active = False

        min_y = PLAYABLE_AREA_TOP + Enemy.SIZE
        max_y = PLAYABLE_AREA_BOTTOM - Enemy.SIZE
        self.y = max(min_y, min(max_y, self.y))

        return bullet_to_fire

    def fire_to_player(self, px, py):
        target_x = px - self.x
        target_y = py - self.y
        angle = math.atan2(target_y, target_x)

        speed = 1.5
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed

        return Bullet(self.x, self.y, dx=dx, dy=dy, color=9, is_player=False)

    def draw(self):
        x, y, r = int(self.x), int(self.y), 3

        if self.type == "TURRET":
            pyxel.rect(x - r, y - r, 2*r, 2*r, 13)
            pyxel.rect(x - r + 3, y - 1, 3, 3, 8)
            pyxel.circ(x, y, 1, 0)
        else:
            pyxel.rect(x - r, y - r, 2*r, 2*r, 6)
            pyxel.circ(x, y, 1, self.color)
            pyxel.rect(x + r - 1, y - 1, 3, 3, 1)
            if self.anim < 10:
                pyxel.line(x - r + 1, y, x + r - 1, y, 7)


# -------------------- ボス (Boss) --------------------
class Boss:
    SIZE = 30
    def __init__(self, stage, loop_count):
        self.x = float(SCREEN_W - 50)
        self.y = float(PLAYABLE_AREA_TOP + PLAYABLE_H_EFFECTIVE // 2 - Boss.SIZE // 2)
        self.stage = stage
        self.loop_count = loop_count
        self.color = STAGE_BG[stage % len(STAGE_BG)]
        
        self.base_hp = 30 + stage * 10
        self.hp = self.base_hp + loop_count * 20
        self.max_hp = self.hp
        
        self.bullets = []
        self.active = True
        self.timer = 0
        self.speed_multiplier = 1 + loop_count * 0.2
        self.score_value = SCORE_BOSS

    def update(self):
        self.timer += 1

        target_y = PLAYABLE_AREA_TOP + PLAYABLE_H_EFFECTIVE // 2 - Boss.SIZE // 2 + math.sin(self.timer * 0.05) * (PLAYABLE_H_EFFECTIVE / 2 - Boss.SIZE)
        self.y += (target_y - self.y) * 0.1

        min_boss_y = PLAYABLE_AREA_TOP + 5
        max_boss_y = PLAYABLE_AREA_BOTTOM - Boss.SIZE - 5
        self.y = max(min_boss_y, min(max_boss_y, self.y))

        bullet_color = 9

        if self.timer % 30 == 0:
            self.bullets.append(Bullet(self.x, self.y + 12, dx=-2 * self.speed_multiplier, dy=0, color=bullet_color, is_player=False))

        if self.stage % 2 != 0 and self.timer % 60 == 0:
            for dy in [-1, 0, 1]:
                self.bullets.append(Bullet(self.x, self.y + 12, dx=-2 * self.speed_multiplier, dy=dy * self.speed_multiplier, color=bullet_color, is_player=False))
        elif self.stage % 2 == 0 and self.timer % 45 == 0:
            self.bullets.append(Bullet(self.x, self.y + 12, dx=-1 * self.speed_multiplier, dy=0.5, color=bullet_color, is_player=False))

        for b in self.bullets: b.update()
        self.bullets = [b for b in self.bullets if b.active]

    def draw(self):
        main_color = 1
        secondary_color = 6
        core_color = 10 if pyxel.frame_count % 8 < 4 else 8

        x, y, size = int(self.x), int(self.y), Boss.SIZE
        body_y = y + size // 2

        pyxel.rect(x - 5, body_y - 10, size + 10, 20, secondary_color)
        pyxel.rectb(x - 5, body_y - 10, size + 10, 20, 7)

        pyxel.rect(int(x + size * 0.2), body_y - 8, int(size * 0.6), 16, main_color)

        pyxel.line(int(x + size * 0.5), body_y - 10, int(x + size * 0.5), body_y + 10, 7)
        pyxel.line(x + 5, body_y - 8, x + 5, body_y + 8, 7)
        pyxel.line(x + 25, body_y - 8, x + 25, body_y + 8, 7)

        pyxel.rect(x + size + 5, body_y - 4, 3, 8, self.color)
        pyxel.rect(x + size + 8, body_y - 3, 2, 6, 7)

        core_x = x + size * 0.5 + 5
        core_y = body_y
        pyxel.circ(int(core_x), int(core_y), 5, core_color)
        pyxel.circb(int(core_x), int(core_y), 6, 8)

        for b in self.bullets: b.draw()


# -------------------- アプリ (App) --------------------
class App:
    MAX_STAGE = 5

    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="HYPER SHOOTER 2025")
        
        self.loop_count = 0
        self.mode = "TITLE"
        
        self.reset_game_state()

        self.stars_far = [(random.randint(0, SCREEN_W), random.randint(PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM), random.randint(5, 7)) for _ in range(70)]
        self.stars_mid = [(random.randint(0, SCREEN_W), random.randint(PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM), random.randint(9, 11)) for _ in range(50)]
        self.stars_near = [(random.randint(0, SCREEN_W), random.randint(PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM), random.randint(12, 14)) for _ in range(30)]

        self.title_timer = 0
        self.title_ship_x = -40
        self.title_exhaust = []
        
        pyxel.run(self.update, self.draw)

    def reset_game_state(self):
        self.player = Player()  
        self.enemies = []
        self.items = []
        self.boss = None
        self.stage = 0
        self.stage_timer = 0
        self.score = 0
        self.explosions = []
        self.is_clearing = False
        self.clear_timer = 0
        self.foreign_bullets = []  
        if self.mode != "TITLE":
            self.mode = "GAME"

    def advance_stage(self):
        if self.stage < App.MAX_STAGE - 1:
            self.stage += 1
            self.stage_timer = 0
            self.boss = None
            self.is_clearing = False
        else:
            self.mode = "ENDING"
            self.clear_timer = 0

    def restart_loop(self):
        self.loop_count += 1
        self.stage = 0
        self.stage_timer = 0
        self.boss = None
        self.enemies = []
        self.items = []
        self.player = Player()
        self.mode = "GAME"
        self.foreign_bullets = []
        try:
            pyxel.playm(1, loop=True)
        except Exception:
            pass

    def player_hit(self):
        if self.player.power_levels["SHIELD"] > 0:
            self.player.power_levels["SHIELD"] -= 1
            self.explosions.append(Explosion(self.player.x, self.player.y))
            try:
                pyxel.play(0, 2)
            except Exception:
                pass
            return

        self.player.life -= 1
        self.explosions.append(Explosion(self.player.x, self.player.y, size_mult=2))

        if self.player.life <= 0:
            self.mode = "GAMEOVER"
            try:
                pyxel.stop()
                pyxel.playm(2, loop=False)
            except Exception:
                pass
        else:
            # 死亡時パワーアップリセット (シールド以外)
            self.player.power_levels = {
                "SPEED": 0, "MSL": 0, "DUAL": 0, 
                "LASER": 0, "OPTION": 0, "SHIELD": 0
            }
            self.player.options = []
            self.player.meter_index = -1
            self.player.bullets = []
            try:
                pyxel.play(0, 3)
            except Exception:
                pass

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q): pyxel.quit()

        # 星のスクロール
        for i in range(len(self.stars_far)):
            x, y, col = self.stars_far[i]
            x = (x - 0.5) % SCREEN_W
            self.stars_far[i] = (x, y, col)
        for i in range(len(self.stars_mid)):
            x, y, col = self.stars_mid[i]
            x = (x - 1.5) % SCREEN_W
            self.stars_mid[i] = (x, y, col)
        for i in range(len(self.stars_near)):
            x, y, col = self.stars_near[i]
            x = (x - 3) % SCREEN_W
            self.stars_near[i] = (x, y, col)

        if self.mode == "TITLE":
            self.title_timer += 1
            self.title_ship_x += 2
            if pyxel.frame_count % 2 == 0:
                self.title_exhaust.append({'x': self.title_ship_x - 10, 'y': SCREEN_H//2 + 30, 'life': 8})
            for e in self.title_exhaust:
                e['x'] -= 2
                e['y'] += random.uniform(-0.5, 0.5)
                e['life'] -= 1
            self.title_exhaust = [e for e in self.title_exhaust if e['life']>0]
            if self.title_ship_x > SCREEN_W + 40:
                self.title_ship_x = -40
                self.title_exhaust = []

            if self.title_timer > 300 or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.mode = "GAME"
                self.title_timer = 0
                self.title_exhaust = []
                try:
                    pyxel.playm(1, loop=True)
                except Exception:
                    pass
            return

        if self.mode == "GAMEOVER":
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.loop_count = 0
                self.reset_game_state()
                try:
                    pyxel.playm(1, loop=True)
                except Exception:
                    pass
            return

        if self.mode == "ENDING":
            self.clear_timer += 1
            if self.clear_timer >= END_CREDIT_TIME:
                self.restart_loop()
            return

        if self.is_clearing:
            self.clear_timer += 1
            if self.clear_timer == 1:
                try:
                    pyxel.stop()
                    pyxel.play(0, 4)
                    pyxel.playm(3, loop=False)
                except Exception:
                    pass

            if self.clear_timer >= STAGE_CLEAR_WAIT:
                self.advance_stage()
                if self.mode == "GAME":
                    try:
                        pyxel.playm(1, loop=True)
                    except Exception:
                        pass
            return

        # --- 通常ゲーム更新 ---
        self.player.update()
        self.stage_timer += 1

        # 敵の出現ロジック
        if self.stage_timer < BOSS_APPEARANCE_TIME and not self.boss:
            if self.stage_timer % 60 == 0:
                self.enemies.append(Enemy(SCREEN_W + 10, random.randint(PLAYABLE_AREA_TOP + 10, PLAYABLE_AREA_BOTTOM - 10), self.loop_count, self.stage, type="FIGHTER"))
            if self.stage_timer % 120 == 60:
                self.enemies.append(Enemy(SCREEN_W + 10, random.randint(PLAYABLE_AREA_TOP + 10, PLAYABLE_AREA_BOTTOM - 10), self.loop_count, self.stage, type="WAVER"))
            if self.stage_timer % 180 == 0:
                self.enemies.append(Enemy(SCREEN_W + 10, random.randint(PLAYABLE_AREA_TOP + 10, PLAYABLE_AREA_BOTTOM - 10), self.loop_count, self.stage, type="TURRET"))
        elif self.stage_timer >= BOSS_APPEARANCE_TIME and not self.boss:
            self.boss = Boss(self.stage, self.loop_count)

        # 敵の更新と衝突判定（自機弾 vs 敵）
        new_enemies = []
        new_boss_bullets = []
        for e in self.enemies:
            bullet_maybe = e.update(self.player.x, self.player.y)
            if bullet_maybe:
                new_boss_bullets.append(bullet_maybe)

            hit = False
            for b in self.player.bullets:
                if (e.active and b.active and
                    b.x + PLAYER_BULLET_W >= e.x - Enemy.SIZE//2 and b.x <= e.x + Enemy.SIZE//2 and
                    b.y + PLAYER_BULLET_H//2 >= e.y - Enemy.SIZE//2 and b.y - PLAYER_BULLET_H//2 <= e.y + Enemy.SIZE//2):
                    hit = True
                    if not b.is_piercing:
                        b.active = False

            if hit:
                e.hp -= 1
                if e.hp <= 0:
                    e.active=False
                    self.score += e.score_value
                    self.explosions.append(Explosion(e.x, e.y))
                    if random.random() < 0.2:
                        self.items.append(PowerUp(e.x, e.y))

            if e.active:
                new_enemies.append(e)
        self.enemies = new_enemies

        # 敵弾の管理
        if self.boss:
            self.boss.bullets.extend(new_boss_bullets)
        else:
            self.foreign_bullets.extend(new_boss_bullets)

        # アイテムの更新と取得
        for it in self.items:
            it.update()
            if abs(it.x - self.player.x) < 8 and abs(it.y - self.player.y) < 8:
                it.active = False
                self.player.acquire_capsule()
        self.items = [it for it in self.items if it.active]

        # 爆発エフェクトの更新
        for ex in self.explosions: ex.update()
        self.explosions = [ex for ex in self.explosions if ex.active]

        # ボスの更新と衝突判定（自機弾 vs ボス）
        if self.boss:
            self.boss.update()

            core_x = self.boss.x + self.boss.SIZE * 0.5 + 5
            core_y = self.boss.y + self.boss.SIZE // 2

            for b in self.player.bullets:
                if (b.active and
                    b.x + PLAYER_BULLET_W >= core_x - 5 and b.x <= core_x + 5 and
                    b.y + PLAYER_BULLET_H//2 >= core_y - 5 and b.y - PLAYER_BULLET_H//2 <= core_y + 5):

                    if not b.is_piercing:
                        b.active = False
                    
                    self.boss.hp -= 1
                    
                    if self.boss.hp <= 0:
                        self.boss.active = False
                        self.score += self.boss.score_value
                        self.explosions.append(Explosion(self.boss.x + self.boss.SIZE//2, self.boss.y + self.boss.SIZE//2, size_mult=3))
                        self.is_clearing = True
                        self.clear_timer = 0
                        
                        self.foreign_bullets.extend(self.boss.bullets)
                        self.boss.bullets = []
                        self.boss = None
                        break 

        # 衝突判定（自機 vs 敵）
        for e in self.enemies:
            if e.active and abs(e.x - self.player.x) < 8 and abs(e.y - self.player.y) < 8:
                self.player_hit()
                e.active = False

        # 衝突判定（自機 vs 敵弾/ボス弾）
        combined_bullets = []
        if self.boss:
            combined_bullets.extend(self.boss.bullets)
        combined_bullets.extend(self.foreign_bullets)

        new_combined = []
        for b in combined_bullets:
            b.update()
            if b.active and abs(b.x - self.player.x) < 7 and abs(b.y - self.player.y) < 7:
                b.active = False
                self.player_hit()
            if b.active:
                new_combined.append(b)

        # 敵弾リストの再分割
        if self.boss:
            boss_bullets = [b for b in new_combined if b.x > self.boss.x - 10]
            foreign = [b for b in new_combined if b.x <= self.boss.x - 10]
            self.boss.bullets = boss_bullets
            self.foreign_bullets = foreign
        else:
            self.foreign_bullets = new_combined

    def draw_heart(self, x, y, size=LIFE_ICON_SIZE, color=8):
        # 6x6のグリッドに合わせたハートを描画
        if size == 6:
            # 1行目 (y)
            pyxel.pset(x + 1, y, color)
            pyxel.pset(x + 3, y, color)
            
            # 2行目 (y+1)
            pyxel.line(x, y + 1, x + 4, y + 1, color)
            
            # 3行目 (y+2)
            pyxel.line(x, y + 2, x + 4, y + 2, color)
            
            # 4行目 (y+3)
            pyxel.line(x, y + 3, x + 3, y + 3, color)
            
            # 5行目 (y+4)
            pyxel.line(x + 1, y + 4, x + 2, y + 4, color)
            
            # 6行目 (y+5)
            pyxel.pset(x + 2, y + 5, color)


    def draw(self):
        if self.mode == "TITLE":
            pyxel.cls(0)
            
            for x, y, col in self.stars_far: pyxel.pset(int(x), int(y), col)
            for x, y, col in self.stars_mid: pyxel.pset(int(x), int(y), col)
            for x, y, col in self.stars_near: pyxel.pset(int(x), int(y), col)
            
            for e in self.title_exhaust:
                color = 8 if e['life']>5 else 10 if e['life']>2 else 9
                r = 1 + e['life'] * 0.1
                pyxel.circ(int(e['x']), int(e['y']), max(1,int(r)), color)
            
            title_text = "HYPER SHOOTER"
            title_len = len(title_text) * 4 # Pyxelのデフォルト文字幅は4px
            title_x = SCREEN_W//2 - title_len//2
            title_y = SCREEN_H//2 - 20
            
            shine_color = 10 if pyxel.frame_count % 10 < 5 else 11
            shadow_color = 9
            
            # 影と本体を重ねて描画
            pyxel.text(title_x + 1, title_y + 1, title_text, shadow_color)
            pyxel.text(title_x, title_y, title_text, shine_color)
            
            pyxel.text(SCREEN_W//2 - 36, SCREEN_H//2 + 10, "PRESS SPACE OR START", 7)
            
            pyxel.text(SCREEN_W - 70, SCREEN_H - 10, "(C)M.Takahashi", 5)

            self.player.draw_icon(self.title_ship_x, SCREEN_H//2+30)
            
            return

        if self.mode == "GAMEOVER":
            pyxel.cls(0)
            pyxel.text(SCREEN_W//2 - 24, SCREEN_H//2 - 10, "GAME OVER", 8)
            pyxel.text(SCREEN_W//2 - 30, SCREEN_H//2 + 10, "PRESS R/START TO RESTART", 7)
            return

        if self.mode == "ENDING":
            pyxel.cls(0)
            
            credit_scroll_speed = 0.5 
            credit_y = SCREEN_H - int(self.clear_timer * credit_scroll_speed)
            
            pyxel.text(SCREEN_W//2 - 24, credit_y, "STAGE 5 CLEAR!", 11)
            pyxel.text(SCREEN_W//2 - 20, credit_y + 20, "GREAT JOB!", 7)
            pyxel.text(SCREEN_W//2 - 30, credit_y + 40, f"LOOP {self.loop_count + 1} COMPLETED", 13)
            
            pyxel.text(SCREEN_W//2 - 70, credit_y + 70, "PROGRAMMING & DESIGN", 10)
            pyxel.text(SCREEN_W//2 - 70, credit_y + 80, "M.Takahashi", 7)
            
            pyxel.text(SCREEN_W//2 - 70, credit_y + 100, "THANKS FOR PLAYING!", 12)

            if self.clear_timer > END_CREDIT_TIME - 60:
                pyxel.text(SCREEN_W//2 - 30, SCREEN_H//2 + 50, "PRESS SPACE TO TITLE", 10)
            
            return

        # --- GAME MODE DRAW ---
        bg_color = STAGE_BG[self.stage % len(STAGE_BG)]
        pyxel.cls(bg_color)

        # 背景の星を描画
        for x, y, col in self.stars_far:
            if PLAYABLE_AREA_TOP < y < PLAYABLE_AREA_BOTTOM: pyxel.pset(int(x), int(y), col)
        for x, y, col in self.stars_mid:
            if PLAYABLE_AREA_TOP < y < PLAYABLE_AREA_BOTTOM: pyxel.pset(int(x), int(y), col)
        for x, y, col in self.stars_near:
            if PLAYABLE_AREA_TOP < y < PLAYABLE_AREA_BOTTOM: pyxel.pset(int(x), int(y), col)

        # プレイエリア境界線
        pyxel.rectb(0, PLAYABLE_AREA_TOP, SCREEN_W, PLAYABLE_H_EFFECTIVE, 7)

        # ゲームオブジェクト描画
        for ex in self.explosions: ex.draw()
        for it in self.items: it.draw()
        for e in self.enemies: e.draw()

        if self.boss:
            for b in self.boss.bullets: b.draw()
        for b in self.foreign_bullets: b.draw()

        if self.boss: self.boss.draw()
        self.player.draw()

        # --- TOP UI描画 ---
        pyxel.rect(0, 0, SCREEN_W, TOP_UI_HEIGHT, 0)
        pyxel.line(0, TOP_UI_HEIGHT - 1, SCREEN_W, TOP_UI_HEIGHT - 1, 7)

        # 1. スコア (左端)
        pyxel.text(4, SCORE_Y, "SCORE", 7)
        score_text = f"{self.score:08}"
        pyxel.text(4, LIFE_Y, score_text, 11)

        # 2. ライフ表示 (左側 - スコアの右)
        life_label_x = 45 
        pyxel.text(life_label_x, SCORE_Y, "LIFE", 7)
        for i in range(self.player.life):
            life_x = life_label_x + 4 + i * (LIFE_ICON_SIZE)
            life_y = LIFE_Y - 1 
            self.draw_heart(life_x, life_y, size=LIFE_ICON_SIZE, color=8)
            
        # 3. ステージ情報 (右端) 
        
        if self.loop_count > 0:
            top_label = f"STAGE L:{self.loop_count + 1}"
        else:
            top_label = "STAGE"
            
        stage_label_x = SCREEN_W - 4 - len(top_label) * 4 
        pyxel.text(stage_label_x, STAGE_Y, top_label, 7)
        
        stage_text = f"{self.stage+1}"
        stage_val_x = SCREEN_W - 4 - len(stage_text) * 4 
        pyxel.text(stage_val_x, LOOP_Y, stage_text, 11) 

        # 4. ボスHPゲージ (右側 - ライフとステージの間)
        if self.boss:
            hp_ratio = self.boss.hp / self.boss.max_hp
            
            # BOSS HPのラベルを Y=2 に配置 (X=95)
            pyxel.text(BOSS_LABEL_X, SCORE_Y, "BOSS HP", 14) 
            
            # HPゲージを Y=10 に配置 (X=90)
            pyxel.rect(BOSS_HP_X, BOSS_HP_Y, HP_BAR_W, 3, 1)
            pyxel.rect(BOSS_HP_X, BOSS_HP_Y, int(HP_BAR_W * hp_ratio), 3, 8)
            pyxel.rectb(BOSS_HP_X, BOSS_HP_Y, HP_BAR_W, 3, 7)


        # --- BOTTOM UI (パワーアップゲージ) ---
        pyxel.rect(0, UI_Y_START, SCREEN_W, UI_HEIGHT, 0)
        pyxel.line(0, UI_Y_START, SCREEN_W, UI_Y_START, 7)

        pyxel.rect(2, UI_Y_START + 2, SCREEN_W - 4, UI_HEIGHT - 4, 1)
        pyxel.rectb(2, UI_Y_START + 2, SCREEN_W - 4, UI_HEIGHT - 4, 7)

        num_items = len(POWER_UP_NAMES)
        item_spacing = (SCREEN_W - 4) // num_items

        for i, name in enumerate(POWER_UP_NAMES):
            x_start = 2 + i * item_spacing

            name_color = 7
            level = self.player.power_levels.get(name, 0)
            
            if level > 0:
                 name_color = 10
            
            # パワーアップ名 (上段)
            pyxel.text(x_start + 2, UI_Y_START + 3, name, name_color)

            if i == self.player.meter_index:
                flash_color = 8 if pyxel.frame_count % 8 < 4 else 10
                pyxel.rectb(x_start, UI_Y_START + 2, item_spacing, UI_HEIGHT - 4, flash_color)
                # 選択中のアイテム名の色を強調
                pyxel.text(x_start + 2, UI_Y_START + 3, name, 13)

            # パワーアップレベル/ON表示 (下段)
            
            if name == "SPEED" or name == "OPTION":
                # 修正1: レベルが0より大きい場合のみ表示
                if level > 0:
                    level_text = f"LV{level}"
                    pyxel.text(x_start + 2, UI_Y_START + 10, level_text, 12)
            elif name == "SHIELD":
                # 修正2: HPが0より大きい場合のみ表示
                if level > 0:
                    level_text = f"HP{level}"
                    pyxel.text(x_start + 2, UI_Y_START + 10, level_text, 12)
            elif level > 0 and (name == "MSL" or name == "DUAL" or name == "LASER"):
                pyxel.text(x_start + 2, UI_Y_START + 10, "ON", 12)

        # 修正3: ゲージが非アクティブな場合の表示 (CAPSULE REQUIRED) を削除


App()