import array, time
from machine import Pin
import rp2
 
# Configure the number of WS2812 LEDs, pins and brightness.
NUM_LEDS = 24
PIN_NUM = 16
brightness = 0.1
 
 
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
 
 
# Create the StateMachine with the ws2812 program, outputting on Pin(16).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
 
# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)
 
# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])
 
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)
 
def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]
 
def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)
 
 
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE,BLACK)

def turn_off_all():
    for cntr in range(NUM_LEDS):
        pixels_set(cntr,BLACK)
    pixels_show()
    
markers=[0,6,12,18]

def set_markers():
    for m in markers:
        if m == 0:
            pixels_set(0,RED)
        else:
            pixels_set(m,BLUE)
    pixels_show()
    
def set_heading(heading):
    global last_led,last_marker
    if heading >= 360:
        heading = 0
    if heading % 15 == 0:
        which = int(heading/15)        
        if last_marker != which:
            set_markers()
        pixels_set(which,GREEN)
        pixels_set(last_led,BLACK)
        last_led=which
        if which in markers:
            last_marker = which
            
    pixels_show()
    
turn_off_all()
set_markers()
time.sleep(1)
global last_led,last_marker
last_led=0
last_marker=0
for cntr in range(0,361):
    set_heading(cntr)
time.sleep(1)
turn_off_all()
set_markers()
for cntr in range(361,0,-1):
    set_heading(cntr)
    
print('Finished!')
time.sleep(2)
turn_off_all()
