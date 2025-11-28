import pyxel
import random

# バーチャルパッドの領域
BTN_LEFT = (0, 100, 50, 120)     # x1,y1,x2,y2
BTN_RIGHT = (50, 100, 100, 120)
BTN_SHOOT = (100, 100, 160, 120)

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Simple Shooting Game (Mobile Pad)")
        self.reset_game()
        pyxel.run(self.update, self.draw)
        self.shoot_timer = 0

    def reset_game(self):
        self.player_x = 70
        self.player_y = 95
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0

    def in_button(self, btn, mx, my):
        x1, y1, x2, y2 = btn
        return x1 <= mx <= x2 and y1 <= my <= y2

def update(self):
    if self.game_over:
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            self.reset_game()
        return

    # --- 自機の移動 ---
    if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
        self.player_x = max(self.player_x - 2, 0)
    if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
        self.player_x = min(self.player_x + 2, 152)

    # --- 自動発射（shoot変数は完全削除） ---
    self.shoot_timer += 1
    if self.shoot_timer > 6:   # ここで発射間隔を調整（小さいほど連射）
        self.bullets.append([self.player_x + 4, self.player_y])
        self.shoot_timer = 0

    # --- 弾の更新 ---
    for b in self.bullets:
        b[1] -= 4
    self.bullets = [b for b in self.bullets if b[1] > 0]

        # 敵の生成
        self.spawn_timer += 1
        if self.spawn_timer > 30:
            self.enemies.append([random.randint(0, 152), 0])
            self.spawn_timer = 0

        # 敵の移動
        for e in self.enemies:
            e[1] += 1.5

        # 衝突判定
        for b in self.bullets:
            for e in self.enemies:
                if abs(b[0] - e[0]) < 6 and abs(b[1] - e[1]) < 6:
                    self.score += 10
                    e[1] = 200
                    b[1] = -10

        self.enemies = [e for e in self.enemies if e[1] < 120]
        self.bullets = [b for b in self.bullets if b[1] > 0]

        # 敵が下に到達したらゲームオーバー
        for e in self.enemies:
            if e[1] >= 110:
                self.game_over = True

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(60, 40, "GAME OVER", 8)
            pyxel.text(50, 55, f"SCORE: {self.score}", 7)
            pyxel.text(20, 75, "Tap screen or Press R to Restart", 6)
            return

        # 自機
        pyxel.rect(self.player_x, self.player_y, 8, 8, 11)

        # 弾
        for b in self.bullets:
            pyxel.rect(b[0], b[1], 2, 3, 10)

        # 敵
        for e in self.enemies:
            pyxel.rect(e[0], e[1], 8, 8, 8)

        # スコア
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)

        # ======== バーチャルパッド描画 ========
        pyxel.rectb(*BTN_LEFT, 9)
        pyxel.text(15, 108, "LEFT", 9)

        pyxel.rectb(*BTN_RIGHT, 9)
        pyxel.text(60, 108, "RIGHT", 9)

        pyxel.rectb(*BTN_SHOOT, 8)
        pyxel.text(115, 108, "SHOT", 8)


App()
