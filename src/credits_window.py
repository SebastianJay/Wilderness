from window import Window
from game_state import GameState, GameMode

class CreditsWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)

    def load(self):
        # team size is small enough that we can define team inline
        credits = (
            ('Programmers', [
                'Winston Liu',
                'Chris Arthur',
                'Daniel Choi',
                'Patrick Kwon',
                'Jack Prescott',
                'Laith Hasanian',
                'Sid Ghatti',
                'William Li',
            ]),
            ('Designers/Writers', [
                'Mark Villadelgado',
                'Rachael Perkins',
                'James Hu',
                'Wooju Lee',
                'Yincheng Ren',
                'Christine Cheng',
                'Jason Keller',
            ])
        )
        footer = 'Directed by Jay Sebastian'
        exitfooter = '[Return] to exit'

        # do drawing once
        rStart = self.height // 6
        for i, (role, members) in enumerate(credits):
            cStart = (self.width // 5) * (i * 2 + 1)
            for c, ch in enumerate(role):
                self.pixels[rStart][cStart + c] = ch
            self.formatting.append(('underline', (rStart*self.width + cStart, rStart*self.width + cStart + len(role)-1)))
            for r, name in enumerate(members):
                for c, ch in enumerate(name):
                    self.pixels[rStart + 2 + r][cStart + c] = ch

        rFooter = self.height * 5 // 6
        cFooter = (self.width - len(footer)) // 2
        for c, ch in enumerate(footer):
            self.pixels[rFooter][cFooter + c] = ch

        rFooter = self.height * 5 // 6 + 1
        cFooter = (self.width - len(exitfooter)) // 2
        for c, ch in enumerate(exitfooter):
            self.pixels[rFooter][cFooter + c] = ch

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key in [' ', 'Return', 'BackSpace']:
                GameState().gameMode = GameMode.TitleScreen
