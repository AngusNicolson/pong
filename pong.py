import pygame
import sys
import numpy as np

FPS = 400 #Sets the speed of the game

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400
LINE_THICKNESS = 10
PADDLE_SIZE = 60
PADDLE_OFFSET = 20 #Distance from sides of pitch
OVERSHOOT = 5 #Min amount of paddle visible on screen
MAX_ANGLE = 45 #degrees
BALL_VELOCITY = 1.2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)



def drawArena():
    DISPLAYSURF.fill(BLACK)
    pygame.draw.rect(DISPLAYSURF, WHITE, ((0,0), (WINDOW_WIDTH, WINDOW_HEIGHT)), LINE_THICKNESS*2)
    pygame.draw.line(DISPLAYSURF, WHITE, (WINDOW_WIDTH/2, 0),(WINDOW_WIDTH/2, WINDOW_HEIGHT), 1)
    
def drawPaddle(paddle):
    if paddle.bottom > WINDOW_HEIGHT - LINE_THICKNESS + PADDLE_SIZE - OVERSHOOT:
        paddle.bottom = WINDOW_HEIGHT - LINE_THICKNESS + PADDLE_SIZE - OVERSHOOT
    elif paddle.top < LINE_THICKNESS - PADDLE_SIZE + OVERSHOOT:
        paddle.top = LINE_THICKNESS - PADDLE_SIZE + OVERSHOOT
    pygame.draw.rect(DISPLAYSURF, WHITE, paddle)

def drawBall(ball):
    pygame.draw.rect(DISPLAYSURF, WHITE, ball)

def moveBall(ball, DirX, DirY):
    global placeX, placeY
    placeX += DirX
    placeY += DirY
    ball.y = int(placeY)
    ball.x = int(placeX)
    """
    ball.y += DirY
    ball.x += DirX
    """
    return ball

def checkEdgeCollision(ball, DirX, DirY):
    global score1, score2
    if ball.bottom >= WINDOW_HEIGHT - LINE_THICKNESS or ball.top <= LINE_THICKNESS:
        DirY = DirY * -1
    if ball.left <= LINE_THICKNESS:
        DirX = DirX * -1
        score2 +=1
    if ball.right >= WINDOW_WIDTH - LINE_THICKNESS:
        DirX = DirX * -1
        score1 +=1
    
    return DirX, DirY

def AI(ball, paddle1, paddle2):
    movement = 0
    if ball.centery > paddle2.centery:
        movement = 1
    elif ball.centery < paddle2.centery:
        movement = 0
    
    return movement

def checkHitBall(ball, paddle1, paddle2, ballDirX):
    if ballDirX == -1 and paddle1.colliderect(ball):
        ballDirX = 1
        
    if ballDirX == 1 and paddle2.colliderect(ball):
        ballDirX = -1
    return ballDirX

def checkHitBall2(ball, paddle1, paddle2, vX, vY):
    if paddle1.colliderect(ball):
        vX, vY = calculateReturnVelocity(placeX, placeY, paddle1)
    if paddle2.colliderect(ball):
        vX, vY = calculateReturnVelocity(placeX, placeY, paddle2)
        vX = -vX
    
    return vX, vY

def calculateReturnVelocity(placeX, placeY, paddle):
    x = placeY - paddle.top + LINE_THICKNESS/2
    angle = 2*MAX_ANGLE*x/PADDLE_SIZE - MAX_ANGLE
    angle = np.deg2rad(angle)
    velocityX = BALL_VELOCITY*np.sqrt(1/(np.tan(angle)**2 + 1))
    velocityY= np.sqrt(BALL_VELOCITY**2- velocityX**2)
    if x < PADDLE_SIZE/2:
        velocityY = -velocityY
    
    return velocityX, velocityY

def displayScore():
    surf1 = scoreFont.render(str(score1), False, WHITE)
    rect1 = surf1.get_rect()
    rect1.topleft = (WINDOW_WIDTH/2 - 60, LINE_THICKNESS)
    DISPLAYSURF.blit(surf1, rect1)
    
    surf2 = scoreFont.render(str(score2), False, WHITE)
    rect2 = surf2.get_rect()
    rect2.topleft = (WINDOW_WIDTH/2 + 35, LINE_THICKNESS)
    DISPLAYSURF.blit(surf2, rect2)


def main():
    pygame.init()
    pygame.font.init()
    #Initialise game
    pygame.display.set_caption('Pong')
    global DISPLAYSURF, placeX, placeY, scoreFont, score1, score2
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    scoreFont = pygame.font.SysFont('Arial', 50, bold=True)
    
    #Set initial coordinates of objects
    ball_X = (WINDOW_WIDTH - LINE_THICKNESS)/2
    ball_Y = (WINDOW_HEIGHT - LINE_THICKNESS)/2
    paddle1_Y = (WINDOW_HEIGHT - PADDLE_SIZE)/2
    paddle2_Y = (WINDOW_HEIGHT - PADDLE_SIZE)/2
    placeX = ball_X
    placeY = ball_Y
    
    #Create objects
    paddle1 = pygame.Rect(PADDLE_OFFSET, paddle1_Y, LINE_THICKNESS, PADDLE_SIZE)
    paddle2 = pygame.Rect(WINDOW_WIDTH - LINE_THICKNESS - PADDLE_OFFSET, paddle2_Y, LINE_THICKNESS, PADDLE_SIZE)
    ball = pygame.Rect(ball_X, ball_Y, LINE_THICKNESS, LINE_THICKNESS)
    
    
    
    #Initial ball direction
    velocityX = -BALL_VELOCITY # -1 = left, 1 = right
    velocityY = 0 # -1 = up, 1 = down
    
    #Initial scores
    score1, score2 = 0, 0
    
    while True:
        #Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        #Player 1 movement
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP]:
            paddle2.y += -1
        if keys_pressed[pygame.K_DOWN]:
            paddle2.y += 1
        
        #Reset game
        if keys_pressed[pygame.K_SPACE]:
            ball = pygame.Rect(ball_X, ball_Y, LINE_THICKNESS, LINE_THICKNESS)
            placeX = ball_X
            placeY = ball_Y
            velocityX = -1
            velocityY = 0
         
        #Player 2 movement
        if keys_pressed[pygame.K_w]:
            paddle1.y += -1
        if keys_pressed[pygame.K_s]:
            paddle1.y += 1
            
        """  
        #AI movement 0 --> up, 1 --> down
        movement = AI(ball, paddle1, paddle2)
        if movement == 0:
            paddle2.y += -1
        elif movement == 1:
            paddle2.y += 1
        """
        #Draw game at each frame
        drawArena()
        drawBall(ball)
        drawPaddle(paddle1)
        drawPaddle(paddle2)
        
        #Collisions and ball movement
        velocityX, velocityY = checkEdgeCollision(ball, velocityX, velocityY)
        velocityX, velocityY = checkHitBall2(ball, paddle1, paddle2, velocityX, velocityY)
        ball = moveBall(ball, velocityX, velocityY)
        
        displayScore()
        
        #Update game for each frame
        pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()
