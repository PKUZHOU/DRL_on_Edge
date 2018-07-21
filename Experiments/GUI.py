import pygame
from pygame.locals import *
from sys import exit
SCREEN_SIZE = (640, 480)
pygame.init()




screen = pygame.display.set_mode((640,480),RESIZABLE,32)
pygame.display.set_caption("Hello World!")
font = pygame.font.SysFont("arial", 16);
font_height = font.get_linesize()
event_text = []

while True:
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (0, 0, 0), (100, 120), 10)
    pygame.draw.circle(screen, (0, 0, 0), (200, 200), 10)
    pygame.draw.line(screen,(0,0,0),(100,120),(200,200),2)
    pygame.display.update()