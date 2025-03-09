import time
import machine
import badger2040
POMODORO_PATCH="./pomodoro.txt"
DEF_SET="""00
25
00"""


try:
    badge = open(POMODORO_PATCH, "r")
except OSError:
    with open(POMODORO_PATCH, "w") as f:
        f.write(DEF_SET)
        f.flush()
    badge = open(POMODORO_PATCH, "r")

hour =int( badge.readline())
minute = int(badge.readline())
second=int(badge.readline())
setSeconds = hour*3600+minute*60+second

texts = [["reset","set","start"],["<","set",">"],["reset","set","stop"]]
textIndex =0
setIndex =0
set_clock=0
currentSec=0
start=0
ledSec=0
lastValue=-1

display = badger2040.Badger2040()
display.set_update_speed(2)
display.set_thickness(4)
display.set_font("bitmap14_outline")

WIDTH, HEIGHT = display.get_bounds()

button_a = badger2040.BUTTONS[badger2040.BUTTON_A]
button_b = badger2040.BUTTONS[badger2040.BUTTON_B]
button_c = badger2040.BUTTONS[badger2040.BUTTON_C]
button_up = badger2040.BUTTONS[badger2040.BUTTON_UP]
button_down = badger2040.BUTTONS[badger2040.BUTTON_DOWN]

try:
    badger2040.pcf_to_pico_rtc()
except RuntimeError:
    pass

rtc = machine.RTC()

def button(pin):
    global last, set_clock, toggle_set_clock,  hour, minute,second, textIndex, setIndex, cur_hour, cur_minute,cur_second, setSeconds, currentSec, start

    time.sleep(0.01)
    if not pin.value():
        return

    if button_a.value() and button_c.value():
        machine.reset()
        
    if button_b.value():
        print("b")
        set_clock=(set_clock+1)%2
        textIndex=(textIndex +1)%2
        draw_clock()
        if set_clock==0:
            with open(POMODORO_PATCH, "w") as f:
                f.write(str(hour))
                f.write("\n")
                f.write(str(minute))
                f.write("\n")
                f.write(str(second))
                f.flush()
            setSeconds = hour*3600+minute*60+second
            currentSec =0
        
    if set_clock==1:
        adjust=0
        if button_a.value():
            setIndex = (setIndex+2)%3
            draw_clock()
        if button_c.value():
            setIndex = (setIndex+1)%3
            draw_clock()
        if button_up.value():
            adjust=1
        if button_down.value():
            adjust=-1
            
        if setIndex==0:
            hour+=adjust
            if hour<0:
                hour=99
            if hour>99:
                hour=00
            draw_clock()
        if setIndex==1:
            minute+=adjust
            if minute<0:
                minute=59
            if minute>59:
                minute=00
            draw_clock()
        if setIndex==2:
            second+=adjust
            if second<0:
                second=59
            if second>59:
                second=00
            draw_clock() 
    else:
        if button_c.value():
            start = (start+1)%2
            if start==1:
                textIndex =2
                if currentSec==setSeconds:
                    currentSec=0
            else:
                textIndex =0
            draw_clock()
                
        if button_a.value():
            currentSec =0
            draw_progress_bar(currentSec,setSeconds,1)
                 
                   
        
def draw_progress_bar(current_value, set_value,force):
    global lastValue
    value = int(((WIDTH-18)/set_value) * current_value)
    if(lastValue != value or force==1):
        
        display.set_pen(0)
        display.rectangle( 5, 5, WIDTH-10, 40)
        
        display.set_pen(15)
        display.rectangle(7, 7, WIDTH-14, 36)
        display.set_pen(0)
        display.rectangle(9, 9, int(((WIDTH-18)/set_value) * current_value), 32)
        display.set_update_speed(3)
        display.partial_update(0,0,WIDTH,48)
        lastValue=value;
        if set_value==current_value:
            stopText ="STOP"
            stopWidth = display.measure_text(stopText, 1)
            display.set_pen(15)
            display.text(stopText, int((badger2040.WIDTH / 2) - (stopWidth / 2)), 20,0,1)
    
    

def draw_clock():
    global second_offset, second_unit_offset, cur_minute, cur_second,setSeconds

    hms = "{:02}h{:02}m{:02}s".format(hour, minute, second)
    a_text =texts[textIndex][0]
    b_text =texts[textIndex][1]
    c_text = texts[textIndex][2]

    hms_width = display.measure_text(hms, 3)
    hms_offset = int((badger2040.WIDTH / 2) - (hms_width / 2))
    
    h_width = display.measure_text(hms[0:2], 3)
    mi_width = display.measure_text(hms[3:5], 3)
    mi_offset = display.measure_text(hms[0:3], 3)
    sek_width = display.measure_text(hms[6:8], 3)
    sek_offset = display.measure_text(hms[3:6], 3)
    
    a_width = display.measure_text(a_text, 1.5)
    a_offset = int((badger2040.WIDTH / 6) - (a_width / 2))
    b_width = display.measure_text(b_text, 1.5)
    b_offset = int((badger2040.WIDTH / 2) - (b_width / 2))
    c_width = display.measure_text(c_text, 1.5)
    c_offset = int((badger2040.WIDTH/6)*5 - (c_width/2) )


    display.set_pen(15)
    display.clear()
    display.set_pen(0)

    display.text(hms, hms_offset, 50, 0, 3)
    display.text(a_text, a_offset, 100,0,1.5)
    display.text(b_text, b_offset, 100,0,1.5)
    display.text(c_text, c_offset, 100,0,1.5)
    draw_progress_bar(currentSec,setSeconds,1)

    hms = "{:02}:{:02}:".format(hour, minute)
    second_offset = hms_offset + display.measure_text(hms, 1.8)
    hms = "{:02}:{:02}:{}".format(hour, minute, second // 10)
    second_unit_offset = hms_offset + display.measure_text(hms, 1.8)
    
    if set_clock:
        display.set_pen(0)
        if setIndex == 0:
            display.line(hms_offset, 90,hms_offset+ h_width, 90, 4)
        if setIndex == 1:
            display.line(hms_offset+mi_offset, 90, hms_offset+mi_offset+mi_width, 90, 4)
        if setIndex == 2:
            display.line(hms_offset+mi_offset+sek_offset, 90, hms_offset+mi_offset+sek_offset+sek_width, 90, 4)      

    display.set_update_speed(2)
    display.update()
    display.set_update_speed(3)
    
last_second=-1
last_minute =-1

for b in badger2040.BUTTONS.values():
    b.irq(trigger=machine.Pin.IRQ_RISING, handler=button)

while True:   
    year, month, day, wd, cur_hour, cur_minute, cur_second, _ = rtc.datetime()
    if cur_second != last_second:
        if cur_minute != last_minute:
            if start==1:
                currentSec =currentSec+1
            draw_clock()
            last_minute = cur_minute
        else:
            if start==1:
                currentSec =currentSec+1
                ledSec=0
            draw_progress_bar(currentSec,setSeconds,0)
        last_second = cur_second
        
        if currentSec == setSeconds:
            ledSec=ledSec+1
            if start==1:
                start=0
                textIndex=0
                draw_clock()
                display.led(255)
            if ledSec>5:
                display.led(0)
                ledSec=10
    time.sleep(0.01)
