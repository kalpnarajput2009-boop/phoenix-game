 # =========================================================
# FLAPPY BIRD ULTRA DELUXE FINAL FIXED VERSION
# RESTART BUG FIXED
# =========================================================
# FIXES:
# ✔ Restart fully working
# ✔ Pipes reset properly
# ✔ Coins reset properly
# ✔ Enemies reset properly
# ✔ Bird reset fixed
# ✔ Powerups reset fixed
# ✔ Shop system fixed
# ✔ Save system fixed
#
# INSTALL:
# pip install pygame
#
# RUN:
# python flappy_final.py



import pygame
import random
import math
import json
import os
import sys

pygame.init()

# =========================================================
# WINDOW
# =========================================================
WIDTH = 520
HEIGHT = 760

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Ultra Deluxe")

clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================
WHITE = (255,255,255)
BLACK = (0,0,0)

BLUE = (120,200,255)
DARK_BLUE = (15,15,40)

GREEN = (0,200,0)
DARK_GREEN = (0,150,0)

RED = (255,60,60)
YELLOW = (255,220,0)
PURPLE = (200,0,255)
ORANGE = (255,140,0)

CYAN = (0,255,255)
GRAY = (60,60,60)

# =========================================================
# SAVE FILE
# =========================================================
SAVE_FILE = "flappy_save.json"

default_data = {
    "highscore":0,
    "coins":0,
    "best_distance":0,
    "unlocked":[0],
    "selected":0
}

if not os.path.exists(SAVE_FILE):

    with open(SAVE_FILE,"w") as f:
        json.dump(default_data,f)

try:

    with open(SAVE_FILE,"r") as f:
        save_data = json.load(f)
    if "best_distance" not in save_data:
        save_data["best_distance"] = 0

except:

    save_data = default_data

    with open(SAVE_FILE,"w") as f:
        json.dump(default_data,f)
    
with open(SAVE_FILE,"w") as f:
    json.dump(save_data,f)

HIGH_SCORE = save_data["highscore"]
coins = save_data["coins"]
BEST_DISTANCE = save_data["best_distance"]
unlocked = save_data["unlocked"]
selected_bird = save_data["selected"]

# =========================================================
# FONTS
# =========================================================
font = pygame.font.SysFont("arial",26)
big_font = pygame.font.SysFont("arial",55)

# =========================================================
# GAME VARIABLES
# =========================================================
gravity = 0.28
jump_power = -6.5

pipe_speed = 4
# MOVING PIPE SYSTEM
moving_pipe_mode = False

moving_pipe_timer = 0

moving_pipe_duration = 300

pipe_move_speed = 2
next_moving_pipe_distance = 1000

score = 0
distance = 0
game_over = False
lives = 3
max_lives = 3
invincible_timer = 0
night_mode = False
# WEATHER
rain_drops = []

wind_force = 0
wind_timer = 0

rain_active = False
rain_timer = 0
rain_duration = 0

# =========================================================
# POWERUPS
# =========================================================
magnet_active = False
magnet_timer = 0

shield_active = False

shield_timer = 0

# =========================================================
# BIRDS
# =========================================================
GOLD = (255,215,0)

birds = [
    {
        "name":"Yellow",
        "color":YELLOW,
        "cost":0,
        "distance":0
    },

    {
        "name":"Red",
        "color":RED,
        "cost":500,
        "distance":1000
    },

    {
        "name":"Purple",
        "color":PURPLE,
        "cost":700,
        "distance":2000
    },

    {
        "name":"Orange",
        "color":ORANGE,
        "cost":900,
        "distance":5000
    },

    {
        "name":"Golden",
        "color":GOLD,
        "cost":5000,
        "distance":10000
    },
]

# =========================================================
# PLAYER
# =========================================================
bird_x = 120
bird_y = HEIGHT // 2

bird_velocity = 0
bird_size = 18

wing_angle = 0
wing_dir = 1
# =========================================================
# CITY BACKGROUND
# =========================================================
buildings = []

for i in range(12):

    width = random.randint(50,90)
    height = random.randint(120,320)

    x = i * 70

    buildings.append([
        x,
        HEIGHT - 30 - height,
        width,
        height
    ])

# =========================================================
# CLOUDS
# =========================================================
clouds = []

for i in range(5):

    clouds.append([
        random.randint(0,WIDTH),
        random.randint(40,250),
        random.randint(60,120)
    ])

# =========================================================
# GAME OBJECT LISTS
# =========================================================
pipes = []
coin_list = []
enemies = []
magnets = []
shields = []
particles = []
trail_particles = []
# RAIN
for i in range(120):

    rain_drops.append([

        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(4, 8)

    ])

# =========================================================
# CREATE FUNCTIONS
# =========================================================
def create_pipe():

    h = random.randint(120,420)
    gap = random.randint(180,270)

    top = pygame.Rect(
        WIDTH,
        0,
        80,
        h
    )

    bottom = pygame.Rect(
        WIDTH,
        h + gap,
        80,
        HEIGHT
    )

    return top,bottom

def create_coin(x):

    return pygame.Rect(
        x,
        random.randint(120,600),
        25,
        25
    )

def create_enemy(x):

    y = random.choice([
        random.randint(70,140),
        random.randint(560,650)
    ])

    return pygame.Rect(
        x,
        y,
        40,
        40
    )

def create_magnet(x):

    return pygame.Rect(
        x,
        random.randint(150,550),
        30,
        30
    )

def create_shield(x):

    return pygame.Rect(
        x,
        random.randint(150,550),
        30,
        30
    )

# =========================================================
# INITIALIZE GAME OBJECTS
# =========================================================
def setup_objects():

    pipes.clear()
    coin_list.clear()
    enemies.clear()
    magnets.clear()
    shields.clear()

    # Pipes
    for i in range(3):

        p = create_pipe()

        p[0].x += i * 260
        p[1].x += i * 260

        pipes.append(p)

    # Coins
    for i in range(4):
        coin_list.append(create_coin(500 + i * 300))

    # Enemies
    for i in range(2):
        enemies.append(create_enemy(900 + i * 500))

    # Magnet
    magnets.append(create_magnet(1400))

    # Shield
    shields.append(create_shield(2000))

setup_objects()

# =========================================================
# SHOP
# =========================================================
shop_open = False

bird_buttons = []

for i in range(len(birds)):

    rect = pygame.Rect(
        60,
        180 + i * 120,
        400,
        90
    )

    bird_buttons.append(rect)

# =========================================================
# SAVE GAME
# =========================================================
def save_game():

    data = {
        "highscore":HIGH_SCORE,
        "coins":coins,
        "best_distance":BEST_DISTANCE,
        "unlocked":unlocked,
        "selected":selected_bird
    }

    with open(SAVE_FILE,"w") as f:
        json.dump(data,f)

# =========================================================
# PARTICLES
# =========================================================
def add_particles(x,y,color):

    for i in range(8):

        particles.append([
            x,
            y,
            random.randint(-4,4),
            random.randint(-4,4),
            random.randint(3,7),
            color
        ])

# =========================================================
# DRAW FUNCTIONS
# =========================================================
# =========================================================
# BETTER PIPE DRAWING
# =========================================================
def draw_pipe(rect):

    # Main pipe
    pygame.draw.rect(
        screen,
        (0,180,0),
        rect,
        border_radius=8
    )

    # Dark side
    pygame.draw.rect(
        screen,
        (0,120,0),
        (
            rect.x + rect.width - 12,
            rect.y,
            12,
            rect.height
        ),
        border_radius=8
    )

    # Light highlight
    pygame.draw.rect(
        screen,
        (120,255,120),
        (
            rect.x + 6,
            rect.y,
            8,
            rect.height
        ),
        border_radius=8
    )

    # Pipe cap
    cap_height = 24

    pygame.draw.rect(
        screen,
        (0,220,0),
        (
            rect.x - 10,
            rect.bottom - cap_height if rect.y == 0 else rect.y,
            rect.width + 20,
            cap_height
        ),
        border_radius=6
    )

    # Outline
    pygame.draw.rect(
        screen,
        (0,80,0),
        rect,
        3,
        border_radius=8
    )

# =========================================================
# DRAW CITY
# =========================================================
def draw_city():

    for b in buildings:

        x,y,w,h = b
        # Main building
        pygame.draw.rect(
            screen,
            (35,35,60),
            (x,y,w,h),
            border_radius=4
        )
        # Dark side shadow
        pygame.draw.rect(
            screen,
            (20,20,35),
            (
                x + w - 10,
                y,
                10,
                h
               ),
            border_radius=4
            )
        # Top highlight
        pygame.draw.rect(
            screen,
            (60,60,90),
            (
                x,
                y,
                w,
                8
                ),
            border_radius=4
         )
        
        
        

        # Move buildings
        b[0] -= 0.3

        # Loop
        if b[0] < -100:

            b[0] = WIDTH + random.randint(20,80)

            b[3] = random.randint(120,320)

            b[2] = random.randint(50,90)

            b[1] = HEIGHT - 30 - b[3]
            
def draw_clouds():

    for c in clouds:

        pygame.draw.ellipse(
            screen,
            WHITE,
            (c[0],c[1],c[2],40)
        )

        c[0] -= 1

        if c[0] < -120:
            c[0] = WIDTH + 50

def draw_bird():

    global wing_angle
    global wing_dir

    wing_angle += wing_dir * 3

    if wing_angle > 20:
        wing_dir = -1

    if wing_angle < -20:
        wing_dir = 1

    color = birds[selected_bird]["color"]

    pygame.draw.circle(
        screen,
        color,
        (bird_x,int(bird_y)),
        bird_size
    )

    wing_y = bird_y + math.sin(
        math.radians(wing_angle)
    ) * 10

    pygame.draw.ellipse(
        screen,
        WHITE,
        (bird_x - 12, wing_y, 22, 12)
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (bird_x + 8,int(bird_y)-5),
        3
    )

    if shield_active:

        pygame.draw.circle(
            screen,
            CYAN,
            (bird_x,int(bird_y)),
            bird_size + 8,
            3
        )

def draw_particles():
    
    for p in particles:

        pygame.draw.circle(
            screen,
            p[5],
            (int(p[0]),int(p[1])),
            p[4]
        )

        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 0.15

    particles[:] = [p for p in particles if p[4] > 0]
    # ==============================
# WEATHER SYSTEM
# ==============================
def draw_weather():

    global wind_force
    global wind_timer

    global rain_active
    global rain_timer
    global rain_duration

    # STOP WEATHER ON GAME OVER
    if game_over:
        return

    # ==========================
    # WIND TIMER
    # ==========================
    wind_timer += 1

    if wind_timer > 180:

        wind_force = random.choice([
            -0.08,
            -0.04,
            0,
            0.04,
            0.08
        ])

        wind_timer = 0

    # ==========================
    # RAIN TIMER
    # ==========================
    rain_timer += 1

    # START RAIN
    if not rain_active and rain_timer > 900:

        rain_active = True

        rain_duration = random.randint(300,500)

        rain_timer = 0

    # STOP RAIN
    if rain_active:

        rain_duration -= 1

        if rain_duration <= 0:

            rain_active = False

    # ==========================
    # DRAW RAIN
    # ==========================
    if rain_active:

        for r in rain_drops:

            pygame.draw.line(

                screen,
                CYAN,

                (r[0], r[1]),
                (r[0] - 3, r[1] + 12),

                2
            )

            r[0] += wind_force * 8
            r[1] += r[2]

            if r[1] > HEIGHT:

                r[0] = random.randint(0, WIDTH)
                r[1] = -20

# =========================================================
# RESET GAME
# =========================================================
def reset_game():

    global bird_y
    global bird_velocity
    global score
    global distance
    global game_over
    global pipe_speed
    global magnet_active
    global shield_active
    global magnet_timer
    global shield_timer
    global moving_pipe_mode
    global moving_pipe_timer
    global next_moving_pipe_distance

    bird_y = HEIGHT // 2
    bird_velocity = 0

    score = 0
    distance = 0
    pipe_speed = 4
    lives = 3
    invincible_timer = 0

    magnet_active = False
    shield_active = False

    magnet_timer = 0
    shield_timer = 0
    moving_pipe_mode = False
    moving_pipe_timer = 0
    next_moving_pipe_distance = 1000

    particles.clear()

    # IMPORTANT FIX
    setup_objects()

    game_over = False

# =========================================================
# =========================================================
# PHOENIX INTRO
# =========================================================
def intro_animation():

    intro_running = True

    title = "PHOENIX"

    shown_text = ""

    letter_index = 0

    text_timer = 0

    blink_timer = 0

    show_press = True

    title_font = pygame.font.SysFont("algerian",90)

    while intro_running:

        clock.tick(60)

        # EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    intro_running = False

        # BACKGROUND
        screen.fill((10,10,30))

        # =====================================
        # TYPEWRITER EFFECT
        # =====================================
        text_timer += 1

        if text_timer > 15 and letter_index < len(title):

            shown_text += title[letter_index]

            # SOUND
            

            letter_index += 1

            text_timer = 0

        # =====================================
        # DRAW TITLE
        # =====================================
        title_surface = title_font.render(
            shown_text,
            True,
            ORANGE
        )

        glow = title_font.render(
            shown_text,
            True,
            YELLOW
        )

        screen.blit(glow,(78,198))
        screen.blit(title_surface,(80,200))

        # =====================================
        # BLINK TEXT
        # =====================================
        blink_timer += 1

        if blink_timer > 30:

            show_press = not show_press

            blink_timer = 0

        if show_press and letter_index == len(title):

            press = font.render(
                "PRESS SPACE TO START",
                True,
                WHITE
            )

            screen.blit(press,(120,420))

        # =====================================
        # SMALL SUBTITLE
        # =====================================
        quote_font = pygame.font.SysFont(
            "Algerian",
            38,
            bold=True
            )
        sub = quote_font.render(
            "    FLY BEYOND LIMITS.",
            True,
            CYAN
            )
        screen.blit(sub,(45,320))
        
            

        pygame.display.update()
# MAIN LOOP
# =========================================================
intro_animation()
running = True

while running:

    clock.tick(60)

    mouse_pos = pygame.mouse.get_pos()

    # =====================================================
    # EVENTS
    # =====================================================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            save_game()
            running = False

        # =================================================
        # MOUSE CLICK
        # =================================================
        if event.type == pygame.MOUSEBUTTONDOWN:
            # SHOP BUTTON CLICK
            if shop_button.collidepoint(mouse_pos):
                shop_open = not shop_open
            
                          



            if shop_open:

                for i,btn in enumerate(bird_buttons):

                    if btn.collidepoint(mouse_pos):

                        # SELECT
                        if i in unlocked:

                            selected_bird = i
                            save_game()

                        # BUY
                        else:
                            if (
                                coins >= birds[i]["cost"]
                                and
                                BEST_DISTANCE >= birds[i]["distance"]
                                ):
                                coins -= birds[i]["cost"]
                                unlocked.append(i)
                                selected_bird = i
                                save_game()

        # =================================================
        # KEYBOARD
        # =================================================
        if event.type == pygame.KEYDOWN:

            # SPACE
            if event.key == pygame.K_SPACE:

                # RESTART FIX
                if game_over:

                    reset_game()

                elif not shop_open:

                    bird_velocity = jump_power
                    
                    

                    add_particles(
                        bird_x - 10,
                        bird_y,
                        WHITE
                    )

            # SHOP
            if event.key == pygame.K_s:
                shop_open = not shop_open

    # =====================================================
    # BACKGROUND
    # =====================================================
    if score >= 10:
        night_mode = True

    if night_mode:
        screen.fill(DARK_BLUE)
    else:
        screen.fill(BLUE)

    draw_city()
    draw_clouds()
    draw_weather()
    
    
    # =====================================================
    # SHOP BUTTON
    # =====================================================
    shop_button = pygame.Rect(20, 10, 120, 45)
    pygame.draw.rect(
        screen,
        (220,40,40),
        shop_button,
        border_radius=10
    )
    pygame.draw.rect(
        screen,
        WHITE,
        shop_button,
        3,
        border_radius=10
    )
    if shop_open:
         button_text = "BACK"
    else:
        button_text = "SHOP"

    shop_text = font.render(
        button_text,
        True,
        WHITE
    )
    screen.blit(
    shop_text,
    (shop_button.x + 25, shop_button.y + 8)
    )
    # =====================================================
    # SHOP SCREEN
    # =====================================================
    if shop_open:
        title = big_font.render(
            "BIRD SHOP",
            True,
            WHITE
        )
        screen.blit(title,(110,60))
        for i,b in enumerate(birds):
            btn = bird_buttons[i]
            if btn.collidepoint(mouse_pos):
                color = (80,80,80)
            else:
                color = GRAY
            pygame.draw.rect(
                screen,
                color,
                btn,
                border_radius=15
                )

            # Bird Preview
            pygame.draw.circle(
                screen,
                b["color"],
                (100,btn.y + 45),
                25
            )
            # Name
            txt = font.render(
                b["name"],
                True,
                WHITE
            )
            screen.blit(txt,(150,btn.y + 12))
            # Status
            if i == selected_bird:

                status = font.render(
                    "USING",
                    True,
                    GREEN
                )

            elif i in unlocked:

                status = font.render(
                    "SELECT",
                    True,
                    CYAN
                )

            else:
                status = font.render(
                     f"{b['cost']} COINS + {b['distance']}m",
                     True,
                     YELLOW
                     )

                
                   
                    
                    
                

            screen.blit(status,(150,btn.y + 45))
            

    # =====================================================
    # GAME
    # =====================================================
    else:

        if not game_over:

            # Physics
            bird_velocity += gravity
            bird_y += bird_velocity
            bird_x += wind_force

            distance += pipe_speed * 0.1
            if distance > BEST_DISTANCE:
                BEST_DISTANCE = int(distance)
            # ==========================================
            # MOVING PIPE ACTIVATION
            # ==========================================
            if int(distance) >= next_moving_pipe_distance:
                if not moving_pipe_mode:
                    moving_pipe_mode = True
                    moving_pipe_timer = moving_pipe_duration
            # TIMER
            if moving_pipe_mode:
                moving_pipe_timer -= 1
                if moving_pipe_timer <= 0:
                    moving_pipe_mode = False
                    next_moving_pipe_distance += 1000

            bird_rect = pygame.Rect(
                bird_x - bird_size,
                bird_y - bird_size,
                bird_size * 2,
                bird_size * 2
            )

            # Ground
            if bird_y > HEIGHT - 40:

                game_over = True

                if score > HIGH_SCORE:
                    HIGH_SCORE = score

                save_game()

            # Ceiling
            if bird_y < 0:
                bird_y = 0
                # SIDE WALLS
                if bird_x < 40:
                    bird_x = 40
                    if bird_x > WIDTH - 40:
                        bird_x = WIDTH - 40

            # =================================================
            # PIPES
            # =================================================
            for top,bottom in pipes:

                top.x -= pipe_speed
                bottom.x -= pipe_speed
                # ==========================================
                # MOVING PIPE
                # ==========================================
                if moving_pipe_mode:
                    move_offset = math.sin(
                        pygame.time.get_ticks() * 0.00008 + top.x*0.02
                        ) * 50
                    current_gap = 220
                    top.height = round(250 + move_offset)
                    bottom.y = top.height + current_gap

                if top.x < -100:

                    new_pipe = create_pipe()

                    top.x = WIDTH + 250
                    bottom.x = WIDTH + 250

                    top.height = new_pipe[0].height

                    bottom.y = new_pipe[1].y
                    bottom.height = new_pipe[1].height

                    score += 1

                    if score % 5 == 0:
                        pipe_speed += 0.4

                draw_pipe(top)
                draw_pipe(bottom)

                # Collision
                if bird_rect.colliderect(top) or bird_rect.colliderect(bottom):

                    if shield_active:
                        shield_active = False
                    else:

                        game_over = True

                        if score > HIGH_SCORE:
                            HIGH_SCORE = score

                        save_game()

            # =================================================
            # COINS
            # =================================================
            for c in coin_list:

                c.x -= pipe_speed

                if c.x < -50:

                    c.x = WIDTH + random.randint(300,700)
                    c.y = random.randint(100,600)

                # Magnet
                if magnet_active:

                    dx = bird_x - c.x
                    dy = bird_y - c.y

                    c.x += dx * 0.08
                    c.y += dy * 0.08
                coin_size = 12 + math.sin(pygame.time.get_ticks() * 0.01) * 3
                pygame.draw.circle(
                    screen,
                    (255,255,150),
                    (c.x + 12,c.y + 12),
                    int(coin_size) + 6
                )
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (c.x + 12,c.y + 12),
                    int(coin_size)
                )

                if bird_rect.colliderect(c):

                    coins += 1

                    add_particles(
                        c.x,
                        c.y,
                        YELLOW
                    )

                    save_game()

                    c.x = WIDTH + random.randint(300,700)
                    c.y = random.randint(100,600)

            # =================================================
            # MAGNETS
            # =================================================
            for m in magnets:

                m.x -= pipe_speed

                pygame.draw.circle(
                    screen,
                    CYAN,
                    (m.x + 15,m.y + 15),
                    15
                )

                if m.x < -50:

                    m.x = WIDTH + random.randint(1000,1500)
                    m.y = random.randint(150,550)

                if bird_rect.colliderect(m):

                    magnet_active = True
                    magnet_timer = 600

                    m.x = WIDTH + 2500

            # =================================================
            # SHIELDS
            # =================================================
            for s in shields:

                s.x -= pipe_speed

                pygame.draw.circle(
                    screen,
                    PURPLE,
                    (s.x + 15,s.y + 15),
                    15
                )

                if s.x < -50:

                    s.x = WIDTH + random.randint(1500,2200)
                    s.y = random.randint(150,550)

                if bird_rect.colliderect(s):

                    shield_active = True
                    shield_timer = 600

                    s.x = WIDTH + 3000

            # =================================================
            # TIMERS
            # =================================================
            if magnet_active:

                magnet_timer -= 1

                if magnet_timer <= 0:
                    magnet_active = False

            if shield_active:

                shield_timer -= 1

                if shield_timer <= 0:
                    shield_active = False

            # =================================================
            # ENEMIES
            # =================================================
            for e in enemies:

                e.x -= pipe_speed + 2

                pygame.draw.circle(
                    screen,
                    RED,
                    (e.x + 20,e.y + 20),
                    20
                )

                if e.x < -60:

                    e.x = WIDTH + random.randint(400,900)

                    e.y = random.choice([
                        random.randint(70,140),
                        random.randint(560,650)
                    ])

                if bird_rect.colliderect(e):

                    if shield_active:

                        shield_active = False
                        e.x = WIDTH + 500

                    else:

                        game_over = True

                        if score > HIGH_SCORE:
                            HIGH_SCORE = score

                        save_game()

            # =================================================
            # DRAW
            # =================================================
            draw_bird()
            draw_particles()

            # ==============================
            # IMPROVED GROUND / BASE
            # ==============================

            # Main ground
            pygame.draw.rect(
                screen,
                (30,120,40),
                (0, HEIGHT - 40, WIDTH, 40)
            )

            # Dark soil layer (depth effect)
            pygame.draw.rect(
                screen,
                (20,80,25),
                (0, HEIGHT - 10, WIDTH, 10)
            )
            
            # Small stones (random ground detail)
            for i in range(10):
                pygame.draw.circle(
                    screen,
                    (100,100,100),
                    (
                        random.randint(0, WIDTH),
                        HEIGHT - random.randint(5, 20)
                        ),
                    2
                )
            # ==========================================
            # MOVING PIPE WARNING
            # ==========================================
            remaining_distance = max(
                0,
                next_moving_pipe_distance - int(distance)
            )

            # UI
            ui = [
                f"Score: {score}",
                f"Distance: {int(distance)} m",
                
                f"Coins: {coins}",
                f"High Score: {HIGH_SCORE}",
                f"Best Distance: {BEST_DISTANCE} m",
                
            ]

            for i,text in enumerate(ui):

                t = font.render(
                    text,
                    True,
                    WHITE
                )

                screen.blit(
                    t,
                    (20,80 + i * 35)
                )
            # ==========================================
            # MOVING PIPE WARNING TEXT
            # ==========================================
            
            warning_text = font.render(
                f"DANGER ZONE IN: {remaining_distance}m",
                True,
                RED
            )
            screen.blit(
                warning_text,
                (WIDTH - 280, 20)
            )

        # =====================================================
        # GAME OVER
        # =====================================================
        else:
            

            over = big_font.render(
                "  GAME OVER",
                True,
                (255,40,40)
            )

            final = font.render(
                f"   Final Score: {score}",
                True,
                WHITE
            )

            restart = font.render(
                "    Press SPACE To Restart",
                True,
                WHITE
            )

            screen.blit(over,(80,250))
            screen.blit(final,(110,350))
            screen.blit(restart,(90,450))

    pygame.display.update()

pygame.quit()
sys.exit()
