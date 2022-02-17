import time
import sys

toolbar_width = 30

# setup toolbar
x = f"[{(' ' * toolbar_width)}]"
# x = '-----------------------------------'

toolbar_width = len(x)
# sys.stdout.write(f"[{(' ' * toolbar_width)}]")
sys.stdout.write(x)
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width + 1))  # return to start of line, after '['

for i in range(toolbar_width):
    time.sleep(0.1)  # do real work here
    # update the bar
    sys.stdout.write("|")
    sys.stdout.flush()

sys.stdout.write("]\n")  # this ends the progress bar
