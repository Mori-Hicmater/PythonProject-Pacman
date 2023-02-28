import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 576
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Game(object):  # класс игры
    def __init__(self):
        self.font = pygame.font.Font(None, 40)
        self.about = False
        self.game_over = True
        self.score = 0
        self.font = pygame.font.Font(None, 35)
        # создание меню игры
        self.menu = Menu(("PRESS ENTER", "FOR", "START"), font_color=RED, font_size=60)
        # создание игрока
        self.player = Player(32, 128, "player.png")
        self.horizontal_blocks = pygame.sprite.Group()
        self.vertical_blocks = pygame.sprite.Group()
        self.dots_group = pygame.sprite.Group()
        # Установка карты:
        for i, row in enumerate(enviroment()):
            for j, item in enumerate(row):
                if item == 1:
                    self.horizontal_blocks.add(Block(j * 32 + 8, i * 32 + 8, BLACK, 16, 16))
                elif item == 2:
                    self.vertical_blocks.add(Block(j * 32 + 8, i * 32 + 8, BLACK, 16, 16))
        # Создание оппонентов
        self.opponent = pygame.sprite.Group()
        self.opponent.add(Ghost(288, 96, 0, 2))
        self.opponent.add(Ghost(288, 320, 0, -2))
        self.opponent.add(Ghost(544, 128, 0, 2))
        self.opponent.add(Ghost(32, 224, 0, 2))
        self.opponent.add(Ghost(160, 64, 2, 0))
        self.opponent.add(Ghost(448, 64, -2, 0))
        self.opponent.add(Ghost(640, 448, 2, 0))
        self.opponent.add(Ghost(448, 320, 2, 0))
        # Добавление точкек внутри игры
        for i, row in enumerate(enviroment()):
            for j, item in enumerate(row):
                if item != 0:
                    self.dots_group.add(Ellipse(j * 32 + 12, i * 32 + 12, WHITE, 8, 8))

        # загрузка звуковых эффектов
        self.pacman_sound = pygame.mixer.Sound("pacman_sound.ogg")
        self.game_over_sound = pygame.mixer.Sound("game_over_sound.ogg")

    def process_events(self):  # функция отработки действий пользователя
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            self.menu.event_handler(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.game_over and not self.about:
                        if self.menu.state == 0:
                            self.__init__()
                            self.game_over = False
                        elif self.menu.state == 2:
                            return True

                elif event.key == pygame.K_RIGHT:
                    self.player.move_right()

                elif event.key == pygame.K_LEFT:
                    self.player.move_left()

                elif event.key == pygame.K_UP:
                    self.player.move_up()

                elif event.key == pygame.K_DOWN:
                    self.player.move_down()

                elif event.key == pygame.K_ESCAPE:
                    self.game_over = True
                    self.about = False

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.player.stop_move_right()
                elif event.key == pygame.K_LEFT:
                    self.player.stop_move_left()
                elif event.key == pygame.K_UP:
                    self.player.stop_move_up()
                elif event.key == pygame.K_DOWN:
                    self.player.stop_move_down()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.player.explosion = True

        return False

    def run_logic(self):  # функция отработки поедания точки
        if not self.game_over:
            self.player.update(self.horizontal_blocks, self.vertical_blocks)
            block_hit_list = pygame.sprite.spritecollide(self.player, self.dots_group, True)
            # Когда block_hit_list содержит один спрайт, это означает, что игрок попал в точку
            if len(block_hit_list) > 0:
                # Здесь будет звуковой эффект
                self.pacman_sound.play()
                self.score += 1
            block_hit_list = pygame.sprite.spritecollide(self.player, self.opponent, True)
            if len(block_hit_list) > 0:
                self.player.explosion = True
                self.game_over_sound.play()
            self.game_over = self.player.game_over
            self.opponent.update(self.horizontal_blocks, self.vertical_blocks)

    def display_frame(self, screen):  # функция отрисовки экрана
        screen.fill(BLACK)
        if self.game_over:
            self.menu.display_frame(screen)
        else:
            self.horizontal_blocks.draw(screen)
            self.vertical_blocks.draw(screen)
            draw_enviroment(screen)
            self.dots_group.draw(screen)
            self.opponent.draw(screen)
            screen.blit(self.player.image, self.player.rect)
            text = self.font.render("Score: " + str(self.score), True, WHITE)
            # Вывод текста на экран
            screen.blit(text, [120, 20])
        pygame.display.flip()

    def display_message(self, screen, message, color=(255, 0, 0)):  # функция определения фона
        label = self.font.render(message, True, color)
        # Получаем ширину и высоту фона
        width = label.get_width()
        height = label.get_height()
        # Определяем положение метки
        posX = (SCREEN_WIDTH / 2) - (width / 2)
        posY = (SCREEN_HEIGHT / 2) - (height / 2)
        screen.blit(label, (posX, posY))


class Menu(object):  # класс отрисовки меню
    state = 0

    def __init__(self, items, font_color=(0, 0, 0), select_color=(255, 0, 0), ttf_font=None, font_size=25):
        self.font_color = font_color
        self.select_color = select_color
        self.items = items
        self.font = pygame.font.Font(ttf_font, font_size)

    def display_frame(self, screen):
        for index, item in enumerate(self.items):
            if self.state == index:
                label = self.font.render(item, True, self.select_color)
            else:
                label = self.font.render(item, True, self.font_color)

            width = label.get_width()
            height = label.get_height()

            posX = (SCREEN_WIDTH / 2) - (width / 2)
            t_h = len(self.items) * height
            posY = (SCREEN_HEIGHT / 2) - (t_h / 2) + (index * height)

            screen.blit(label, (posX, posY))

    def event_handler(self, event):  # функция обработки действий
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.state > 0:
                    self.state -= 1
            elif event.key == pygame.K_DOWN:
                if self.state < len(self.items) - 1:
                    self.state += 1


class Block(pygame.sprite.Sprite):  # класс для создания стен
    def __init__(self, x, y, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        # задаём цвет фона
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Ellipse(pygame.sprite.Sprite):  # класс для создания точек
    def __init__(self, x, y, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        # устанавливаем цвет фона и делаем его прозрачным
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        # рисуем эллипс
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Player(pygame.sprite.Sprite):  # класс игрока
    change_x = 0
    change_y = 0
    explosion = False
    game_over = False

    def __init__(self, x, y, filename):
        # вызываем конструктор родительского класса (sprite)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        # загружаем изображение, которое будет использоваться для анимации
        img = pygame.image.load("walk.png").convert()
        # Create the animations objects
        self.move_right_animation = Animation(img, 32, 32)
        self.move_left_animation = Animation(pygame.transform.flip(img, True, False), 32, 32)
        self.move_up_animation = Animation(pygame.transform.rotate(img, 90), 32, 32)
        self.move_down_animation = Animation(pygame.transform.rotate(img, 270), 32, 32)
        img = pygame.image.load("game-off.png").convert()
        self.explosion_animation = Animation(img, 30, 30)
        self.player_image = pygame.image.load(filename).convert()
        self.player_image.set_colorkey(BLACK)

    def update(self, horizontal_blocks, vertical_blocks):
        if not self.explosion:
            if self.rect.right < 0:
                self.rect.left = SCREEN_WIDTH
            elif self.rect.left > SCREEN_WIDTH:
                self.rect.right = 0
            if self.rect.bottom < 0:
                self.rect.top = SCREEN_HEIGHT
            elif self.rect.top > SCREEN_HEIGHT:
                self.rect.bottom = 0
            self.rect.x += self.change_x
            self.rect.y += self.change_y

            # остановка пользователя от перехода вверх или вниз, когда он находится внутри коробки

            for block in pygame.sprite.spritecollide(self, horizontal_blocks, False):
                self.rect.centery = block.rect.centery
                self.change_y = 0
            for block in pygame.sprite.spritecollide(self, vertical_blocks, False):
                self.rect.centerx = block.rect.centerx
                self.change_x = 0

            # Запуск анимации

            if self.change_x > 0:
                self.move_right_animation.update(10)
                self.image = self.move_right_animation.get_current_image()
            elif self.change_x < 0:
                self.move_left_animation.update(10)
                self.image = self.move_left_animation.get_current_image()

            if self.change_y > 0:
                self.move_down_animation.update(10)
                self.image = self.move_down_animation.get_current_image()
            elif self.change_y < 0:
                self.move_up_animation.update(10)
                self.image = self.move_up_animation.get_current_image()
        else:
            if self.explosion_animation.index == self.explosion_animation.get_length() - 1:
                pygame.time.wait(500)
                self.game_over = True
            self.explosion_animation.update(12)
            self.image = self.explosion_animation.get_current_image()

    def move_right(self):  # функция движения
        self.change_x = 3

    def move_left(self):  # функция движения
        self.change_x = -3

    def move_up(self):  # функция движения
        self.change_y = -3

    def move_down(self):  # функция движения
        self.change_y = 3

    def stop_move_right(self):  # функция поворота изображения игрока
        if self.change_x != 0:
            self.image = self.player_image
        self.change_x = 0

    def stop_move_left(self):  # функция поворота изображения игрока
        if self.change_x != 0:
            self.image = pygame.transform.flip(self.player_image, True, False)
        self.change_x = 0

    def stop_move_up(self):  # функция поворота изображения игрока
        if self.change_y != 0:
            self.image = pygame.transform.rotate(self.player_image, 90)
        self.change_y = 0

    def stop_move_down(self):  # функция поворота изображения игрока
        if self.change_y != 0:
            self.image = pygame.transform.rotate(self.player_image, 270)
        self.change_y = 0


class Animation(object):  # класс отрисовки анимаций из избражений
    def __init__(self, img, width, height):
        self.sprite_sheet = img
        # создание списка для хранения изображений
        self.image_list = []
        self.load_images(width, height)
        self.index = 0
        self.clock = 1

    def load_images(self, width, height):  # функция загрузки изображений
        for y in range(0, self.sprite_sheet.get_height(), height):
            for x in range(0, self.sprite_sheet.get_width(), width):
                img = self.get_image(x, y, width, height)
                self.image_list.append(img)

    def get_image(self, x, y, width, height):
        # Создаём новое пустое изображение
        image = pygame.Surface([width, height]).convert()
        # копируем спрайт с большого листа на меньший
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        # предположим, что черный работает как прозрачный цвет
        image.set_colorkey((0, 0, 0))
        return image

    def get_current_image(self):
        return self.image_list[self.index]

    def get_length(self):
        return len(self.image_list)

    def update(self, fps=60):
        step = 30 // fps
        l = range(1, 30, step)
        if self.clock == 30:
            self.clock = 1
        else:
            self.clock += 1

        if self.clock in l:
            # Increase index
            self.index += 1
            if self.index == len(self.image_list):
                self.index = 0


class Ghost(pygame.sprite.Sprite):  # класс призраков
    def __init__(self, x, y, change_x, change_y):
        pygame.sprite.Sprite.__init__(self)
        self.change_x = change_x
        self.change_y = change_y
        self.image = pygame.image.load("ghost.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, horizontal_blocks, vertical_blocks):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = SCREEN_HEIGHT
        elif self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0

        if self.rect.topleft in self.get_intersection_position():
            direction = random.choice(("left", "right", "up", "down"))
            if direction == "left" and self.change_x == 0:
                self.change_x = -2
                self.change_y = 0
            elif direction == "right" and self.change_x == 0:
                self.change_x = 2
                self.change_y = 0
            elif direction == "up" and self.change_y == 0:
                self.change_x = 0
                self.change_y = -2
            elif direction == "down" and self.change_y == 0:
                self.change_x = 0
                self.change_y = 2

    def get_intersection_position(self):  # функция положения пересечения
        items = []
        for i, row in enumerate(enviroment()):
            for j, item in enumerate(row):
                if item == 3:
                    items.append((j * 32, i * 32))

        return items


def enviroment():  # поле
    grid = ((0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 1),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 1),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 1),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 1),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0),
            (0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0))

    return grid


def draw_enviroment(screen):  # функция отрисовки поля
    for i, row in enumerate(enviroment()):
        for j, item in enumerate(row):
            if item == 1:
                pygame.draw.line(screen, BLUE, [j * 32, i * 32], [j * 32 + 32, i * 32], 3)
                pygame.draw.line(screen, BLUE, [j * 32, i * 32 + 32], [j * 32 + 32, i * 32 + 32], 3)
            elif item == 2:
                pygame.draw.line(screen, BLUE, [j * 32, i * 32], [j * 32, i * 32 + 32], 3)
                pygame.draw.line(screen, BLUE, [j * 32 + 32, i * 32], [j * 32 + 32, i * 32 + 32], 3)


def main():
    # инициализируем все импортированные модули pygame
    pygame.init()
    # установка ширины и высоты экрана [ширина, высота]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # установка заголовка текущего окна
    pygame.display.set_caption("PACMAN")
    # Цикл рботает до тех пор, пока пользователь не нажмет кнопку закрытия.
    done = False
    clock = pygame.time.Clock()
    game = Game()
    while not done:
        # События процесса (нажатия клавиш, щелчки мыши и т.д.)
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        clock.tick(30)
    # выход из pygame
    pygame.quit()


if __name__ == '__main__':
    main()
