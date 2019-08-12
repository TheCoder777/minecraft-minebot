# Minecraft MineBot

This is a fully automatic minebot for minecraft version 1.14.x (not tested in other versions).
It works via screen capturing and some sort of color detection through opencv!


## Dependencies
What you need to have installed:

+ numpy
+ pyautogui
+ pyscreenshot
+ keyboard
+ opencv (cv2)
+ pynput

To install all of them:

```bash
pip instal numpy pyautogui pyscreenshot keyboard opencv-python pynput
```

## How to use

To use this, you first need to use the provided texturepack!

In game, you need to fill the first 5 slots, counted from the upper left, with stone pickaxes.
Fill the first 5 slots counted from the left of the second row of the inventory with iron pickaxes.
Last but not least, fill the first 5 slots from the left bottom of the inventory with stone shovels.

In your hotbar:
You need to have a stone pickaxe at 2nd slot,
a iron pickaxe at 3rd slot,
a stone shovel at 4th slot,
and some torches at your 9th slot (I recommend at least one stack, cause if the stack is empty, the minebot will stop!).

For purpose of lightning, you will need to have at least one torch in your off-hand,
and you need to hold your torches in the 9th slot of your inventory hotbar!
(if torches are empty, the minebot will stop!)

To start mining, start the programm from you terminal of choice
(you need to execute is with sudo on linux, because I'm using the keyboard module at some parts!).
First you'll be asked for some healt stats of your tools, then a countdown will appear!
As the countdown counts down, you have to switch you mouse focus to the mincraft window.
To make the minebot work properly,
you have to look at the top block in front of you in a 2 block high and 1 block wide mining tunnel!


## Settings

You can change pretty much every kind of value in the 'defaults' or the 'timings' classes!
There are also some settings like debugging and also some values you can touch on your own risk!
(really, dont touch them!)


## Status
Lava detection works excellent!
Ore detection is also pretty good!
Picaxe/shovel swapping works also pretty well!
There is some delay between detecting dirt and selecting the shovel!

If someone wants to help developing this minebot, please to that!
I'm not actively developing this anymore!
