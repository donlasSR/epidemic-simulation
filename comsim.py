import pygame
import random
import math
import time
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from io import BytesIO
import tkinter as tk
from tkinter import filedialog


matplotlib.use("Agg")  


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TAU = 2 * math.pi
POP_SIZE = 500
PERSON_SIZE = 5
VELOCITY = 10
INFECTION_RADIUS = 10
RECOVERY_TIME = 15
AVOIDANCE_RADIUS_MULTIPLIER = 10.0
INFECTION_PROBABILITY = 0.7
RECOVERY_TIME_VARIANCE = 3
RECOVERY_PROBABILITY = 0.95

paused = False
show_settings = False

DT = 0.05

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

GRAPH_WIDTH = 600
GRAPH_HEIGHT = 400

class Person:
    def __init__(self, x=None, y=None, infected=False):
        self.x = x if x is not None else random.randint(GRAPH_WIDTH, SCREEN_WIDTH)
        self.y = y if y is not None else random.randint(0, SCREEN_HEIGHT)
        self.status = 1 if infected else 0  # 0 = susceptible, 1 = infected, 2 = recovered , 3 = dead
        self.will_die = False
        self.infected = infected
        self.recovery_time = RECOVERY_TIME

    def move(self):
        angle = random.uniform(0, TAU)
        new_x = self.x + VELOCITY * math.cos(angle)
        new_y = self.y + VELOCITY * math.sin(angle)

        if new_x < GRAPH_WIDTH:
            new_x = GRAPH_WIDTH + 1
        if new_x > SCREEN_WIDTH:
            new_x = SCREEN_WIDTH -1
        if new_y < 0:
            new_y = 1
        if new_y > SCREEN_HEIGHT:
            new_y = SCREEN_HEIGHT -1
        self.x = new_x % SCREEN_WIDTH
        self.y = new_y % SCREEN_HEIGHT

    def move_away_from_infected(self, others):
        nearest = None
        min_dist = float('inf')
        for other in others:
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < min_dist:
                min_dist = dist
                nearest = other

        if nearest and min_dist <  AVOIDANCE_RADIUS_MULTIPLIER:
            dx = self.x - nearest.x
            dy = self.y - nearest.y
            angle = math.atan2(dy, dx)
        else:
            angle = random.uniform(0, TAU)

        new_x = self.x + VELOCITY * math.cos(angle)
        new_y = self.y + VELOCITY * math.sin(angle)

        if new_x < GRAPH_WIDTH:
            new_x = GRAPH_WIDTH + 1
        if new_x > SCREEN_WIDTH:
            new_x = SCREEN_WIDTH -1
        if new_y < 0:
            new_y = 1
        if new_y > SCREEN_HEIGHT:
            new_y = SCREEN_HEIGHT -1
        self.x = new_x % SCREEN_WIDTH
        self.y = new_y % SCREEN_HEIGHT

def draw_person(screen, person):
    if person.status == 0:
        color = BLUE
    elif person.status == 1:
        color = RED
        pygame.draw.circle(screen, YELLOW, (int(person.x), int(person.y)), INFECTION_RADIUS, 1)
    elif person.status == 2:
        color = GREEN
    else:
        color = GRAY
    pygame.draw.circle(screen, color, (int(person.x), int(person.y)), PERSON_SIZE)

def draw_graph(history_S, history_I, history_R, history_D):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    ax.plot(history_S, label='Susceptible', color='blue')
    ax.plot(history_I, label='Infected', color='red')
    ax.plot(history_R, label='Recovered', color='green')
    ax.plot(history_D, label='Death', color='gray')
    ax.set_ylim(0, 100)
    ax.set_title("Graph")
    ax.legend(loc='upper right')
    ax.set_xlabel("Time")
    ax.set_ylabel("Percentage")

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = pygame.image.load(buf)
    buf.close()
    plt.close(fig)
    return image

def draw_buttons(screen, font):
    pygame.draw.rect(screen, RED, (50, 420, 100, 50), 2)
    pause_text = font.render("Pause", True, WHITE)
    screen.blit(pause_text, (65, 435))

    pygame.draw.rect(screen, RED, (50, 500, 100, 50), 2)
    settings_text = font.render("Setting", True, WHITE)
    screen.blit(settings_text, (60, 515))

setting_rects = []

def draw_settings(screen, font):
    global setting_rects
    setting_rects = []
    settings_info = [
        ("VELOCITY", VELOCITY),
        ("INFECTION_RADIUS", INFECTION_RADIUS),
        ("INFECTION_PROBABILITY", INFECTION_PROBABILITY),
        ("RECOVERY_TIME", RECOVERY_TIME),
        ("RECOVERY_TIME_VARIANCE", RECOVERY_TIME_VARIANCE),
        ("RECOVERY_PROBABILITY", RECOVERY_PROBABILITY),
        ("AVOIDANCE_RADIUS_MULTIPLIER", AVOIDANCE_RADIUS_MULTIPLIER)
    ]
    for i, (label, value) in enumerate(settings_info):
        line = f"{label} = {value}"
        text_surface = font.render(line, True, WHITE)
        rect = text_surface.get_rect(topleft=(50, 600 + i * 30))
        screen.blit(text_surface, rect)
        setting_rects.append((label, rect))

def save_graph(history_S, history_I, history_R, history_D,save_path):
    fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
    ax.plot(history_S, label='Susceptible', color='blue')
    ax.plot(history_I, label='Infected', color='red')
    ax.plot(history_R, label='Recovered', color='green')
    ax.plot(history_D, label='Death', color='gray')
    ax.set_ylim(0, 100)
    ax.set_title("Graph")
    ax.legend(loc='upper right')
    ax.set_xlabel("Time")
    ax.set_ylabel("Percentage")

    plt.savefig(save_path) 
    plt.close(fig)

def main():
    global paused, show_settings

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Epidemic Simulation")
    font = pygame.font.SysFont(None, 30)
    clock = pygame.time.Clock()

    population = [Person() for _ in range(POP_SIZE)]
    for i in range(3):
        population[i].status = 1

    t = 0
    history_S, history_I, history_R , history_D = [], [], [], []
    running = True

    while running:
        screen.fill(BLACK)

        n_S = n_I = n_R = n_D = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if 50 <= x <= 150 and 420 <= y <= 470:
                    paused = not paused
                    
                elif 50 <= x <= 150 and 500 <= y <= 550:
                    show_settings = not show_settings
                elif show_settings:
                    for label, rect in setting_rects:
                        if rect.collidepoint(x, y):
                            adjust = 0.5 if event.button == 1 else -0.5
                            adjustAVOID = 10 if event.button == 1 else -10
                            adjustInfProb = 0.05 if event.button == 1 else -0.05
                            if label == "VELOCITY":
                                globals()["VELOCITY"] = round(globals()["VELOCITY"] + adjust, 2)
                            elif label == "INFECTION_RADIUS":
                                globals()["INFECTION_RADIUS"] = max(1, round(globals()["INFECTION_RADIUS"] + adjust, 2))
                            elif label == "INFECTION_PROBABILITY":
                                globals()["INFECTION_PROBABILITY"] = max(0, round(globals()["INFECTION_PROBABILITY"] + adjustInfProb, 2))
                            elif label == "RECOVERY_TIME":
                                globals()["RECOVERY_TIME"] = max(1, round(globals()["RECOVERY_TIME"] + adjust, 2))
                            elif label == "RECOVERY_TIME_VARIANCE":
                                globals()["RECOVERY_TIME_VARIANCE"] = max(1, round(globals()["RECOVERY_TIME_VARIANCE"] + adjust, 2))
                            elif label == "RECOVERY_PROBABILITY":
                                globals()["RECOVERY_PROBABILITY"] = max(0, round(globals()["RECOVERY_PROBABILITY"] + adjustInfProb, 2))
                            elif label == "AVOIDANCE_RADIUS_MULTIPLIER":
                                globals()["AVOIDANCE_RADIUS_MULTIPLIER"] = max(0, round(globals()["AVOIDANCE_RADIUS_MULTIPLIER"] + adjustAVOID, 2))
                elif x > GRAPH_WIDTH:
                    if event.button == 2 or (event.button == 1 and pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        # Middle click or Shift + Left click spawns an infected person
                        population.append(Person(x, y, infected=True))
        if paused:
            for i, p in enumerate(population):
                        draw_person(screen, p)
        if not paused:
            for i, p in enumerate(population):
                if p.status == 0:
                    for other in population:
                        if other.status == 1:
                            if math.hypot(p.x - other.x, p.y - other.y) < INFECTION_RADIUS:
                                if random.random() < INFECTION_PROBABILITY:
                                    p.status = 1
                                    p.recovery_time = random.uniform(max(0, RECOVERY_TIME - RECOVERY_TIME_VARIANCE),RECOVERY_TIME + RECOVERY_TIME_VARIANCE)
                                break

                if p.status == 1:
                    p.recovery_time -= DT
                    if p.recovery_time <= 0:
                        if random.random() < RECOVERY_PROBABILITY:
                            p.status = 2
                        else: # 50% chance to die
                            p.status = 3

                if p.status != 3:
                    if p.status == 0:
                        infected_people = [other for other in population if other.status == 1]
                        p.move_away_from_infected(infected_people)
                    else:
                        p.move()

                draw_person(screen, p)

                if p.status == 0: n_S += 1
                elif p.status == 1: n_I += 1
                elif p.status == 2: n_R += 1
                elif p.status == 3: n_D += 1

            history_S.append(n_S * 100 / POP_SIZE)
            history_I.append(n_I * 100 / POP_SIZE)
            history_R.append(n_R * 100 / POP_SIZE)
            history_D.append(n_D * 100 / POP_SIZE)

        graph_surface = draw_graph(history_S[-10000:], 
                                   history_I[-10000:], 
                                   history_R[-10000:], 
                                   history_D[-10000:],)
        screen.blit(graph_surface, (0, 0))

        stat_text = f"t={t:.1f}  S={history_S[-1]:.2f}%  I={history_I[-1]:.2f}%  R={history_R[-1]:.2f}%  D={history_D[-1]:.2f}%"
        text_surface = font.render(stat_text, True, WHITE)
        screen.blit(text_surface, (GRAPH_WIDTH + 10, 10))

        draw_buttons(screen, font)
        if show_settings:
            draw_settings(screen, font)

        pygame.display.flip()
        clock.tick(20)
        if not paused:
            t += DT

        if n_I == 0 and not paused:
            time.sleep(2)
            running = False
    root = tk.Tk()
    root.withdraw()  # Hide main Tk window

    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")],
        title="Select file to save the graph"
    )
    save_graph( history_S[-10000:], 
                history_I[-10000:], 
                history_R[-10000:], 
                history_D[-10000:],
                save_path) #edit save path here
    pygame.quit()

if __name__ == "__main__":
    main()
