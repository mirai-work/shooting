import pyxel
import math
import random

# ==================================================
# 設定値
# ==================================================
WIDTH, HEIGHT = 160, 120
SPEED_FACTOR = 1.0
SCENE_TITLE, SCENE_STAGE, SCENE_BOSS, SCENE_ENDING, SCENE_GAMEOVER = 0, 1, 2, 3, 4

class Bell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vy = -3.0 * SPEED_FACTOR 
        self.vx = random.uniform(-0.8, 0.8) * SPEED_FACTOR
        self.state, self.hit_count, self.dead = 0, 0, False

    def update(self):
        self.vy += 0.12 * SPEED_FACTOR
        self.y += self.vy
        self.x += self.vx
        if self.x < 10 or self.x > WIDTH-10: self.vx *= -1
        if self.y > HEIGHT: self.dead = True

    def hit(self):
        self.hit_count += 1
        self.vy = -3.5 * SPEED_FACTOR
        if self.hit_count <= 25: self.state = self.hit_count // 5
        elif self.hit_count > 30: self.state = 5

    def draw(self):
        colors = [10, 7, 12, 11, 8, 0] # 黄色、白、青、緑、赤、黒
        c = colors[self.state]
        pyxel.circ(self.x, self.y-2, 3, c)
        pyxel.rect(self.x-3, self.y-2, 7, 4, c)
        pyxel.rect(self.x-4, self.y+1, 9, 2, c)
        pyxel.rect(self.x-1, self.y+3, 3, 1, 7)

class TwinBeeBellRestored:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="TwinBee: Bell Restored")
        self.scene = SCENE_TITLE
        self.reset_full_game()
        pyxel.run(self.update, self.draw)

    def reset_full_game(self):
        self.score, self.lives, self.bg_y, self.frame = 0, 3, 0, 0
        self.p = {"x": 80, "y": 100, "arms": True, "speed": 2.0, "twin": False, "beam": False, "alive": True, "inv": 0}
        self.bullets, self.missiles, self.bells, self.enemies = [], [], [], []
        self.ground_enemies, self.items, self.boss_bullets = [], [], []
        self.explosions = []
        self.particles = []
        self.ground_kill_count = 0
        # 雲にベルを持たせるフラグをTrueに
        self.clouds = [{"x": random.randint(10, 150), "y": random.randint(-50, 80), "has_bell": True} for _ in range(4)]
        self.boss = None
        self.boss_guards = []
        self.ambulance = None
        self.ending_timer = 0

    def update(self):
        if self.scene == SCENE_TITLE:
            if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A): 
                self.scene = SCENE_STAGE; self.reset_full_game()
            return
        if self.scene == SCENE_ENDING:
            self.ending_timer += 1
            if pyxel.frame_count % 2 == 0:
                self.particles.append({"x": random.randint(0, WIDTH), "y": HEIGHT, "v": -random.uniform(1, 4), "c": random.randint(8, 15)})
            for p in self.particles: p["y"] += p["v"]
            if self.ending_timer > 210: self.scene = SCENE_TITLE
            return
        if self.scene == SCENE_GAMEOVER:
            if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A): self.scene = SCENE_TITLE
            return

        self.frame += 1
        self.update_player()
        self.update_ambulance()
        self.update_background()
        self.update_entities()
        self.process_collisions()
        for exp in self.explosions: exp["r"] += 1
        self.explosions = [e for e in self.explosions if e["r"] < 10]

    def update_player(self):
        p = self.p
        if not p["alive"]:
            if self.frame % 45 == 0:
                self.lives -= 1
                if self.lives > 0: self.respawn_player()
                else: self.scene = SCENE_GAMEOVER
            return
        dx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
        dy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP))
        p["x"] = max(4, min(WIDTH-12, p["x"] + dx * p["speed"]))
        p["y"] = max(4, min(HEIGHT-12, p["y"] + dy * p["speed"]))
        if p["inv"] > 0: p["inv"] -= 1
        
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.bullets.append({"x": p["x"]+4, "y": p["y"], "vx": 0, "vy": -6, "dead": False})
            if p["twin"]: self.bullets.append({"x": p["x"]-1, "y": p["y"]+2, "vx": 0, "vy": -6, "dead": False})
            if p["beam"]:
                self.bullets.append({"x": p["x"]+4, "y": p["y"], "vx": -2, "vy": -5, "dead": False})
                self.bullets.append({"x": p["x"]+4, "y": p["y"], "vx": 2, "vy": -5, "dead": False})
            self.missiles.append({"x": p["x"]+4, "y": p["y"]+8, "vy": 3, "dead": False})

    def update_ambulance(self):
        if not self.p["arms"] and not self.ambulance and self.p["alive"]:
            self.ambulance = {"x": -20, "y": -20}
        if self.ambulance:
            amb = self.ambulance
            target_x, target_y = self.p["x"], self.p["y"] - 14
            amb["x"] += (target_x - amb["x"]) * 0.1
            amb["y"] += (target_y - amb["y"]) * 0.1
            if abs(amb["x"] - target_x) < 4 and abs(amb["y"] - target_y) < 4:
                for _ in range(5):
                    self.explosions.append({"x": amb["x"], "y": amb["y"], "r": 0})
                self.p["arms"] = True
                self.ambulance = None

    def respawn_player(self):
        self.p.update({"x": 80, "y": 100, "alive": True, "inv": 60, "arms": True, "speed": 2.0, "twin": False, "beam": False})

    def update_background(self):
        self.bg_y = (self.bg_y + 1.0) % HEIGHT
        for c in self.clouds:
            c["y"] += 0.5
            if c["y"] > HEIGHT: c["y"], c["x"], c["has_bell"] = -20, random.randint(10, 150), True

    def update_entities(self):
        for bb in self.boss_bullets:
            bb["x"] += bb["vx"]
            bb["y"] += bb["vy"]

        if self.scene == SCENE_STAGE:
            if self.frame % 40 == 0:
                sx = random.randint(20, 140)
                v = random.choice(["DAIKON", "CARROT", "TOMATO"])
                for i in range(4): self.enemies.append({"x": sx, "y": -10-i*15, "base_x": sx, "t": 0, "type": v})
            if self.frame % 80 == 0:
                self.ground_enemies.append({"x": WIDTH, "y": random.randint(80, 110), "speed": -1.2})
            if self.score >= 3000: 
                self.scene = SCENE_BOSS
                self.boss = {"x": 80, "y": -40, "hp": 50, "t": 0, "flash": 0}
                self.boss_guards = [{"angle": i * 36} for i in range(10)]

        if self.boss:
            bs = self.boss
            bs["t"] += 1; bs["y"] = min(30, bs["y"] + 0.5)
            bs["x"] = 80 + math.sin(bs["t"] * 0.05) * 50
            if bs["flash"] > 0: bs["flash"] -= 1
            if bs["y"] >= 30 and bs["t"] % 25 == 0:
                angle = math.atan2(self.p["y"] - bs["y"], self.p["x"] - bs["x"])
                self.boss_bullets.append({"x": bs["x"], "y": bs["y"], "vx": math.cos(angle)*3.2, "vy": math.sin(angle)*3.2})
            for g in self.boss_guards: g["angle"] = (g["angle"] + 3) % 360

    def process_collisions(self):
        for b in self.bullets: b["x"] += b["vx"]; b["y"] += b["vy"]
        for m in self.missiles: m["y"] += m["vy"]
        
        # 雲を撃つとベルが出る判定を復活
        for c in self.clouds:
            for b in self.bullets:
                if not b["dead"] and abs(b["x"]-c["x"]) < 10 and abs(b["y"]-c["y"]) < 10:
                    if c["has_bell"]:
                        self.bells.append(Bell(c["x"], c["y"]))
                        c["has_bell"] = False
                    b["dead"] = True

        for it in self.items:
            it["y"] += 1
            if abs(it["x"] - self.p["x"]) < 8 and abs(it["y"] - self.p["y"]) < 8:
                self.p["beam"] = True; it["dead"] = True
                
        # ベルの更新と弾が当たった時の色変化
        for bl in self.bells:
            bl.update()
            # ベルを撃った時の色変化
            for b in self.bullets:
                if not b["dead"] and abs(b["x"]-bl.x) < 8 and abs(b["y"]-bl.y) < 8:
                    bl.hit(); b["dead"] = True
            # ベルの取得判定
            if self.p["alive"] and abs(bl.x-self.p["x"]-4) < 8 and abs(bl.y-self.p["y"]-4) < 8:
                if bl.state == 1: self.p["twin"] = True # 白: ツイン
                elif bl.state == 2: self.p["speed"] = min(3.5, self.p["speed"] + 0.4) # 青: スピード
                self.score += 500; bl.dead = True

        for b in self.bullets:
            if self.boss:
                for g in self.boss_guards:
                    gx = self.boss["x"] + math.cos(math.radians(g["angle"])) * 32
                    gy = self.boss["y"] + math.sin(math.radians(g["angle"])) * 32
                    if not b["dead"] and abs(b["x"]-gx) < 8 and abs(b["y"]-gy) < 8:
                        self.boss_guards.remove(g); b["dead"] = True; break

        for m in self.missiles:
            for ge in self.ground_enemies:
                if not m["dead"] and abs(m["x"]-ge["x"]) < 8 and abs(m["y"]-ge["y"]) < 8:
                    self.explosions.append({"x": ge["x"], "y": ge["y"], "r": 0})
                    self.score += 200; ge["x"] = -100; m["dead"] = True
                    self.ground_kill_count += 1
                    if self.ground_kill_count % 5 == 0:
                        self.items.append({"x": m["x"], "y": m["y"], "dead": False})

        for e in self.enemies:
            e["t"] += 8; e["y"] += 2.0
            e["x"] = e["base_x"] + math.sin(math.radians(e["t"])) * 25
            if self.p["alive"] and self.p["inv"] == 0 and abs(e["x"]-self.p["x"]-4) < 7 and abs(e["y"]-self.p["y"]-4) < 7:
                if self.p["arms"]: self.p["arms"] = False; self.p["inv"] = 30; e["y"] = 200
                else: self.p["alive"] = False
            for b in self.bullets:
                if not b["dead"] and abs(b["x"]-e["x"]) < 8 and abs(b["y"]-e["y"]) < 8:
                    self.score += 100; e["y"] = 200; b["dead"] = True

        for ge in self.ground_enemies: ge["x"] += ge["speed"]
        if self.boss:
            bs = self.boss
            for b in self.bullets:
                if not b["dead"] and abs(b["x"]-bs["x"]) < 18 and abs(b["y"]-bs["y"]) < 18:
                    bs["hp"] -= 1; bs["flash"] = 3; b["dead"] = True
                    if bs["hp"] <= 0: 
                        self.score += 10000
                        self.ending_timer = 0
                        self.scene = SCENE_ENDING

        for bb in self.boss_bullets:
            if self.p["alive"] and self.p["inv"] == 0 and abs(bb["x"]-self.p["x"]-4) < 4 and abs(bb["y"]-self.p["y"]-4) < 4:
                if self.p["arms"]: self.p["arms"] = False; self.p["inv"] = 30; bb["y"] = 200
                else: self.p["alive"] = False

        self.bullets = [b for b in self.bullets if -10 < b["y"] < 130 and not b["dead"]]
        self.missiles = [m for m in self.missiles if m["y"] < 130 and not m["dead"]]
        self.enemies = [e for e in self.enemies if e["y"] < 130]
        self.ground_enemies = [ge for ge in self.ground_enemies if ge["x"] > -20]
        self.items = [it for it in self.items if it["y"] < 130 and not getattr(it, 'dead', False)]
        self.boss_bullets = [bb for bb in self.boss_bullets if -10 < bb["y"] < 130 and -10 < bb["x"] < WIDTH + 10]
        self.bells = [bl for bl in self.bells if not bl.dead]

    def draw(self):
        pyxel.cls(3)
        if self.scene == SCENE_TITLE:
            pyxel.cls(0)
            c = [7, 10, 9, 8][(pyxel.frame_count // 4) % 4]
            pyxel.text(50, 40, "★ TWINBEE REBORN ★", c)
            if pyxel.frame_count % 20 < 10: 
                pyxel.text(48, 70, "PRESS START OR ENTER", 7)
            return
        if self.scene == SCENE_ENDING:
            pyxel.cls(12)
            for p in self.particles: pyxel.pset(p["x"], p["y"], p["c"])
            pyxel.text(45, 55, "!!! MISSION COMPLETE !!!", 7)
            pyxel.text(50, 75, f"FINAL SCORE: {self.score}", 10)
            wait = 7 - (self.ending_timer // 30)
            pyxel.text(65, 95, f"WAIT.. {wait}", 7)
            return
        if self.scene == SCENE_GAMEOVER:
            pyxel.cls(0); pyxel.text(60, 55, "GAME OVER", 8); return

        for j in range(5): pyxel.line(0, (self.bg_y + j*30)%120, WIDTH, (self.bg_y + j*30)%120, 11)
        for c in self.clouds: pyxel.circ(c["x"], c["y"], 8, 7)
        for ge in self.ground_enemies:
            pyxel.tri(ge["x"], ge["y"]-4, ge["x"]-4, ge["y"]+4, ge["x"]+4, ge["y"]+4, 4)
            pyxel.rect(ge["x"]-2, ge["y"], 4, 4, 11)
        for it in self.items: pyxel.circ(it["x"], it["y"], 3, 14); pyxel.rect(it["x"]-4, it["y"]-1, 8, 2, 7)
        for exp in self.explosions: pyxel.circb(exp["x"], exp["y"], exp["r"], 10 if exp["r"]%2==0 else 7)
        for bl in self.bells: bl.draw()
        if self.boss: 
            self.draw_onion(self.boss["x"], self.boss["y"], self.boss["flash"] > 0)
            for g in self.boss_guards:
                gx = self.boss["x"] + math.cos(math.radians(g["angle"])) * 32
                gy = self.boss["y"] + math.sin(math.radians(g["angle"])) * 32
                self.draw_enemy({"x": gx, "y": gy, "type": "DAIKON"})
        for e in self.enemies: self.draw_enemy(e)
        for bb in self.boss_bullets: pyxel.circ(bb["x"], bb["y"], 2, 8)
        if self.ambulance: self.draw_ambulance(self.ambulance["x"], self.ambulance["y"])
        if self.p["alive"] and (self.p["inv"] % 4 < 2): self.draw_twinbee(self.p["x"], self.p["y"], self.p["arms"])
        for b in self.bullets: pyxel.rect(b["x"], b["y"], 2, 4, 10)
        for m in self.missiles: pyxel.rect(m["x"], m["y"], 1, 3, 7)
        pyxel.text(5, 5, f"SCORE: {self.score}  LIFE: {self.lives}", 7)

    def draw_twinbee(self, x, y, arms):
        wing_y = math.sin(self.frame * 0.6) * 2
        if arms:
            pyxel.tri(x-2, y+2, x-6, y+wing_y, x-2, y+6, 7) 
            pyxel.tri(x+10, y+2, x+14, y+wing_y, x+10, y+6, 7) 
            
        pyxel.circ(x+4, y+4, 5, 12)
        pyxel.circ(x+4, y+3, 3, 6)
        pyxel.pset(x+3, y+2, 7)
        pyxel.rect(x+1, y+8, 2, 2, 10)
        pyxel.rect(x+5, y+8, 2, 2, 10)
        
        if arms:
            pyxel.rect(x-1, y+4, 2, 4, 7); pyxel.circ(x, y+8, 1, 10)
            pyxel.rect(x+7, y+4, 2, 4, 7); pyxel.circ(x+8, y+8, 1, 10)

    def draw_ambulance(self, x, y):
        c = 8 if pyxel.frame_count % 10 < 5 else 7
        pyxel.rect(x-4, y-2, 9, 6, 7); pyxel.rect(x-2, y-4, 5, 2, c)
        pyxel.text(x-3, y, "+", 8)

    def draw_enemy(self, e):
        x, y = e["x"], e["y"]
        if e["type"] == "DAIKON": pyxel.rect(x-2, y-4, 4, 8, 7); pyxel.rect(x-2, y-6, 4, 2, 3)
        elif e["type"] == "CARROT": pyxel.tri(x, y+4, x-3, y-4, x+3, y-4, 9); pyxel.rect(x-1, y-6, 2, 2, 3)
        elif e["type"] == "TOMATO": pyxel.circ(x, y, 4, 8); pyxel.rect(x-1, y-5, 2, 2, 3)

    def draw_onion(self, x, y, flash):
        col = 7 if flash else 4
        pyxel.circ(x, y, 15, col); pyxel.tri(x-15, y, x+15, y, x, y-25, col)
        pyxel.rect(x-2, y-28, 4, 6, 3); pyxel.rect(x-6, y-2, 2, 4, 0); pyxel.rect(x+4, y-2, 2, 4, 0)

TwinBeeBellRestored()
