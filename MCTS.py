import numpy as np
import copy
#from Ticket import Player
class Player:
	def __init__(self, name, color, long_route, short1, short2, short3):
		self.name = name
		self.color = color
		self.long_route = long_route
		self.short1 = short1
		self.short2 = short2
		self.short3 = short3

class MCTSNode:
	def __init__(self, player, edges, parent):
		self.edges = edges
		self.rollout_edges = copy.deepcopy(edges)
		self.player = player
		self.player_col =  player.color
		self.moves = len(self.get_open_edges(edges))
		self.parent = parent
		self.children = dict()
		self.terminal_state = (self.moves <= 3)

		for m in range(self.moves):
			self.children[m] = None

		self.n = 0
		self.w = 0
		self.c = np.sqrt(2)

	def max_child(self):
		max_n = 0
		max_m = None

		for m in range(self.moves):
			if self.children[m].n > max_n:
				max_n = self.children[m].n
				for i in self.get_open_edges(self.rollout_edges):
					if m == i:
						max_m = i.number

		return max_m

	def upper_bound(self, N):
		return ((self.w / self.n) + (self.c * (np.sqrt(np.log(N) / self.n))))

	def get_open_edges(self, edges):
		open_edges = []
		for edge in edges:
			if edge.taken == "":
				open_edges.append(edge)

		return open_edges

	def select(self):
		max_ub = -np.inf
		max_child = None 
		if self.terminal_state:
			return self
		for m in range(self.moves):
			if self.children[m] is None:
				available_edges = self.get_open_edges(self.rollout_edges)
				new_move = np.random.choice(available_edges)
				self.set_edge(new_move, self.player.color)
				self.children[m] = MCTSNode(self.player, self.rollout_edges, self) 
				return self.children[m] 
			current_ub = self.children[m].upper_bound(self.n)
			print("		", m,  " ", current_ub)

			if current_ub > max_ub:
				max_ub = current_ub
				max_child = m

		return self.children[max_child].select()

	def simulate(self):
		reward = 0
		if self.terminal_state:
			mcts_edges = []
			for edge in self.rollout_edges:
				if edge.taken == self.player.color:
					mcts_edges.append(edge)
			reward += self.route_complete(self.player.long_route[0], self.player.long_route[1], copy.deepcopy(mcts_edges), 20)
			reward += self.route_complete(self.player.short1[0], self.player.short1[1], copy.deepcopy(mcts_edges), 6)
			reward += self.route_complete(self.player.short2[0], self.player.short2[1], copy.deepcopy(mcts_edges), 6)
			reward += self.route_complete(self.player.short3[0], self.player.short3[1], copy.deepcopy(mcts_edges), 6)

		elif not self.terminal_state:
			turn = self.player.color
			while True:
				available_edges = self.get_open_edges(self.rollout_edges)
				new_move = np.random.choice(available_edges)
				self.set_edge(new_move, turn)

				if len(available_edges) <= 3:
					mcts_edges = []
					for edge in self.edges:
						if edge.taken == self.player.color:
							mcts_edges.append(edge)

					reward += self.route_complete(self.player.long_route[0], self.player.long_route[1], copy.deepcopy(mcts_edges), 20)
					reward += self.route_complete(self.player.short1[0], self.player.short1[1], copy.deepcopy(mcts_edges), 6)
					reward += self.route_complete(self.player.short2[0], self.player.short2[1], copy.deepcopy(mcts_edges), 6)
					reward += self.route_complete(self.player.short3[0], self.player.short3[1], copy.deepcopy(mcts_edges), 6)
					break
				else:
					if turn == "Yellow":
						turn = "Green"
					elif turn == "Green":
						turn = "Black"
					elif turn == "Black":
						turn = "Blue"
					else:
						turn = "Yellow"

		self.w += reward
		self.n += 1
		self.parent.back(reward)

	def back(self, score):
		self.n += 1
		self.w += score
		if self.parent is not None:
			self.parent.back(score)

	def set_edge(self, taken_edge, turn):
		for edge in self.rollout_edges:
			if (edge.number == taken_edge.number):
				taken_edge.taken = turn

	def route_complete(self, start, goal, edges, reward):
		if edges == None:
			return 0 

		for edge in edges:
			#print("    " + edge.node1 + " - " + edge.node2)
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