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

    write_stats(screen, ball1, (50, 750), font)
    write_stats(screen, ball2, (450, 750), font)

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

def start_game(balls=["sword","spear"]):
    if len(balls) == 2:
        ball1 = Ball([float(WIDTH // 2) - 100, float(HEIGHT // 2)], balls[0])
        ball2 = Ball([float(WIDTH // 2) + 100, float(HEIGHT // 2)], balls[1])
        return [ball1,ball2]

balls = start_game(["sword", "spear"])
ball1 = balls[0]
ball2 = balls[1]

if ball1.type != "unarmed":
    ball1.weapon.spin_speed *= -1

clock = pygame.time.Clock()
FPS = 240

countdown_overlay()
clock.tick()

frames = 0

running = True
while running:
    dt_scale = clock.tick(FPS) / 1000 * 60 # Feels like 60 FPS (what it was before)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_game(dt_scale)
    weapon_check(ball1, ball2, dt_scale)

    pygame.display.flip()
    frames += 1
    if frames >= FPS / 2: # 2 Times a second
        for ball in balls:
            if ball.type == "unarmed":
                ball.speed += 1
                if ball.speed > ball.max_speed:
                    ball.speed = ball.max_speed
        frames = 0

    move_balls(balls, dt_scale)

    handle_collision(ball1, ball2)

pygame.quit()
