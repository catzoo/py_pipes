# Pipes
 That one screensaver that had pipes. Only on the terminal

![Video of pipes](/img/pipes.gif)

### Requirements
This script uses [blessed](https://github.com/jquast/blessed) to output into the terminal.

### Keybinds
Here are the controls if input is enabled:

| Key | Action |
|:---:|:---:|
| `r` | Resets the screen |
| `q` | Quit |

### Configuration

These variables can be found at the top of `pipe.py`.

```python
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
```
