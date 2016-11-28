from window import Window

class LoadingWindow(Window):

	def __init__(self, w, h):
		super().__init__(w, h)

	def reset(self):
		self.animIndex = 0
		self.animTimer = 0.0
		self.animReset = 0.25
		self.animStates = [
			[("L", (self.width // 2 - 5, self.height // 2)),
			 ("o", (self.width // 2 - 4, self.height // 2)),
			 ("a", (self.width // 2 - 3, self.height // 2)),
			 ("d", (self.width // 2 - 2, self.height // 2)),
			 ("i", (self.width // 2 - 1, self.height // 2)),
			 ("n", (self.width // 2, self.height // 2)),
			 ("g", (self.width // 2 + 1, self.height // 2)),
			 (".", (self.width // 2 + 2, self.height // 2)),
			 (" ", (self.width // 2 + 3, self.height // 2)),
			 (" ", (self.width // 2 + 4, self.height // 2))],

			[("L", (self.width // 2 - 5, self.height // 2)),
			 ("o", (self.width // 2 - 4, self.height // 2)),
			 ("a", (self.width // 2 - 3, self.height // 2)),
			 ("d", (self.width // 2 - 2, self.height // 2)),
			 ("i", (self.width // 2 - 1, self.height // 2)),
			 ("n", (self.width // 2, self.height // 2)),
			 ("g", (self.width // 2 + 1, self.height // 2)),
			 (".", (self.width // 2 + 2, self.height // 2)),
			 (".", (self.width // 2 + 3, self.height // 2)),
			 (" ", (self.width // 2 + 4, self.height // 2))],

			[("L", (self.width // 2 - 5, self.height // 2)),
			 ("o", (self.width // 2 - 4, self.height // 2)),
			 ("a", (self.width // 2 - 3, self.height // 2)),
			 ("d", (self.width // 2 - 2, self.height // 2)),
			 ("i", (self.width // 2 - 1, self.height // 2)),
			 ("n", (self.width // 2, self.height // 2)),
			 ("g", (self.width // 2 + 1, self.height // 2)),
			 (".", (self.width // 2 + 2, self.height // 2)),
			 (".", (self.width // 2 + 3, self.height // 2)),
			 (".", (self.width // 2 + 4, self.height // 2))]
		 ]

	def draw(self):
		for i in self.animStates[self.animIndex]:
			self.pixels[int(i[1][1])][int(i[1][0])] = i[0]
		return self.pixels

	def update(self, timestep, keypresses):
		self.animTimer += timestep
		if self.animTimer >= self.animReset:
			self.animTimer = 0.0
			self.animIndex = (self.animIndex + 1) % len(self.animStates)

if __name__ == '__main__':
	from time import sleep
	l = LoadingWindow(20, 10, True)
	for x in range(10):
		sleep(0.1)
		l.update(0.1, [])
		l.debugDraw()
