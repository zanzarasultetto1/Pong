import time
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import sys
import random

print('\n--- Pong ---\n')
print("Select a game mode: \n\t1) You vs AI \n\t2) You vs A Person")
two_players = False if input("> ") == "1" else True

if not two_players:
	controller = True if input("\nDo you want to use a Controller? [Y/n] ").upper() == "Y" else False

else:
	controller = True if input("\nDo you want to use a Controller? [Y/n] ").upper() == "Y" else False

pygame.init()

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

if controller:
	num = 2 if two_players else 1
	while len(joysticks) < num:
		for event in pygame.event.get():
			if event.type == pygame.JOYDEVICEADDED:
				joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

	print([joystick.get_name() for joystick in joysticks])

point_to_arrive = int(input("\nWhat score do you want to arrive? "))

fullscreen = True if input("\nDo you want the fullscreen? [Y/n] ").upper() == "Y" else False


class Block(pygame.sprite.Sprite):
	def __init__(self, path, x_pos, y_pos):
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center=(x_pos, y_pos))


class Player(Block):
	def __init__(self, path, x_pos, y_pos, speed):
		super().__init__(path, x_pos, y_pos)
		self.speed = speed
		self.movement = 0

	def screen_constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screen_height:
			self.rect.bottom = screen_height

	def update(self, ball_group):
		self.rect.y += self.movement
		self.screen_constrain()


class Ball(Block):
	def __init__(self, path, x_pos, y_pos, speed_x, speed_y, paddles):
		super().__init__(path, x_pos, y_pos)
		self.speed_x = speed_x * random.choice((-1, 1))
		self.speed_y = speed_y * random.choice((-1, 1))
		self.paddles = paddles
		self.active = False
		self.score_time = 0

	def update(self):
		if self.active:
			self.rect.x += self.speed_x
			self.rect.y += self.speed_y
			self.collisions()
		else:
			self.restart_counter()
		
	def collisions(self):
		if self.rect.top <= 0 or self.rect.bottom >= screen_height:
			pygame.mixer.Sound.play(plob_sound)
			self.speed_y *= -1

		if pygame.sprite.spritecollide(self, self.paddles, False):
			pygame.mixer.Sound.play(plob_sound)
			collision_paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect
			if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
				self.speed_x *= -1
			if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
				self.speed_x *= -1
			if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
				self.rect.top = collision_paddle.bottom
				self.speed_y *= -1
			if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
				self.rect.bottom = collision_paddle.top
				self.speed_y *= -1

	def reset_ball(self):
		self.active = False
		self.speed_x *= random.choice((-1, 1))
		self.speed_y *= random.choice((-1, 1))
		self.score_time = pygame.time.get_ticks()
		self.rect.center = (screen_width/2, screen_height/2)
		pygame.mixer.Sound.play(score_sound)

	def restart_counter(self):
		current_time = pygame.time.get_ticks()
		countdown_number = 3

		if current_time - self.score_time <= 700:
			countdown_number = 3
		if 700 < current_time - self.score_time <= 1400:
			countdown_number = 2
		if 1400 < current_time - self.score_time <= 2100:
			countdown_number = 1
		if current_time - self.score_time >= 2100:
			self.active = True

		time_counter = basic_font.render(str(countdown_number), True, accent_color)
		time_counter_rect = time_counter.get_rect(center=(screen_width/2, screen_height/2 + 50))
		pygame.draw.rect(screen, bg_color, time_counter_rect)
		screen.blit(time_counter, time_counter_rect)


class Opponent(Block):
	def __init__(self, path, x_pos, y_pos, speed):
		super().__init__(path, x_pos, y_pos)
		self.speed = speed

	def update(self, ball_group):
		if self.rect.top < ball_group.sprite.rect.y:
			self.rect.y += self.speed
		if self.rect.bottom > ball_group.sprite.rect.y:
			self.rect.y -= self.speed
		self.constrain()

	def constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screen_height:
			self.rect.bottom = screen_height


class GameManager:
	def __init__(self, ball_group, paddle_group):
		self.player_score = 0
		self.opponent_score = 0
		self.ball_group = ball_group
		self.paddle_group = paddle_group

	def run_game(self):
		# Drawing the game objects
		self.paddle_group.draw(screen)
		self.ball_group.draw(screen)

		# Updating the game objects
		self.paddle_group.update(self.ball_group)
		self.ball_group.update()
		self.reset_ball()
		self.draw_score()

	def reset_ball(self):
		if self.ball_group.sprite.rect.right >= screen_width:
			self.opponent_score += 1
			self.ball_group.sprite.reset_ball()
		if self.ball_group.sprite.rect.left <= 0:
			self.player_score += 1
			self.ball_group.sprite.reset_ball()

	def draw_score(self):
		player_score = basic_font.render(str(self.player_score), True, accent_color)
		opponent_score = basic_font.render(str(self.opponent_score), True, accent_color)

		player_score_rect = player_score.get_rect(midleft=(screen_width / 2 + 40, screen_height/2))
		opponent_score_rect = opponent_score.get_rect(midright=(screen_width / 2 - 40, screen_height/2))

		screen.blit(player_score, player_score_rect)
		screen.blit(opponent_score, opponent_score_rect)


# General setup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

# Main Window
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width, screen_height)) if not fullscreen else pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Pong')

# Global Variables
bg_color = pygame.Color('#2F373F')
accent_color = (27, 35, 43)
basic_font = pygame.font.Font('freesansbold.ttf', 32)
plob_sound = pygame.mixer.Sound("assets/pong.ogg")
score_sound = pygame.mixer.Sound("assets/score.ogg")
middle_strip = pygame.Rect(screen_width/2 - 2, 0, 4, screen_height)

# Game objects
player = Player('assets/Paddle.png', screen_width - 20, screen_height/2, 5)
opponent = Opponent('assets/Paddle.png', 20, screen_width/2, 5) if not two_players else Player('assets/Paddle.png', 20, screen_width/2, 5)
if controller:
	player_controller = joysticks[0]
	if two_players:
		opponent_controller = joysticks[1]
paddle_group = pygame.sprite.Group()
paddle_group.add(player)
paddle_group.add(opponent)

ball = Ball('assets/Ball.png', screen_width/2, screen_height/2, 4, 4, paddle_group)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)

game_manager = GameManager(ball_sprite, paddle_group)

if controller:
	up_player, down_player = False, False
	up_opponent, down_opponent = False, False

run = True
while run:
	for event in pygame.event.get():
		if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			pygame.quit()
			sys.exit()
			run = False

		if controller:
			if event.type == pygame.JOYBUTTONDOWN:
				if event.button == 7:
					pygame.quit()
					sys.exit()

					run = False

		if not controller:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					player.movement -= player.speed
				if event.key == pygame.K_DOWN:
					player.movement += player.speed
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_UP:
					player.movement += player.speed
				if event.key == pygame.K_DOWN:
					player.movement -= player.speed

			if two_players:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_w:
						opponent.movement -= opponent.speed
					if event.key == pygame.K_s:
						opponent.movement += opponent.speed
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_w:
						opponent.movement += opponent.speed
					if event.key == pygame.K_s:
						opponent.movement -= opponent.speed

		else:
			if event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
				if event.button == 3:
					player.movement -= player.speed
				if event.button == 0:
					player.movement += player.speed
			if event.type == pygame.JOYBUTTONUP and event.joy == 0:
				if event.button == 3:
					player.movement += player.speed
				if event.button == 0:
					player.movement -= player.speed

			if two_players:
				if event.type == pygame.JOYBUTTONDOWN and event.joy == 1:
					if event.button == 3:
						opponent.movement -= opponent.speed
					if event.button == 0:
						opponent.movement += opponent.speed
				if event.type == pygame.JOYBUTTONUP and event.joy == 1:
					if event.button == 3:
						opponent.movement += opponent.speed
					if event.button == 0:
						opponent.movement -= opponent.speed

	if game_manager.player_score == point_to_arrive or game_manager.opponent_score == point_to_arrive:
		run = False

	# Background Stuff
	screen.fill(bg_color)
	pygame.draw.rect(screen, accent_color, middle_strip)
	
	# Run the game
	game_manager.run_game()

	# Rendering
	pygame.display.flip()
	clock.tick(120)

print(f'\n\n***********************************************\nPlayer1: {game_manager.opponent_score} | Player2: {game_manager.player_score}\n***********************************************\n')
winner = "Player1" if game_manager.opponent_score > game_manager.player_score else "Player2"
print(winner + " won.")
