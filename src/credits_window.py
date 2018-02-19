"""
Window displaying credits of people who worked on the game
"""
from window import Window
from game_state import GameState, GameMode

class CreditsWindow(Window):

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
        startRow = self.height // 6
        for i, (role, members) in enumerate(credits):
            startCol = (self.width // 5) * (i * 2 + 1)
            self.writeText(role, startRow, startCol, False, 'underline')
            self.writeTextLines(members, startRow+1, startCol)

        self.writeText(footer, self.height * 5 // 6, (self.width - len(footer)) // 2)
        self.writeText(exitfooter, self.height * 5 // 6 + 1, (self.width - len(exitfooter)) // 2)

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key in [' ', 'Return', 'BackSpace']:
                GameState().gameMode = GameMode.TitleScreen
