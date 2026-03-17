import pyxel
import math
import random

WIDTH, HEIGHT = 160, 120
SCENE_OPENING, SCENE_STAGE, SCENE_BOSS, SCENE_RESULT, SCENE_ENDING, SCENE_GAMEOVER = 0, 1, 2, 3, 4, 5

# ==================================================
# ベルクラス
# ==================================================
class Bell:
    def __init__(self, x, y, player_ref):
        self.x, self.y = x, y
        self.vy, self.vx = -3.0, random.uniform(-0.6, 0.6)
        self.hit_count = 0
        self.state = 0 # 0:黄, 1:青, 2:白, 3:点滅, 4:赤, 5:ハチ
        self.dead = False
        self.hit_wobble_timer = 0
        self.p = player_ref

    def update(self):
        self.vy += 0.1
        self.y += self.vy
        self.x += self.vx
        if self.x < 5 or self.x > WIDTH-5: self.vx *= -1
        if self.y > HEIGHT: self.dead = True
        if self.hit_wobble_timer > 0: self.hit_wobble_timer -= 1

    def hit(self):
        self.hit_count += 1
        self.vy = -3.5
        self.hit_wobble_timer = 10
        pyxel.play(3, 2) 
        new_state = self.hit_count // 5
        if self.hit_count >= 30:
            self.state = 5
            return
        if new_state == 3 and self.p["barrier"] > 0:
            new_state = 4
        if new_state == 4 and self.p["clones"] > 0:
            new_state = 0
        self.state = new_state % 5

    def draw(self):
        flash_c = 11 if pyxel.frame_count % 4 < 2 else 3
        wobble_x = 0
        if self.hit_wobble_timer > 0:
            wobble_x = math.sin(self.hit_wobble_timer * 1.5) * 2
        bx, by = self.x + wobble_x, self.y
        if self.state == 5:
            pyxel.ellipse(bx-6, by-2, 5, 4, 12)
            pyxel.ellipse(bx+2, by-2, 5, 4, 12)
            pyxel.rect(bx-2, by-3, 5, 2, 14) 
            pyxel.rect(bx-2, by-1, 5, 2, 7)   
            pyxel.rect(bx-2, by+1, 5, 2, 14) 
            pyxel.rect(bx, by-5, 1, 2, 12)
            pyxel.rect(bx, by+3, 1, 2, 14)
        else:
            c = 10
            if self.state == 0: c = 10
            elif self.state == 1: c = 12
            elif self.state == 2: c = 7
            elif self.state == 3: c = flash_c
            elif self.state == 4: c = 8
            pyxel.circ(bx, by - 2, 3, c)
            pyxel.rect(bx - 3, by - 2, 7, 4, c)
            pyxel.rect(bx - 4, by + 1, 9, 2, c)
            pyxel.rect(bx - 1, by + 3, 3, 1, 7)

# ==================================================
# メインゲームクラス
# ==================================================
class TwinBeeFinal:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="ONEBEE: AGGRESSIVE POTATO")
        self.setup_sounds() 
        self.scene = SCENE_OPENING
        self.frame = 0
        self.reset_full_game()
        pyxel.playm(3, loop=True)
        pyxel.run(self.update, self.draw)

    def trigger_damage(self):
        p = self.p
        pyxel.stop()
        pyxel.play(1, 9) 
        p["speed"] = 2.0
        p["twin"] = False
        p["clones"] = 0
        p["candy"] = False
        self.bell_combo = 0 
        if p["barrier"] > 0: 
            p["barrier"] = 0 
            p["inv"] = 30
            pyxel.playm(0, loop=True)
        elif p["arms"]: 
            p["arms"] = False 
            p["inv"] = 40
            pyxel.playm(0, loop=True)
        else: 
            p["alive"] = False 
            self.explosions.append({"x": p["x"], "y": p["y"], "t": 0})

    def setup_sounds(self):
        pyxel.sounds[0].set("a2a1c1", "p", "7", "vff", 5)
        pyxel.sounds[1].set("c2c1g1g0", "n", "7", "vfff", 10)
        pyxel.sounds[2].set("e3g3e4g4", "s", "6", "vvvv", 10)
        pyxel.sounds[3].set("g2g3g4", "t", "7", "vvv", 10)
        pyxel.sounds[4].set("c3e3g3c4 g3e3c3g2 a2c3e3a3 g3e3c3g2 f2a2c3f3 e2g2c3e3 d2f2a2d3 g2b2d3g3", "p", "6", "v", 20)
        pyxel.sounds[5].set("c2 c2 g1 g1 a1 a1 e1 e1 f1 f1 c1 c1 d1 d1 g1 g1", "n", "5", "v", 20)
        pyxel.sounds[6].set("c2e2c2e2 f2a2f2a2 g2b2g2b2 c3e3c3e3", "t", "7", "v", 10)
        pyxel.sounds[7].set("c3g3c4g3 a3f3a3f3 g3e3g3e3 d3b2d3b2", "s", "6", "v", 15)
        pyxel.sounds[8].set("c3 g2 e2 c2", "p", "6", "vvvv", 40)
        pyxel.sounds[9].set("c3c2c1", "s", "7", "v", 20)
        pyxel.musics[0].set([4], [5], [], []) 
        pyxel.musics[1].set([6], [5], [], []) 
        pyxel.musics[2].set([7], [5], [], []) 
        pyxel.musics[3].set([7], [], [], [])  

    def reset_full_game(self):
        self.stage = 1
        self.boss_rush_step = 0
        self.score, self.lives, self.bg_y = 0, 3, 0
        self.p = {"x": 80, "y": 140, "arms": True, "speed": 2.0, "twin": False, 
                  "barrier": 0, "clones": 0, "history": [], "alive": True, "inv": 0, "candy": False}
        self.bullets, self.missiles, self.bells, self.enemies = [], [], [], []
        self.ground_enemies, self.explosions = [], []
        self.boss_bullets, self.items = [], [] 
        self.ground_kills = 0 
        self.bell_combo = 0 
        self.end_timer = 0
        self.result_timer = 0
        self.clouds = [{"x": random.randint(10, 140), "y": random.randint(0, HEIGHT), "s": 0.6, "has_bell": True} for _ in range(5)]
        self.boss, self.ambulance = None, None
        self.op_timer = 0
        self.fireworks = []
        self.gameover_timer = 0

    def start_next_stage(self):
        self.scene = SCENE_STAGE
        self.bullets, self.missiles, self.enemies, self.ground_enemies = [], [], [], []
        self.boss_bullets, self.items = [], []
        self.p["x"], self.p["y"] = 80, 100
        self.boss = None
        self.boss_rush_step = 0
        self.stage_start_score = self.score
        pyxel.playm(0, loop=True)

    def respawn_player(self):
        self.p.update({"x": 80, "y": 100, "alive": True, "inv": 90, "arms": True, "speed": 2.0, "twin": False, "barrier": 0, "clones": 0, "history": [], "candy": False})
        self.bell_combo = 0
        pyxel.playm(0, loop=True) 

    def update(self):
        self.frame += 1
        if self.scene == SCENE_OPENING:
            self.op_timer += 1
            if self.p["y"] > 90: self.p["y"] -= 0.5
            if self.op_timer > 30 and (pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)):
                self.start_next_stage()
            return
        if self.scene == SCENE_RESULT:
            self.result_timer += 1
            if self.result_timer > 90:
                if self.stage < 4:
                    self.stage += 1
                    self.start_next_stage()
                else:
                    self.scene = SCENE_ENDING
                    self.end_timer = 0
            return
        if self.scene == SCENE_ENDING:
            self.end_timer += 1
            if self.end_timer == 1: pyxel.playm(2, loop=True) 
            if self.frame % 15 == 0:
                self.fireworks.append({"x": random.randint(20, 140), "y": random.randint(20, 60), "t": 0, "c": random.choice([7, 8, 10, 12, 14])})
            for fw in self.fireworks[:]:
                fw["t"] += 1
                if fw["t"] > 20: self.fireworks.remove(fw)
            if self.end_timer > 200:
                if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                    self.scene = SCENE_OPENING
                    self.reset_full_game()
                    pyxel.playm(3, loop=True) 
            return
        if self.scene == SCENE_GAMEOVER:
            self.gameover_timer += 1
            self.bg_y = (self.bg_y + 1.0) % HEIGHT
            self.update_entities()
            if self.gameover_timer == 1: 
                pyxel.stop()
                pyxel.play(3, 8) 
            if self.gameover_timer > 150:
                self.scene = SCENE_OPENING
                self.reset_full_game()
                pyxel.playm(3, loop=True)
            return

        self.update_player()
        self.update_ambulance()
        self.bg_y = (self.bg_y + 1.0) % HEIGHT
        self.update_entities()
        self.process_collisions()

    def update_player(self):
        p = self.p
        if not p["alive"]:
            if self.frame % 45 == 0:
                self.lives -= 1
                if self.lives > 0: self.respawn_player()
                else: 
                    self.scene = SCENE_GAMEOVER
                    self.gameover_timer = 0
            return
        p["tilt"] = 0
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): 
            p["x"] = max(p["x"] - p["speed"], 0)
            p["tilt"] = -1
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): 
            p["x"] = min(p["x"] + p["speed"], WIDTH - 10)
            p["tilt"] = 1
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP): p["y"] = max(p["y"] - p["speed"], 0)
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): p["y"] = min(p["y"] + p["speed"], HEIGHT - 10)
        
        if pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
            if self.frame % 4 == 0:
                self.bullets.append({"x": p["x"]+4, "y": p["y"], "vx": 0, "vy": -6})
                pyxel.play(0, 0)
                if p["twin"]: self.bullets.append({"x": p["x"]-2, "y": p["y"]+2, "vx": 0, "vy": -6})
                if p["candy"]:
                    self.bullets.append({"x": p["x"]+4, "y": p["y"], "vx": -2, "vy": -5.5}) 
                    self.bullets.append({"x": p["x"]+4, "y": p["y"], "vx": 2, "vy": -5.5})  

        if pyxel.btn(pyxel.KEY_X) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B):
            if p["arms"] and self.frame % 5 == 0:
                self.missiles.append({"x": p["x"]+4, "y": p["y"]+8, "vx": 0, "vy": 3})
        
        p["history"].insert(0, (p["x"], p["y"]))
        if len(p["history"])-1 > 30: p["history"].pop()
        if p["inv"] > 0: p["inv"] -= 1

    def update_ambulance(self):
        if not self.p["arms"] and not self.ambulance and self.p["alive"]:
            self.ambulance = {"x": -20, "y": HEIGHT + 10, "t": 0}
        if self.ambulance:
            amb = self.ambulance
            amb["t"] += 1
            tx, ty = self.p["x"], self.p["y"] - 14 + math.sin(amb["t"] * 0.15) * 4
            amb["x"] += (tx - amb["x"]) * 0.06
            amb["y"] += (ty - amb["y"]) * 0.06
            if abs(amb["x"] - self.p["x"]) < 6 and abs(amb["y"] - (self.p["y"]-12)) < 6:
                self.p["arms"] = True
                pyxel.play(3, 3)
                for _ in range(5): self.explosions.append({"x": amb["x"]+random.randint(-4,4), "y": amb["y"]+random.randint(-4,4), "t": 0})
                self.ambulance = None

    def spawn_boss(self, boss_type):
        hp_base = 25 + (self.stage * 15)
        if self.stage == 4: hp_base += (self.boss_rush_step * 20)
        # ボスの初期化
        self.boss = {"x": 80, "y": -50, "hp": hp_base, "t": 0, "flash": 0, "type": boss_type, "history": []}
        # 3面ボス(POTATO)の場合、移動目標tx, tyを初期化
        if boss_type == "POTATO":
            self.boss["tx"], self.boss["ty"] = 80, 30
            
        guard_count = 10 + (self.stage * 2)
        self.boss_guards = [{"angle": i * (360/guard_count)} for i in range(guard_count)]
        pyxel.playm(1, loop=True) 

    def update_entities(self):
        if self.scene == SCENE_STAGE:
            spawn_rate = max(20, 50 - self.stage * 8)
            if self.frame % spawn_rate == 0:
                sx = random.randint(20, 140)
                stage_enemies = {1: ["TOMATO"], 2: ["CARROT"], 3: ["DAIKON"], 4: ["TOMATO", "CARROT", "DAIKON"]}
                t = random.choice(stage_enemies[self.stage])
                count = 4 + (self.stage // 2)
                for i in range(count): self.enemies.append({"x": sx, "y": -15-i*18, "bx": sx, "t": 0, "type": t})
            if self.frame % 90 == 0: self.ground_enemies.append({"x": WIDTH, "y": random.randint(30, 100)})
            
            target_score = 20000 if self.stage == 4 else 10000
            if self.score - self.stage_start_score >= target_score:
                self.scene = SCENE_BOSS
                types = {1: "ONION", 2: "CABBAGE", 3: "POTATO", 4: "ONION"}
                self.spawn_boss(types[self.stage])

        if self.boss:
            b = self.boss
            b["t"] += 1
            if b["y"] < 30: b["y"] += (30.0 - b["y"]) * 0.04 + 0.1
            else:
                if b["type"] == "ONION":
                    b["x"] = 80.0 + math.sin(b["t"] * 0.15) * 75.0 
                    b["y"] = 40.0 + math.sin(b["t"] * 0.3) * 30.0
                    if b["t"] % 15 == 0:
                        for angle in range(-40, 41, 20):
                            rad = math.radians(angle)
                            self.boss_bullets.append({"x": b["x"], "y": b["y"]+8, "vx": math.sin(rad)*2.5, "vy": math.cos(rad)*2.5})
                
                elif b["type"] == "CABBAGE":
                    b["x"] += (self.p["x"] - b["x"]) * 0.15
                    b["y"] = 35.0 + math.cos(b["t"] * 0.2) * 40.0
                    if b["t"] % 8 == 0:
                        dx, dy = (self.p["x"]+4) - b["x"], (self.p["y"]+4) - b["y"]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist > 0: self.boss_bullets.append({"x": b["x"], "y": b["y"]+8, "vx": dx/dist*3.5, "vy": dy/dist*3.5})

                elif b["type"] == "POTATO":
                    # --- 3面ボスの動き激化ロジック ---
                    if b["t"] % 20 == 0: 
                        b["tx"], b["ty"] = random.randint(10, 150), random.randint(10, 80)
                    b["x"] += (b["tx"] - b["x"]) * 0.35
                    b["y"] += (b["ty"] - b["y"]) * 0.35
                    if b["t"] % 30 == 0:
                        for i in range(12):
                            ang = i * 30 + (b["t"] % 360)
                            self.boss_bullets.append({"x": b["x"], "y": b["y"], "vx": math.cos(math.radians(ang))*2.2, "vy": math.sin(math.radians(ang))*2.2})

                elif b["type"] == "TURNIP":
                    b["x"] = 80.0 + math.sin(b["t"] * 0.2) * 65.0 + (self.p["x"] - 80) * 0.5
                    b["y"] = 45.0 + math.cos(b["t"] * 0.25) * 35.0
                    if b["t"] % 20 == 0:
                        for angle in [-30, 0, 30]:
                            rad = math.radians(angle); self.boss_bullets.append({"x": b["x"], "y": b["y"], "vx": math.sin(rad)*2, "vy": math.cos(rad)*2})
                    if b["t"] % 15 == 0:
                        dx, dy = (self.p["x"]+4) - b["x"], (self.p["y"]+4) - b["y"]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist > 0: self.boss_bullets.append({"x": b["x"], "y": b["y"], "vx": dx/dist*4, "vy": dy/dist*4})

            b["history"].insert(0, (b["x"], b["y"]))
            if len(b["history"]) > 8: b["history"].pop()
            if b["flash"] > 0: b["flash"] -= 1
            for g in self.boss_guards: g["angle"] = (g["angle"] + 2.0 + self.stage * 0.5) % 360.0

        for e in self.enemies: e["t"] += 4; e["y"] += 1.2 + (self.stage * 0.1); e["x"] = e["bx"] + math.sin(math.radians(e["t"] * 2.5)) * 35
        for bl in self.bells:
            bl.update()
            if bl.y > HEIGHT: self.bell_combo = 0
        self.bells = [bl for bl in self.bells if not bl.dead]
        for g in self.ground_enemies: g["x"] -= 1.0
        for it in self.items: it["x"] -= 1.0 
        for bb in self.boss_bullets: bb["x"] += bb.get("vx", 0); bb["y"] += bb.get("vy", 2)
        for ex in self.explosions[:]:
            ex["t"] += 1
            if ex["t"] > 10: self.explosions.remove(ex)

    def process_collisions(self):
        p = self.p
        for b in self.bullets[:]:
            b["y"] += b["vy"]
            b["x"] += b.get("vx", 0)
            if b["y"] < 0 or b["x"] < 0 or b["x"] > WIDTH:
                if b in self.bullets: self.bullets.remove(b)
                continue
            if self.boss and abs(b["x"] - self.boss["x"]) < 20 and abs(b["y"] - self.boss["y"]) < 20:
                self.boss["hp"] -= 1; self.boss["flash"] = 3
                if b in self.bullets: self.bullets.remove(b)
                if self.boss["hp"] <= 0: 
                    pyxel.play(1, 1); self.explosions.append({"x": self.boss["x"], "y": self.boss["y"], "t": 0})
                    if self.stage < 4: self.scene = SCENE_RESULT; self.result_timer = 0; pyxel.stop()
                    else:
                        self.boss_rush_step += 1
                        if self.boss_rush_step == 1: self.spawn_boss("CABBAGE")
                        elif self.boss_rush_step == 2: self.spawn_boss("POTATO")
                        elif self.boss_rush_step == 3: self.spawn_boss("TURNIP")
                        else: self.scene = SCENE_RESULT; self.result_timer = 0
                    continue
            for c in self.clouds:
                if abs(b["x"] - c["x"]) < 10 and abs(b["y"] - c["y"]) < 10:
                    if c["has_bell"] and random.random() < 0.8: self.bells.append(Bell(c["x"], c["y"], self.p))
                    c["has_bell"] = False
                    if b in self.bullets: self.bullets.remove(b)
                    break
            for bl in self.bells:
                if abs(b["x"] - bl.x) < 8 and abs(b["y"] - bl.y) < 8:
                    bl.hit()
                    if b in self.bullets: self.bullets.remove(b)
                    break
            for e in self.enemies[:]:
                if abs(b["x"] - e["x"]) < 8 and abs(b["y"] - e["y"]) < 8:
                    self.score += 100; self.explosions.append({"x": e["x"], "y": e["y"], "t": 0}); pyxel.play(1, 1)
                    if e in self.enemies: self.enemies.remove(e)
                    if b in self.bullets: self.bullets.remove(b)
                    break

        for m in self.missiles[:]:
            m["y"] += m["vy"]
            if m["y"] > HEIGHT or m["x"] < 0 or m["x"] > WIDTH:
                if m in self.missiles: self.missiles.remove(m)
                continue
            for ge in self.ground_enemies[:]:
                if abs(m["x"] - ge["x"]) < 8 and abs(m["y"] - ge["y"]) < 8:
                    self.score += 200; self.explosions.append({"x": ge["x"], "y": ge["y"], "t": 0}); pyxel.play(1, 1); self.ground_kills += 1
                    if self.ground_kills % 5 == 0: self.items.append({"x": ge["x"], "y": ge["y"], "type": "CANDY"})
                    if ge in self.ground_enemies: self.ground_enemies.remove(ge)
                    if m in self.missiles: self.missiles.remove(m)
                    break

        for it in self.items[:]:
            if abs(it["x"] - (p["x"]+4)) < 8 and abs(it["y"] - (p["y"]+4)) < 8:
                if it["type"] == "CANDY":
                    if p["candy"]: 
                        pyxel.play(1, 1) 
                        for e in self.enemies:
                            self.score += 100
                            self.explosions.append({"x": e["x"], "y": e["y"], "t": 0})
                        self.enemies = [] 
                    p["candy"] = True
                pyxel.play(3, 2)
                self.items.remove(it)

        for bl in self.bells[:]:
            if p["alive"] and abs(bl.x - (p["x"]+4)) < 8 and abs(bl.y - (p["y"]+4)) < 8:
                if bl.state == 5: self.trigger_damage()
                else:
                    pyxel.play(3, 2)
                    if bl.state == 0: self.bell_combo += 1; points = [500, 1000, 5000, 10000]; idx = min(self.bell_combo - 1, len(points)-1); self.score += points[idx]
                    elif bl.state == 1: p["speed"] = min(3.5, p["speed"]+0.3)
                    elif bl.state == 2: p["twin"] = True
                    elif bl.state == 3: p["clones"] = 2
                    elif bl.state == 4: p["barrier"] = 10 
                self.bells.remove(bl)

        if p["alive"] and p["inv"] == 0:
            hit = False
            for e in self.enemies:
                if abs(e["x"] - (p["x"]+4)) < 6 and abs(e["y"] - (p["y"]+4)) < 6: hit = True
            for bb in self.boss_bullets:
                if abs(bb["x"] - (p["x"]+4)) < 6 and abs(bb["y"] - (p["y"]+4)) < 6: hit = True
            if self.boss and abs(self.boss["x"] - (p["x"]+4)) < 18 and abs(self.boss["y"] - (p["y"]+4)) < 18: hit = True
            if hit: self.trigger_damage()

    def draw(self):
        bg_colors = {1: 3, 2: 12, 3: 1, 4: 0}
        pyxel.cls(bg_colors[self.stage]); self.draw_background()
        if self.scene == SCENE_OPENING: self.draw_opening(); return
        if self.scene == SCENE_ENDING: self.draw_ending(); return
        if self.scene == SCENE_RESULT:
            pyxel.text(55, 40, f"STAGE {self.stage} CLEAR!", 7); pyxel.text(50, 60, f"TOTAL SCORE: {self.score}", 10); pyxel.text(40, 80, "GET READY FOR NEXT...", pyxel.frame_count % 16); return
        for bl in self.bells: bl.draw()
        for ge in self.ground_enemies: self.draw_ground_enemy(ge["x"], ge["y"])
        for it in self.items: self.draw_item(it)
        if self.boss: self.draw_boss()
        for bb in self.boss_bullets: pyxel.circ(bb["x"], bb["y"], 2, 14)
        for e in self.enemies: self.draw_enemy(e)
        if self.ambulance: self.draw_ambulance()
        for ex in self.explosions: pyxel.circ(ex["x"], ex["y"], ex["t"], 7 if ex["t"] < 5 else 10)
        if self.scene == SCENE_GAMEOVER:
            pyxel.text(60, 50, "GAME OVER", 8); pyxel.text(50, 65, f"TOTAL SCORE:{self.score}", 7); return
        if self.p["alive"] and (self.p["inv"] % 4 < 2):
            self.draw_twinbee(self.p["x"], self.p["y"], self.p["arms"], tilt=self.p.get("tilt", 0))
            if self.p["barrier"] > 0: pyxel.circb(self.p["x"]+4, self.p["y"]+4, 11, 8)
        for b in self.bullets: pyxel.rect(b["x"], b["y"], 2, 4, 10)
        for m in self.missiles: pyxel.circ(m["x"], m["y"], 2, 14)
        pyxel.rect(0, 0, WIDTH, 10, 0); pyxel.text(5, 2, f"SCORE:{self.score:06}  LIFE:{self.lives}  STAGE:{self.stage}", 7)

    def draw_item(self, it):
        if it["type"] == "CANDY":
            x, y = it["x"], it["y"]
            pyxel.rect(x-4, y-2, 9, 5, 5) 
            pyxel.rect(x-1, y-2, 3, 5, 6) 
            pyxel.tri(x-6, y-3, x-4, y, x-6, y+3, 12) 
            pyxel.tri(x+6, y-3, x+4, y, x+6, y+3, 12) 

    def draw_ambulance(self):
        a = self.ambulance; pulse = pyxel.frame_count % 10 < 5; c_lamp = 8 if pulse else 7
        pyxel.rect(a["x"]-5, a["y"]-2, 11, 6, 7); pyxel.rect(a["x"]-3, a["y"]-4, 7, 2, c_lamp); pyxel.line(a["x"], a["y"]-1, a["x"], a["y"]+2, 8); pyxel.line(a["x"]-1, a["y"], a["x"]+1, a["y"], 8)

    def draw_background(self):
        colors = {1: [11, 3], 2: [12, 7], 3: [1, 5], 4: [0, 1]}; c_river, c_land = colors[self.stage]
        for j in range(-32, HEIGHT + 32, 32):
            yy = (j + self.bg_y) % (HEIGHT + 32) - 32; sw = math.sin(self.frame * 0.02 + j) * 8
            pyxel.rect(60 + sw, yy, 25, 32, c_river); pyxel.line(65+sw, yy, 65+sw, yy+32, 7 if self.stage<4 else 12)
            mx = 20 + math.sin(self.frame*0.01)*5; pyxel.circ(mx, yy+10, 12, c_land); pyxel.circ(mx+5, yy+18, 10, c_land); pyxel.circ(WIDTH-20, yy+5, 15, c_land); pyxel.pset(mx+2, yy+10, 7 if self.stage==1 else 0)
        for cl in self.clouds:
            cl["y"] = (cl["y"] + cl["s"]) % HEIGHT
            if cl["y"] < 1:
                cl["has_bell"] = True 
            pyxel.circ(cl["x"], cl["y"], 6, 7); pyxel.circ(cl["x"]+4, cl["y"]+2, 4, 7)

    def draw_twinbee(self, x, y, arms, is_clone=False, tilt=0):
        c1, c2 = (12, 6) if not is_clone else (5, 1); tx = tilt * 2
        if not is_clone: pyxel.tri(x+3, y+8, x+5, y+8, x+4-tx, y+11+pyxel.frame_count%3, 10)
        pyxel.circ(x+4, y+4, 5, 1); pyxel.circ(x+4+tx, y+3, 5, c1); pyxel.circ(x+4+tx*1.5, y+2, 3, c2) 
        if arms: pyxel.rect(x-1+tx, y+3-tx, 2, 5, c1); pyxel.rect(x+7+tx, y+3+tx, 2, 5, c1); pyxel.circ(x+tx, y+7-tx, 2, 8); pyxel.circ(x+8+tx, y+7+tx, 2, 8)
        pyxel.rect(x+1+tx, y+8, 2, 2, 8); pyxel.rect(x+5+tx, y+8, 2, 2, 8)

    def draw_enemy(self, e):
        x, y = e["x"], e["y"]
        if e["type"] == "DAIKON": pyxel.circ(x, y, 4, 7); pyxel.circ(x, y-2, 3, 7); pyxel.circ(x, y+2, 3, 7); pyxel.rect(x-1, y-6, 3, 3, 3)
        elif e["type"] == "TOMATO": pyxel.circ(x, y, 5, 8); pyxel.pset(x, y-5, 3)
        elif e["type"] == "CARROT": pyxel.tri(x-3, y-4, x+3, y-4, x, y+5, 9); pyxel.pset(x, y-5, 3)
        pyxel.pset(x-1, y-1, 0); pyxel.pset(x+1, y-1, 0)

    def draw_ground_enemy(self, x, y):
        pyxel.tri(x-4, y+4, x+4, y+4, x, y-4, 4); pyxel.line(x-2, y+1, x+2, y+1, 11); pyxel.line(x-1, y-1, x+1, y-1, 11) 

    def draw_boss(self):
        b = self.boss; bx, by = b["x"], b["y"]; flash_c = 7 if b["flash"] > 0 else -1
        def draw_pastel_circ(x, y, r, c_base):
            if flash_c != -1:
                pyxel.circ(x, y, r, 7)
                return
            pyxel.circ(x, y, r, c_base)
            if r > 4:
                pyxel.circ(x - r*0.3, y - r*0.3, r*0.35, 7)

        for i, pos in enumerate(b["history"]):
            if i % 2 == 0: pyxel.circ(pos[0], pos[1], 18 - i, 13 if i < 4 else 5)
        if b["type"] == "ONION": draw_pastel_circ(bx, by, 18, 10); pyxel.tri(bx-8, by-15, bx+8, by-15, bx, by-28, 3) 
        elif b["type"] == "CABBAGE": draw_pastel_circ(bx, by, 20, 3); [pyxel.line(bx, by, bx+math.cos(math.radians(i*90+b["t"]))*15, by+math.sin(math.radians(i*90+b["t"]))*15, 11) for i in range(4)]
        elif b["type"] == "POTATO": draw_pastel_circ(bx, by, 18, 4); [pyxel.pset(bx+dx, by+dy, 13) for dx, dy in [(-6, -6), (7, 2), (-3, 8)]]
        elif b["type"] == "TURNIP": draw_pastel_circ(bx, by, 22, 7); pyxel.rect(bx-5, by-32, 10, 12, 3); pyxel.rect(bx-2, by-35, 4, 15, 11) 
        eye_color = 1 if (b["t"] // 60) % 5 != 0 else 7; pyxel.pset(bx-8, by-2, eye_color); pyxel.pset(bx+8, by-2, eye_color)
        mouth_w = 6 if b["hp"] > 10 else 10; pyxel.rect(bx - mouth_w//2, by+8, mouth_w, 2, 8)
        for g in self.boss_guards:
            gx = bx + math.cos(math.radians(g["angle"])) * (35.0 + self.stage * 2.0); gy = by + math.sin(math.radians(g["angle"])) * (35.0 + self.stage * 2.0); pyxel.circ(gx, gy, 3, 10); pyxel.pset(gx-1, gy-1, 7) 

    def draw_opening(self):
        pyxel.cls(0); pyxel.text(55, 30, "O N E B E E", pyxel.frame_count % 15 + 1); pyxel.text(45, 50, "ULTIMATE EDITION", 7); self.draw_twinbee(76, self.p["y"], True)
        if self.frame % 30 < 15: pyxel.text(40, 100, "PUSH START or Z KEY", 7)

    def draw_ending(self):
        pyxel.cls(0); [pyxel.pset(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([6, 7, 12])) for _ in range(20)]
        for fw in self.fireworks: pyxel.circb(fw["x"], fw["y"], fw["t"], fw["c"])
        self.draw_twinbee(WIDTH//2-4, 60 + math.sin(self.frame*0.05)*10, True)
        c = pyxel.frame_count % 15 + 1; 
        if self.end_timer > 200:
            if pyxel.frame_count % 30 < 15: 
                pyxel.text(36, 25, "PUSH START/Z TO TITLE", 7)
        pyxel.text(48, 35, "CONGRATULATIONS!", c)
        pyxel.text(48, 80, "ALL STAGE CLEAR!", 7)
        pyxel.text(50, 90, f"FINAL SCORE:{self.score}", 10)
        pyxel.text(54, 102, "PROGRAM BY M.T", 7)
        pyxel.text(38, 110, "(C)MIRAI WORK/M.T 2026", 7)

TwinBeeFinal()