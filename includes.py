import random
import pygame
import math

# Pygame setup

pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Sim")

border_size = 650
border_thickness = 5
border_color = (0, 0, 0)
border_rect = pygame.Rect(
    (WIDTH - border_size) // 2,
    (HEIGHT - border_size) // 2,
    border_size,
    border_size,
)
font = pygame.font.Font(None, 50)

# Classes

class Ball():
    def __init__(self, pos, type):
        self.pos = pos
        self.radius = 50
        raw_dir = [random.choice([-1, 1]) * random.random(), random.choice([-1, 1]) * random.random()]
        self.direction = normalize(raw_dir)
        self.base_speed = 10
        self.health = 100
        self.dead = False
        self.damage = 1
        self.knockback_velocity = [0, 0]
        self.hit_flash_time = 0
        self.flash_duration = 200
        self.type = type

        if type == "sword":
            self.color = (243, 65, 55)
        elif type == "unarmed":
            self.color = (240, 240, 240)
        elif type == "spear":
            self.color = (235, 45, 235)
        elif type == "dagger":
            self.color = (45, 235, 45)
        elif type == "bow":
            self.color = (255, 255, 20)

        self.base_color = self.color

        if type == "unarmed":
            self.base_speed = 4
            self.max_speed = 1
            self.speed = 1
            self.attack_debounce = 300
            self.debounce = 0
        elif type == "dagger":
            self.weapon = Weapon(self)
            self.attack_debounce = 250
            self.debounce = 0
        else:
            self.weapon = Weapon(self)
            self.attack_debounce = 500
            self.debounce = 0

    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash_time = pygame.time.get_ticks()
        if self.health <= 0:
            self.dead = True

class Weapon():
    def __init__(self, ball):
        self.ball = ball
        if ball.type == "sword":
            self.length = 100
            self.width = 50
            self.spin_speed = 3
        elif ball.type == "spear":
            self.length = 100
            self.width = 40
            self.spin_speed = 2
        elif ball.type == "dagger":
            self.length = 55
            self.width = 35
            self.spin_speed = 10
        elif ball.type == "bow":
            self.length = 40
            self.width = 100
            self.spin_speed = 3
            self.arrows = 1
        
        self.angle = random.randint(0, 359)
        self.colour = self.ball.color

    def draw(self, dt_scale):
        self.angle += self.spin_speed * dt_scale
        rad = math.radians(self.angle)
        offset_x = math.cos(rad) * (self.ball.radius + 5 + self.length / 2)
        offset_y = math.sin(rad) * (self.ball.radius + 5 + self.length / 2)
        weapon_surf = pygame.Surface((self.width, self.length), pygame.SRCALPHA)
        pygame.draw.rect(weapon_surf, self.colour, (0, 0, self.width, self.length))
        rotated_surf = pygame.transform.rotate(weapon_surf, -self.angle - 90)
        rect_center = (self.ball.pos[0] + offset_x, self.ball.pos[1] + offset_y)
        rotated_rect = rotated_surf.get_rect(center=rect_center)
        screen.blit(rotated_surf, rotated_rect)
        return rect_center, self.angle

# Helper Functions

def normalize(vec):
    x, y = vec
    length = math.sqrt(x*x + y*y)
    if length == 0:
        return [1, 0]
    return [x / length, y / length]

def brighten_color(color, amount=60):
    r = min(color[0] + amount, 255)
    g = min(color[1] + amount, 255)
    b = min(color[2] + amount, 255)
    return (r, g, b)

# Text

def write(screen, text, pos, font):
    text_surface = font.render(text, True, (0, 0, 0))
    screen.blit(text_surface, pos)

def write_stats(screen, ball, pos, font):
    if ball.type == "unarmed":
        write(screen, "Damage/Speed: " + str(ball.speed), pos, font)
    elif ball.type == "sword":
        write(screen, "Damage: " + str(ball.damage), pos, font)
    elif ball.type == "spear":
        write(screen, "Damage/Length: " + str(ball.damage), pos, font)
    elif ball.type == "dagger":
        write(screen, "Attack Speed: " + str(abs(ball.weapon.spin_speed)), pos, font)

# Collisions

def handle_collision(ball1, ball2):
    if not ball1.dead and not ball2.dead:
        dx = ball2.pos[0] - ball1.pos[0]
        dy = ball2.pos[1] - ball1.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        min_dist = ball1.radius + ball2.radius

        if dist < min_dist:
            nx = dx / dist
            ny = dy / dist

            p1 = ball1.direction[0]*nx + ball1.direction[1]*ny
            p2 = ball2.direction[0]*nx + ball2.direction[1]*ny

            ball1.direction[0] += (p2 - p1) * nx * 1.1
            ball1.direction[1] += (p2 - p1) * ny * 1.1
            ball2.direction[0] += (p1 - p2) * nx * 1.1
            ball2.direction[1] += (p1 - p2) * ny * 1.1

            ball1.direction = normalize(ball1.direction)
            ball2.direction = normalize(ball2.direction)

            overlap = 1 * (min_dist - dist)
            ball1.pos[0] -= overlap * nx
            ball1.pos[1] -= overlap * ny
            ball2.pos[0] += overlap * nx
            ball2.pos[1] += overlap * ny

            if ball1.type == "unarmed":
                if pygame.time.get_ticks() >= ball1.debounce:
                    ball1.max_speed += 1
                    ball2.take_damage(ball1.speed)
                    ball1.speed = 1
                    ball1.debounce = pygame.time.get_ticks() + ball1.attack_debounce

            if ball2.type == "unarmed":
                if pygame.time.get_ticks() >= ball2.debounce:
                    ball2.max_speed += 1
                    ball1.take_damage(ball2.speed)
                    ball2.speed = 1
                    ball2.debounce = pygame.time.get_ticks() + ball2.attack_debounce

def weapons_collide(weapon1_center, weapon1_length, weapon2_center, weapon2_length):
    r1 = weapon1_length / 2
    r2 = weapon2_length / 2
    
    dx = weapon2_center[0] - weapon1_center[0]
    dy = weapon2_center[1] - weapon1_center[1]
    dist_sq = dx*dx + dy*dy

    return dist_sq <= (r1 + r2) ** 2

def weapon_hits_ball(weapon_center, weapon_angle, weapon_length, weapon_width, target_ball):
    rad = math.radians(weapon_angle)

    half_len = weapon_length / 2
    half_wid = weapon_width / 2

    dx = target_ball.pos[0] - weapon_center[0]
    dy = target_ball.pos[1] - weapon_center[1]

    local_x = dx * math.cos(rad) + dy * math.sin(rad)
    local_y = -dx * math.sin(rad) + dy * math.cos(rad)
    
    if (-half_wid - target_ball.radius <= local_x <= half_wid + target_ball.radius and
        -half_len - target_ball.radius <= local_y <= half_len + target_ball.radius):
        return True
    return False

def move_balls(balls, dt_scale):
    for ball in balls:
        if not ball.dead:
            if ball.type == "unarmed":
                ball.pos[0] += ball.direction[0] * ball.base_speed * ball.speed * dt_scale
                ball.pos[1] += ball.direction[1] * ball.base_speed * ball.speed * dt_scale
            else:
                ball.pos[0] += ball.direction[0] * ball.base_speed * dt_scale
                ball.pos[1] += ball.direction[1] * ball.base_speed * dt_scale

            ball.pos[0] += ball.knockback_velocity[0] * dt_scale
            ball.pos[1] += ball.knockback_velocity[1] * dt_scale
            
            decay = 0.8 ** dt_scale
            ball.knockback_velocity[0] *= decay
            ball.knockback_velocity[1] *= decay

            if ball.pos[0] - ball.radius <= border_rect.left or ball.pos[0] + ball.radius >= border_rect.right:
                ball.direction[0] *= -1

            if ball.pos[1] - ball.radius <= border_rect.top or ball.pos[1] + ball.radius >= border_rect.bottom:
                ball.direction[1] *= -1

            if ball.pos[0] + ball.radius > border_rect.right:
                ball.pos[0] = border_rect.right - ball.radius - 1

            if ball.pos[0] - ball.radius < border_rect.left:
                ball.pos[0] = border_rect.left + ball.radius + 1

            if ball.pos[1] + ball.radius > border_rect.bottom:
                ball.pos[1] = border_rect.bottom - ball.radius - 1

            if ball.pos[1] - ball.radius < border_rect.top:
                ball.pos[1] = border_rect.top + ball.radius + 1

def handle_collisions(balls):
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            handle_collision(balls[i], balls[j])

def weapon_check_all(balls, dt_scale):
    weapon_info = {}
    for ball in balls:
        if not ball.dead and ball.type != "unarmed":
            weapon_center, weapon_angle = ball.weapon.draw(dt_scale)
            weapon_info[ball] = (weapon_center, ball.weapon.length)
            for opponent in balls:
                if opponent is not ball and not opponent.dead:
                    if weapon_hits_ball(weapon_center, weapon_angle, ball.weapon.length, ball.weapon.width, opponent):
                        if pygame.time.get_ticks() >= ball.debounce:
                            opponent.take_damage(ball.damage)
                            if opponent.type == "unarmed":
                                opponent.speed = 1
                            dx = opponent.pos[0] - weapon_center[0]
                            dy = opponent.pos[1] - weapon_center[1]
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist != 0:
                                nx = dx / dist
                                ny = dy / dist
                                dot = opponent.direction[0] * nx + opponent.direction[1] * ny
                                opponent.direction[0] -= 2 * dot * nx
                                opponent.direction[1] -= 2 * dot * ny
                                opponent.direction = normalize(opponent.direction)
                                knockback_strength = 8 * dt_scale
                                opponent.knockback_velocity[0] += nx * knockback_strength
                                opponent.knockback_velocity[1] += ny * knockback_strength
                            ball.debounce = pygame.time.get_ticks() + ball.attack_debounce
                            if ball.type == "sword":
                                ball.damage += 1
                            elif ball.type == "spear":
                                ball.damage += 0.5
                                ball.weapon.length += 10
                            elif ball.type == "dagger":
                                ball.weapon.spin_speed += 3 * (ball.weapon.spin_speed / abs(ball.weapon.spin_speed))

    weapon_balls = [b for b in balls if b.type != "unarmed" and not b.dead]
    for i in range(len(weapon_balls)):
        for j in range(i + 1, len(weapon_balls)):
            ball1, ball2 = weapon_balls[i], weapon_balls[j]
            w1_center, w1_length = weapon_info[ball1]
            w2_center, w2_length = weapon_info[ball2]
            if pygame.time.get_ticks() >= getattr(ball1.weapon, "hit_debounce", 0) and \
               pygame.time.get_ticks() >= getattr(ball2.weapon, "hit_debounce", 0):
                if weapons_collide(w1_center, w1_length, w2_center, w2_length):
                    ball1.weapon.spin_speed *= -1
                    ball2.weapon.spin_speed *= -1
                    now = pygame.time.get_ticks()
                    ball1.weapon.hit_debounce = now + 300
                    ball2.weapon.hit_debounce = now + 300
