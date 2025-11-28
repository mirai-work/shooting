import pyxel
import random

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Simple Shooting Game (Mobile Supported)")
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player_x = 70
        self.player_y = 100
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()
            return

        # ============
        # PC: キーボード操作
        # ============
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(self.player_x - 2, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(self.player_x + 2, 160 - 8)
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.bullets.append([self.player_x + 4, self.player_y])

        # ============
        # スマホ: タッチ操作
        # ============
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            tx = pyxel.mouse_x
            ty = pyxel.mouse_y

            # タッチ位置が画面下部 → 移動
            if ty > 80:
                # 画面左半分 → 左移動
                if tx < 80:
                    self.player_x = max(self.player_x - 2, 0)
                # 画面右半分 → 右移動
                else:
                    self.player_x = min(self.player_x + 2, 160 - 8)

            # 上部タップで弾発射
            if ty <= 80 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.bullets.append([self.player_x + 4, self.player_y])

        # 弾の更新
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

        # 衝突判定（弾と敵）
        for b in self.bullets:
            for e in self.enemies:
                if abs(b[0] - e[0]) < 6 and abs(b[1] - e[1]) < 6:
                    self.score += 10
                    e[1] = 200  # 画面外
                    b[1] = -10  # 弾削除
        self.enemies = [e for e in self.enemies if e[1] < 120]
        self.bullets = [b for b in self.bullets if b[1] > 0]

        # 敵が下に到達したらゲームオーバー
        for e in self.enemies:
            if e[1] >= 110:
                self.game_over = True

    def draw(self):
        pyxel.cls(0)
        if self.game_over:
            pyxel.text(60, 50, "GAME OVER", 8)
            pyxel.text(50, 65, f"SCORE: {self.score}", 7)
            pyxel.text(25, 80, "Tap or Press R to Restart", 6)
            return

        # 自機
        pyxel.rect(self.player_x, self.player_y, 8, 8, 11)

        # 弾
        for b in self.bullets:
            pyxel.rect(b[0], b[1], 2, 4, 10)

        # 敵
        for e in self.enemies:
            pyxel.rect(e[0], e[1], 8, 8, 8)

        # スコア
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)

App()
