import random
import pygame
import os
import sys
import json
from pathlib import Path


size = width, height = 800, 800
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.font.init()


# 143
class Game:
    def __init__(self):
        self.data = {
            "apple": {
                "image": "apple.png"
            },
            "bad_apple": {
                "image": "bad_apple.png"
            },
            "snake": {
                "body": {
                    "image": "body.png",
                    "size": (20, 20)
                },
                "head": {
                    "image": "body.png",
                    "size": (20, 20)
                }
            },
            "text": {
                "font": "Arial"
            },
            "settings": {
                "game_speed": 60,
                "snake_speed": 5,
                "mega_apple_time": 10,
                "mega_apple_cost": 5,
                "bad_apple_cost": -2,
                "bad_apple_time": 5,
                "border_width": 10,
                "delete_bad_apples": 25,
                "platform_gains": [20, 30, 25, 25, 100000000000000000]
            }
        }

        self.sprites = pygame.sprite.Group()
        self.apples = pygame.sprite.Group()
        self.bodyes = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.txts = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.pause_logo = pygame.sprite.Group()
        self.start_text = pygame.sprite.Group()

        self.gran = 120
        self.platform_gain = self.data["settings"]["platform_gains"]
        self.redraw_platforms = False
        self.bad_apple_spawn = self.data["settings"]["bad_apple_time"]
        self.delete_bad_apples = self.data["settings"]["delete_bad_apples"]

        self.start = True
        self.all_board = [(x, y) for x in range(self.gran + 20 + 10, 800 - self.gran - 20 - 10)
                          for y in range(self.gran + 20 + 10, 800 - self.gran - 20 - 10)]

        self.all_bodyies = []

        self.count = 0
        self.high_count = self.first_open()

        self.pause = False

        self.apple = self.Apple(get_random_pos(self.all_board.copy(), self.all_bodyies), self)
        self.btn = self.Button("start game", 200, 100, (300, 340), self)
        self.snake = self.SnakeHead((390, 390), self.data["settings"]["snake_speed"], self)
        self.high_txt = self.Text(f"High score: {self.high_count}", 200, 80, (20, 5), 20, self.data["text"]["font"],
                                  self.txts)
        self.txt = self.Text(f"Score: {self.count}", 200, 80, (20, 35), 30, self.data["text"]["font"], self.txts)

        self.start_text_menu()

    def run(self):
        running = True
        screen.fill(pygame.Color(0, 0, 0))
        self.sprites.draw(screen)
        self.sprites.update()
        pygame.display.flip()
        tick = self.data["settings"]["game_speed"]
        clock.tick(tick)
        self.draw_borders()

        while running:
            if self.pause:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.last_close()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.pause = False
                            self.delete_pause()
                            continue
                screen.fill(pygame.Color(0, 0, 0))
                self.txts.update()
                self.sprites.draw(screen)
                self.platforms.draw(screen)
                self.pause_logo.draw(screen)
            elif not self.start:
                for event in pygame.event.get():
                    if not self.pause:
                        if event.type == pygame.QUIT:
                            self.last_close()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                self.pause = True
                                self.draw_pause()
                                continue

                            ys = self.snake.y_speed != 0
                            xs = self.snake.x_speed != 0
                            turns = [
                                (event.key == pygame.K_a or event.key == pygame.K_LEFT) and ys,
                                (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and ys,
                                (event.key == pygame.K_w or event.key == pygame.K_UP) and xs,
                                (event.key == pygame.K_s or event.key == pygame.K_DOWN) and xs
                            ]
                            if any(turns):
                                if not self.snake.turn:
                                    spd = self.data["settings"]["snake_speed"]
                                    self.snake.x_speed = turns[0] * -spd + turns[1] * spd
                                    self.snake.y_speed = turns[2] * -spd + turns[3] * spd

                                    self.snake.turn.append([self.snake.rect.x, self.snake.rect.y, self.snake.x_speed,
                                                            self.snake.y_speed])

                if self.redraw_platforms:
                    for i in self.platforms:
                        i.kill()
                    self.draw_borders()

                screen.fill(pygame.Color(0, 0, 0))
                self.txts.update()
                self.sprites.draw(screen)
                self.platforms.draw(screen)
                self.sprites.update()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.last_close()
                        sys.exit()
                    if pygame.mouse.get_pressed()[0]:
                        self.delete_text_menu()
                        self.btn.onPressed = True
                        self.start = False
                        running = True
                        self.btn.kill()
                    else:
                        self.btn.onPressed = False
                screen.fill(pygame.Color(0, 0, 0))
                self.start_text.update()
                self.sprites.draw(screen)
                self.buttons.update()

            pygame.display.flip()
            clock.tick(tick)

    def draw_borders(self):
        self.Platform((self.gran, self.gran), width - self.gran * 2, self.data["settings"]["border_width"],
                      self.platforms)
        self.Platform((self.gran, height - self.gran), width - self.gran * 2, self.data["settings"]["border_width"],
                      self.platforms)
        self.Platform((self.gran, self.gran), self.data["settings"]["border_width"], height - self.gran * 2,
                      self.platforms)
        self.Platform((width - self.gran - self.data["settings"]["border_width"], self.gran),
                      self.data["settings"]["border_width"], height - self.gran * 2, self.platforms)

    def draw_pause(self):
        self.Platform((width // 2 - 60, height // 2 - 60), 40, 120, self.pause_logo)
        self.Platform((width // 2 + 20, height // 2 - 60), 40, 120, self.pause_logo)

    def delete_pause(self):
        for i in self.pause_logo:
            i.kill()

    def first_open(self):
        my_file = Path("./statistic.txt")
        if my_file.is_file():
            with open('statistic.txt') as stats:
                data = json.load(stats)
                return data["high_score"]
        return 0

    def last_close(self):
        if self.count > self.high_count:
            data = {
                "high_score": self.count
            }
            with open('statistic.txt', 'w') as stats:
                json.dump(data, stats)
            return self.count
        return self.high_count

    def start_text_menu(self):
        ba = self.data["settings"]["mega_apple_cost"]
        bda = self.data["settings"]["bad_apple_cost"]
        self.Text(f" - apples to give 1 to your score", 200, 80, (30, 20), 30, self.data["text"]["font"],
                  self.start_text)
        self.Text(f" - big apple to give {ba} to your score", 200, 80, (30, 60), 30, self.data["text"]["font"],
                  self.start_text)
        self.Text(f" - poison apples to minus {bda} from your score", 200, 80, (30, 100), 30, self.data["text"]["font"],
                  self.start_text)
        self.Text(f"If you collide with white platform or your body, game will end.",
                  200, 80, (30, 140), 30, self.data["text"]["font"],
                  self.start_text)
        self.Apple((5, 25), self)
        self.MegaApple((-5, 55), self)
        self.BadApple((5, 105), self)

    def delete_text_menu(self):
        try:
            for i in range(3):
                self.apples.sprites()[1].kill()
        except IndexError:
            pass

        for i in self.start_text:
            i.kill()

    def refresh(self):
        self.sprites = pygame.sprite.Group()
        self.apples = pygame.sprite.Group()
        self.bodyes = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.txts = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.pause_logo = pygame.sprite.Group()

        self.gran = 120
        self.platform_gain = self.data["settings"]["platform_gains"]
        self.redraw_platforms = False
        self.bad_apple_spawn = self.data["settings"]["bad_apple_time"]
        self.delete_bad_apples = self.data["settings"]["delete_bad_apples"]

        self.start = True
        self.all_board = [(x, y) for x in range(self.gran + 20 + 10, 800 - self.gran - 20 - 10)
                          for y in range(self.gran + 20 + 10, 800 - self.gran - 20 - 10)]

        self.all_bodyies = []

        self.count = 0
        self.high_count = self.first_open()

        self.pause = False

        self.apple = self.Apple(get_random_pos(self.all_board.copy(), self.all_bodyies), self)
        self.btn = self.Button("start game", 200, 100, (300, 340), self)
        self.snake = self.SnakeHead((390, 390), self.data["settings"]["snake_speed"], self)
        self.high_txt = self.Text(f"High score: {self.high_count}", 200, 80, (20, 5), 20, self.data["text"]["font"],
                                  self.txts)
        self.txt = self.Text(f"Score: {self.count}", 200, 80, (20, 35), 30, self.data["text"]["font"], self.txts)

        self.draw_borders()
        self.start_text_menu()

    class Platform(pygame.sprite.Sprite):
        def __init__(self, pos, w, h, spr):
            super().__init__(spr)
            self.image = pygame.Surface((w, h))
            self.image.fill(pygame.Color("white"))
            self.rect = (pos, (w, h))

    class SnakeHead(pygame.sprite.Sprite):
        def __init__(self, pos, spd, game):
            super().__init__(game.sprites)
            self.image = load_image(game.data["snake"]["head"]["image"])
            self.rect = pygame.Rect(pos, game.data["snake"]["head"]["size"])
            self.x_speed = 0
            self.y_speed = spd
            self.turn = []
            self.pred = None
            self.last = self
            self.screen = screen
            self.game = game

        def update(self):
            check = pygame.sprite.spritecollideany(self, self.game.apples)
            if check:
                if check.type == 1 or check.type == 2:
                    for i in range(self.game.apple.cost):
                        body = Game.SnakeBody((self.last.rect.x - 20 * get_sign(self.last.x_speed)
                                               - 5 * get_sign(self.last.x_speed) * (i > 0),
                                               self.last.rect.y - 20 * get_sign(self.last.y_speed)
                                               - 5 * get_sign(self.last.y_speed) * (i > 0)),
                                              (self.last.x_speed, self.last.y_speed), self.game,
                                              self.game.count + i + 1)

                        self.game.all_bodyies.append(body)
                        if self.pred is None:
                            self.game.bodyes.remove(body)

                        self.last.pred = body
                        self.last = body

                    self.game.count += self.game.apple.cost
                    self.game.bad_apple_spawn -= self.game.apple.cost
                    self.game.delete_bad_apples -= self.game.apple.cost

                    if self.game.platform_gain[0] - self.game.apple.cost <= 0:
                        ost = self.game.platform_gain.pop(0)
                        self.game.platform_gain[0] -= ost - self.game.apple.cost
                        if len(self.game.platform_gain) == 4:
                            self.game.gran = 60
                        elif len(self.game.platform_gain) == 3:
                            self.game.gran = 30
                        elif len(self.game.platform_gain) == 2:
                            self.game.gran = 15
                        else:
                            self.game.gran = -20

                        if self.game.gran > 0:
                            self.game.all_board = [(x, y) for x in
                                                   range(self.game.gran + 20 + 10, 800 - self.game.gran - 20 - 10)
                                                   for y in
                                                   range(self.game.gran + 20 + 10, 800 - self.game.gran - 20 - 10)]
                        else:
                            self.game.all_board = [(x, y) for x in
                                                   range(20 + 10, 800 - self.game.gran - 20 - 10)
                                                   for y in
                                                   range(20 + 10, 800 - self.game.gran - 20 - 10)]

                        self.game.redraw_platforms = True
                    else:
                        self.game.platform_gain[0] -= self.game.apple.cost

                    check.kill()

                    if len(self.game.apples) and self.game.delete_bad_apples <= 0:
                        for i in self.game.apples:
                            i.kill()
                        self.game.delete_bad_apples = self.game.data["settings"]["delete_bad_apples"]

                    if self.game.count % self.game.data["settings"]["mega_apple_time"] == 0:
                        self.game.apple = Game.MegaApple(get_random_pos(self.game.all_board.copy(),
                                                                        self.game.all_bodyies), self.game)
                    else:
                        self.game.apple = Game.Apple(get_random_pos(self.game.all_board.copy(), self.game.all_bodyies),
                                                     self.game)

                    if self.game.bad_apple_spawn <= 0:
                        Game.BadApple(get_random_pos(self.game.all_board.copy(), self.game.all_bodyies), self.game)
                        self.game.bad_apple_spawn = self.game.data["settings"]["bad_apple_time"]

                    self.game.sprites.remove(self.game.txt)
                    self.game.txt = self.game.Text(f"Score: {self.game.count}", 200, 80, (20, 35), 30,
                                                   self.game.data["text"]["font"], self.game.txts)

                elif check.type == 3:
                    for i in range(abs(check.cost)):
                        self.game.all_bodyies.pop().kill()

                    self.last = self.game.all_bodyies[-1]

                    self.game.count += self.game.data["settings"]["bad_apple_cost"]
                    check.kill()

                    self.game.sprites.remove(self.game.txt)
                    self.game.txt = self.game.Text(f"Score: {self.game.count}", 200, 80, (20, 35), 30,
                                                   self.game.data["text"]["font"], self.game.txts)

            if pygame.sprite.spritecollideany(self, self.game.bodyes) or \
                    pygame.sprite.spritecollideany(self, self.game.platforms):
                self.game.high_count = self.game.last_close()
                self.game.refresh()
                return

            self.rect = self.rect.move(self.x_speed, self.y_speed)

            if self.turn:
                if self.pred is not None:
                    self.pred.turn.append(self.turn.pop(0))
                else:
                    self.turn.pop(0)

    class Button(pygame.sprite.Sprite):
        def __init__(self, text, w, h, pos, game):
            super().__init__(game.sprites)
            self.add(game.buttons)
            self.image = pygame.Surface((w, h))
            self.image.fill(pygame.Color("red"))
            self.rect = pygame.Rect(pos, (w, h))
            font = pygame.font.SysFont('Arial', 40)
            self.txt = font.render(text, True, (255, 255, 255))
            self.onPressed = False

        def update(self):
            mouse = pygame.mouse.get_pos()
            self.image.fill(pygame.Color("red"))
            if self.rect.collidepoint(mouse):
                self.image.fill(pygame.Color("grey"))
            if self.onPressed:
                self.image.fill(pygame.Color("green"))
            self.image.blit(self.txt, [
                self.rect.width // 2 - self.txt.get_rect().width // 2,
                self.rect.height // 2 - self.txt.get_rect().height // 2
            ])
            screen.blit(self.image, self.rect)

    class Text(pygame.sprite.Sprite):
        def __init__(self, text, w, h, pos, f_size, font, spr):
            super().__init__(spr)
            self.image = pygame.Surface((w, h))
            font = pygame.font.SysFont(font, f_size)
            self.txt = font.render(text, True, (255, 255, 255))
            self.rect = pygame.Rect(pos, (w, h))

        def update(self):
            screen.blit(self.image, self.rect)
            screen.blit(self.txt, self.rect)

    class Bonus(pygame.sprite.Sprite):
        def __init__(self, pos, game):
            super().__init__(game.sprites)
            self.add(game.apples)
            self.rect = pygame.Rect(pos, (16, 16))
            self.game = game

    class Apple(Bonus):
        def __init__(self, pos, game):
            super().__init__(pos, game)
            self.add(self.game.apples)
            self.image = load_image(game.data["apple"]["image"])
            self.image = pygame.transform.scale(self.image, (30, 30))
            self.rect = pygame.Rect(pos, (16, 16))
            self.cost = 1
            self.type = 1

    class MegaApple(Apple):
        def __init__(self, pos, game):
            super().__init__(pos, game)
            self.cost = game.data["settings"]["mega_apple_cost"]
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.rect.width = 30
            self.rect.height = 30
            self.type = 2

    class BadApple(Apple):
        def __init__(self, pos, game):
            super().__init__(pos, game)
            self.image = load_image(game.data["bad_apple"]["image"])
            self.image = pygame.transform.scale(self.image, (30, 30))
            self.cost = game.data["settings"]["bad_apple_cost"]
            self.type = 3

    class SnakeBody(pygame.sprite.Sprite):
        def __init__(self, pos, spds, game, index):
            super().__init__(game.sprites)
            self.add(game.bodyes)
            self.image = load_image(game.data["snake"]["body"]["image"])
            self.rect = pygame.Rect(pos, game.data["snake"]["body"]["size"])
            self.x_speed = spds[0]
            self.y_speed = spds[1]
            self.pred = None
            self.game = game
            self.turn = []
            self.index = index

        def update(self):
            self.rect = self.rect.move(self.x_speed, self.y_speed)

            if self.turn:
                if distance(self.rect.x, self.turn[0][0]) < self.game.data["settings"]["snake_speed"] and \
                        distance(self.rect.y, self.turn[0][1]) < self.game.data["settings"]["snake_speed"]:
                    self.x_speed = self.turn[0][2]
                    self.y_speed = self.turn[0][3]
                    if self.pred is not None:
                        self.pred.turn.append(self.turn.pop(0))
                    else:
                        self.turn.pop(0)


def load_image(name, colorkey=None):
    if not os.path.isfile(name):
        print(f"Файл с изображением '{name}' не найден")
        sys.exit()
    image = pygame.image.load(name)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def get_random_pos(matrix, poses):

    pos = random.choice(matrix)
    c = map(lambda x: x.rect, poses)
    while pos in c:
        pos = random.choice(matrix)

    return pos


def distance(coord1, coord2):
    return abs(coord1 - coord2)


def get_sign(x):
    if x < 0:
        return -1
    elif x == 0:
        return 0
    return 1


g = Game()
g.run()
pygame.quit()
