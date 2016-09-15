class CoolClass:
    def __init__(self):
        self.coolness = 10

    def increaseCoolness(self, delta):
        self.coolness += delta

    def __str__(self):
        return "I am " + str(self.coolness) + " cool!"

    def fun():
        if 1:
            if [1]:
                if True:
                    if "some_string":
                        print("all true")

        first_squares = [x**2 for x in range(10)]
        print(first_squares)

        dct = {
            'apple': 'red',
            'banana': 'yellow',
            'plum': 'purple'
        }
        print(dct['apple'])

c = CoolClass()
c.increaseCoolness(7)
print(c)

CoolClass.fun()
