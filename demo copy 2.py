import pygame, sys, random, math
from pygame.locals import *

WINDOWWIDTH =800
WINDOWHEIGHT = 600
TILE_SIZE = 50
NUM_TILES_WIDTH = WINDOWWIDTH // (TILE_SIZE)
NUM_TILES_HEIGHT = WINDOWHEIGHT // (TILE_SIZE)
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
FPS = 60
fpsClock = pygame.time.Clock()

backgroud_image = pygame.image.load('images\\background.png')
wall_image = pygame.image.load('images\\wall.png')
knigh_image = pygame.image.load('images\knight.png')
sword_image = pygame.image.load('images\\sword.png')
door_open_image = pygame.image.load('images\\door_open.png')
door_close_image = pygame.image.load('images\\door_close.png')
door_close_image_scale = pygame.transform.scale(door_close_image,(50,50))
door_open_image_scale = pygame.transform.scale(door_open_image,(50,50))
guard_image = pygame.image.load('images\\guard.png')
guard_image_scale = pygame.transform.scale(guard_image,(50,50))


class Background():
    def __init__(self):
        self.image = backgroud_image
    
    def draw(self): #draw background in all of the screen except the wall
        for i in range(1, NUM_TILES_WIDTH -1 ):
            for j in range(1, NUM_TILES_HEIGHT -1):
                x = i*(TILE_SIZE)
                y = j*(TILE_SIZE)
                DISPLAYSURF.blit(self.image,(x,y))


class Wall():
    def __init__(self):
        self.image = wall_image

    def draw(self):
        for i in range(NUM_TILES_WIDTH): #draw the up wall and dowm wall
            x_up = i * TILE_SIZE
            y_up = 0
            DISPLAYSURF.blit(self.image,(x_up,y_up))

            x_bot = i * TILE_SIZE 
            y_bot = WINDOWHEIGHT - TILE_SIZE
            DISPLAYSURF.blit(self.image,(x_bot,y_bot))

        for i in range(1, NUM_TILES_HEIGHT - 1): #draw the left wall and the right wall
            x_left = 0                         
            y_left = i*(TILE_SIZE)
            DISPLAYSURF.blit(self.image,(x_left,y_left))

            x_right = WINDOWWIDTH - TILE_SIZE
            y_right = i*(TILE_SIZE)
            DISPLAYSURF.blit(self.image,(x_right,y_right))


class Knight():
    def __init__(self):
        self.image = knigh_image
        self.x =  TILE_SIZE
        self.y = WINDOWHEIGHT - 2* TILE_SIZE
        self.move_speed = 5 # pixels per frame
        self.move_direction = None
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE,TILE_SIZE)
    
    def update(self, move_left, move_right, move_up, move_down, obstacles):
        if move_left: #move if the new position is not collied with the obstacle                                                  
            new_x = self.x - self.move_speed
            if not any(check_collision(pygame.Rect(new_x, self.y, TILE_SIZE,TILE_SIZE), obstacle)\
                        for obstacle in obstacles):
                self.x = new_x
        if move_right:
            new_x = self.x + self.move_speed
            if not any(check_collision(pygame.Rect(new_x, self.y, TILE_SIZE,TILE_SIZE), obstacle)\
                        for obstacle in obstacles):
                self.x = new_x
        if move_up:
            new_y = self.y - self.move_speed
            if not any(check_collision(pygame.Rect(self.x, new_y, TILE_SIZE,TILE_SIZE), obstacle)\
                        for obstacle in obstacles):
                self.y = new_y
        if move_down:
            new_y = self.y + self.move_speed
            if not any(check_collision(pygame.Rect(self.x, new_y, TILE_SIZE,TILE_SIZE), obstacle)\
                        for obstacle in obstacles):
                self.y = new_y
        #dont allow the kngit move through the wall
        if self.x < TILE_SIZE:
            self.x = TILE_SIZE
        if self.y < TILE_SIZE:
            self.y = TILE_SIZE
        if self.x > WINDOWWIDTH - 2* TILE_SIZE:
            self.x = WINDOWWIDTH - 2* TILE_SIZE
        if self.y > WINDOWHEIGHT - 2* TILE_SIZE:
            self.y = WINDOWHEIGHT - 2* TILE_SIZE
    
    def draw(self):
        DISPLAYSURF.blit(self.image,(self.x,self.y))


class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = wall_image
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        DISPLAYSURF.blit(self.image, ((self.x, self.y, self.width, self.height)))
        

class Sword():
    def __init__(self,x,y):
        self.image = sword_image
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        DISPLAYSURF.blit(self.image,(self.x,self.y))


class Door():
    def __init__(self):
        self.image = door_close_image_scale
        self.x = WINDOWWIDTH - TILE_SIZE
        self.y = WINDOWHEIGHT - 2* TILE_SIZE
    
    def draw(self):
        DISPLAYSURF.blit(self.image,(self.x,self.y))
    
    def open(self):
        self.image = door_open_image_scale
        

class Guard():
    def __init__(self, x, y):
        self.image = guard_image_scale
        self.x = x
        self.y = y
        self.speed = 2
        self.direction = 'forward'
        self.start_x = x

    def draw(self):
        DISPLAYSURF.blit(self.image,(self.x, self.y))

    def update(self,knight):
        #if self.direction == 'forward':
        #    self.x += self.speed
        #    if self.x > self.start_x + 4* TILE_SIZE:
        #        self.direction = 'backward'
        #else:
        #    self.x -= self.speed
        #    if self.x <= self.start_x:
        #        self.direction = 'forward'
            if knight.x > self.x :
                self.x += self.speed
            if knight.x < self.x :
                self.x -= self.speed
            if knight.y > self.y :
                self.y += self.speed
            if knight.y < self.y :
                self.y -= self.speed


def check_collision(rect_1, rect_2): #check if two object are collided as rectangle
    rect1_rect = pygame.Rect(rect_1.x, rect_1.y, 50, 50)
    rect2_rect = pygame.Rect(rect_2.x, rect_2.y, 50, 50)
    if rect1_rect.colliderect(rect2_rect):
        return True
    return False

def gameplay(background, wall, knight, door, obstacle_list,guard_list, win):
    knight.__init__()
    door.__init__()
    count = 0
    swords = []
    move_left = False
    move_right = False
    move_up = False
    move_down =False
    #create obstacle and insert them into a list
    obstacke_1 = Obstacle(200,150)
    obstacke_2 = Obstacle(250,100)
    obstacle_list.append(obstacke_1)
    obstacle_list.append(obstacke_2)
    #create key and insert them into a list
    for k in range(3):
        x = random.randint(1,14) * TILE_SIZE
        y = random.randint(1,10) * TILE_SIZE
        swords.append(Sword(x,y))
        
    while True:
        win = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return
                if event.key == K_LEFT:
                    move_left = True
                if event.key == K_RIGHT:
                    move_right = True
                if event.key == K_UP:
                    move_up = True
                if event.key == K_DOWN:
                    move_down = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    move_left = False
                if event.key == K_RIGHT:
                    move_right = False
                if event.key == K_UP:
                    move_up = False
                if event.key == K_DOWN:
                    move_down = False
    
        background.draw()
        wall.draw()
        
        door.draw()
        knight.draw()
        knight.update(move_left,move_right,move_up,move_down, obstacle_list)
        for obstacle in obstacle_list:
            obstacle.draw()

        for sword in swords: #if the knght touch the key, the key disappears and count increase by one
            if check_collision(knight, sword):
                swords.remove(sword)
                count += 1
        
        for sword in swords:
                sword.draw()
        for guard in guard_list:
            guard.draw()
            guard.update(knight)
        if count == 3: #if pick up 3 key then the door is opened
            door.open()
            # if the knight stand close the door when the door open, win
            if knight.x == WINDOWWIDTH - 2* TILE_SIZE and knight.y == WINDOWHEIGHT - 2* TILE_SIZE:
                win = True
                return
        if any(check_collision(knight, guard) for guard in guard_list):
                win = False
                return
        
        #print the number of key has picked up
        font = pygame.font.SysFont('consolas', 30)
        text = font.render(f":{count}/3", True, (0, 0, 0))
        DISPLAYSURF.blit(text, (40,22))
        DISPLAYSURF.blit(sword_image, (0,10))

        fpsClock.tick(FPS)
        pygame.display.update()

def gameover():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return
            
            font = pygame.font.SysFont('consolas', 70)
            text = font.render("You lose!", True, (255,0,0))
            text_rect = text.get_rect()
            text_rect.centerx = WINDOWWIDTH // 2
            text_rect.centery = WINDOWHEIGHT // 2
            DISPLAYSURF.blit(text, (text_rect))

            # print the text you won! in the middle of the screen
            font = pygame.font.SysFont('consolas', 70)
            text = font.render("You win!", True, (255,0,0))
            text_rect = text.get_rect()
            text_rect.centerx = WINDOWWIDTH // 2
            text_rect.centery = WINDOWHEIGHT // 2
            DISPLAYSURF.blit(text, (text_rect))
        
        fpsClock.tick(FPS)
        pygame.display.update()
            
def main():
    background = Background()
    wall = Wall()
    knight = Knight()
    door = Door()
    guard_list = []
    obstacle_list = []   
    guard_1 = Guard(150,200)
    guard_2 = Guard(200, 250)
    guard_list.append(guard_1)
    guard_list.append(guard_2)
    win = True
    while True:
        gameplay(background, wall, knight, door, obstacle_list, guard_list)
        gameover(background, wall, knight, door, obstacle_list, guard_list)

if __name__ == '__main__':
    main()