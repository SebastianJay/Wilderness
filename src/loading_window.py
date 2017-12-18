from window import Window

class LoadingWindow(Window):

	def reset(self):
		self.animIndex = 0
		self.animTimer = 0.0
		self.animReset = 0.25
		self.animStates = [
			'Loading.  ',
			'Loading.. ',
			'Loading...',
		]

	def update(self, timestep, keypresses):
		self.animTimer += timestep
		if self.animTimer >= self.animReset:
			self.animTimer = 0.0
			self.animIndex = (self.animIndex + 1) % len(self.animStates)

	def draw(self):
		self.writeText(self.animStates[self.animIndex], self.height // 2, self.width // 2 - 5)
