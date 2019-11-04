#!/usr/bin/env python3
import pygame
import sys
import numpy as np
import argparse

DESCRIPTION="A classic game of Pong."

FPS = 400 # Sets the speed of the game

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400
LINE_THICKNESS = 10
PADDLE_SIZE = 60
PADDLE_OFFSET = 20 # Distance from sides of pitch
OVERSHOOT = 5 # Min amount of paddle visible on screen
MAX_ANGLE = 45 # degrees
BALL_VELOCITY = 1.3
SCORE_OFFSETS = [-60, 35]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class agent(object):
    def __init__(self):
        self.test = 0
        self.actions = ["up", "down"]
        self.epsilon = 0.2
        self.Q = [0.49, 0.51]
        self.side = 1 # or 2

    def train(self, num_episodes):
        for episode in range(num_episodes):
            if np.rand() < self.epsilon:
                action = np.random.choice(self.actions)
        else:
                action = self.actions[max(self.Q).index] 

    def get_train_data(self, game):
       return game
        

class Ball(object):
    def __init__(self, x, y, size):
        self.x = float(x)
        self.y = float(y)
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.vx = 0
        self.vy = 0

    def draw(self, game):
        pygame.draw.rect(game.DISPLAYSURF, WHITE, self.rect)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def place(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


class Paddle(object):
    def __init__(self, x, y, x_size, y_size):
        self.x = x
        self.y = y
        self.x_size = x_size
        self.y_size = y_size
        self.rect = pygame.Rect(x, y, x_size, y_size)    
    
    def draw(self, game):
        if self.rect.bottom > WINDOW_HEIGHT - LINE_THICKNESS + PADDLE_SIZE - OVERSHOOT:
            self.rect.bottom = WINDOW_HEIGHT - LINE_THICKNESS + PADDLE_SIZE - OVERSHOOT
            self.x, self.y = self.rect.topleft
        elif self.rect.top < LINE_THICKNESS - PADDLE_SIZE + OVERSHOOT:
            self.rect.top = LINE_THICKNESS - PADDLE_SIZE + OVERSHOOT
            self.x, self.y = self.rect.topleft
        pygame.draw.rect(game.DISPLAYSURF, WHITE, self.rect)
    
    def move(self, dy):
        self.y += dy
        self.rect.y = int(self.y)
        
    def place(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        
class Game(object):
    def __init__(self, display=True):
        self.display = display
        
        #Set initial coordinates of objects
        ball_X = (WINDOW_WIDTH - LINE_THICKNESS)/2
        ball_Y = (WINDOW_HEIGHT - LINE_THICKNESS)/2
        paddle_l_X = PADDLE_OFFSET
        paddle_l_Y = (WINDOW_HEIGHT - PADDLE_SIZE)/2
        paddle_r_X = WINDOW_WIDTH - LINE_THICKNESS - PADDLE_OFFSET
        paddle_r_Y = (WINDOW_HEIGHT - PADDLE_SIZE)/2
        
        #Create objects
        self.paddles = []
        self.paddles.append(Paddle(paddle_l_X, paddle_l_Y, LINE_THICKNESS, PADDLE_SIZE))
        self.paddles.append(Paddle(paddle_r_X, paddle_r_Y, LINE_THICKNESS, PADDLE_SIZE))
        self.ball = Ball(ball_X, ball_Y, LINE_THICKNESS)
        
        
        #Initial ball direction
        self.ball.vx = -BALL_VELOCITY # -1 = left, 1 = right
        self.ball.vy = 0 # -1 = up, 1 = down
        
        #Initial scores
        self.scores = [0, 0]
        
        #Random initial serve
        if np.random.rand() > 0.5:
            self.serve = 0
        else:
            self.serve = 1
   
    
    def drawArena(self):
        self.DISPLAYSURF.fill(BLACK)
        pygame.draw.rect(self.DISPLAYSURF, WHITE, ((0,0), (WINDOW_WIDTH, WINDOW_HEIGHT)), LINE_THICKNESS*2)
        pygame.draw.line(self.DISPLAYSURF, WHITE, (WINDOW_WIDTH/2, 0),(WINDOW_WIDTH/2, WINDOW_HEIGHT), 1)
    
    
    def checkEdgeCollision(self):
        point = False
        if  self.ball.y <= LINE_THICKNESS:
            self.ball.vy = self.ball.vy * -1
            self.ball.place(self.ball.x, LINE_THICKNESS)
        if  self.ball.y >= WINDOW_HEIGHT - 2*LINE_THICKNESS:
            self.ball.vy = self.ball.vy * -1
            self.ball.place(self.ball.x, WINDOW_HEIGHT - 2*LINE_THICKNESS)
        if self.ball.x <= LINE_THICKNESS:
            self.ball.vx = self.ball.vx * -1
            self.scores[1] +=1
            self.reset()
            point = True
        if self.ball.x >= WINDOW_WIDTH - 2*LINE_THICKNESS:
            self.ball.vx = self.ball.vx * -1
            self.scores[0] +=1
            self.reset()
            point = True
        
        return point
    
    
    def AI(self):
        movement = 0
        if self.ball.rect.centery > self.paddles[1].rect.centery:
            movement = 1
        elif self.ball.rect.centery < self.paddles[1].rect.centery:
            movement = 0
        
        return movement
    
    
    @staticmethod
    def calculateReturnVelocity(x, y, paddle):
        dunno = y - paddle.top + LINE_THICKNESS/2
        angle = 2*MAX_ANGLE*dunno/PADDLE_SIZE - MAX_ANGLE
        angle = np.deg2rad(angle)
        velocityX = BALL_VELOCITY*np.sqrt(1/(np.tan(angle)**2 + 1))
        velocityY= np.sqrt(BALL_VELOCITY**2- velocityX**2)
        if dunno < PADDLE_SIZE/2:
            velocityY = -velocityY
        
        return velocityX, velocityY

    def checkHitBall(self):
        hit = False
        if self.paddles[0].rect.colliderect(self.ball.rect):
            self.ball.vx, self.ball.vy = self.calculateReturnVelocity(self.ball.x, self.ball.y, self.paddles[0].rect)
            hit = True
            
        if self.paddles[1].rect.colliderect(self.ball.rect):
            self.ball.vx, self.ball.vy = self.calculateReturnVelocity(self.ball.x, self.ball.y, self.paddles[1].rect)
            hit = True
            self.ball.vx = -self.ball.vx
        
        return hit


    def displayScore(self): 
        for i in range(2):
            surf = self.scoreFont.render(str(self.scores[i]), False, WHITE)
            rect = surf.get_rect()
            rect.topleft = (WINDOW_WIDTH/2 + SCORE_OFFSETS[i], LINE_THICKNESS)
            self.DISPLAYSURF.blit(surf, rect)

        
    def reset_ball(self):
        ball_X = (WINDOW_WIDTH - LINE_THICKNESS)/2
        ball_Y = (WINDOW_HEIGHT - LINE_THICKNESS)/2
        self.ball = Ball(ball_X, ball_Y, LINE_THICKNESS)
        self.ball.vx = -BALL_VELOCITY # -1 = left, 1 = right
        self.ball.vy = 0 # -1 = up, 1 = down
    
    def reset(self):
        ball_X = (WINDOW_WIDTH - LINE_THICKNESS)/2
        ball_Y = (WINDOW_HEIGHT - LINE_THICKNESS)/2
        self.ball.place(ball_X, ball_Y)
        self.ball.vy = 0
        if self.serve == 1:
            self.ball.vx = -1
            self.serve = -1
        else:
            self.ball.vx = +1
            self.serve = 1
            
        paddle_l_X = PADDLE_OFFSET
        paddle_l_Y = (WINDOW_HEIGHT - PADDLE_SIZE)/2
        paddle_r_X = WINDOW_WIDTH - LINE_THICKNESS - PADDLE_OFFSET
        paddle_r_Y = (WINDOW_HEIGHT - PADDLE_SIZE)/2
        
        self.paddles[0].place(paddle_l_X, paddle_l_Y)
        self.paddles[1].place(paddle_r_X, paddle_r_Y)
        
        self.ball.draw(self)
        self.paddles[0].draw(self)
        self.paddles[1].draw(self)
        
        

    def main(self):
        parser = argparse.ArgumentParser(description=DESCRIPTION)
        parser.add_argument(
                "--ai",
                default=None,
                help="Play against AI? Default is No."
        )
        args = parser.parse_args()

        # Initialise game 
        pygame.init()
        pygame.font.init()
        
        pygame.display.set_caption('Pong')
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.scoreFont = pygame.font.SysFont('Arial', 50, bold=True)
        
        while True:
            # Quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Player 1 movement
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_UP]:
                self.paddles[1].move(-1)
            if keys_pressed[pygame.K_DOWN]:
                self.paddles[1].move(1)
            
            # Reset game
            if keys_pressed[pygame.K_SPACE]:
                self.reset_ball()
             
            # Player 2 movement
            if keys_pressed[pygame.K_w]:
                self.paddles[0].move(-1)
            if keys_pressed[pygame.K_s]:
                self.paddles[0].move(1)
                
            if args.ai is not None:
            	#AI movement 0 --> up, 1 --> down
            	movement = self.AI()
            	if movement == 0:
                	self.paddles[1].move(-1)
            	elif movement == 1:
                	self.paddle[1].move(1)
            
            # Draw game at each frame
            self.drawArena()
            self.ball.draw(self)
            self.paddles[0].draw(self)
            self.paddles[1].draw(self)
            
            # Collisions and ball movement
            point = self.checkEdgeCollision()
            hit = self.checkHitBall()
           
            if point == True:
                
                self.drawArena()
                self.ball.draw(self)
                self.paddles[0].draw(self)
                self.paddles[1].draw(self)
                self.displayScore()
                pygame.display.update()
                self.FPSCLOCK.tick(FPS)
                pygame.time.wait(500)
                
            else:
                self.ball.move()
                self.displayScore()
                # Update game for each frame
                pygame.display.update()
                self.FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    new_game = Game()
    
    new_game.main()
