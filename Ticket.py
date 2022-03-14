#Modified 11.17.2020 to include MCTS option
# system libs
import argparse
import multiprocessing as mp
import tkinter as tk
from PIL import ImageTk, Image
from functools import partial
import numpy as np
import random
import copy
from MCTS import MCTSNode


class Node:
	def __init__(self, name, fx, fy, tx, ty, px, py):
		self.name = name
		self.fx = fx
		self.fy = fy
		self.tx = tx
		self.ty = ty
		self.px = px
		self.py = py

class Player:
	def __init__(self, name, color, long_route, short1, short2, short3):
		self.name = name
		self.color = color
		self.long_route = long_route
		self.short1 = short1
		self.short2 = short2
		self.short3 = short3


class Edge:
	def __init__(self, node1, node2, fx, fy, tx, ty, number, taken):
		self.node1 = node1
		self.node2 = node2
		self.fx = fx
		self.fy = fy
		self.tx = tx
		self.ty = ty
		self.number = number
		self.taken = taken

class Game:
	def __init__(self):
		self.player_ready = False
		self.to_city = ""
		self.from_city = ""
		self.edges = []
		self.nodes = []
		self.human = Player("Caleb", "Orange", [], [], [], [])
		self.random1 = Player("rand1", "Blue", [], [], [], [])
		self.random2 = Player("rand2", "Black", [], [], [], [])
		self.mcts1 = Player("mcts", "Yellow", [], [], [], [])
		self.long_routes = []
		self.short_routes = []

		self.set_edges()
		self.set_nodes()
		self.set_routes()

		self.window = tk.Tk()
		self.window.title("Ticket to Ride")
		self.window.geometry("1280x1024")
		self.window.configure(background='')
		self.c = tk.Canvas(self.window,  width=1280, height=1024)
		self.fromtext = self.c.create_text(80, 20, text="From: ", fill="black")
		self.totext = self.c.create_text(80, 40, text="To: ")
		self.paint_board()
		#self.main()

	def set_routes(self):
		self.long_routes.append(['Lisbon', 'Amsterdam'])
		self.long_routes.append(['Cadiz', 'London'])
		self.long_routes.append(['Edinburgh', 'Barcelona'])
		self.long_routes.append(['Palermo', 'Essen'])
		self.long_routes.append(['Roma', 'Copenhagen'])
		self.long_routes.append(['Barcelona', 'Frankfurt'])

		self.short_routes.append(['Stockholm', 'Berlin'])
		self.short_routes.append(['Edinburgh', 'Paris'])
		self.short_routes.append(['Brest', 'Roma'])
		self.short_routes.append(['Berlin', 'Venezia'])
		self.short_routes.append(['Zurich', 'Berlin'])
		self.short_routes.append(['Paris', 'Brindsi'])
		self.short_routes.append(['Pamplona', 'Munchen'])
		self.short_routes.append(['Bruxelles', 'Venezia'])
		self.short_routes.append(['Madrid', 'Zurich'])

		self.human.long_route = random.choice(self.long_routes)
		self.human.short1 = random.choice(self.short_routes)
		self.human.short2 = random.choice(self.short_routes)
		self.human.short3 = random.choice(self.short_routes)
		self.random1.long_route = random.choice(self.long_routes)
		self.random1.short1 = random.choice(self.short_routes)
		self.random1.short2 = random.choice(self.short_routes)
		self.random1.short3 = random.choice(self.short_routes)
		self.random2.long_route = random.choice(self.long_routes)
		self.random2.short1 = random.choice(self.short_routes)
		self.random2.short2 = random.choice(self.short_routes)
		self.random2.short3 = random.choice(self.short_routes)
		self.mcts1.long_route = random.choice(self.long_routes)
		self.mcts1.short1 = random.choice(self.short_routes)
		self.mcts1.short2 = random.choice(self.short_routes)
		self.mcts1.short3 = random.choice(self.short_routes)


	def set_edges(self):
		self.edges.append(Edge("Lisbon", "Madrid", 40, 845, 135, 815, 1, ""))
		self.edges.append(Edge("Lisbon", "Cadiz", 40, 845, 135, 895, 2, ""))
		self.edges.append(Edge("Cadiz", "Madrid", 135, 895, 135, 815, 3, ""))
		self.edges.append(Edge("Barcelona", "Madrid", 235, 835, 135, 815, 4, ""))
		self.edges.append(Edge("Pamplona", "Barcelona", 205, 765, 235, 835, 1, ""))
		self.edges.append(Edge("Pamplona", "Madrid", 205, 765, 135, 815, 5, ""))
		self.edges.append(Edge("Pamplona", "Brest", 205, 765, 205, 605, 6, ""))
		self.edges.append(Edge("Pamplona", "Paris", 194, 769, 299, 609, 7, ""))
		self.edges.append(Edge("Paris", "Brest", 305, 615, 205, 605, 8, ""))
		self.edges.append(Edge("Brest", "Dieppe", 205, 605, 265, 575, 9, ""))
		self.edges.append(Edge("Dieppe", "Paris", 265, 575, 305, 615, 10, ""))
		self.edges.append(Edge("Pamplona", "Paris", 206, 781, 311, 621, 11, ""))
		self.edges.append(Edge("Dieppe", "London", 259, 569, 284, 480, 12, ""))
		self.edges.append(Edge("Dieppe", "London", 271, 581, 296, 480, 13, ""))
		self.edges.append(Edge("Edinburgh", "London", 256, 355, 281, 495, 14, ""))
		self.edges.append(Edge("Edinburgh", "London", 270, 355, 295, 495, 15, ""))
		self.edges.append(Edge("Amsterdam", "London", 385, 485, 290, 495, 16, ""))
		self.edges.append(Edge("Dieppe", "Bruxelles", 265, 575, 345, 535, 17, ""))
		self.edges.append(Edge("Bruxelles", "Amsterdam", 345, 535, 385, 485, 18, ""))
		self.edges.append(Edge("Paris", "Bruxelles", 295, 615, 338, 535, 19, ""))
		self.edges.append(Edge("Paris", "Bruxelles", 312, 615, 352, 535, 20, ""))
		self.edges.append(Edge("Amsterdam", "Essen", 385, 485, 445, 505, 21, ""))
		self.edges.append(Edge("Copenhagen", "Essen", 508, 390, 438, 505, 22, ""))
		self.edges.append(Edge("Copenhagen", "Essen", 522, 390, 452, 505, 23, ""))
		self.edges.append(Edge("Barcelona", "Marseille", 235, 835, 360, 745, 24, ""))
		self.edges.append(Edge("Pamplona", "Marseille", 205, 765, 360, 745, 25, ""))
		self.edges.append(Edge("Paris", "Marseille", 305, 615, 360, 745, 26, ""))
		self.edges.append(Edge("Roma", "Marseille", 485, 775, 360, 745, 27, ""))
		self.edges.append(Edge("Zurich", "Marseille", 425, 665, 360, 745, 28, ""))
		self.edges.append(Edge("Frankfurt", "Amsterdam", 435, 575, 385, 485, 29, ""))
		self.edges.append(Edge("Frankfurt", "Bruxelles", 435, 575, 345, 535, 30, ""))
		self.edges.append(Edge("Frankfurt", "Essen", 435, 575, 445, 505, 31, ""))
		self.edges.append(Edge("Frankfurt", "Munchen", 435, 575, 500, 615, 32, ""))
		self.edges.append(Edge("Frankfurt", "Paris", 435, 568, 305, 608, 33, ""))
		self.edges.append(Edge("Frankfurt", "Paris", 435, 582, 305, 622, 34, ""))
		self.edges.append(Edge("Zurich", "Munchen", 425, 665, 500, 615, 35, ""))
		self.edges.append(Edge("Zurich", "Venezia", 425, 665, 530, 690, 36, ""))
		self.edges.append(Edge("Copenhagen", "Stockholm", 510, 385, 590, 320, 37, ""))
		self.edges.append(Edge("Copenhagen", "Stockholm", 520, 395, 600, 330, 38, ""))
		self.edges.append(Edge("Roma", "Palermo", 485, 775, 595, 895, 39, ""))
		self.edges.append(Edge("Brindsi", "Palermo", 645, 855, 595, 895, 40, ""))
		self.edges.append(Edge("Brindsi", "Roma", 645, 855, 485, 775, 41, ""))
		self.edges.append(Edge("Venezia", "Roma", 530, 690, 485, 775, 42, ""))
		self.edges.append(Edge("Venezia", "Munchen", 530, 690, 500, 615, 43, ""))
		self.edges.append(Edge("Zurich", "Paris", 425, 665, 305, 615, 44, ""))
		self.edges.append(Edge("Essen", "Berlin", 445, 505, 530, 495, 45, ""))
		self.edges.append(Edge("Frankfurt", "Berlin", 440, 570, 525, 490, 46, ""))
		self.edges.append(Edge("Frankfurt", "Berlin", 450, 580, 535, 500, 47, ""))




	def set_nodes(self):
		self.nodes.append(Node("Lisbon", 25, 830, 55, 860, 90, 80))
		self.nodes.append(Node("Madrid", 120, 800, 150, 830, 10, 80))
		self.nodes.append(Node("Cadiz", 120, 880, 150, 910, 170, 80))
		self.nodes.append(Node("Barcelona", 220, 820, 250, 850, 250, 80))
		self.nodes.append(Node("Pamplona", 190, 750, 220, 780, 90, 100))
		self.nodes.append(Node("Paris", 290, 600, 320, 630, 10, 100))
		self.nodes.append(Node("Brest", 190, 590, 220, 620, 410, 80))
		self.nodes.append(Node("Dieppe", 250, 560, 280, 590, 330, 80))
		self.nodes.append(Node("London", 275, 480, 305, 510, 170, 100))
		self.nodes.append(Node("Edinburgh", 250, 340, 280, 370, 250, 100))
		self.nodes.append(Node("Amsterdam", 370, 470, 400, 500, 330, 100))
		self.nodes.append(Node("Bruxelles", 330, 520, 360, 550, 410, 100))
		self.nodes.append(Node("Marseille", 345, 730, 375, 760, 10, 120))
		self.nodes.append(Node("Essen", 430, 490, 460, 520, 90, 120))
		self.nodes.append(Node("Berlin", 515, 480, 545, 510, 170, 120))
		self.nodes.append(Node("Frankfurt", 430, 560, 460, 590, 250, 120))
		self.nodes.append(Node("Munchen", 485, 600, 515, 630, 330, 120))
		self.nodes.append(Node("Copenhagen", 500, 375, 530, 405, 410, 120))
		self.nodes.append(Node("Stockholm", 580, 310, 610, 340, 10, 140))
		self.nodes.append(Node("Zurich", 410, 650, 440, 680, 90, 140))
		self.nodes.append(Node("Venezia", 515, 675, 545, 705, 170, 140))
		self.nodes.append(Node("Roma", 470, 760, 500, 790, 250, 140))
		self.nodes.append(Node("Brindsi", 630, 840, 660, 870, 330, 140))
		self.nodes.append(Node("Palermo", 580, 880, 610, 910, 410, 140))


	def paint_board(self):
	    #This creates the main window of an application
	    movebut = tk.Button(self.c, text="Make Move", command=self.makemove, activebackground='green')
	    movebut.configure(width=10)
	    movebutwin = self.c.create_window(130, 10, anchor="nw", window=movebut)

	    clearmovebut = tk.Button(self.c, text="Clear", command=self.clearCities, activebackground='green')
	    clearmovebut.configure(width=10)
	    clearmovebutwin = self.c.create_window(130, 30, anchor="nw", window=clearmovebut)

	    ranmovebut = tk.Button(self.c, text="Random 1", command=partial(self.randomMove, "Black"), activebackground='green')
	    ranmovebut.configure(width=10)
	    ranmovebutwin = self.c.create_window(230, 10, anchor="nw", window=ranmovebut)

	    mcmovebut = tk.Button(self.c, text="MCTS Agent", command=partial(self.randomMove, "Yellow"), activebackground='green')
	    mcmovebut.configure(width=10)
	    mcmovebutwin = self.c.create_window(330, 10, anchor="nw", window=mcmovebut)

	    ranmovebut = tk.Button(self.c, text="Random 2", command=partial(self.randomMove, "Blue"), activebackground='green')
	    ranmovebut.configure(width=10)
	    ranmovebutwin = self.c.create_window(230, 30, anchor="nw", window=ranmovebut)

	    path = "europe_clear.png"
	    img = ImageTk.PhotoImage(Image.open(path))

	    self.c.create_image(0, 0, image=img, anchor="nw")
	    self.c.create_rectangle(0,0,800,250,fill="white")
	    self.c.create_line(525, 0, 525, 250, fill="black")

	    self.fromtext = self.c.create_text(80, 20, text="From: ", fill="black")
	    self.totext = self.c.create_text(80, 40, text="To: ")
	    self.c.create_text(550, 50, anchor='w', text="Player: " + self.human.name)
	    self.c.create_text(550, 70, anchor='w', text="Long Route: " + self.human.long_route[0] + " - " + self.human.long_route[1])
	    self.c.create_text(550, 90, anchor='w', text="Short Route 1: " + self.human.short1[0] + " - " + self.human.short1[1])
	    self.c.create_text(550, 110, anchor='w', text="Short Route 2: " + self.human.short2[0] + " - " + self.human.short2[1])
	    self.c.create_text(550, 130, anchor='w', text="Short Route 3: " + self.human.short3[0] + " - " + self.human.short3[1])



	    for edge in self.edges:
	    	self.c.create_line(edge.fx, edge.fy, edge.tx, edge.ty, fill='#FF0000', width=10)

	    for node in self.nodes:
	    	self.c.create_oval(node.fx, node.fy, node.tx, node.ty, fill='#FF0000')
	    	self.c.create_text(node.fx+20, node.fy+40, fill="black", font="Times 20 bold", text=node.name)
	    	but = tk.Button(self.c, text=node.name, command=partial(self.cityclick, node.name))
	    	but.configure(width=10)
	    	self.c.create_window(node.px, node.py, anchor="nw", window=but)

	    
	    self.c.pack()

	    self.window.mainloop()

	def randomMove(self, color):
		open_edges = []
		for edge in self.edges:
			if edge.taken == "":
				open_edges.append(edge)
		if len(open_edges) == 0:
			print("That's all folks!")
			self.tally_scores()
		else:
			newEdge = random.choice(open_edges)
			self.c.create_line(newEdge.fx, newEdge.fy, newEdge.tx, newEdge.ty, fill=color, width=10)
			newEdge.taken = color

	def makemove(self):
		if self.from_city == "" or self.to_city == "":
			print("Please select two cities")
		edge_num = -1
		true_edge = Edge("", "", 0, 0, 0, 0, 0, "")
		for edge in self.edges:
			if ((edge.node1 == self.to_city and edge.node2 == self.from_city) or (edge.node1 == self.from_city and edge.node2 == self.to_city)) and edge.taken == "":
				print("Edge exists")
				edge.taken = "Green"
				edge_num = edge.number
				true_edge = edge
			if edge_num > 0:
				self.c.create_line(true_edge.fx, true_edge.fy, true_edge.tx, true_edge.ty, fill='green', width=10)
				self.c.itemconfig(self.fromtext, text="From: ")
				self.from_city=""
				self.c.itemconfig(self.totext, text="To: ")
				self.to_city=""
				self.player_ready = True

	def mctsMove(self, color):
		max_iterations = 200

		root = MCTSNode(self.mcts1, self.edges, None)

		for i in range(max_iterations):
			cur_node = root.select()
			cur_node.simulate()

		print('MCTS chooses action', root.max_child())
		for edge in self.edges:
			if edge.number ==  root.max_child():
				edge.taken = color

	def tally_scores(self):
		print("Here")
		black_edges = []
		blue_edges = []
		green_edges = []

		for edge in self.edges:
			if edge.taken == "Black":
				black_edges.append(edge)
			elif edge.taken == "Blue":
				blue_edges.append(edge)
			elif edge.taken == "Green":
				green_edges.append(edge)


		print("We're going in!")
		green_val = self.route_complete(self.human.long_route[0], self.human.long_route[1], copy.deepcopy(green_edges), 20)
		black_val = self.route_complete(self.random1.long_route[0], self.random1.long_route[1], copy.deepcopy(black_edges), 20)
		blue_val = self.route_complete(self.random2.long_route[0], self.random2.long_route[1], copy.deepcopy(blue_edges), 20)
		print("We're going in!")
		green_val += self.route_complete(self.human.short1[0], self.human.short1[1], copy.deepcopy(green_edges), 6)
		black_val += self.route_complete(self.random1.short1[0], self.random1.short1[1], copy.deepcopy(black_edges), 6)
		blue_val += self.route_complete(self.random2.short1[0], self.random2.short1[1], copy.deepcopy(blue_edges), 6)

		green_val += self.route_complete(self.human.short2[0], self.human.short2[1], copy.deepcopy(green_edges), 6)
		black_val += self.route_complete(self.random1.short2[0], self.random1.short2[1], copy.deepcopy(black_edges), 6)
		blue_val += self.route_complete(self.random2.short2[0], self.random2.short2[1], copy.deepcopy(blue_edges), 6)

		green_val += self.route_complete(self.human.short3[0], self.human.short3[1], copy.deepcopy(green_edges), 6)
		black_val += self.route_complete(self.random1.short3[0], self.random1.short3[1], copy.deepcopy(black_edges), 6)
		blue_val += self.route_complete(self.random2.short3[0], self.random2.short3[1], copy.deepcopy(blue_edges), 6)
		

		self.c.create_rectangle(500, 500, 750, 750, fill='lightgray')
		self.c.create_text(515, 515, anchor='w', text='Final Scores', font="Times 20 bold")
		self.c.create_text(515, 600, anchor='w', text='Green: '  + str(green_val))
		self.c.create_text(515, 615, anchor='w', text='Blue: '  + str(blue_val))
		self.c.create_text(515, 630, anchor='w', text='Black: '  + str(black_val))
		self.c.pack()


	def route_complete(self, start, goal, edges, reward):
		
		if edges == None:
			return 0 
		else:
			print(start + " - " + goal + " with " + str(len(edges)))
		for edge in edges:
			print("    " + edge.node1 + " - " + edge.node2)
			if (edge.node1 == start and edge.node2 == goal) or (edge.node2 == start and edge.node1 == goal):
				print("Route Completed!")
				return reward
			if (edge.node1 == start):
				edges.remove(edge)
				return self.route_complete(edge.node2, goal, edges, reward)
			if (edge.node2 == start):
				edges.remove(edge)
				return self.route_complete(edge.node1, goal, edges, reward)
		return 0



	def clearCities(self):
		self.to_city = ""
		self.from_city = ""
		self.c.itemconfig(self.totext, text="To: ")
		self.c.itemconfig(self.fromtext, text="From: ")

	def cityclick(self, city_name):
		print(city_name)
		if self.from_city == "":
			self.c.itemconfig(self.fromtext, text="From: " + city_name)
			self.from_city=city_name
		elif self.to_city == "":
			self.c.itemconfig(self.totext, text="To: " + city_name)
			self.to_city=city_name


if __name__=='__main__':

	cities = ['Lisbon', 'Madrid', 'Cadiz', 'Barcelona', 'Pamplona', 'Paris', 'Brest', 'Dieppe'] #, 'Bruxelles', 'Amsterdam', 'London', 'Edinburgh', 'Essen', 'Frankfurt', 'München', 'Zurich', 'Marseille', 'Venezia', 'Roma']

	game = Game()