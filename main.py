from includes import *

def draw_game(dt_scale):
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, border_color, border_rect, border_thickness)

    for ball in balls:
        if not ball.dead:
            if pygame.time.get_ticks() - ball.hit_flash_time < ball.flash_duration:
                flash_color = brighten_color(ball.base_color, 100)
                pygame.draw.circle(screen, (0, 0, 0), (int(ball.pos[0]), int(ball.pos[1])), ball.radius + 3)
                pygame.draw.circle(screen, flash_color, (int(ball.pos[0]), int(ball.pos[1])), ball.radius)
            else:
                pygame.draw.circle(screen, (0, 0, 0), (int(ball.pos[0]), int(ball.pos[1])), ball.radius + 3)
                pygame.draw.circle(screen, ball.base_color, (int(ball.pos[0]), int(ball.pos[1])), ball.radius)
                
    for ball in balls:
        if not ball.dead:
            if ball.type != "unarmed":
                ball.weapon.draw(dt_scale)
            text_surface = font.render(str(int(ball.health)), True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=ball.pos)
            screen.blit(text_surface, text_rect)

    for i, ball in enumerate(balls):
        pos = (50 + i * 200, 750)
        write_stats(screen, ball, pos, font)

def countdown_overlay():
    countdown_texts = ["3", "2", "1", "GO"]
    for text in countdown_texts:
        draw_game(1)
        overlay = font.render(text, True, (0, 0, 0))
        rect = overlay.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(overlay, rect)
        pygame.display.flip()
        pygame.event.pump()
        start_time = pygame.time.get_ticks()
        wait_time = 1000 if text != "GO" else 500
        while pygame.time.get_ticks() - start_time < wait_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

def start_game(types):
    balls = []
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    radius = 200
    for i, t in enumerate(types):
        angle = math.radians(360 / len(types) * i)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        balls.append(Ball([x, y], t))
    return balls

ball_types = ["sword", "bow"]
balls = start_game(ball_types)

for i, ball in enumerate(balls):
    if ball.type != "unarmed":
        ball.weapon.spin_speed *= (-1 if i % 2 else 1) # Every other ball is facing the other way

clock = pygame.time.Clock()
FPS = 240

countdown_overlay()
clock.tick()

frames = 0
_frames = 0

running = True
while running:
    dt_scale = clock.tick(FPS) / 1000 * 60  # Feels like 60 FPS (what it was before)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_game(dt_scale)
    weapon_check_all(balls, dt_scale)
    pygame.display.flip()

    frames += 1
    if frames >= FPS / 2: # 2 Times a second
        if _frames >= 2: # 1 Time a second
            for ball in balls:
                if ball.type == "bow":
                    for i in range(ball.weapon.arrows):
                        pass # fire arrows

        for ball in balls:
            if ball.type == "unarmed":
                ball.speed += 1
                if ball.speed > ball.max_speed:
                    ball.speed = ball.max_speed
        _frames += 1
        frames = 0

    move_balls(balls, dt_scale)
    handle_collisions(balls)

pygame.quit()
