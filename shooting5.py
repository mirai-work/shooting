import pyxel

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Shooting + VirtualPad", display_scale=3)

        # プレイヤー
        self.x = 70
        self.y = 100

        pyxel.mouse(True)  # スマホのためマウス(タッチ)ON
        pyxel.run(self.update, self.draw)

    # -------------------------------------------------------
    # 仮想ボタンの判定
    # -------------------------------------------------------
    def virtual_button(self):
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        m = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)

        left = right = shot = False

        if m:
            # 左ボタン領域
            if 0 <= mx < 50 and 80 <= my < 120:
                left = True

            # 右ボタン領域
            if 50 <= mx < 100 and 80 <= my < 120:
                right = True

            # ショットボタン領域
            if 110 <= mx < 160 and 70 <= my < 120:
                shot = True

        return left, right, shot

    # -------------------------------------------------------
    # 更新
    # -------------------------------------------------------
    def update(self):
        left, right, shot = self.virtual_button()

        # PC のキーボード操作も残す
        if pyxel.btn(pyxel.KEY_LEFT) or left:
            self.x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT) or right:
            self.x += 2

        if pyxel.btnp(pyxel.KEY_SPACE) or shot:
            self.fire_bullet()

    # -------------------------------------------------------
    # ショット処理
    # -------------------------------------------------------
    def fire_bullet(self):
        # 本来は弾リストへ追加するなど
        print("SHOT!")  # デバッグ出力

    # -------------------------------------------------------
    # 描画
    # -------------------------------------------------------
    def draw(self):
        pyxel.cls(0)

        # プレイヤー
        pyxel.circ(self.x, self.y, 4, 10)

        # 仮想ゲームパッド描画
        self.draw_virtual_pad()

    # -------------------------------------------------------
    # 仮想ボタン描画
    # -------------------------------------------------------
    def draw_virtual_pad(self):
        # 左ボタン
        pyxel.rect(0, 80, 50, 40, 1)
        pyxel.text(18, 96, "L", 7)

        # 右ボタン
        pyxel.rect(50, 80, 50, 40, 1)
        pyxel.text(68, 96, "R", 7)

        # ショットボタン
        pyxel.rect(110, 70, 50, 50, 8)
        pyxel.text(128, 94, "SHOT", 7)

App()
