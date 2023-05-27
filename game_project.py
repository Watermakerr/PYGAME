import pygame, sys, math
from pygame.locals import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 600
TILE_SIZE = 50
NUM_TILES_WIDTH = WINDOWWIDTH // (TILE_SIZE)
NUM_TILES_HEIGHT = WINDOWHEIGHT // (TILE_SIZE)
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
FPS = 60
fpsClock = pygame.time.Clock()

backgroud_image = pygame.image.load("images\\background.png")
wall_image = pygame.image.load("images\\wall.png")
knigh_image = pygame.image.load("images\\knight.png")
knigh_image_scale = pygame.transform.scale(knigh_image,(50,50))
sword_image = pygame.image.load("images\\sword.png")
door_open_image = pygame.image.load("images\\door_open.png")
door_close_image = pygame.image.load("images\\door_close.png")
door_close_image_scale = pygame.transform.scale(door_close_image, (50, 50))
door_open_image_scale = pygame.transform.scale(door_open_image, (50, 50))
guard_image = pygame.image.load("images\\guard.png")
guard_image_scale = pygame.transform.scale(guard_image, (50, 50))


class Background:
    def __init__(self):
        self.image = backgroud_image

    # draw background in all of the screen except the wall
    def draw(self):  
        for i in range(1, NUM_TILES_WIDTH - 1):
            for j in range(1, NUM_TILES_HEIGHT - 1):
                x = i * (TILE_SIZE)
                y = j * (TILE_SIZE)
                DISPLAYSURF.blit(self.image, (x, y))


class Wall:
    def __init__(self):
        self.image = wall_image

    def draw(self):
        # draw the top wall and dowm wall
        for i in range(NUM_TILES_WIDTH):  
            x_top = i * TILE_SIZE
            y_top = 0
            DISPLAYSURF.blit(self.image, (x_top, y_top))

            x_bot = i * TILE_SIZE
            y_bot = WINDOWHEIGHT - TILE_SIZE
            DISPLAYSURF.blit(self.image, (x_bot, y_bot))

        # draw the left wall and the right wall
        for i in range(1, NUM_TILES_HEIGHT - 1):  
            x_left = 0
            y_left = i * (TILE_SIZE)
            DISPLAYSURF.blit(self.image, (x_left, y_left))

            x_right = WINDOWWIDTH - TILE_SIZE
            y_right = i * (TILE_SIZE)
            DISPLAYSURF.blit(self.image, (x_right, y_right))


class Knight:
    def __init__(self):
        self.image = knigh_image_scale
        self.x = TILE_SIZE
        self.y = WINDOWHEIGHT - 2 * TILE_SIZE
        self.move_speed = 5  # pixels per frame
        self.move_direction = None
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
    def update(self, move_left, move_right, move_top, move_down, obstacles):
        # move if the new position is not collied with the obstacle
        if move_left:
            new_x = self.x - self.move_speed
            if not any(
                check_collision(
                    pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE), obstacle
                )
                for obstacle in obstacles
            ):
                self.x = new_x
        if move_right:
            new_x = self.x + self.move_speed
            if not any(
                check_collision(
                    pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE), obstacle
                )
                for obstacle in obstacles
            ):
                self.x = new_x
        if move_top:
            new_y = self.y - self.move_speed
            if not any(
                check_collision(
                    pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE), obstacle
                )
                for obstacle in obstacles
            ):
                self.y = new_y
        if move_down:
            new_y = self.y + self.move_speed
            if not any(
                check_collision(
                    pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE), obstacle
                )
                for obstacle in obstacles
            ):
                self.y = new_y
        # dont allow the kngit move through the wall
        if self.x < TILE_SIZE:
            self.x = TILE_SIZE
        if self.y < TILE_SIZE:
            self.y = TILE_SIZE
        if self.x > WINDOWWIDTH - 2 * TILE_SIZE:
            self.x = WINDOWWIDTH - 2 * TILE_SIZE
        if self.y > WINDOWHEIGHT - 2 * TILE_SIZE:
            self.y = WINDOWHEIGHT - 2 * TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = wall_image
        self.width = TILE_SIZE
        self.height = TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, ((self.x, self.y, self.width, self.height)))


class Sword:
    def __init__(self, x, y):
        self.image = sword_image
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, (self.x, self.y))


class Door:
    def __init__(self):
        self.image = door_close_image_scale
        self.x = WINDOWWIDTH - TILE_SIZE
        self.y = WINDOWHEIGHT - 2 * TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, (self.x, self.y))

    def open(self):
        self.image = door_open_image_scale


class Guard:
    def __init__(self, x, y, knight):
        self.image = guard_image_scale
        self.x = x
        self.y = y
        self.speed = 3
        self.start_x = x
        self.knight = knight
        self.width = TILE_SIZE
        self.height = TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, (self.x, self.y))

    #make the guard following the knight
    #the guard cant move through the wall
    def update(self,obstacles):
        if self.knight.x > self.x:
            new_x = self.x + self.speed
            if not any(
                check_collision(
                    pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE), obstacle)\
                for obstacle in obstacles):
                self.x = new_x

        if self.knight.x < self.x:
            new_x = self.x - self.speed
            if not any(
                check_collision(
                    pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE), obstacle)\
                for obstacle in obstacles):
                self.x = new_x

        if self.knight.y < self.y:
            new_y = self.y - self.speed
            if not any(
                check_collision(
                    pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE), obstacle)\
                for obstacle in obstacles):
                self.y = new_y

        if self.knight.y > self.y:
            new_y = self.y + self.speed
            if not any(
                check_collision(
                    pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE), obstacle)\
                        for obstacle in obstacles):
                self.y = new_y


class Bullet():
    #dest_x, dest_y is location of the knight
    def __init__(self,guard, dest_x, dest_y):
        self.x = guard.x + 50 // 2
        self.y = guard.y + 50 // 2
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.speed = 10
        self.color = (255,0,0)
        self.radius = 8
        self.last_shot_time = 0
        self.dx = 0
        self.dy = 0
        self.width = self.radius*2
        self.height = self.radius*2
 
    #the bullet will fire from the guard
    #and aim to the the location of the knight
    #using the location of the guard and knight make the bullet moving
    #in the right direction
    def update(self):
        if self.dx == 0 and self.dy == 0:
            dx = self.dest_x - self.x
            dy = self.dest_y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.dx = dx / dist
                self.dy = dy / dist
        else:
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed

    def draw(self):
        pygame.draw.circle(DISPLAYSURF, self.color, (int(self.x), int(self.y)), self.radius)

# check if two object are collided 
def check_collision(rect_1, rect_2): 
    rect1_rect = pygame.Rect(rect_1.x, rect_1.y, rect_1.width, rect_1.height)
    rect2_rect = pygame.Rect(rect_2.x, rect_2.y, rect_2.width, rect_2.height)
    if rect1_rect.colliderect(rect2_rect):
        return True
    return False

def gameplay(background, wall, knight, door, obstacle_list, guard,bullets, sword):
    guard.__init__(150, 200, knight)
    knight.__init__()
    door.__init__()
    count = 0
    swords = sword
    move_left = False
    move_right = False
    move_top = False
    move_down = False
    last_shot_time = 0
    shoot_interval = 500

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    move_left = True
                if event.key == K_RIGHT:
                    move_right = True
                if event.key == K_UP:
                    move_top = True
                if event.key == K_DOWN:
                    move_down = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    move_left = False
                if event.key == K_RIGHT:
                    move_right = False
                if event.key == K_UP:
                    move_top = False
                if event.key == K_DOWN:
                    move_down = False

        background.draw()
        wall.draw()
        door.draw()

        for sword in swords:
            sword.draw()

        guard.draw()
        guard.update( obstacle_list)
        for obstacle in obstacle_list:
            obstacle.draw()

        # Get the current time
        current_time = pygame.time.get_ticks()
        # Check if it's time to shoot a bullet
        if current_time - last_shot_time > shoot_interval:
        # Create a new bullet at the guard's location and add it to the list
            new_bullet = Bullet(guard, knight.x, knight.y)
            bullets.append(new_bullet)
        # update the last shot time
            last_shot_time = current_time

        for bullet in bullets:
            bullet.update()
            bullet.draw()

        knight.draw()
        knight.update(move_left, move_right, move_top, move_down, obstacle_list)
        
        # if knight pick 3 keys, the door is opened
        if count == 3:  
            door.open()
            # if the knight stand close the door when the door open, win
            if (knight.x == WINDOWWIDTH - 2 * TILE_SIZE\
                and knight.y == WINDOWHEIGHT - 2 * TILE_SIZE):
                return
            
        # if the knght touch the key, the key disappears
        # and count increase by one
        for sword in swords:
            if check_collision(knight, sword):
                swords.remove(sword)
                count += 1
        #if the knght touach the bullet, game end
        for bullet in bullets:
            if check_collision(knight,bullet):
                return
            # if the bullet hit the wall, remove the bullet
            if bullet.x < TILE_SIZE or bullet.x > WINDOWWIDTH - TILE_SIZE or \
            bullet.y < TILE_SIZE or bullet.y > WINDOWHEIGHT - TILE_SIZE:
                bullets.remove(bullet)
                continue  # skip collision checks if bullet is out of bounds
            # if the bullet hit the obstacle, remove the bullet
            for obstacle in obstacle_list:
                if check_collision(bullet, obstacle):
                    bullets.remove(bullet)
                    break  # no need to check for more collisions if bullet hits an obstacle
            
        #if the knght touch the guard, game end
        if check_collision(knight, guard):
            return
        
        # print the number of key has picked top
        font = pygame.font.SysFont("consolas", 30)
        text = font.render(f":{count}/3", True, (0, 0, 0))
        DISPLAYSURF.blit(text, (40, 22))
        DISPLAYSURF.blit(sword_image, (0, 10))

        fpsClock.tick(FPS)
        pygame.display.update()


def gameover(background, wall, knight, door, obstacle_list, guard, bullets, swords):
    font = pygame.font.SysFont("consolas", 40)
    return_text = font.render("Press space to return to menu", True, (0,0,0))
    return_text_rect = return_text.get_rect()
    return_text_rect.centerx = WINDOWWIDTH // 2
    return_text_rect.centery = WINDOWHEIGHT // 2 +70
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return

        background.draw()
        wall.draw()
        door.draw()
        knight.draw()
        guard.draw()
        for sword in swords:
            sword.draw()

        for bullet in bullets:
            bullet.draw()
            
        for obstacle in obstacle_list:
            obstacle.draw()
        
        #if the knight touches the guard or bullet, lose
        #print the message lose
        if check_collision(knight, guard) or any(check_collision(knight, bullet) for bullet in bullets):

            text = font.render("You lose!", True, (0,0,0))
            text_rect = text.get_rect()
            text_rect.centerx = WINDOWWIDTH // 2 
            text_rect.centery = WINDOWHEIGHT // 2
            DISPLAYSURF.blit(text, (text_rect))
            DISPLAYSURF.blit(return_text, (return_text_rect))

        #if winning moving the knight forward until cant see anymore
        #print the message win
        else:   
            if (knight.x < WINDOWWIDTH):  
                knight.x += 1
            text = font.render("You won!", True, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.centerx = WINDOWWIDTH // 2
            text_rect.centery = WINDOWHEIGHT // 2
            DISPLAYSURF.blit(text, (text_rect))
            DISPLAYSURF.blit(return_text, (return_text_rect))
            
        fpsClock.tick(FPS)
        pygame.display.update()
def gamestart(wall, background):
    font = pygame.font.SysFont("consolas", 70)
    text = font.render('Press space to start', True, (255, 255, 255))

    # Set top the initial state of the text
    text_rect = text.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2))
    is_visible = True
    blink_interval = 500  # milliseconds
    last_blink_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return

        # update the state of the text
        # make the text disappear and appear depending on the time
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time >= blink_interval:
            is_visible = not is_visible
            last_blink_time = current_time
    
        # Draw the text
        wall.draw()
        background.draw()
        if is_visible:
            DISPLAYSURF.blit(text, text_rect)

        pygame.display.update()
        fpsClock.tick(FPS)    
def main():
    background = Background()
    wall = Wall()
    knight = Knight()
    door = Door()
    guard = Guard(150, 200, knight)
    obstacle_list = []
    for i in range(4,9):
        obstacle = Obstacle(TILE_SIZE * i, 250)
        obstacle_list.append(obstacle)
    sword_1 = Sword(550,400)
    sword_2 = Sword(300,100)
    sword_3 = Sword(700,200)
    while True:
        #each time the game restart, renew the bullets and swords
        bullets = []
        swords = []
        swords.append(sword_1)
        swords.append(sword_2)
        swords.append(sword_3)
        gamestart(wall, background)
        gameplay(background, wall, knight, door, obstacle_list, guard,bullets, swords)
        gameover(background, wall, knight, door, obstacle_list, guard,bullets, swords)

if __name__ == "__main__":
    main()
