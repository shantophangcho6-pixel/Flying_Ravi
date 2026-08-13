import pygame, random

pygame.init()

# ================= WINDOW =================
W, H = 700, 1000
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Ultimate Flying Game")
clock = pygame.time.Clock()

# ================= COLORS =================
SKY = (135, 206, 235)
WHITE = (255, 255, 255)
GREEN = (35, 150, 65)
DARK_GREEN = (20, 110, 45)
GROUND = (220, 185, 120)
BROWN = (170, 130, 75)
RED = (230, 55, 55)
BLACK = (20, 20, 20)
YELLOW = (255, 220, 40)
BLUE = (50, 130, 220)

font = pygame.font.SysFont(None, 38, True)
big = pygame.font.SysFont(None, 65, True)
small = pygame.font.SysFont(None, 24, True)

# ================= AUDIO =================
try:
    pygame.mixer.init()

    pygame.mixer.music.load("kishan.mp3")

    over_sound = pygame.mixer.Sound("k.mp3")

except:
    over_sound = None

# ================= PLAYER =================
try:
    bird = pygame.image.load(
        "kishan.png"
    ).convert_alpha()

    bird = pygame.transform.scale(
        bird, (70, 70)
    )

except:
    bird = None

# ================= GAME VARIABLES =================
player_x = 130
player_y = H // 2
velocity = 0

gravity = 0.48
jump = -9

pipe_w = 75
gap = 220
pipe_x = W
pipe_h = random.randint(180, 450)

speed = 4

score = 0
best = 0

started = False
game_over = False
paused = False

sound_done = False

clouds = []
particles = []

# ================= CLOUDS =================
for i in range(8):
    clouds.append([
        random.randint(0, W),
        random.randint(60, 350),
        random.randint(50, 100),
        random.uniform(0.3, 0.8)
    ])

# ================= BUTTONS =================
def get_buttons():

    return {
        "pause":
        pygame.Rect(W - 120, 20, 100, 45),

        "restart":
        pygame.Rect(
            W // 2 - 100,
            H // 2 + 70,
            200,
            55
        )
    }


# ================= PARTICLES =================
def make_particle(x, y):

    particles.append([
        x,
        y,
        random.uniform(-2, 2),
        random.uniform(-2, 2),
        30
    ])


# ================= RESET =================
def reset_game():

    global player_y, velocity
    global pipe_x, pipe_h
    global score, speed
    global game_over, started
    global sound_done, paused
    global particles

    # STOP OLD GAME-OVER SOUND
    if over_sound:
        try:
            over_sound.stop()
        except:
            pass

    # RESTART BACKGROUND MUSIC
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.play(-1)
    except:
        pass

    player_y = H // 2
    velocity = 0

    pipe_x = W
    pipe_h = random.randint(180, 450)

    score = 0
    speed = 4

    game_over = False
    started = True
    sound_done = False
    paused = False

    particles.clear()


# ================= GAME OVER =================
def die():

    global game_over
    global sound_done
    global best

    if game_over:
        return

    game_over = True
    best = max(best, score)

    try:

        pygame.mixer.music.stop()

        if over_sound:

            over_sound.stop()
            over_sound.play()

    except:
        pass

    sound_done = True


# ================= EVENTS =================
running = True

while running:

    dt = clock.tick(60) / 16.67

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # ================= TOUCH / MOUSE =================
        elif event.type == pygame.MOUSEBUTTONDOWN:

            x, y = event.pos
            buttons = get_buttons()

            # GAME OVER
            if game_over:

                if buttons["restart"].collidepoint(x, y):
                    reset_game()

            # PAUSE
            elif buttons["pause"].collidepoint(x, y):

                paused = not paused

            # FLY
            else:

                started = True
                velocity = jump

                for _ in range(3):
                    make_particle(
                        player_x,
                        player_y + 35
                    )

        # ================= KEYBOARD =================
        elif event.type == pygame.KEYDOWN:

            if event.key in (
                pygame.K_SPACE,
                pygame.K_UP
            ):

                if game_over:
                    reset_game()

                else:
                    started = True
                    velocity = jump

            elif event.key == pygame.K_p:

                paused = not paused

            elif event.key == pygame.K_r:

                reset_game()

    # =================================================
    # GAME UPDATE
    # =================================================

    if started and not game_over and not paused:

        # ---------- PLAYER ----------
        velocity += gravity * dt
        player_y += velocity * dt

        # ---------- PARTICLES ----------
        if random.random() < 0.25:

            make_particle(
                player_x,
                player_y + 35
            )

        # ---------- PIPE ----------
        pipe_x -= speed * dt

        if pipe_x < -pipe_w:

            pipe_x = W

            pipe_h = random.randint(
                150,
                max(180, 430 - score * 3)
            )

            score += 1

            # Gradually harder
            speed = min(
                8,
                4 + score * 0.08
            )

        # ---------- COLLISION ----------
        player_rect = pygame.Rect(
            player_x + 10,
            int(player_y + 10),
            50,
            50
        )

        top_pipe = pygame.Rect(
            pipe_x,
            0,
            pipe_w,
            pipe_h
        )

        bottom_pipe = pygame.Rect(
            pipe_x,
            pipe_h + gap,
            pipe_w,
            H
        )

        if (
            player_rect.colliderect(top_pipe)
            or
            player_rect.colliderect(bottom_pipe)
        ):
            die()

        # ---------- SKY / GROUND ----------
        if (
            player_y < 0
            or
            player_y > H - 120
        ):
            die()

    # =================================================
    # DRAW SKY
    # =================================================

    screen.fill(SKY)

    # ================= CLOUDS =================
    for cloud in clouds:

        cloud[0] -= cloud[3] * dt

        if cloud[0] < -150:

            cloud[0] = W + 100
            cloud[1] = random.randint(60, 350)

        pygame.draw.ellipse(
            screen,
            WHITE,
            (
                int(cloud[0]),
                int(cloud[1]),
                cloud[2],
                35
            )
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(cloud[0] + 25),
                int(cloud[1] - 10)
            ),
            25
        )

    # =================================================
    # PIPES
    # =================================================

    # TOP
    pygame.draw.rect(
        screen,
        DARK_GREEN,
        (
            pipe_x,
            0,
            pipe_w,
            pipe_h
        )
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            pipe_x - 7,
            pipe_h - 25,
            pipe_w + 14,
            25
        )
    )

    # BOTTOM
    pygame.draw.rect(
        screen,
        DARK_GREEN,
        (
            pipe_x,
            pipe_h + gap,
            pipe_w,
            H
        )
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            pipe_x - 7,
            pipe_h + gap,
            pipe_w + 14,
            25
        )
    )

    # =================================================
    # GROUND
    # =================================================

    pygame.draw.rect(
        screen,
        GROUND,
        (
            0,
            H - 80,
            W,
            80
        )
    )

    # Moving ground pattern
    offset = int(
        -score * speed
    ) % 40

    for x in range(
        offset,
        W,
        40
    ):

        pygame.draw.line(
            screen,
            BROWN,
            (x, H - 80),
            (x + 20, H),
            5
        )

    # =================================================
    # PLAYER
    # =================================================

    if bird:

        angle = max(
            -25,
            min(45, velocity * 3)
        )

        image = pygame.transform.rotate(
            bird,
            angle
        )

        screen.blit(
            image,
            image.get_rect(
                center=(
                    player_x + 35,
                    int(player_y) + 35
                )
            )
        )

    else:

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                player_x + 35,
                int(player_y) + 35
            ),
            30
        )

    # =================================================
    # PARTICLES
    # =================================================

    for p in particles[:]:

        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(p[0]),
                int(p[1])
            ),
            2
        )

        if p[4] <= 0:
            particles.remove(p)

    # =================================================
    # SCORE
    # =================================================

    score_text = font.render(
        str(score),
        True,
        BLACK
    )

    screen.blit(
        score_text,
        score_text.get_rect(
            center=(W // 2, 50)
        )
    )

    # =================================================
    # PAUSE BUTTON
    # =================================================

    if started and not game_over:

        b = get_buttons()

        pygame.draw.rect(
            screen,
            BLUE,
            b["pause"],
            border_radius=10
        )

        pause_text = small.render(
            "RESUME" if paused else "PAUSE",
            True,
            WHITE
        )

        screen.blit(
            pause_text,
            pause_text.get_rect(
                center=b["pause"].center
            )
        )

    # =================================================
    # START SCREEN
    # =================================================

    if not started:

        overlay = pygame.Surface(
            (W, H),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 80)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        title = big.render(
            "FLY!",
            True,
            YELLOW
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    W // 2,
                    H // 2 - 60
                )
            )
        )

        instruction = font.render(
            "TAP TO START",
            True,
            WHITE
        )

        screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    W // 2,
                    H // 2 + 20
                )
            )
        )

    # =================================================
    # GAME OVER
    # =================================================

    if game_over:

        overlay = pygame.Surface(
            (W, H),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 160)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        title = big.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    W // 2,
                    H // 2 - 70
                )
            )
        )

        result = font.render(
            f"Score: {score}   Best: {best}",
            True,
            WHITE
        )

        screen.blit(
            result,
            result.get_rect(
                center=(
                    W // 2,
                    H // 2
                )
            )
        )

        # PLAY AGAIN BUTTON
        b = get_buttons()

        pygame.draw.rect(
            screen,
            GREEN,
            b["restart"],
            border_radius=12
        )

        restart_text = font.render(
            "PLAY AGAIN",
            True,
            BLACK
        )

        screen.blit(
            restart_text,
            restart_text.get_rect(
                center=b["restart"].center
            )
        )

    # =================================================
    pygame.display.flip()

pygame.quit()