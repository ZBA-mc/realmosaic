from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random
import numpy as np
from ursina.scene import Scene


def perturb_perlin_value(original_noise_val, perturb_strength=0.05):
    perturbed_val = original_noise_val + random.uniform(-perturb_strength, perturb_strength)
    perturbed_val = np.clip(perturbed_val, -1.0, 1.0)
    return perturbed_val

def toggle_pause(is_paused):
    pause_menu.enabled = is_paused
    mouse.locked = not is_paused
    mouse.visible = is_paused
    player.enabled = not is_paused
    application.paused = is_paused

app = Ursina()

# 纹理/音效加载
grass_texture = load_texture('assets/textures/block/grass_block.png')
stone_texture = load_texture('assets/textures/block/stone.png')
dirt_texture = load_texture('assets/textures/block/dirt.png')
bedrock_texture = load_texture('assets/textures/block/bedrock.png')
arm_texture = load_texture('assets/textures/entity/arm_texture.png')
punch_sound = Audio('assets/sounds/punch_sound.wav', loop=False, autoplay=False)
block_pick = 1

# 窗口设置
window.fps_counter.x = -0.88
window.fps_counter.y = 0.47
window.collider_counter.x = -0.88
window.collider_counter.y = 0.43
window.entity_counter.x = -0.88
window.entity_counter.y = 0.39
window.fps_counter.enabled = False
window.collider_counter.enabled = False
window.entity_counter.enabled = False
window.exit_button.visible = False

scene.fog_color = color.white
scene.fog_density = 0

coord_display = Text(
    parent=camera.ui,
    text="X: 0.00 Y: 0.00 Z: 0.00",
    position=(-0.88, 0.35),  # 放在计数器下方
    size=0.025,
    color=color.white,
    enabled=False  # 初始隐藏
)

# 输入处理
def input(key):
    if key == 'escape':
        toggle_pause(not pause_menu.enabled)

    if key == 'f3':
        coord_display.enabled = not coord_display.enabled
        window.collider_counter.enabled = not window.collider_counter.enabled
        window.entity_counter.enabled = not window.entity_counter.enabled
        window.fps_counter.enabled = not window.fps_counter.enabled

    if key == 'f':
        if scene.fog_density == 0:
            scene.fog_density = 0.04
        else:
            scene.fog_density = 0


def update():
    global block_pick
    if held_keys['1']: block_pick = 1
    if held_keys['2']: block_pick = 2
    if held_keys['3']: block_pick = 3
    if held_keys['4']: block_pick = 4

    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    if coord_display.enabled:
        # 保留2位小数，坐标更整洁
        x = round(player.x, 2)
        y = round(player.y, 2)
        z = round(player.z, 2)
        coord_display.text = f"X: {x} Y: {y} Z: {z}"

# 方块类
class Block(Button):
    def __init__(self, position=(0,0,0),texture=grass_texture):
        super().__init__(
            parent = scene,
            position = position,
            model = 'assets/models/block',
            origin_y = 0.5,
            texture = texture,
            color = color.white,
            highlight_color = color.hsv(0,0,0.9),
            scale = 0.5
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse button':
                punch_sound.play()
                if block_pick == 1:block = Block(position=self.position + mouse.normal,texture=grass_texture)
                if block_pick == 2: block = Block(position=self.position + mouse.normal, texture=stone_texture)
                if block_pick == 3: block = Block(position=self.position + mouse.normal, texture=dirt_texture)
                if block_pick == 4: block = Block(position=self.position + mouse.normal, texture=bedrock_texture)
            elif key == 'right mouse button':
                punch_sound.play()
                destroy(self)

# 手部类
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='assets/models/arm',
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.6)
        )

    def active(self):
        self.position = Vec2(0.3, -0.6)

    def passive(self):
        self.position = Vec2(0.4, -0.6)

# 地形生成
noise = PerlinNoise(octaves=random.uniform(2,5),seed=random.uniform(0,99999))
scale = random.uniform(24,32)

for z in range(32):
    for x in range(32):
        y = floor(perturb_perlin_value(noise([x/scale,z/scale]),random.uniform(0,0.1))*random.uniform(7,9))
        block = Block(position=(x,y,z))

        for i in range(-2,y):
            block = Block(position=(x, i, z),texture=dirt_texture)

# 暂停菜单（改用英文）
pause_menu = Entity(
    parent=camera.ui,
    enabled=False,
    z=0
)

menu_background = Entity(
    parent=pause_menu,
    model='quad',
    color=color.black50,
    scale=Vec2(2, 2),
    z=1
)

menu_title = Text(
    text='Pause Menu',  # 英文标题
    parent=pause_menu,
    position=(0, 0.2),
    color=color.white,
    scale=3,
    z=0
)

continue_button = Button(
    text='Continue',  # 英文继续
    parent=pause_menu,
    position=(0, 0),
    color=color.green,
    text_color=color.white,
    scale=0.2,
    z=0,
    on_click=lambda: toggle_pause(False)
)

quit_button = Button(
    text='Quit',  # 英文退出
    parent=pause_menu,
    position=(0, -0.2),
    color=color.red,
    text_color=color.white,
    scale=0.2,
    z=0,
    on_click=application.quit
)

# 玩家/场景初始化
player = FirstPersonController()
mouse.locked = True
mouse.visible = False
sky = Sky()
hand = Hand()

app.run()