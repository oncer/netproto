from pygame import draw

class Player:
    MAX_SPEED = 7
    RADIUS = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0

    def input(self, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_LEFT:
                    self.ax = -1
                elif e.key == K_RIGHT:
                    self.ax = 1
                elif e.key == K_UP:
                    self.ay = -1
                elif e.key == K_DOWN:
                    self.ay = 1
            elif e.type == KEYUP:
                if e.key == K_LEFT and self.ax == -1\
                    or e.key == K_RIGHT and self.ax == 1:
                    self.ax = 0
                if e.key == K_UP and self.ay == -1\
                    or e.key == K_DOWN and self.ay == 1:
                    self.ay = 0

    def logic(self):
        if self.ax != 0:
            self.vx += self.ax / 2.0
            if self.vx > Player.MAX_SPEED:
                self.vx = Player.MAX_SPEED
            if self.vx < -Player.MAX_SPEED:
                self.vx = -Player.MAX_SPEED
        else:
            self.vx *= 0.94
            if self.vx > 0 and self.vx < 0.33\
                or self.vx < 0 and self.vx > -0.33:
                self.vx = 0

        if self.ay != 0:
            self.vy += self.ay / 2.0
            if self.vy > Player.MAX_SPEED:
                self.vy = Player.MAX_SPEED
            if self.vy < -Player.MAX_SPEED:
                self.vy = -Player.MAX_SPEED
        else:
            self.vy *= 0.94
            if self.vy > 0 and self.vy < 0.33\
                or self.vy < 0 and self.vy > -0.33:
                self.vy = 0

        self.x += self.vx
        if self.x < Player.RADIUS and self.vx < 0:
            self.x = 2 * Player.RADIUS - self.x
            self.vx = -self.vx
        elif self.x > (WIDTH - Player.RADIUS) and self.vx > 0:
            self.x = 2 * (WIDTH - Player.RADIUS) - self.x
            self.vx = -self.vx

        self.y += self.vy
        if self.y < Player.RADIUS and self.vy < 0:
            self.y = 2 * Player.RADIUS - self.y
            self.vy = -self.vy
        elif self.y > (HEIGHT - Player.RADIUS) and self.vy > 0:
            self.y = 2 * (HEIGHT - Player.RADIUS) - self.y
            self.vy = -self.vy
    
    def draw(self, s):
        color = (255, 255, 255)
        pos = (int(self.x), int(self.y))
        draw.circle(s, color, pos, Player.RADIUS)

