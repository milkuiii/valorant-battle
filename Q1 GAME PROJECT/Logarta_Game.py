import pygame
import random
#import button

pygame.init()

clock = pygame.time.Clock()
fps = 60

# SCREEN SIZE
bottom_panel = 150
screen_width = 600
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Valorant Battle')

# DEFINE FONT
font = pygame.font.SysFont('VCR OSD Mono', 18)

# DEFINE COLORS
red = (94, 52, 49)
green = (0, 255, 0)
bright_red = (255, 0, 0)

# INGAME VARIABLES
current_fighter = 1
total_fighters = 6
action_cooldown = 0
action_wait_time = 90

attack = False
healing = False
aoe = False
flash = False
clicked = False
game_over = 0

# LOAD IMAGES !!
# BACKGROUND IMG
background_img = pygame.image.load('image assets/background/background.png').convert_alpha()

# PANEL IMG
panel_img = pygame.image.load('image assets/background/panel1.png').convert_alpha()

# BUTTON IMAGES
atk_button = pygame.image.load('image assets/buttons/button_atk.png').convert_alpha()
skill_button = pygame.image.load('image assets/buttons/button_skill.png').convert_alpha()
knife = pygame.image.load('image assets/buttons/knife.png').convert_alpha()
knife = pygame.transform.scale(knife, (knife.get_width() * .7, knife.get_height() * .7))

# VICTORY AND DEFEAT IMAGES
victory_img = pygame.image.load('image assets/background/victory.png').convert_alpha()
defeat_img = pygame.image.load('image assets/background/defeat.png').convert_alpha()

# FUNCTION FOR DRAWING TEXT
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# FUNCTION FOR DRAWING BG
def draw_bg():
    screen.blit(background_img, (0, 0))

# FUNCTION FOR DRAWING PANEL
def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    # SHOW AGENT STATS
    for count, i in enumerate(defenders_team):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 20, (screen_height - bottom_panel +10) + count * 20)

    for count, i in enumerate(attackers_team):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 280, (screen_height - bottom_panel +10) + count * 20)


# AGENT CLASS
class Agent():
    def __init__(self, x, y, name, max_hp, atk, speed):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
        self.speed = speed
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0 is idle, 1 is atk, 2 is hurt, 3 is dead
        self.update_time = pygame.time.get_ticks()
        # LOADING IMAGES - IDLE
        temp_list = []
        for i in range(2):
            img = pygame.image.load(f'image assets/characters/{self.name}/idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * .75, img.get_height() * .75))
            temp_list.append(img)
        self.animation_list.append(temp_list)
         # LOADING IMAGES - ATK
        temp_list = []
        for i in range(2):
            img = pygame.image.load(f'image assets/characters/{self.name}/atk/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * .75, img.get_height() * .75))
            temp_list.append(img)
        self.animation_list.append(temp_list)
         # LOADING IMAGES - HURT
        temp_list = []
        for i in range(2):
            img = pygame.image.load(f'image assets/characters/{self.name}/hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * .8, img.get_height() * .8))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # LOADING IMAGES - DEAD
        temp_list = []
        img = pygame.image.load(f'image assets/characters/dead.png')
        img = pygame.transform.scale(img, (img.get_width() * .8, img.get_height() * .8))
        temp_list.append(img)
        self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 600
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        #deal damage to enemy
        rand = random.randint(-5, 5)
        damage = self.atk + rand
        target.hp -= damage
        # ATK ANIMATIon
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        # run enemy hurt animation
        target.hurt()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), bright_red)
        damage_text_group.add(damage_text)

        # CHECK IF TARGET DIED
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.dead()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def dead(self):
        self.action = 3
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 100, 10))
        pygame.draw.rect(screen, green, (self.x, self.y, 100 * ratio, 10))

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        #move damage text up
        self.rect.y -= 1
        #delete the text after a few seconds
        self.counter += 1
        if self.counter > 30:
            self.kill()

damage_text_group = pygame.sprite.Group()           

# AGENTS
jett = Agent(100, 260, 'jett', 100, 20, 1)
reyna = Agent(500, 260, 'reyna', 100, 20, 2)
sage = Agent(50, 300, 'sage', 100, 20, 6)
chamber = Agent(550, 300, 'chamber', 100, 20, 4)
skye = Agent(450, 300, 'skye', 100, 20, 3)
kayo =Agent(150, 300, 'kayo', 100, 20, 5)

defenders_team = []
defenders_team.append(jett)
defenders_team.append(kayo)
defenders_team.append(sage)
attackers_team = []
attackers_team.append(reyna)
attackers_team.append(skye)
attackers_team.append(chamber)

jett_health_bar = HealthBar(160, screen_height - bottom_panel + 15, jett.hp, jett.max_hp)
kayo_health_bar = HealthBar(160, screen_height - bottom_panel + 35, kayo.hp, kayo.max_hp)
sage_health_bar = HealthBar(160, screen_height - bottom_panel + 55, sage.hp, sage.max_hp)

reyna_health_bar = HealthBar(460, screen_height - bottom_panel + 15, reyna.hp, reyna.max_hp)
chamber_health_bar = HealthBar(460, screen_height - bottom_panel + 55, chamber.hp, chamber.max_hp)
skye_health_bar = HealthBar(460, screen_height - bottom_panel + 35, skye.hp, skye.max_hp)


# GAME LOOP
run = True
while run:
    clock.tick(fps)

    # INITIALIZE SCREEN
    draw_bg()
    draw_panel()
    jett_health_bar.draw(jett.hp)
    reyna_health_bar.draw(reyna.hp)
    sage_health_bar.draw(sage.hp)
    chamber_health_bar.draw(chamber.hp)
    skye_health_bar.draw(skye.hp)
    kayo_health_bar.draw(kayo.hp)

    for agent in defenders_team:
        agent.update()
        agent.draw()

    for agent in attackers_team:
        agent.update()
        agent.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)
        
    # CONTROLS
    # RESET ACTION VARIABLES
    attack = False
    healing = False
    aoe = False
    flash = False
    target = None
    target_ally = random.choice(defenders_team)

    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, agent in enumerate(attackers_team):
        if agent.rect.collidepoint(pos):
            # HIDE MOUSE, SHOW KNIFE
            pygame.mouse.set_visible(False)
            screen.blit(knife, pos)
            if clicked == True and agent.alive == True:
                attack = True
                target = attackers_team[count]

    if game_over == 0:
        # PLAYER ACTION
        for count, agent in enumerate(defenders_team):
            if agent.speed == current_fighter:
                if agent.alive == True:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if attack == True and target != None:
                            agent.attack(target)
                            current_fighter += 1
                            action_cooldown = 0
                else:
                    current_fighter += 1
    else:
        game_over = -1
    # ENEMY ACTION   
    for count, agent in enumerate(attackers_team):
        if agent.speed == current_fighter:
            if agent.alive == True:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    agent.attack(target_ally)
                    current_fighter += 1
                    action_cooldown = 0
            else:
                current_fighter += 1

    if current_fighter > total_fighters:
        current_fighter = 1
    
    alive_agents = 0
    for agent in attackers_team:
        if agent.alive == True:
            alive_agents += 1
    if alive_agents == 0:
        game_over = 1

    # CHECK IF GAME OVER
    if game_over != 0:
        if game_over == 1:
            screen.blit(victory_img, (0, 50))
        if game_over == -1:
            screen.blit(defeat_img, (0, 50))
        current_fighter = 1
        action_cooldown
        game_over = 0

    for event in pygame.event.get():

        # QUIT GAME
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

pygame.quit()