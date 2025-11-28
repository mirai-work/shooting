import pyxel
import random

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Slide Pad Shooting Game")
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

        # スライドパッド用
        self.pad_active = False
        self.pad_start_x = 0

        # 自動連射
        self.shot_timer = 0


    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return

        # ===========================
        # PCキー操作（残しておく）
        # ===========================
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(self.player_x - 2, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(self.player_x + 2, 160 - 8)

        # ===========================
        # スマホ：スライドパッド操作
        # ===========================
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y

            # 下部左80pxがパッド領域
            if my > 90 and mx < 80:
                if not self.pad_active:
                    # パッド開始
                    self.pad_active = True
                    self.pad_start_x = mx
                else:
                    # 差分で移動
                    diff = mx - self.pad_start_x
                    self.player_x += diff * 0.3   # 移動感度
                    self.player_x = max(0, min(self.player_x, 152))
                    self.pad_start_x = mx  # 位置更新

        else:
            self.pad_active = False

        # ===========================
        # 自動連射ショット
        # ===========================
        self.shot_timer += 1
        if self.shot_timer >= 5:  # 5フレームごとに発射
            self.bullets.append([self.player_x + 4, self.player_y])
            self.shot_timer = 0

        # 弾の更新
        for b in self.bullets:
            b[1] -= 4
        self.bullets = [b for b in self.bullets if b[1] > 0]

        # ===========================
        # 敵生成
        # ===========================
        self.spawn_timer += 1
        if self.spawn_timer > 30:
            self.enemies.append([random.randint(0, 152), 0])
            self.spawn_timer = 0

        # 敵移動
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

        # ゲームオーバー
        for e in self.enemies:
            if e[1] >= 110:
                self.game_over = True


    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(60, 40, "GAME OVER", 8)
            pyxel.text(50, 55, f"SCORE: {self.score}", 7)
            pyxel.text(20, 75, "Tap screen or press R to restart", 6)
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

        # ============================================
        # スライドパッドUI
        # ============================================
        pyxel.rect(0, 100, 80, 20, 5)
        pyxel.text(22, 108, "SLIDE PAD", 7)

        # 説明（見やすいように）
        pyxel.text(90, 108, "AUTO SHOT", 6)


App()
