import pyxel
import random
import math

# --- 画面サイズ ---
W, H = 160, 120
SCENE_TITLE, SCENE_PLAY, SCENE_PAUSE, SCENE_BOSS = 0, 1, 2, 3
SCENE_GAMEOVER, SCENE_STAGE_CLEAR, SCENE_ENDING = 4, 5, 6
SCENE_TUTORIAL = 7 
MAX_STAGE = 5
POWER_MAX = 4

class StarSoldier:
    def __init__(self):
        pyxel.init(W, H, title="STAR SHOTTER! KAI", fps=60)
        self.init_sound()
        self.stage_colors = {
            1: (7, 1), 2: (12, 5), 3: (10, 1), 4: (8, 0), 5: (7, 0)
        }
        self.scene = SCENE_TITLE
        self.gameover_timer = 0
        self.clear_timer = 0 
        self.scroll_y = 0    
        self.reset_all()
        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def init_sound(self):
        # 効果音
        pyxel.sounds[0].set("g2g1", "p", "7", "f", 5)
        pyxel.sounds[1].set("c2c1c0", "n", "4", "f", 10)
        pyxel.sounds[2].set("c3e3g3c4", "p", "4", "v", 15)
        pyxel.sounds[3].set("g3c4g3c4", "p", "3", "v", 10)

        # --- Title BGM ---
        pyxel.sounds[10].set("c3e3g3c4e3g3c4e4", "p"*8, "6"*8, "n"*8, 20)
        pyxel.sounds[11].set("c2c2c2c2g1g1g1g1", "t"*8, "5"*8, "n"*8, 20)
        pyxel.musics[0].set([10], [11], [], [])

        # --- Stage BGM ---
        pyxel.sounds[20].set("a2a2e3e3d3d3c3c3", "p"*8, "6"*8, "n"*8, 15)
        pyxel.sounds[21].set("a1a1g1g1f1f1e1e1", "t"*8, "5"*8, "n"*8, 15)
        pyxel.musics[1].set([20], [21], [], [])

        # --- Boss BGM ---
        pyxel.sounds[30].set("c2d2e2f2g2f2e2d2", "s"*8, "6"*8, "n"*8, 12)
        pyxel.sounds[31].set("c1c1c1c1c1c1c1c1", "t"*8, "7"*8, "n"*8, 12)
        pyxel.musics[2].set([30], [31], [], [])

        # --- Game Over ---
        pyxel.sounds[40].set("e3c3g2e2c2g1e1c1", "p"*8, "6"*8, "n"*8, 40)
        pyxel.musics[3].set([40], [], [], [])
      
    def reset_all(self):
        self.stage = 1; self.score = 0; self.lives = 3
        self.kill_count = 0; self.barrier_hp = 0
        self.scene_timer = 0
        self.reset_stage_env()
        self.x, self.y = 80, 100
        self.respawn_player()
        self.stars = [[random.randint(0, W), random.randint(0, H), (random.random()*1.2+0.3)*0.6] for _ in range(60)]

    def reset_stage_env(self):
        self.frame = 0; self.stage_timer = 0; self.shots = []; self.enemy_shots = []
        self.enemies = []; self.capsules = []; self.explosions = []; self.ground_targets = []; self.boss = None

    def respawn_player(self):
        self.power = 1; self.inv_timer = 90; self.enemy_shots = []; self.barrier_hp = 0

    def check_any_button(self):
        for b in [pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B, pyxel.GAMEPAD1_BUTTON_X, pyxel.GAMEPAD1_BUTTON_Y]:
            if pyxel.btnp(b): return True
        return False

    def update(self):
        for s in self.stars:
            s[1] += s[2]
            if s[1] > H: s[1], s[0] = 0, random.randint(0, W)
        if not hasattr(self, 'scene_timer'): self.scene_timer = 0
        self.scene_timer += 1
        if self.scene == SCENE_TITLE:
            self.update_play_logic()
            if self.scene_timer > 840 or pyxel.btnp(pyxel.KEY_SPACE) or self.check_any_button():
                self.scene = SCENE_TUTORIAL; self.scene_timer = 0; pyxel.playm(1, loop=True)
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): 
                self.scene_timer = 0; self.handle_start_button()
        elif self.scene == SCENE_TUTORIAL:
            self.update_play_logic()
            if self.scene_timer > 420 or pyxel.btnp(pyxel.KEY_SPACE) or self.check_any_button():
                self.scene = SCENE_TITLE; self.scene_timer = 0; pyxel.playm(0, loop=True)
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): 
                self.scene_timer = 0; self.handle_start_button()
        elif self.scene == SCENE_GAMEOVER:
            self.update_entities()
            if self.boss: self.update_boss()
            if self.scene_timer > 480: 
                self.reset_all(); self.scene = SCENE_TITLE; pyxel.playm(0, loop=True)
        elif self.scene == SCENE_STAGE_CLEAR:
            self.clear_timer += 1
            if self.clear_timer > 120 or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.scene_timer = 0; self.next_stage()
        elif self.scene == SCENE_ENDING:
            self.scroll_y += 0.5 * 0.6
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.scene = SCENE_TITLE; self.scene_timer = 0; pyxel.playm(0, loop=True)
        elif self.scene in (SCENE_PLAY, SCENE_BOSS, SCENE_PAUSE):
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.handle_start_button(); self.scene_timer = 0
            if self.scene != SCENE_PAUSE:
                self.update_play()
                if self.scene == SCENE_BOSS: self.update_boss()

    def handle_start_button(self):
        if self.scene in (SCENE_TITLE, SCENE_TUTORIAL):
            pyxel.play(2, 2); self.reset_all(); self.scene = SCENE_PLAY; pyxel.playm(1, loop=True)
        elif self.scene == SCENE_PLAY: self.scene = SCENE_PAUSE; pyxel.stop()
        elif self.scene == SCENE_PAUSE: self.scene = SCENE_PLAY; pyxel.playm(1, loop=True)

    def update_play_logic(self):
        self.frame += 1
        curr_stg = self.stage if self.scene not in (SCENE_TITLE, SCENE_TUTORIAL) else 1
        if self.frame % 166 == 0: self.ground_targets.append({"x": random.randint(20, W-20), "y": -15, "hp": 5})
        spawn_rate = max(5, int((35 - curr_stg * 6) / 0.6))
        if self.frame % spawn_rate == 0:
            self.enemies.append({"x": random.randint(10, W-10), "y": -10, "type": random.choice(["sotta", "kappa", "calderon"]), "t": 0, "vx": 0, "vy": 0})
        self.update_entities()

    def update_play(self):
        self.stage_timer += 1
        if self.inv_timer > 0: self.inv_timer -= 1
        dx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
        dy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP))
        self.x = max(0, min(W-8, self.x + dx * 1.6 * 0.6))
        self.y = max(0, min(H-8, self.y + dy * 1.6 * 0.6))
        shot_interval = int((12 if self.power == 1 else 6) / 0.6)
        if any(pyxel.btn(k) for k in [pyxel.KEY_Z, pyxel.KEY_X, pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B]):
            if pyxel.frame_count % shot_interval == 0:
                self.fire(); pyxel.play(0, 0)
        if self.scene == SCENE_PLAY:
            self.update_play_logic()
            if self.stage_timer > (1100 + self.stage * 100) / 0.6: self.init_boss()
        else: self.update_entities()

    def fire(self):
        if self.power >= 4:
            for ang in [-10, 0, 10, 170, 190]: self.shots.append([self.x+4, self.y, ang])
        elif self.power == 3:
            for ang in [-10, 0, 10, 170, 190]: self.shots.append([self.x+4, self.y, ang])
        elif self.power == 2:
            for ang in [-5, 5, 180]: self.shots.append([self.x+4, self.y, ang])
        else:
            for ang in [-5, 5]: self.shots.append([self.x+4, self.y, ang])

    def update_entities(self):
        for s in self.shots[:]:
            rad = math.radians(s[2]-90)
            s[0] += math.cos(rad)*6*0.6; s[1] += math.sin(rad)*6*0.6
            if not (-10 < s[1] < H+10 and -10 < s[0] < W+10):
                if s in self.shots: self.shots.remove(s)
        
        for g in self.ground_targets[:]:
            g["y"] += 0.5 * 0.6
            for s in self.shots[:]:
                if abs(g["x"]-s[0]) < 8 and abs(g["y"]-s[1]) < 8:
                    g["hp"] -= 1
                    if s in self.shots: self.shots.remove(s)
                    if g["hp"] <= 0:
                        self.score += 1000; pyxel.play(1, 1)
                        if g in self.ground_targets: self.ground_targets.remove(g)
                        self.explosions.append([g["x"], g["y"], 0])
                    break
            if g["y"] > H:
                if g in self.ground_targets: self.ground_targets.remove(g)

        for e in self.enemies[:]:
            e["t"] += 1
            if e["type"] == "sotta":
                e["y"] += (1.5 + (self.stage * 0.1)) * 0.6
                target_x = self.x if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) else W//2
                e["x"] += (target_x - e["x"]) * 0.05 * 0.6
            elif e["type"] == "kappa":
                if e["t"] < 35 / 0.6: e["y"] += 3.0 * 0.6
                else:
                    if e["vx"] == 0: target_x = self.x if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) else W//2; e["vx"] = 2.5 * 0.6 if e["x"] < target_x else -2.5 * 0.6
                    e["x"] += e["vx"]; e["y"] += 0.6 * 0.6
            elif e["type"] == "calderon":
                e["y"] += 1.2 * 0.6
                if e["t"] % max(20, int((45 - self.stage*5) / 0.6)) == 0 and self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL): 
                    self.shoot_at_player(e["x"], e["y"], (1.8 + (self.stage*0.3)) * 0.6)
            for s in self.shots[:]:
                if abs(e["x"]-s[0]) < 6 and abs(e["y"]-s[1]) < 6:
                    self.score += 100; self.explosions.append([e["x"], e["y"], 0]); pyxel.play(1, 1)
                    if e in self.enemies: self.enemies.remove(e)
                    if s in self.shots: self.shots.remove(s)
                    self.kill_count += 1
                    if self.kill_count >= 10:
                        if random.random() > (self.stage * 0.18):
                            self.capsules.append({"x": e["x"], "y": e["y"], "type": "barrier"})
                        self.kill_count = 0
                    else:
                        rand_val = random.random()
                        drop_rate_factor = max(0.05, 0.8 - (self.stage * 0.15))
                        if rand_val < 0.04 * drop_rate_factor: self.capsules.append({"x": e["x"], "y": e["y"], "type": "1up"})
                        elif rand_val < 0.12 * drop_rate_factor: self.capsules.append({"x": e["x"], "y": e["y"], "type": "power"})
                    break
            if e in self.enemies and self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) and self.inv_timer == 0:
                if abs(e["x"]-(self.x+4)) < 6 and abs(e["y"]-(self.y+4)) < 6: self.hit_player()
            if e["y"] > H:
                if e in self.enemies: self.enemies.remove(e)

        for s in self.enemy_shots[:]:
            if len(s) == 2: s[1] += (2.2 + (self.stage * 0.1)) * 0.6
            else: s[0] += s[2]; s[1] += s[3]
            if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) and self.inv_timer == 0:
                if abs(s[0]-(self.x+4)) < 4 and abs(s[1]-(self.y+4)) < 4: 
                    self.hit_player()
                    if s in self.enemy_shots: self.enemy_shots.remove(s)
            if not (-20 < s[1] < H+20 and -20 < s[0] < W+20):
                if s in self.enemy_shots: self.enemy_shots.remove(s)

        for c in self.capsules[:]:
            c["y"] += 0.8 * 0.6
            if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_TUTORIAL) and abs(c["x"]-(self.x+4)) < 8 and abs(c["y"]-(self.y+4)) < 8:
                if c["type"] == "power":
                    if self.power >= POWER_MAX:
                        for e in self.enemies[:]:
                            self.score += 100; self.explosions.append([e["x"], e["y"], 0])
                            self.enemies.remove(e)
                        self.enemy_shots = []
                        if self.boss: self.boss["hp"] -= 20
                        pyxel.play(1, 1)
                    else:
                        self.power = min(POWER_MAX, self.power + 1)
                    self.score += 500; pyxel.play(2, 2)
                elif c["type"] == "barrier":
                    if self.barrier_hp > 0 or self.inv_timer > 0:
                        for e in self.enemies[:]:
                            self.score += 100; self.explosions.append([e["x"], e["y"], 0])
                            self.enemies.remove(e)
                        self.enemy_shots = []
                        if self.boss: self.boss["hp"] -= 20
                        pyxel.play(1, 1)
                    self.barrier_hp = 3; self.score += 500; pyxel.play(2, 2)
                elif c["type"] == "1up": self.lives += 1; self.score += 1000; pyxel.play(3, 1)
                self.capsules.remove(c)
            elif c["y"] > H: self.capsules.remove(c)

        for ex in self.explosions[:]:
            ex[2] += 1
            if ex[2] > 12: self.explosions.remove(ex)

    def shoot_at_player(self, ex, ey, speed):
        ang = math.atan2((self.y+4)-ey, (self.x+4)-ex); self.enemy_shots.append([ex, ey, math.cos(ang)*speed, math.sin(ang)*speed])

    def hit_player(self):
        if self.barrier_hp > 0:
            self.barrier_hp -= 1; pyxel.play(3, 0); self.inv_timer = 30; return
        self.lives -= 1; pyxel.play(1, 1); self.explosions.append([self.x+4, self.y+4, 0])
        if self.lives <= 0: self.scene = SCENE_GAMEOVER; self.scene_timer = 0; pyxel.playm(3, loop=False)
        else: self.respawn_player()

    def init_boss(self):
        self.scene = SCENE_BOSS; self.enemies = []; self.ground_targets = []
        self.boss = {"x": 80, "y": -20, "hp": 100 + self.stage * 60, "t": 0}; pyxel.playm(2, loop=True)

    def update_boss(self):
        b = self.boss
        if not b: return
        b["t"] += 0.05 * 0.6; b["y"] = min(25, b["y"] + 0.5 * 0.6)
        if self.stage == 1: b["x"] = 80 + math.sin(b["t"]) * 40
        elif self.stage == 2: b["x"] = 80 + math.cos(b["t"] * 1.2) * 60; b["y"] = 25 + math.sin(b["t"] * 2.0) * 10
        elif self.stage == 3: b["x"] = 80 + math.sin(b["t"]) * 60; b["y"] = 25 + math.sin(b["t"] * 2) * 15
        elif self.stage == 4:
            b["x"] = 80 + math.sin(b["t"] * 0.5) * 70
            if int(b["t"]) % 2 == 0: b["x"] += math.sin(b["t"] * 10) * 5
        else: b["x"] = 80 + math.cos(b["t"] * 1.5) * 50; b["y"] = 30 + math.sin(b["t"] * 1.5) * 20
        if self.scene != SCENE_GAMEOVER:
            shot_interval = max(3, int((22 - self.stage * 4) / 0.6))
            if pyxel.frame_count % shot_interval == 0:
                if self.stage >= 2 and random.random() < (0.2 + self.stage * 0.15):
                    self.shoot_at_player(b["x"], b["y"], (2.0 + (self.stage * 0.35)) * 0.6)
                else: self.enemy_shots.append([b["x"], b["y"]])
                if self.stage >= 3 and pyxel.frame_count % (shot_interval * 3) == 0:
                    for a in [-45, -20, 20, 45]:
                        rad = math.radians(90 + a); self.enemy_shots.append([b["x"], b["y"], math.cos(rad)*2.2*0.6, math.sin(rad)*2.2*0.6])
        for s in self.shots[:]:
            if abs(s[0]-b["x"]) < 20 and abs(s[1]-b["y"]) < 15:
                b["hp"] -= 1; self.score += 50
                if s in self.shots: self.shots.remove(s)
        if b["hp"] <= 0:
            self.score += 10000; self.scene = SCENE_STAGE_CLEAR; self.clear_timer = 0; self.boss = None; pyxel.play(2, 2); pyxel.stop()

    def next_stage(self):
        if self.stage >= MAX_STAGE: self.scene = SCENE_ENDING; self.scroll_y = 0; pyxel.playm(0, loop=True)
        else: 
            p, b, s, l = self.power, self.barrier_hp, self.score, self.lives
            self.stage += 1; self.scene = SCENE_PLAY; self.reset_stage_env()
            self.x, self.y = 80, 100; self.inv_timer = 90
            self.power, self.barrier_hp, self.score, self.lives = p, b, s, l
            pyxel.playm(1, loop=True)

    def draw(self):
        draw_stage = self.stage if self.scene not in (SCENE_TITLE, SCENE_ENDING, SCENE_TUTORIAL) else 1
        star_col, bg_col = self.stage_colors.get(draw_stage, (7, 1))
        pyxel.cls(bg_col)
        for s in self.stars:
            col = star_col if s[2] > (0.8 * 0.6) else 13
            pyxel.pset(s[0], s[1], col)
        if self.scene == SCENE_ENDING: self.draw_ending(); return
        for g in self.ground_targets:
            gx, gy = g["x"], g["y"]
            pyxel.rect(gx-7, gy-7, 14, 14, 13); pyxel.rectb(gx-7, gy-7, 14, 14, 7)
            for dx, dy in [(-5,-5), (5,-5), (-5,5), (5,5)]: pyxel.pset(gx+dx, gy+dy, 7)
            pyxel.circ(gx, gy, 4, 1); pyxel.circb(gx, gy, 4, 7)
            core_col = 8 if pyxel.frame_count % 10 < 5 else 2
            pyxel.pset(gx, gy, core_col)
        for e in self.enemies:
            ex, ey = e["x"], e["y"]
            if e["type"] == "sotta":
                rot = (pyxel.frame_count // 2) % 4
                pyxel.circ(ex, ey, 3, 1); pyxel.circb(ex, ey, 3, 12)
                pyxel.pset(ex + math.cos(rot)*2, ey + math.sin(rot)*2, 7)
            elif e["type"] == "kappa":
                pyxel.tri(ex, ey+4, ex-5, ey-2, ex+5, ey-2, 12)
                pyxel.line(ex, ey-2, ex, ey+4, 7); pyxel.pset(ex, ey+1, 8)
            else: 
                pyxel.rect(ex-4, ey-4, 8, 8, 13); pyxel.rectb(ex-4, ey-4, 8, 8, 7)
                pyxel.line(ex-4, ey, ex+3, ey, 5); pyxel.line(ex, ey-4, ex, ey+3, 5)
                for dx, dy in [(-3,-3), (2,-3), (-3,2), (2,2)]: pyxel.pset(ex+dx, ey+dy, 7)
                pyxel.pset(ex, ey, 9)
        for s in self.shots: pyxel.rect(s[0], s[1], 1, 4, 10)
        for s in self.enemy_shots: pyxel.circ(s[0], s[1], 1, 8)
        for c in self.capsules:
            if c["type"] == "barrier":
                col = 12 if pyxel.frame_count % 4 < 2 else 6
                pyxel.circ(c["x"], c["y"], 4, col); pyxel.circb(c["x"], c["y"], 4, 7); pyxel.text(c["x"]-1, c["y"]-2, "B", 7)
            else:
                col_main = 8 if pyxel.frame_count % 4 < 2 else 10
                if c["type"] == "1up": col_main = 3 if pyxel.frame_count % 4 < 2 else 11
                pyxel.circ(c["x"], c["y"], 4, col_main); pyxel.circb(c["x"], c["y"], 4, 7)
                item_char = "P" if c["type"] == "power" else "1U"
                pyxel.text(c["x"]-1 if c["type"]=="power" else c["x"]-3, c["y"]-2, item_char, 7)
        for ex in self.explosions:
            pyxel.circb(ex[0], ex[1], ex[2], 7)
            if ex[2] < 6: pyxel.circ(ex[0], ex[1], ex[2]//2, 10)
        if self.scene not in (SCENE_TITLE, SCENE_GAMEOVER, SCENE_STAGE_CLEAR, SCENE_ENDING, SCENE_TUTORIAL):
            if self.inv_timer == 0 or (pyxel.frame_count % 2 == 0):
                pyxel.rect(self.x+3, self.y, 2, 8, 8); pyxel.tri(self.x, self.y+7, self.x+3, self.y+2, self.x+3, self.y+7, 7)
                pyxel.tri(self.x+8, self.y+7, self.x+5, self.y+2, self.x+5, self.y+7, 7); pyxel.pset(self.x+3, self.y+7, 12); pyxel.pset(self.x+4, self.y+7, 12)
                if self.barrier_hp > 0:
                    b_col = 12 if self.barrier_hp > 1 else 6 
                    pyxel.circb(self.x+4, self.y+4, 10, b_col if pyxel.frame_count % 2 == 0 else 7)
        if self.boss and (self.scene != SCENE_TITLE and self.scene != SCENE_TUTORIAL):
            bx, by = self.boss["x"], self.boss["y"]
            pyxel.rect(bx-16, by-14, 32, 28, 13); pyxel.rectb(bx-16, by-14, 32, 28, 7) 
            for side in [-1, 1]:
                ax = bx + side * 24; pyxel.rect(ax-8, by-16, 16, 32, 13); pyxel.rectb(ax-8, by-16, 16, 32, 7)
                pyxel.line(ax-8, by, ax+7, by, 5); pyxel.rect(bx + side*16, by-4, 8, 8, 5)
            pyxel.circ(bx, by, 10, 1); pyxel.circb(bx, by, 10, 7)
            letter = chr(ord('A') + self.stage - 1); core_col = 8 if pyxel.frame_count % 20 < 10 else 7
            pyxel.text(bx-1, by-2, letter, core_col)
            for dx, dy in [(-12,-10), (12,-10), (-12,10), (12,10)]: pyxel.pset(bx+dx, by+dy, 7)
            pyxel.line(bx-16, by-7, bx+15, by-7, 5); pyxel.line(bx-16, by+7, bx+15, by+7, 5)
        
        # --- 文字情報表示の修正 ---
        if self.scene == SCENE_TITLE:
            pyxel.text(50, 40, "STAR SHOTTER! KAI", pyxel.frame_count % 16)
            pyxel.text(36, 60, "PRESS START/ENTER BUTTON", 7); pyxel.text(20, 80, "PUSH ANY/SPACE KEY: HOW TO PLAY", 10 if pyxel.frame_count % 20 < 10 else 7)
            pyxel.text(46, 105, "(C)MIRAI WORK / M.T", 7)
        elif self.scene == SCENE_TUTORIAL:
            pyxel.rect(20, 20, 120, 80, 1); pyxel.rectb(20, 20, 120, 80, 7)
            pyxel.text(55, 30, "- HOW TO PLAY -", 10); pyxel.text(35, 45, "ARROW: MOVE", 7); pyxel.text(35, 55, "Z/X/A/B: FIRE", 7)
            pyxel.text(35, 70, "P: POWER UP / B: BARRIER", 12); pyxel.text(35, 80, "1U: 1UP (EXTRA LIFE)", 11); pyxel.text(26, 92, "ANY/SPACE KEY:BACK TO TITLE", 13 if pyxel.frame_count % 10 < 5 else 5)
        elif self.scene == SCENE_GAMEOVER:
            # ゲームオーバー時：GAMEOVERとSCOREのみ表示
            pyxel.text(62, 50, "GAME OVER", 8); score_text = f"SCORE: {self.score:07}"
            pyxel.text(W//2 - len(score_text)*2, 62, score_text, 7)
        elif self.scene == SCENE_STAGE_CLEAR:
            pyxel.text(48, 50, "STAGE CLEAR!", 11); pyxel.text(45, 65, "GET READY FOR NEXT", 7)

        # ゲームオーバー時以外に表示するHUD
        if self.scene not in (SCENE_TITLE, SCENE_TUTORIAL, SCENE_GAMEOVER):
            pyxel.text(5, 4, f"SCORE {self.score:07}", 7); pyxel.text(100, 4, f"STAGE {self.stage}", 7)
            pyxel.text(5, 112, "PLAYER", 7)
            for i in range(self.lives): pyxel.rect(32 + i*6, 112, 3, 5, 8)
            b_status = f" B:{self.barrier_hp}" if self.barrier_hp > 0 else ""
            pyxel.text(100, 112, f"POWER {self.power}{b_status}", 10)

    def draw_ending(self):
        texts = ["CONGRATULATIONS!", "", "YOU HAVE SAVED", "THE GALAXY", "", "--- STAFF ---", "", "DIRECTOR: M.T", "GRAPHIC: M.T", "MUSIC: M.T", "SPECIAL THANKS: YOU", "", "", "PRESENTED BY", "MIRAI WORK 2026"]
        for i, t in enumerate(texts):
            y = H - self.scroll_y + i * 12
            if -10 < y < H + 10: pyxel.text(W//2 - len(t)*2, y, t, 7 if i % 2 == 0 else 10)
        if H - self.scroll_y + len(texts) * 12 < -20: pyxel.text(45, 60, "THANKS FOR PLAYING", pyxel.frame_count % 16)

StarSoldier()