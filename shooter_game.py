from pygame import *
from random import *
from time import time as timer
import sys
import os
 
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    elif hasattr(sys, "_MEIPASS2"):
        return os.path.join(sys._MEIPASS2, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)
 
image_folder = resource_path(".")
 
 
WIDTH = 700
HEIGHT = 500
FPS = 60
 
mixer.init()
back_music = os.path.join(image_folder, "space.ogg")
mixer.music.load(back_music)
mixer.music.set_volume(0.01)
mixer.music.play()
f_sound = os.path.join(image_folder, "fire.ogg")
fire_sound = mixer.Sound(f_sound)
fire_sound.set_volume(0.01)
clock = time.Clock()
 
display.set_caption("Shooter")
window = display.set_mode((WIDTH, HEIGHT))
back_img = os.path.join(image_folder, "galaxy.jpg")
background = transform.scale(image.load(back_img), (WIDTH, HEIGHT))
 
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
 
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
 
class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < WIDTH - 80:
            self.rect.x += self.speed
 
    def fire(self):
        img_bullet = os.path.join(image_folder, "bullet.png")
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)
        fire_sound.play()
 
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > WIDTH:
            self.rect.x = randint(80, WIDTH - 80)
            self.rect.y = 0
            lost += 1
 
class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()
 
font.init()
font1 = font.Font(None, 36)
lose = font1.render("YOU LOSE!", True, (255, 215, 0))
win = font1.render("YOU WIN!", True, (255, 255, 255))
 
img_ship = os.path.join(image_folder, "rocket.png")
ship = Player(img_ship, 5, HEIGHT - 100, 80, 100, 10)
 
bullets = sprite.Group()
monsters = sprite.Group()
for i in range(1, 6):
    img_ufo = os.path.join(image_folder, "ufo.png")
    monster = Enemy(img_ufo, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)
 
asteroids = sprite.Group()
for i in range(1, 3):
    img_asteroid = os.path.join(image_folder, "asteroid.png")
    asteroid = Enemy(img_asteroid, randint(30, WIDTH - 30), -40, 80, 50, randint(1, 7))
    asteroids.add(asteroid)
 
score = 0
lost = 0
max_lost = 10
goal = 20
life = 3
last_time = 0
rel_time = True
num_fire = 0    
finish = False
run = True 
 
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and not rel_time:
                    num_fire += 1
                    ship.fire()
                if num_fire >= 5 and not rel_time:
                    last_time = timer()
                    rel_time = True
 
    if not finish: # finish != True
        window.blit(background, (0, 0))
 
        score_text = font1.render('Счёт: '+ str(score), True, (255, 215, 0))
        window.blit(score_text, (10, 20))
        lost_text = font1.render('Пропущено: '+ str(lost), True, (255, 215, 0))
        window.blit(lost_text, (10, 50))
 
        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update()
 
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)
        ship.reset()
 
        if rel_time:
            now_time = timer()
 
            if now_time - last_time < 3:
                reload = font1.render("Перезарядка...", 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0
                rel_time = False
 
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for collide in collides:
            score += 1
            img_ufo = os.path.join(image_folder, "ufo.png")
            monster = Enemy(img_ufo, randint(80, WIDTH-80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
 
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life -= 1
 
        if life == 0 or lost >= max_lost:
            finish = True
            mixer.music.stop()
            window.blit(lose, (200, 200))
 
        if score >= goal:
            finish = True
            mixer.music.stop()
            window.blit(win, (200, 200))
 
        if life == 3:
            life_color = (0, 150, 0)
        if life == 2:
            life_color = (150, 150, 0)
        if life == 1:
            life_color = (150, 0, 0)
 
        text_life = font1.render("Жизни: " + str(life), 1, life_color)
        window.blit(text_life, (550, 10))
 
    else:
        finish = False
        score = 0
        lost = 0
        num_fire = 0
        life = 3
        mixer.music.load(back_music)
        mixer.music.set_volume(0.01)
        mixer.music.play()
 
        for bullet in bullets:
            bullet.kill()
 
        for monster in monsters:
            monster.kill()
 
        for asteroid in asteroids:
            asteroid.kill()
 
        time.delay(3000)
        for i in range(1, 6):
            img_ufo = os.path.join(image_folder, "ufo.png")
            monster = Enemy(img_ufo, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
        for i in range(1, 3):
            img_asteroid = os.path.join(image_folder, "asteroid.png")
            asteroid = Enemy(img_asteroid, randint(30, WIDTH - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(asteroid)   
 
    time.delay(50)
    display.update()
    clock.tick(FPS)