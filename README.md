# Pipes
 That one screensaver that had pipes. Only on the terminal

![Video of pipes](/img/pipes.gif)

### Requirements
This script uses [blessed](https://github.com/jquast/blessed) to output into the terminal.

### Configuration

These variables can be found at the top of `pipe.py`.

```python
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
```
