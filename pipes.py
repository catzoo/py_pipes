import blessed
import random
import time

# Minimal ticks until it can do a turn. Small number is smaller lines, larger is bigger lines.
MIN_TICKS_UNTIL_TURN = 5
# When there is already a pipe. This will replace it with a "+" if it's going across or is a turn.
REPLACE_WITH_PLUS = False
# This will add "+" with other pipes. Set to False to only add "+" with itself rather than other pipes.
# Only works if REPLACE_WITH_PLUS is True
# Warning. When this is set to True, it will clear the screen variable.
# Meaning, PIPE_ADD_ONE won't properly keep track if there is already a pipe there or not.
ADD_PLUS_WITH_OTHER_PIPES = True
# Changes the "+" color. Value will be a RGB tuple "(255, 255, 255)" Set to None to use the Pipe's color.
PLUS_COLOR = None  # (255, 255, 255)
# Tick rate is in seconds
TICK_RATE = 0.01
# Blessed input adds more delay to the tick rate. Disable it to remove the delay.
# But it will also disable the "r" and "q" keys
DISABLE_INPUT = False
# If the screen is over a percentage filled, it will clear the screen. Set to 0 to disable this.
MAX_PERCENTAGE_FILLED = 0.50
# When keeping track of how many characters are on the screen. This will change it to always add by one.
# Set False to not count the character if there is already a pipe.
# Set True to always count the character.
PIPE_ADD_ONE = True


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
        self.characters = 0  # Number of characters on the screen
        self.generate_screen()
        self.random_color_pos()

    def percentage_of_screen_filled(self) -> bool:
        """
        Checks how much the screen is filled.
        If it's over a certain percentage, it returns True.

        :return: bool
        """
        return self.characters >= (self.size[0] * self.size[1]) * MAX_PERCENTAGE_FILLED

    def generate_screen(self) -> None:
        """
        Screen helps with keeping track where there are already pipes.
        This clears / generates self.screen with 0's
        """
        self.screen = []
        for _ in range(self.size[1]):
            line = []
            for _ in range(self.size[0]):
                line.append(-1)
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

    def draw(self, char: int, turn=False) -> None:
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
            temp = self.screen[self.pos[1]][self.pos[0]]
            color = self.color

            if REPLACE_WITH_PLUS and temp != -1:
                # Making sure the line is not going the same direction
                difference = temp - self.direction
                if turn or temp == 4 or not (difference == -2 or difference == 2 or difference == 0):
                    char = Line.plus
                    turn = True
                    if PLUS_COLOR is not None:
                        color = PLUS_COLOR

            if PIPE_ADD_ONE:
                self.characters += 1
            elif temp == -1:
                self.characters += 1

            if turn:
                # Marking the position as a turn
                self.screen[self.pos[1]][self.pos[0]] = 4
            else:
                # Marking the position with the direction
                self.screen[self.pos[1]][self.pos[0]] = self.direction

            print(self.term.move_xy(*self.pos) + self.term.color_rgb(*color) + chr(char), end='', flush=True)

        else:
            if self.percentage_of_screen_filled():
                self.clearing = True
            else:
                self.random_color_pos()
                if PIPE_ADD_ONE and ADD_PLUS_WITH_OTHER_PIPES is False:
                    # Clear the screen to only keep track of one pipe.
                    self.generate_screen()

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
        self.draw(char, True)
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
        self.characters = 0

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

    def get_input(self, wait: float) -> str:
        if DISABLE_INPUT:
            time.sleep(wait)
            return ""
        else:
            return self.term.inkey(timeout=wait)

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
                        val = self.get_input(3)
                        self.clear()
                    else:
                        val = self.get_input(TICK_RATE)
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
