import pygame, sys, math
from pygame.locals import *

WINDOWWIDTH = 900
WINDOWHEIGHT = 650
TILE_SIZE = 50
NUM_TILES_WIDTH = WINDOWWIDTH // (TILE_SIZE)
NUM_TILES_HEIGHT = WINDOWHEIGHT // (TILE_SIZE)
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
FPS = 60
fpsClock = pygame.time.Clock()
icon = pygame.image.load("images\guard.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Dungeon")

key_image = pygame.transform.scale(pygame.image.load("images\\key.png"), (TILE_SIZE,TILE_SIZE))
start_button_image = pygame.image.load("images\start_button.png")
exit_button_image = pygame.image.load("images\exit_button.png")
back_button_image = pygame.image.load("images\\back_button.png")
replay_button_image = pygame.image.load("images\\replay_button.png")

class Background:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("images\\background.png"), (TILE_SIZE,TILE_SIZE))

    # draw background in all of the screen except the wall
    def draw(self):  
        for i in range(1, NUM_TILES_WIDTH - 1):
            for j in range(1, NUM_TILES_HEIGHT - 1):
                x = i * (TILE_SIZE)
                y = j * (TILE_SIZE)
                DISPLAYSURF.blit(self.image, (x, y))


class Wall:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("images\\wall.png"), (TILE_SIZE,TILE_SIZE))

    #draw the wall in the edge of the screen
    def draw(self):
        # draw the top wall and bottom wall
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
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images\\knight.png"),(TILE_SIZE,TILE_SIZE))
        self.x = x
        self.y = y
        self.move_speed = 5 
        self.width = TILE_SIZE
        self.height = TILE_SIZE
    #moving the knight 
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
        self.image = pygame.transform.scale(pygame.image.load("images\\obstacle.png"), (TILE_SIZE,TILE_SIZE))
        self.width = TILE_SIZE
        self.height = TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, ((self.x, self.y, self.width, self.height)))


class Key:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images\\key.png"),(TILE_SIZE,TILE_SIZE))
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, (self.x, self.y))


class Door:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("images\\door_close.png"), (TILE_SIZE,TILE_SIZE))
        self.x = WINDOWWIDTH - TILE_SIZE
        self.y = WINDOWHEIGHT - 2 * TILE_SIZE

    def draw(self):
        DISPLAYSURF.blit(self.image, (self.x, self.y))

    def open(self):
        self.image = pygame.transform.scale(pygame.image.load("images\\door_open.png"), (TILE_SIZE,TILE_SIZE))


class Guard:
    def __init__(self, x, y, knight):
        self.image = pygame.transform.scale(pygame.image.load("images\\guard.png"), (TILE_SIZE,TILE_SIZE))
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
        self.dx = 0
        self.dy = 0
        self.width = self.radius
        self.height = self.radius
 
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


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    #draw the button
    def draw(self):
		#draw button on screen
        DISPLAYSURF.blit(self.image, (self.rect.x, self.rect.y))

    def is_click(self):
        action = False
		#get mouse position
        pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        return action


class Score():
    def __init__(self):
        self.time = 0
    
    def update(self, start_time):
        time = pygame.time.get_ticks() - start_time
        self.time = round(time/1000,2)
    
    
# check if two object are collided 
def check_collision(rect_1, rect_2): 
    rect1_rect = pygame.Rect(rect_1.x, rect_1.y, rect_1.width, rect_1.height)
    rect2_rect = pygame.Rect(rect_2.x, rect_2.y, rect_2.width, rect_2.height)
    if rect1_rect.colliderect(rect2_rect):
        return True
    return False

def gameplay(background, wall, knight, door, obstacle_list, guard_list,bullets, keys, score):
    door.__init__()
    score.__init__()
    count = 0
    move_left = False
    move_right = False
    move_top = False
    move_down = False
    last_shot_time = 0
    shoot_interval = 500
    start_time = pygame.time.get_ticks()
    key_count = len(keys)
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

        for key in keys:
            key.draw()

        for guard in guard_list:
            guard.draw()
            guard.update(obstacle_list)

        for obstacle in obstacle_list:
            obstacle.draw()

        # Get the current time
        # Check if it's time to shoot a bullet
        # Create a new bullet at the guard's location and add it to the list
        # update the last shot time
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time > shoot_interval:
            for guard in guard_list:
                new_bullet = Bullet(guard, knight.x, knight.y)
                bullets.append(new_bullet)
                last_shot_time = current_time

        for bullet in bullets:
            bullet.update()
            bullet.draw()

        knight.draw()
        knight.update(move_left, move_right, move_top, move_down, obstacle_list)
        score.update(start_time)

        # if knight pick enough keys, the door is opened
        if count == key_count:  
            door.open()
            # if the knight stand close the door when the door open, win
            if (knight.x == WINDOWWIDTH - 2 * TILE_SIZE\
                and knight.y == WINDOWHEIGHT - 2 * TILE_SIZE):
                return
            
        # if the knght touch the key, the key disappears
        # and count increase by one
        for key in keys:
            if check_collision(knight, key):
                keys.remove(key)
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
            
        #if the knight touch the guard, game end
        for guard in guard_list:
            if (check_collision(knight, guard)):
                return
        
        # print the number of key has picked top
        font = pygame.font.SysFont("consolas", 30)
        text = font.render(f":{count}/{key_count}", True, (0, 0, 0))
        DISPLAYSURF.blit(text, (40, 22))
        DISPLAYSURF.blit(key_image, (0, 10))

        fpsClock.tick(FPS)
        pygame.display.update()

#tell the player that they won or lost
#add return button and replay button
def gameover(background, wall, knight, door, obstacle_list, guard_list, bullets, keys,score):
    button_back = Button(300,400,back_button_image,3)
    replay_button = Button(500, 400, replay_button_image,3)
    font = pygame.font.SysFont("consolas", 40)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        background.draw()
        wall.draw()
        door.draw()
        knight.draw()
        
        for guard in guard_list:
            guard.draw()

        for key in keys:
            key.draw()

        for bullet in bullets:
            bullet.draw()
            
        for obstacle in obstacle_list:
            obstacle.draw()
        
        #if the knight touches the guard or bullet, lose
        #print the message lose
        if any(check_collision(knight, guard) for guard in guard_list) or any(check_collision(knight, bullet) for bullet in bullets):
            text = font.render("You lose!", True, (0,0,139))
            text_rect = text.get_rect()
            text_rect.centerx = WINDOWWIDTH // 2 
            text_rect.centery = WINDOWHEIGHT // 2 - 50
            DISPLAYSURF.blit(text, (text_rect))

        #if winning moving the knight forward until cant see anymore
        #print the message win and the time it took
        else:   
            if (knight.x < WINDOWWIDTH):  
                knight.x += 1
            text = font.render("You win!", True, (0,0,139))
            score_text = font.render(f"You finish the game in {score.time}s ", True, (0,0,139))
            text_rect = text.get_rect()
            score_text_rect = score_text.get_rect()
            text_rect.centerx = WINDOWWIDTH // 2
            text_rect.centery= WINDOWHEIGHT // 2 - 50
            score_text_rect.centerx = WINDOWWIDTH // 2 
            score_text_rect.centery = WINDOWHEIGHT // 2 
            DISPLAYSURF.blit(text, (text_rect))
            DISPLAYSURF.blit(score_text, (score_text_rect))
        
        button_back.draw()
        replay_button.draw()

        if button_back.is_click():
            return 1
        if replay_button.is_click():
            return
        
        fpsClock.tick(FPS)
        pygame.display.update()

def gamestart(wall, background):
    start_button = Button(159, 275, start_button_image,3)
    exit_button = Button(550, 275, exit_button_image,3)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        wall.draw()
        background.draw()
        start_button.draw()
        exit_button.draw()
        if start_button.is_click():
            return
        if exit_button.is_click():
            pygame.quit()
            sys.exit()

        pygame.display.update()
        fpsClock.tick(FPS)

def main():
    background = Background()
    wall = Wall()
    door = Door()
    obstacle_list = []
    #create obstacle 
    for i in range(3,7):
        obstacle = Obstacle(TILE_SIZE * i, TILE_SIZE * 5)
        obstacle_list.append(obstacle)
    for i in range (8,10):
        obstacle = Obstacle(TILE_SIZE * 3, TILE_SIZE * i)
        obstacle_list.append(obstacle)
    for i in range (1,5):
        obstacle = Obstacle(TILE_SIZE * 9, TILE_SIZE * i)
        obstacle_list.append(obstacle)
    for i in range (3,5):
        obstacle = Obstacle(TILE_SIZE * 10, TILE_SIZE * i)
        obstacle_list.append(obstacle)
    for i in range (7,10):
        obstacle = Obstacle(TILE_SIZE * 9, TILE_SIZE * i)
        obstacle_list.append(obstacle)
    for i in range (12,15):
        obstacle = Obstacle(TILE_SIZE * i, TILE_SIZE * 6)
        obstacle_list.append(obstacle)
    
    key_1 = Key(550,400)
    key_2 = Key(300,100)
    key_3 = Key(600,100)
    score = Score()
    while True:
        gamestart(wall, background)
        while True:
            #each time a newgame start, renew the bullets and keys and location of guards
            knight = Knight(TILE_SIZE, WINDOWHEIGHT - 2 * TILE_SIZE)
            guard_list = []
            guard_1 = Guard(TILE_SIZE*10, TILE_SIZE*2, knight)
            guard_2 = Guard(250,300, knight)
            guard_list.append(guard_2)
            guard_list.append(guard_1)
            bullets = []
            keys = []
            keys.append(key_1)
            keys.append(key_2)
            keys.append(key_3)
            gameplay(background, wall, knight, door, obstacle_list, guard_list, bullets, keys,score)
            # Check if the game is over and the "Replay" button was clicked
            if gameover(background, wall, knight, door, obstacle_list, guard_list, bullets, keys,score) == 1:
                break

if __name__ == "__main__":
    main()