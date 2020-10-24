import pygame
import random


WIN_WINDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load('imgs/bird1.png')),
            pygame.transform.scale2x(pygame.image.load('imgs/bird2.png')),
            pygame.transform.scale2x(pygame.image.load('imgs/bird3.png'))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load('imgs/pipe.png'))
BASE_IMG = pygame.transform.scale2x(pygame.image.load('imgs/base.png'))
BG_IMG = pygame.transform.scale2x(pygame.image.load('imgs/bg.png'))

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 80)

class Bird(object):
    IMGS = BIRD_IMGS
    MAX_ROTATION = 30
    ROT_VEL = 10
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.vel = -10

    def jump(self):
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.3 * self.tick_count**2

        if d >= 12:
            d = 12 # thermal vel
        if d < 0:
            d -= 2

        self.y += d

        if d < 0 or self.y < self.height - 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # making the bird flapping
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < 2 * self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count < 3 * self.ANIMATION_TIME:
            self.img = self.IMGS[2]
        elif self.img_count < 4 * self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count < 4 * self.ANIMATION_TIME + 1:
            self.img = self.IMGS[0]
            self.img_count = 1

        # if flying downward the bild is not flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = 2 * self.ANIMATION_TIME

        # rotate the img around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft =
                                            (self.x, self.y)).center)

        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe(object):
    GAP = 200
    VEL = -5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x += self.VEL


    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # check for an overlap (return None if not overlapping)
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if t_point or b_point:
            return True
        return False


    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


class Base(object):
    VEL = -5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 += self.VEL
        self.x2 += self.VEL

        # put the img after other img if it moved out of the window
        if self.x1 <= -self.WIDTH:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 <= -self.WIDTH:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_ingame_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0,0))

    bird.draw(win)
    base.draw(win)
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f'Score: {score}', 1, (255, 255, 255))
    win.blit(text, (WIN_WINDTH - 10 - text.get_width(), 10))

    pygame.display.update()


def draw_endgame_window(win, score):
    clock = pygame.time.Clock()

    start_next_game = True
    run = True
    while run:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                start_next_game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start_next_game = True
                else:
                    start_next_game = False
                run = False
        win.blit(BG_IMG, (0,0))
        base = Base(730)
        base.draw(win)

        current = END_FONT.render(f'Score: {score}', 1, (255, 255, 255))
        win.blit(current, (WIN_WINDTH/2 - current.get_width()/2, 300))

        highscore = updateFile(score)

        best = END_FONT.render(f'Highscore: {highscore}', 1, (255, 255, 255))
        win.blit(best, (WIN_WINDTH/2 - best.get_width()/2, 400))

        next = STAT_FONT.render('press space to play again', 1, (255, 255, 255))
        win.blit(next, (WIN_WINDTH/2 - next.get_width()/2, 550))

        if score >= highscore:
            draw_high = END_FONT.render('New Highscore!', 1, (255, 255, 255))
            win.blit(draw_high, (WIN_WINDTH/2 - draw_high.get_width()/2, 150))


        pygame.display.update()

    return start_next_game


def updateFile(score):
    f = open('scores.txt','r')
    file = f.readlines()
    highscore = int(file[1].split()[1])
    f.close()

    if highscore < int(score):
        file = open('scores.txt', 'w')
        file.write('This file tracks the highscore of the flappy birds game.\n')
        file.write(f'Highscore: {score}')
        file.close()

        return score

    return highscore


def game_loop(win):
    bird = Bird(int(WIN_WINDTH/2 - BIRD_IMGS[0].get_width()/2), 350)
    base = Base(730)
    pipes = [Pipe(700)]

    clock = pygame.time.Clock()

    score = 0
    add_pipe = False

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                bird.jump()

        bird.move()
        base.move()

        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                run = False

            if pipe.x + pipe.PIPE_TOP.get_width() <= 0:
                rem.append(pipe)
            if not pipe.passed and pipe.x + pipe.PIPE_TOP.get_width() < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(500))
            add_pipe = False

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() > base.y:
            run = False

        draw_ingame_window(win, bird, pipes, base, score)

    return score


if __name__ == "__main__":
    win = pygame.display.set_mode((WIN_WINDTH, WIN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    score = game_loop(win)
    print(score)
    pygame.time.Clock().tick(2)
    start_next_game = draw_endgame_window(win, score)
    while start_next_game:
        score = game_loop(win)
        pygame.time.Clock().tick(2)
        start_next_game = draw_endgame_window(win, score)
    pygame.quit()
    quit()
