import blessed
import random

# Minimal ticks until it can do a turn. Small number is smaller lines, larger is bigger lines.
MIN_TICKS_UNTIL_TURN = 5
# When the line turns and there is already a pipe there. This replaces it with a "+" symbol
REPLACE_TURNS_WITH_PLUS = False
# Tick rate is in seconds
TICK_RATE = 0.01
# If the screen is over a percentage filled, it will clear the screen. Set to 0 to disable this.
MAX_PERCENTAGE_FILLED = 0.25
# When keeping track of pipes on the screen. This will add a pipe to a spot rather than set it to one.
# Mainly used to check how much of the screen is filled. Set this to True to count for pipes laying on top of each other
# Leave False to only set to one.
PIPE_ADD_ONE = False


class Line:
    horizontal = 9475
    vertical = 9473
    down_right = 9487
    down_left = 9491
    up_right = 9495
    up_left = 9499
    plus = 9547


LINE_TURN = {
    # (old_direction, new_direction): char
    (0, 1): Line.down_right,
    (0, 3): Line.down_left,
    (1, 0): Line.up_left,
    (1, 2): Line.down_left,
    (2, 1): Line.up_right,
    (2, 3): Line.up_left,
    (3, 0): Line.up_right,
    (3, 2): Line.down_right
}


class Pipes:
    def __init__(self):
        self.term = blessed.Terminal()
        self.size = (self.term.width, self.term.height)
        self.direction = 0
        self.pos = [0, 0]
        self.color = (255, 255, 255)
        self.last_turn = 0  # Ticks since last turn
        self.clearing = False  # Flag to clear the screen. Main difference is to wait a few seconds before clearing
        self.screen = None
        self.generate_screen()
        self.random_color_pos()

    def percentage_of_screen_filled(self) -> bool:
        """
        Checks how much the screen is filled.
        If it's over a certain percentage, it returns True.

        :return: bool
        """
        if MAX_PERCENTAGE_FILLED == 0:
            return False

        total = 0
        for x in self.screen:
            total += sum(x)

        return total >= (self.size[0] * self.size[1]) * MAX_PERCENTAGE_FILLED

    def generate_screen(self) -> None:
        """
        Screen helps with keeping track where there are already pipes.
        This clears / generates self.screen with 0's
        """
        self.screen = []
        for _ in range(self.size[1]):
            line = []
            for _ in range(self.size[0]):
                line.append(0)
            self.screen.append(line)

    def random_color_pos(self) -> None:
        """
        Randomly generates a color and position.

        The position will aim for the edge of the screen rather than the middle
        """
        # Grabbing random color
        while True:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            # Making sure the color isn't too dark
            if sum(color) > 255:
                break

        # Grabbing random position at the edge of the screen
        pos = [0, 0]
        i = random.randint(0, 1)
        pos[i] = random.choice((-1, self.size[i]))
        pos[i-1] = random.randint(0, self.size[i-1] - 1)

        # Determining the direction
        if i == 0:
            if pos[i] > 0:
                self.direction = 3
            else:
                self.direction = 1
        else:
            if pos[i] > 0:
                self.direction = 0
            else:
                self.direction = 2

        self.pos = pos
        self.color = color

    def draw(self, char: int, replace_plus=False) -> None:
        """
        Moves position forward depending on direction. Then print the character.

        Direction is almost like a compass -
            0 - N
            1 - E
            2 - S
            3 - W

        This can also replace the char with a "+" if there already is a pipe at the position.
        """
        # Adding self.pos depending on direction
        if self.direction == 2:
            self.pos[1] += 1

        elif self.direction == 1:
            self.pos[0] += 1

        elif self.direction == 0:
            self.pos[1] += -1

        elif self.direction == 3:
            self.pos[0] += -1

        # Checking if position is outside of the screen
        if 0 <= self.pos[0] < self.size[0] and 0 <= self.pos[1] < self.size[1]:
            if replace_plus and self.screen[self.pos[1]][self.pos[0]] != 0:
                char = Line.plus

            if PIPE_ADD_ONE:
                self.screen[self.pos[1]][self.pos[0]] += 1
            else:
                self.screen[self.pos[1]][self.pos[0]] = 1

            print(self.term.move_xy(*self.pos) + self.term.color_rgb(*self.color) + chr(char), end='', flush=True)

        else:
            if self.percentage_of_screen_filled():
                self.clearing = True
            else:
                self.random_color_pos()

    def resize(self) -> bool:
        """
        Detects if the screen size was changed.

        :return: bool
        """
        current_size = (self.term.width, self.term.height)
        if self.size != current_size:
            self.size = current_size
            self.clear()
            return True
        else:
            return False

    def turn(self, direction: int) -> None:
        """
        Changes the direction and draws a turn.
        """
        if direction == 0:
            return

        old = self.direction
        new = self.direction + direction

        if new < 0:
            new = 3

        elif new > 3:
            new = 0

        char = LINE_TURN[(old, new)]
        self.draw(char, REPLACE_TURNS_WITH_PLUS)
        self.direction = new

    def line(self) -> None:
        """
        Draws a line depending on the direction.
        """
        if self.direction == 0 or self.direction == 2:
            self.draw(Line.horizontal)
        else:
            self.draw(Line.vertical)

    def clear(self) -> None:
        """
        Clears the terminal and resets the position / color.
        """
        print(self.term.clear, end="", flush=True)
        self.generate_screen()
        self.random_color_pos()
        self.clearing = False

    def tick(self) -> None:
        """
        Process a tick. Basically, draws a line or turns the line.
        """
        if self.last_turn >= MIN_TICKS_UNTIL_TURN and random.randint(0, 100) > 85:
            self.turn(random.choice([-1, 1]))
            self.last_turn = 0
        else:
            self.line()
            self.last_turn += 1

    @classmethod
    def start(cls) -> None:
        """
        Starts the pipes
        """
        self = cls()

        val = ''
        while val != 'q':
            with self.term.cbreak(), self.term.fullscreen(), self.term.hidden_cursor():
                while True:
                    if self.clearing:
                        val = self.term.inkey(timeout=3)
                        self.clear()
                    else:
                        val = self.term.inkey(timeout=TICK_RATE)
                    val = val.lower()

                    if val == "r":
                        self.clear()
                    elif val == "q":
                        break

                    if self.resize():
                        break
                    else:
                        self.tick()


if __name__ == '__main__':
    Pipes.start()
