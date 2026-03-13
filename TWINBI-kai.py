import pyxel
import math
import random

# ==================================================
# 設定値（標準スピードに調整）
# ==================================================
WIDTH, HEIGHT = 160, 120
SPEED_FACTOR = 1.0  # 0.6から1.0に向上
SCENE_TITLE, SCENE_STAGE, SCENE_BOSS, SCENE_ENDING, SCENE_GAMEOVER = 0, 1, 2, 3, 4

class Bell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        # 重力と初速のバランスを標準化
        self.vy = -3.0 * SPEED_FACTOR 
        self.vx = random.uniform(-0.8, 0.8) * SPEED_FACTOR
        self.state, self.hit_count, self.angle, self.dead = 0, 0, 0, False

    def update(self):
        self.vy += 0.12 * SPEED_FACTOR
        self.y += self.vy
        self.x += self.vx
        if self.x < 10 or self.x > WIDTH-10: self.vx *= -1
        if self.y > HEIGHT: self.dead = True

    def hit(self):
        self.hit_count += 1
        self.vy = -3.5 * SPEED_FACTOR # 叩いた時の跳ね返りを強化
        if self.hit_count <= 25: self.state = self.hit_count // 5
        elif self.hit_count > 30: self.state = 5

    def draw(self):
        colors = [10, 7, 12, 11, 8, 0]
        c = colors[self.state]
        x, y = self.x, self.y
        pyxel.circ(x, y-2, 3, c)
        pyxel.rect(x-3, y-2, 7, 4, c)
        pyxel.rect(x-4, y+1, 9, 2, c)
        pyxel.rect(x-1, y+3, 3, 1, 7)

class TwinBeePerfectFixed:
    def __init__(self):
        # 30FPS（標準）で動作
        pyxel.init(WIDTH, HEIGHT, title="TwinBee: Standard Speed")
        self.scene = SCENE_TITLE
        self.reset_full_game()
        pyxel.run(self.update, self.draw)

    def reset_full_game(self):
        self.score, self.lives, self.bg_y, self.frame = 0, 3, 0, 0
        self.p = {"x": 80, "y": 100, "arms": True, "speed": 2.0, "twin": False, "alive": True, "inv": 0}
        self.bullets, self.bells, self.enemies = [], [], []
        self.clouds = [{"x": random.randint(10, 150), "y": random.randint(-50, 80), "has_bell": True} for _ in range(4)]
        self.boss = None
        self.ambulance = None

    def update(self):
        if self.scene == SCENE_TITLE:
            if pyxel.btnp(pyxel.KEY_Z): self.scene = SCENE_STAGE; self.reset_full_game()
            return
        if self.scene in [SCENE_ENDING, SCENE_GAMEOVER]:
            if pyxel.btnp(pyxel.KEY_Z): self.scene = SCENE_TITLE
            return

        self.frame += 1
        self.update_player()
        self.update_ambulance()
        self.update_background()
        self.update_entities()
        self.process_collisions()

    def update_player(self):
        p = self.p
        if not p["alive"]:
            if self.frame % 45 == 0: # 復活待機を少し短縮
                self.lives -= 1
                if self.lives > 0: self.respawn_player()
                else: self.scene = SCENE_GAMEOVER
            return
        
        dx = (pyxel.btn(pyxel.KEY_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT))
        dy = (pyxel.btn(pyxel.KEY_DOWN)) - (pyxel.btn(pyxel.KEY_UP))
        
        # 移動速度の適用
        p["x"] = max(4, min(WIDTH-12, p["x"] + dx * p["speed"]))
        p["y"] = max(4, min(HEIGHT-12, p["y"] + dy * p["speed"]))
        
        if p["inv"] > 0: p["inv"] -= 1
        
        # ショット
        if pyxel.btnp(pyxel.KEY_Z):
            self.bullets.append({"x": p["x"]+4, "y": p["y"], "dead": False})
            if p["twin"]: self.bullets.append({"x": p["x"]-1, "y": p["y"]+2, "dead": False})

    def update_ambulance(self):
        if not self.p["arms"] and not self.ambulance and self.p["alive"]:
            self.ambulance = {"x": WIDTH, "y": -20}
        if self.ambulance:
            amb = self.ambulance
            amb["x"] += (self.p["x"] - amb["x"]) * 0.1 # 少し追従を速く
            amb["y"] += (self.p["y"] - 12 - amb["y"]) * 0.1
            if abs(amb["x"] - self.p["x"]) < 5 and abs(amb["y"] - (self.p["y"]-12)) < 5:
                self.p["arms"] = True; self.ambulance = None

    def respawn_player(self):
        self.p["x"], self.p["y"], self.p["alive"], self.p["inv"] = 80, 100, True, 60
        self.p["arms"] = True
        self.p["speed"] = 2.0 # 速度リセット
        self.p["twin"] = False

    def update_background(self):
        self.bg_y = (self.bg_y + 1.0) % HEIGHT
        for c in self.clouds:
            c["y"] += 0.5
            if c["y"] > HEIGHT: c["y"], c["x"], c["has_bell"] = -20, random.randint(10, 150), True

    def update_entities(self):
        if self.scene == SCENE_STAGE:
            if self.frame % 40 == 0: # 敵の出現間隔を短く（スリル向上）
                sx = random.randint(20, 140)
                v = random.choice(["DAIKON", "CARROT", "TOMATO"])
                for i in range(4): self.enemies.append({"x": sx, "y": -10-i*15, "base_x": sx, "t": 0, "type": v})
            if self.score >= 3000: 
                self.scene = SCENE_BOSS
                self.boss = {"x": 80, "y": -40, "hp": 60, "t": 0, "flash": 0}

    def process_collisions(self):
        # 弾の移動を速く
        for b in self.bullets: b["y"] -= 6 
        
        for bl in self.bells:
            bl.update()
            if self.p["alive"] and abs(bl.x-self.p["x"]-4) < 8 and abs(bl.y-self.p["y"]-4) < 8:
                if bl.state == 1: self.p["twin"] = True
                elif bl.state == 2: self.p["speed"] = min(3.5, self.p["speed"] + 0.4)
                self.score += 500; bl.dead = True

        for b in self.bullets:
            for c in self.clouds:
                if c["has_bell"] and abs(b["x"]-c["x"]) < 10 and abs(b["y"]-c["y"]) < 10:
                    self.bells.append(Bell(c["x"], c["y"])); c["has_bell"] = False; b["dead"] = True
            for bl in self.bells:
                if not b["dead"] and abs(b["x"]-bl.x) < 8 and abs(b["y"]-bl.y) < 8: bl.hit(); b["dead"] = True

        for e in self.enemies:
            e["t"] += 8 # サイン波の動きを速く
            e["y"] += 2.0 # 敵の落下速度を向上
            e["x"] = e["base_x"] + math.sin(math.radians(e["t"])) * 25
            
            if self.p["alive"] and self.p["inv"] == 0 and abs(e["x"]-self.p["x"]-4) < 7 and abs(e["y"]-self.p["y"]-4) < 7:
                if self.p["arms"]: self.p["arms"] = False; self.p["inv"] = 30; e["y"] = 200
                else: self.p["alive"] = False
            
            for b in self.bullets:
                if not b["dead"] and abs(b["x"]-e["x"]) < 8 and abs(b["y"]-e["y"]) < 8:
                    self.score += 100; e["y"] = 200; b["dead"] = True

        if self.boss:
            bs = self.boss; bs["t"] += 3; bs["y"] = min(30, bs["y"] + 1.0)
            bs["x"] = 80 + math.sin(bs["t"] * 0.05) * 50
            if bs["flash"] > 0: bs["flash"] -= 1
            for b in self.bullets:
                if not b["dead"] and abs(b["x"]-bs["x"]) < 18 and abs(b["y"]-bs["y"]) < 18:
                    bs["hp"] -= 1; bs["flash"] = 3; b["dead"] = True
                    if bs["hp"] <= 0: self.score += 10000; self.scene = SCENE_ENDING

        self.bullets = [b for b in self.bullets if b["y"] > -10 and not b["dead"]]
        self.enemies = [e for e in self.enemies if e["y"] < 130]
        self.bells = [bl for bl in self.bells if not bl.dead]

    def draw(self):
        pyxel.cls(3)
        if self.scene == SCENE_TITLE:
            pyxel.cls(0); pyxel.text(50, 40, "TWINBEE REBORN", 10); pyxel.text(55, 70, "PRESS [Z] KEY", 7); return
        if self.scene == SCENE_ENDING:
            pyxel.cls(12); pyxel.text(45, 55, "MISSION ACCOMPLISHED!", 7); return
        if self.scene == SCENE_GAMEOVER:
            pyxel.cls(0); pyxel.text(60, 55, "GAME OVER", 8); return

        # 背景
        for j in range(5): pyxel.line(0, (self.bg_y + j*30)%120, WIDTH, (self.bg_y + j*30)%120, 11)
        for c in self.clouds: pyxel.circ(c["x"], c["y"], 8, 7)
        for bl in self.bells: bl.draw()
        if self.boss: self.draw_onion(self.boss["x"], self.boss["y"], self.boss["flash"] > 0)
        for e in self.enemies: self.draw_enemy(e)
        if self.ambulance: self.draw_ambulance(self.ambulance["x"], self.ambulance["y"])
        if self.p["alive"] and (self.p["inv"] % 4 < 2): self.draw_twinbee(self.p["x"], self.p["y"], self.p["arms"])
        for b in self.bullets: pyxel.rect(b["x"], b["y"], 2, 4, 10)
        pyxel.text(5, 5, f"SCORE: {self.score}  LIFE: {self.lives}", 7)

    def draw_twinbee(self, x, y, arms):
        wing_y = math.sin(self.frame * 0.6) * 2 # 羽ばたきを速く
        pyxel.tri(x-2, y+2, x-6, y+wing_y, x-2, y+6, 7)
        pyxel.tri(x+10, y+2, x+14, y+wing_y, x+10, y+6, 7)
        pyxel.circ(x+4, y+4, 5, 12)
        pyxel.circ(x+4, y+3, 3, 6)
        pyxel.pset(x+3, y+2, 7) 
        pyxel.rect(x+1, y+8, 2, 2, 10); pyxel.rect(x+5, y+8, 2, 2, 10)
        if arms:
            pyxel.rect(x-1, y+4, 2, 4, 7); pyxel.circ(x, y+8, 1, 10)
            pyxel.rect(x+7, y+4, 2, 4, 7); pyxel.circ(x+8, y+8, 1, 10)

    def draw_ambulance(self, x, y):
        pyxel.rect(x-4, y-2, 9, 6, 7); pyxel.rect(x-2, y-4, 5, 2, 8)
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

TwinBeePerfectFixed()
