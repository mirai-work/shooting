import pyxel
import random
import math

# --- 画面サイズ ---
W, H = 160, 120

# --- シーン定義 ---
SCENE_TITLE, SCENE_PLAY, SCENE_PAUSE, SCENE_BOSS = 0, 1, 2, 3
SCENE_GAMEOVER, SCENE_STAGE_CLEAR, SCENE_ENDING = 4, 5, 6

MAX_STAGE = 5
POWER_MAX = 4

class StarSoldier:
    def __init__(self):
        pyxel.init(W, H, title="STAR SHOTTER! EVO", fps=60)
        self.init_sound()  # 音楽・効果音の定義
        self.stage_colors = {
            1: (7, 0), 2: (12, 1), 3: (10, 5), 4: (8, 2), 5: (14, 0)
        }
        self.scene = SCENE_TITLE
        self.gameover_timer = 0
        self.reset_all()
        
        # タイトルBGM再生
        pyxel.playm(0, loop=True)
        
        pyxel.run(self.update, self.draw)

    def init_sound(self):
        # --- 効果音 (Sounds) ---
        # 0: ショット音 (高音・短め)
        pyxel.sounds[0].set("c3c3c2", "p", "3", "f", 5)
        # 1: 爆発音 (ノイズ)
        pyxel.sounds[1].set("c2g1c1", "n", "4", "f", 10)
        # 2: パワーアップ・決定音 (上昇音)
        pyxel.sounds[2].set("c3e3g3c4", "p", "3", "v", 15)
        
        # --- BGM用音色 (Musics) ---
        # 10-12: タイトルBGM (勇壮なメロディ)
        pyxel.sounds[10].set("a2c3e3a3 g2b2d3g3 f2a2c3f3 e2g2b2e3", "p", "5", "v", 20)
        pyxel.sounds[11].set("a1a1e1e1 g1g1d1d1 f1f1c1c1 e1e1b0b0", "t", "4", "v", 20)
        pyxel.musics[0].set([10], [11], [], [])

        # 20-22: メイン道中BGM (疾走感のあるアルペジオ)
        pyxel.sounds[20].set("a2e3a3e3 c3g3c4g3 a2e3a3e3 g2d3g3d3", "p", "4", "v", 10)
        pyxel.sounds[21].set("a1e2 a1e2 c1g2 c1g2 a1e2 a1e2 g1d2 g1d2", "t", "3", "v", 20)
        pyxel.sounds[22].set("c1g1 c1c1g1", "n", "2", "f", 10)
        pyxel.musics[1].set([20], [21], [22], [])

        # 30-32: ボスBGM (不気味な半音階)
        pyxel.sounds[30].set("c2c#2d2d#2 e2d#2d2c#2", "s", "6", "v", 15)
        pyxel.sounds[31].set("c1c1 c1c1", "t", "4", "v", 25)
        pyxel.musics[2].set([30], [31], [], [])

    def reset_all(self):
        self.stage = 1
        self.score = 0
        self.lives = 3
        self.reset_stage_env()
        self.respawn_player()
        self.stars = [[random.randint(0, W), random.randint(0, H), random.random()*1.2+0.3] for _ in range(60)]

    def reset_stage_env(self):
        self.frame = 0
        self.stage_timer = 0
        self.shots = []
        self.enemy_shots = []
        self.enemies = []
        self.capsules = []
        self.explosions = []
        self.ground_targets = []
        self.boss = None

    def respawn_player(self):
        self.x, self.y = 80, 100
        self.power = 1
        self.inv_timer = 90
        self.enemy_shots = []

    def update(self):
        # 背景スクロール
        for s in self.stars:
            s[1] += s[2]
            if s[1] > H: s[1], s[0] = 0, random.randint(0, W)

        if self.scene == SCENE_TITLE:
            self.update_play_logic() 
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.handle_start_button()
            return

        if self.scene == SCENE_GAMEOVER:
            self.gameover_timer += 1
            if self.gameover_timer > 180:
                self.scene = SCENE_TITLE
                self.reset_all()
                pyxel.playm(0, loop=True) # タイトルBGM
            return

        if self.scene == SCENE_STAGE_CLEAR:
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.next_stage()
            return

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
            self.handle_start_button()
            return

        if self.scene in (SCENE_PLAY, SCENE_BOSS):
            self.update_play()
            if self.scene == SCENE_BOSS: self.update_boss()

    def handle_start_button(self):
        if self.scene == SCENE_TITLE:
            pyxel.play(2, 2) # 決定音
            self.reset_all()
            self.scene = SCENE_PLAY
            pyxel.playm(1, loop=True) # 道中BGM
        elif self.scene == SCENE_PLAY: 
            self.scene = SCENE_PAUSE
            pyxel.stop() # 一時停止
        elif self.scene == SCENE_PAUSE: 
            self.scene = SCENE_PLAY
            pyxel.playm(1, loop=True) # 再開
        elif self.scene == SCENE_ENDING: 
            self.scene = SCENE_TITLE
            pyxel.playm(0, loop=True)

    def update_play_logic(self):
        self.frame += 1
        # タイトル画面なら強制的に1面のアルゴリズムを使用
        curr_stg = self.stage if self.scene != SCENE_TITLE else 1
        
        if self.frame % 100 == 0:
            self.ground_targets.append({"x": random.randint(20, W-20), "y": -15, "hp": 5})
            
        spawn_rate = max(10, 45 - curr_stg * 6)
        if self.frame % spawn_rate == 0:
            self.enemies.append({"x": random.randint(10, W-10), "y": -10, "type": random.choice(["sotta", "kappa", "calderon"]), "t": 0, "vx": 0, "vy": 0})
        
        self.update_entities()

    def update_play(self):
        self.stage_timer += 1
        if self.inv_timer > 0: self.inv_timer -= 1
        
        dx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
        dy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP))
        self.x = max(0, min(W-8, self.x + dx * 1.6))
        self.y = max(0, min(H-8, self.y + dy * 1.6))
        
        if any(pyxel.btnp(k, 0, 5) for k in [pyxel.KEY_Z, pyxel.KEY_X, pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B]):
            self.fire()
            pyxel.play(0, 0) # ショット音
            
        if self.scene == SCENE_PLAY:
            self.update_play_logic()
            if self.stage_timer > 1100 + self.stage * 100: self.init_boss()
        else:
            self.update_entities()

    def fire(self):
        p_patterns = {1: [0], 2: [-10, 10], 3: [-20, 0, 20], 4: [-15, -5, 5, 15]}
        for ang in p_patterns.get(self.power, [0]):
            self.shots.append([self.x+4, self.y, ang])

    def update_entities(self):
        for s in self.shots[:]:
            rad = math.radians(s[2]-90)
            s[0] += math.cos(rad)*6; s[1] += math.sin(rad)*6
            if not (-10 < s[1] < H+10 and -10 < s[0] < W+10):
                if s in self.shots: self.shots.remove(s)
                
        for g in self.ground_targets[:]:
            g["y"] += 0.5
            for s in self.shots[:]:
                if abs(g["x"]-s[0]) < 8 and abs(g["y"]-s[1]) < 8:
                    g["hp"] -= 1
                    if s in self.shots: self.shots.remove(s)
                    if g["hp"] <= 0:
                        self.score += 1000
                        pyxel.play(1, 1) # 爆発音
                        if g in self.ground_targets: self.ground_targets.remove(g)
                        self.explosions.append([g["x"], g["y"], 0])
                    break
            if g["y"] > H:
                if g in self.ground_targets: self.ground_targets.remove(g)
                
        # --- 敵のアルゴリズム ---
        for e in self.enemies[:]:
            e["t"] += 1
            if e["type"] == "sotta":
                e["y"] += 1.3
                target_x = self.x if self.scene != SCENE_TITLE else W//2
                e["x"] += (target_x - e["x"]) * 0.04
            elif e["type"] == "kappa":
                if e["t"] < 35: e["y"] += 2.8
                else:
                    if e["vx"] == 0: 
                        target_x = self.x if self.scene != SCENE_TITLE else W//2
                        e["vx"] = 2 if e["x"] < target_x else -2
                    e["x"] += e["vx"]; e["y"] += 0.5
            elif e["type"] == "calderon":
                e["y"] += 1.0
                if e["t"] % 45 == 0 and self.scene != SCENE_TITLE: self.shoot_at_player(e["x"], e["y"], 1.5 + (self.stage*0.1))
            
            for s in self.shots[:]:
                if abs(e["x"]-s[0]) < 6 and abs(e["y"]-s[1]) < 6:
                    self.score += 100; self.explosions.append([e["x"], e["y"], 0])
                    pyxel.play(1, 1) # 爆発音
                    if e in self.enemies: self.enemies.remove(e)
                    if s in self.shots: self.shots.remove(s)
                    if random.random() < 0.1: self.capsules.append({"x": e["x"], "y": e["y"]})
                    break
            
            if self.scene != SCENE_TITLE and self.inv_timer == 0:
                if abs(e["x"]-(self.x+4)) < 6 and abs(e["y"]-(self.y+4)) < 6: self.hit_player()
            if e["y"] > H:
                if e in self.enemies: self.enemies.remove(e)
                
        for s in self.enemy_shots[:]:
            if len(s) == 2: s[1] += 2.0
            else: s[0] += s[2]; s[1] += s[3]
            if self.scene != SCENE_TITLE and self.inv_timer == 0:
                if abs(s[0]-(self.x+4)) < 4 and abs(s[1]-(self.y+4)) < 4: self.hit_player()
            if not (-10 < s[1] < H+10):
                if s in self.enemy_shots: self.enemy_shots.remove(s)
                
        for c in self.capsules[:]:
            c["y"] += 0.8
            if self.scene != SCENE_TITLE and abs(c["x"]-(self.x+4)) < 8 and abs(c["y"]-(self.y+4)) < 8:
                self.power = min(POWER_MAX, self.power + 1); self.score += 500; self.capsules.remove(c)
                pyxel.play(2, 2) # パワーアップ音
            elif c["y"] > H: self.capsules.remove(c)
            
        for ex in self.explosions[:]:
            ex[2] += 1
            if ex[2] > 12: self.explosions.remove(ex)

    def shoot_at_player(self, ex, ey, speed):
        ang = math.atan2((self.y+4)-ey, (self.x+4)-ex)
        self.enemy_shots.append([ex, ey, math.cos(ang)*speed, math.sin(ang)*speed])

    def hit_player(self):
        self.lives -= 1
        pyxel.play(1, 1) # ミス時も爆発音
        self.explosions.append([self.x+4, self.y+4, 0])
        if self.lives <= 0: 
            self.scene = SCENE_GAMEOVER
            self.gameover_timer = 0
            pyxel.stop() # BGM停止
        else: self.respawn_player()

    def init_boss(self):
        self.scene = SCENE_BOSS
        self.enemies = []; self.ground_targets = []
        self.boss = {"x": 80, "y": -20, "hp": 60 + self.stage * 40, "t": 0}
        pyxel.playm(2, loop=True) # ボスBGM

    def update_boss(self):
        b = self.boss
        if not b: return
        b["t"] += 0.05
        b["y"] = min(25, b["y"] + 0.5)
        b["x"] = 80 + math.sin(b["t"]) * 40
        
        # ボス弾幕
        if self.stage == 1:
            if pyxel.frame_count % 25 == 0: self.enemy_shots.append([b["x"], b["y"]])
        elif self.stage == 2:
            if pyxel.frame_count % 20 == 0:
                for angle in [-10, 0, 10]: self.enemy_shots.append([b["x"] + angle, b["y"]])
        # ...（中略：他ステージも同様）
        elif self.stage >= 3:
             if pyxel.frame_count % 15 == 0: self.enemy_shots.append([b["x"], b["y"]])
                
        for s in self.shots[:]:
            if abs(s[0]-b["x"]) < 20 and abs(s[1]-b["y"]) < 15:
                b["hp"] -= 1
                if s in self.shots: self.shots.remove(s)
                self.score += 50
        if b["hp"] <= 0:
            self.score += 10000; self.scene = SCENE_STAGE_CLEAR; self.boss = None
            pyxel.play(2, 2) # クリア音
            pyxel.stop() # BGM停止

    def next_stage(self):
        if self.stage >= MAX_STAGE: 
            self.scene = SCENE_ENDING
            pyxel.playm(0, loop=True)
        else:
            self.stage += 1; self.scene = SCENE_PLAY
            self.reset_stage_env(); self.respawn_player()
            pyxel.playm(1, loop=True) # 道中BGM再開

    def draw(self):
        draw_stage = self.stage if self.scene != SCENE_TITLE else 1
        star_col, bg_col = self.stage_colors.get(draw_stage, (7, 0))
        pyxel.cls(bg_col)
        for s in self.stars: pyxel.pset(s[0], s[1], star_col if s[2] > 1.5 else 5)
        
        for g in self.ground_targets:
            pyxel.rectb(g["x"]-6, g["y"]-6, 12, 12, 13)
            pyxel.rect(g["x"]-2, g["y"]-2, 4, 4, 2 if g["hp"] > 2 else 8)

        for e in self.enemies:
            ex, ey = e["x"], e["y"]
            if e["type"] == "sotta":
                pyxel.circ(ex, ey, 3, 1); pyxel.circb(ex, ey, 3, 7); pyxel.pset(ex, ey, 8)
            elif e["type"] == "kappa":
                pyxel.tri(ex, ey+4, ex-4, ey-2, ex+4, ey-2, 12); pyxel.line(ex, ey-2, ex, ey+4, 7)
            else:
                pyxel.rect(ex-3, ey-3, 6, 6, 13); pyxel.rectb(ex-3, ey-3, 6, 6, 7); pyxel.pset(ex, ey, 9)

        for s in self.shots: pyxel.rect(s[0], s[1], 1, 3, 10)
        for s in self.enemy_shots: pyxel.circ(s[0], s[1], 1.5, 8)
        for c in self.capsules: pyxel.circ(c["x"], c["y"], 3, 14); pyxel.text(c["x"]-2, c["y"]-2, "P", 7)
        for ex in self.explosions: pyxel.circb(ex[0], ex[1], ex[2], 7)

        # 自機
        if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_STAGE_CLEAR, SCENE_ENDING):
            if self.inv_timer % 4 < 2:
                pyxel.rect(self.x+2, self.y+1, 4, 6, 7) 
                pyxel.rect(self.x+3, self.y+3, 2, 2, 12)
                pyxel.tri(self.x, self.y+7, self.x+2, self.y+4, self.x+2, self.y+7, 13)
                pyxel.tri(self.x+8, self.y+7, self.x+6, self.y+4, self.x+6, self.y+7, 13)
                pyxel.pset(self.x+3, self.y+7, 8); pyxel.pset(self.x+4, self.y+7, 8)

        # ボス
        if self.boss and self.scene != SCENE_TITLE:
            bx, by = self.boss["x"], self.boss["y"]
            pyxel.rect(bx-25, by-15, 50, 30, 13); pyxel.rectb(bx-25, by-15, 50, 30, 7)
            pyxel.rect(bx-22, by-10, 8, 20, 9); pyxel.rectb(bx-22, by-10, 8, 20, 10)
            pyxel.rect(bx+14, by-10, 8, 20, 9); pyxel.rectb(bx+14, by-10, 8, 20, 10)
            pyxel.circ(bx, by, 7, 8); pyxel.circb(bx, by, 8, 12)
            stage_letters = {1:"A", 2:"B", 3:"C", 4:"D", 5:"E"}
            pyxel.text(bx-3, by-2, stage_letters.get(self.stage, "X"), 7)

        if self.scene == SCENE_TITLE:
            pyxel.text(55, 50, "STAR SHOTTER!", pyxel.frame_count % 16)
            pyxel.text(40, 70, "PRESS START/RETURN", 7)
            pyxel.text(46, 95, "(C)MIRAI WORK/M.T", 7)
        elif self.scene == SCENE_GAMEOVER:
            pyxel.text(60, 50, "GAME OVER", 8); pyxel.text(45, 70, f"SCORE {self.score}", 7)
        elif self.scene == SCENE_STAGE_CLEAR:
            pyxel.text(45, 50, f"STAGE {self.stage} CLEAR", 11); pyxel.text(40, 70, "PRESS START", 7)
        elif self.scene == SCENE_ENDING:
            pyxel.text(50, 40, "CONGRATULATIONS", 10); pyxel.text(40, 60, "YOU SAVED THE STAR", 7); pyxel.text(30, 90, "PRESS START/RETURN", 7); pyxel.text(20, 110, "(C)MIRAI WORK/M.T", 7)
        
        if self.scene != SCENE_TITLE:
            pyxel.text(5, 5, f"ST:{self.stage} SC:{self.score} L:{self.lives} P:{self.power}", 7)
            if self.scene == SCENE_PAUSE: pyxel.text(70, 60, "PAUSE", 7)

StarSoldier()
