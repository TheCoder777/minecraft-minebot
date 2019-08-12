import os, sys, time, cv2, keyboard, multiprocessing, queue, readline
import pyscreenshot as ImageGrab # for linux
import pyautogui as pag
import numpy as np
from time import sleep


class Gametime():
    def __init__(self):
        self.set()

    def set(self):
        self.game_start_time = time.time()

    def getTime(self):
        return(float("{0:.4f}".format(time.time() - self.game_start_time)))
## Global instance
gametime = Gametime()


## coords of items
class Coords():
    def __init__(self):
        # first 5 of each row
        self.slot_hot = [[675, 830], [745, 830], [815, 830], [885, 830], [955, 830]]
        self.slot_1 = [[675, 600], [745, 600], [815, 600], [885, 600], [955, 600]]
        self.slot_2 = [[675, 675], [745, 675], [815, 675], [885, 675], [955, 675]]
        self.slot_3 = [[675, 745], [745, 745], [815, 745], [885, 745], [955, 745]]
# Global instance
coords = Coords()


## default values for ingame stuff
class Defaults():
    def __init__(self):
        ## Default vals
        # self.ores = {"emerald":0, "diamond":0, "gold":0, "iron":0, "coal":0, "lapis":0, "redstone":0}
        self.ores = {"reg":0, "diamond":0, "iron":0, "coal":0, "lapis":0, "gravel":0, "dirt":0, "sadg":0}
        self.default_pickaxe_health_game = 131
        self.iron_pickaxe_health_game = 250
        self.default_shovel_health_game = 131
        self.debug = True # debugging output on/off

        ## GAME ## DON'T TOUCH THESE VALUES ##
        self.default_default_pickaxe_health = 131
        self.default_iron_pickaxe_health = 250
        self.default_shovel_health = 131
        self.lowest_light_level = 30
        # self.Gamecoords=(560,600,1360,850) # for bbox in ImageGrab (pyscreenshot) (smaller)
        self.Gamecoords_lava = (560,300,1360,850) # for bbox in ImageGrab (pyscreenshot) (bigger)
        self.Gamecoords = (910,490, 1010,590) # only one block
        self.ores_need_default_pickaxe = ["iron", "coal", "lapis"]
        self.ores_need_iron_pickaxe = ["reg", "diamond"]
        self.ores_need_default_shovel = ["dirt", "gravel"]

        # numbers
        self.torch_interval = 6 # place torch every 6 blocks for example
        self.torches = 64 # how many torches in inventory
        self.default_pickaxe_num = 5 # how many 'default' pickaxes you have in your inventory (top left to top right)
        self.iron_pickaxe_num = 5
        self.default_shovel_num = 5

        # turning
        self.turn_right_range = 500
        self.turn_left_range = -500

        # moving
        self.turn_one_block_down_range = 300 # down increases
        self.turn_one_block_up_range = -300 # up decreases

        # keys ingame
        self.drop_key = "g"
        self.inventory_key = "q"
        self.move_back_key = "s"
        self.move_forward_key = "w"
        self.move_right_key = "d"
        self.move_left_key = "a"
        self.jump_key = "space"

        # slots
        self.default_pickaxe_slot = "2"
        self.iron_pickaxe_slot = "3"
        self.default_shovel_slot = "4"
        self.torch_slot = "9"

        # item coords
        self.default_pickaxe_slot_coords = coords.slot_hot[int(self.default_pickaxe_slot) - 1]
        self.iron_pickaxe_slot_coords = coords.slot_hot[int(self.iron_pickaxe_slot) - 1]
        self.default_shovel_slot_coords = coords.slot_hot[int(self.default_shovel_slot) - 1]

        # keys pause
        self.pause_key = "p"
        self.shutdown_key = "m"

# Global instance
defaults = Defaults()


## colors for output
class Colors:
    def __init__(self):
        self.RED = '\033[31m'
        self.GREEN = '\033[32m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.MAGENTA = '\033[35m'
        self.CYAN = '\033[36m'
        self.LIGHT_GRAY = '\033[37m'

        self.STATUS = self.CYAN
        self.WARNING = self.YELLOW
        self.CRITICAL = self.RED
        self.GOOD = self.GREEN
        self.ACTION = self.MAGENTA
        self.INPUT = self.LIGHT_GRAY
        if defaults.debug:
            self.DEBUG = self.RED

        self.BOLD = '\033[1m'
        self.DIM = '\033[2m'
        self.UNDERLINE = '\033[4m'
        self.END = '\033[0m'
# Global instance
colors = Colors()


class Status:
    def __init__(self):
        self.STATUS = colors.STATUS + "[ STATUS @{}s ] ".format(gametime.getTime()) + colors.END
        self.WARNING = colors.WARNING + colors.BOLD + "[ WARNING @{}s ] ".format(gametime.getTime()) + colors.END
        self.CRITICAL = colors.CRITICAL + colors.BOLD + "[ CRITICAL @{}s ] ".format(gametime.getTime()) + colors.END
        self.GOOD = colors.GOOD + "[ OK @{}s ] ".format(gametime.getTime()) + colors.END
        self.ACTION = colors.ACTION + "[ ACTION @{}s ] ".format(gametime.getTime()) + colors.END
        self.INPUT = colors.INPUT + colors.BOLD + "[ INPUT @{}s ] ".format(gametime.getTime()) + colors.END
        if defaults.debug:
            self.DEBUG = colors.DEBUG + colors.BOLD + "[ DEBUG @{}s ] ".format(gametime.getTime()) + colors.END
# Global instance
status = Status()

class Timings:
    def __init__(self):
        self.start_countdown = 5
        self.modifier = 0.2 # if the MineBot holds the mouse too short, this adds some time to make sure the block gets destroyed

        ## digging
        # default pickaxe (stone)
        self.default_pickaxe = 0.56  + self.modifier # for stoneblock
        self.default_pickaxe_ore = 1.13 + self.modifier
        # self.default_pickaxe_coal = 1.13
        # self.default_pickaxe_iron = 1.13
        # self.default_pickaxe_lapis = 1.13

        # iron pickaxe
        self.iron_pickaxe = 0.38 + self.modifier # for stoneblock
        self.iron_pickaxe_ore = 0.75 + self.modifier
        # self.iron_pickaxe_gold = 0.75
        # self.iron_pickaxe_diamond = 0.75
        # self.iron_pickaxe_emerald = 0.75

        # all shovels
        self.shovel_wait_gravel = 0.2 # wait till gravel falls down

        # default shovel (stone)
        self.default_shovel = 0.23 + self.modifier # longest dig time for shovel
        self.default_shovel_dirt = 0.19 + self.modifier
        self.default_shovel_gravel = 0.23 + self.modifier + self.shovel_wait_gravel

        # iron shovel
        self.iron_shovel_dirt = 0.13 + self.modifier
        self.iron_shovel_gravel = 0.15 + self.modifier

        # default time
        self.hold_mouse = self.default_pickaxe

        # moving
        self.sec_move_backward = 0.5
        self.sec_move_forward = 0.5
        self.sec_lava_rescue = 5
        self.hold_shutdown_key = 1

        # other
        # self.ore_scanner_wait = 1
        self.sleep_run = 0.5 # only lavaScanner
# Global instance
timings = Timings()

class ColorRange():
    def __init__(self):
        #                      darkest          lightest (RGB)
        self.lava_colors = [([213, 81, 0]), ([214, 81, 0])]
        self.lava_lower = np.array(self.lava_colors[0], dtype = "uint8")
        self.lava_upper = np.array(self.lava_colors[1], dtype = "uint8")

        self.reg_colors = [([55, 0, 0]), ([201, 0, 0])] # 'r'edstone, 'e'merald, 'g'old
        self.reg_lower = np.array(self.reg_colors[0], dtype = "uint8")
        self.reg_upper = np.array(self.reg_colors[1], dtype = "uint8")

        self.sadg_colors = [([13, 13, 11]), ([58, 58, 58])] # 's'tone, 'd'iorite, 'a'ndeside, 'g'ranite
        self.sadg_lower = np.array(self.sadg_colors[0], dtype = "uint8")
        self.sadg_upper = np.array(self.sadg_colors[1], dtype = "uint8")

        self.dirt_colors = [([2, 64, 0]), ([5, 200, 0])]
        self.dirt_lower = np.array(self.dirt_colors[0], dtype = "uint8")
        self.dirt_upper = np.array(self.dirt_colors[1], dtype = "uint8")

        self.gravel_colors = [([71, 0, 49]), ([201, 0, 154])]
        self.gravel_lower = np.array(self.gravel_colors[0], dtype = "uint8")
        self.gravel_upper = np.array(self.gravel_colors[1], dtype = "uint8")

        self.diamond_colors = [([16, 50, 39]), ([48, 176, 177])]
        self.diamond_lower = np.array(self.diamond_colors[0], dtype = "uint8")
        self.diamond_upper = np.array(self.diamond_colors[1], dtype = "uint8")

        self.iron_colors = [([64, 51, 0]), ([147, 137, 0])]
        self.iron_lower = np.array(self.iron_colors[0], dtype = "uint8")
        self.iron_upper = np.array(self.iron_colors[1], dtype = "uint8")

        self.coal_colors = [([0, 0, 0]), ([0, 0, 0])]
        self.coal_lower = np.array(self.coal_colors[0], dtype = "uint8")
        self.coal_upper = np.array(self.coal_colors[1], dtype = "uint8")

        self.lapis_colors = [([0, 5, 33]), ([0, 12, 110])]
        self.lapis_lower = np.array(self.lapis_colors[0], dtype = "uint8")
        self.lapis_upper = np.array(self.lapis_colors[1], dtype = "uint8")


class keyListener():
    def __init__(self):
        self.name = "keyListener"
        self.running = True
        global shutdown, pause
        shutdown.clear() # clear == running; set == shutdown
        pause.set() # clear == pause; set == running # cause we use pause.wait()

    def listen(self):
        while self.running:
            # check shutdown key
            if keyboard.is_pressed(defaults.shutdown_key):
                sleep(timings.hold_shutdown_key) # hold shutdown key, not only one press
                if keyboard.is_pressed(defaults.shutdown_key):
                    if defaults.debug:
                        print(status.DEBUG + "keyListener: Key {} detected!".format(defaults.shutdown_key))
                    shutdown.set()
                    if defaults.debug:
                        print(status.DEBUG + self.name + "@listen: exiting process")
                    break
            # check pause key
            if keyboard.is_pressed(defaults.pause_key):
                if defaults.debug:
                    print(status.DEBUG + "keyListener: Key {} detected!".format(defaults.pause_key))
                pause.clear()
                self.paused = True
                print(status.WARNING + "PAUSING! YOU CAN DO OTHER STUFF WHILE I'LL WAIT!\n")
                while self.paused:
                    if defaults.debug:
                        print(status.DEBUG + "WAITING FOR PAUSE KEY TO RESUME!")
                    sleep(1)
                    if keyboard.is_pressed(defaults.pause_key):
                        if defaults.debug:
                            print(status.DEBUG + "PAUSE KEY PRESSED, RESUME!")
                        print(status.WARNING + "RESUME!")
                        pause.set()
                        sleep(1)
                        break
                    # check shutdown key in pause screen
                    if keyboard.is_pressed(defaults.shutdown_key):
                        pause.set() # resume
                        sleep(timings.hold_shutdown_key) # hold shutdown key, not only one press
                        if keyboard.is_pressed(defaults.shutdown_key):
                            if defaults.debug:
                                print(status.DEBUG + "keyListener: Key {} detected!".format(defaults.shutdown_key))
                            pause.set() # going out of pause into shutdown
                            shutdown.set()
                            if defaults.debug:
                                print(status.DEBUG + self.name + "@listen: exiting process")
                            break
                        else:
                            pause.clear() # pause if no shutdown key!
                    # os.system("clear")
            if shutdown.is_set():
                self.running = False
                if defaults.debug:
                    print(status.DEBUG + self.name + "@listen: shutdown process")
        return True

    def resetKeys(self):
        pag.press(defaults.jump_key)
        pag.press(defaults.move_back_key)
        pag.press(defaults.move_forward_key)
        # pag.press("space")
        # pag.press("s")
        # pag.press("w")

        # defaults.drop_key         = "g"
        # defaults.inventory_key    = "q"
        # defaults.move_forward_key = "w"
        # defaults.move_left_key    = "a"
        # defaults.move_back_key    = "s"
        # defaults.move_right_key   = "d"
        # defaults.jump_key         = "space"

class lavaScanner(multiprocessing.Process):
    def __init__(self, Gamecoords=defaults.Gamecoords_lava):
        multiprocessing.Process.__init__(self)
        self.name = "lavaScanner"
        self.running = True
        self.color_range = ColorRange()
        self.Gamecoords = Gamecoords
        global lava, shutdown, pause, running
        running = True

    def run(self):
        global running
        while running:
            if defaults.debug:
                self.start_lava_time = time.time()

            self.getScreen()
            self.checkLava()
            pause.wait() # if set, pause scanner
            if defaults.debug:
                print(status.DEBUG + "Lava scan took {0:.4f}s".format(time.time() - self.start_lava_time))
            self.checkShutdown()
            sleep(timings.sleep_run)
            # if shutdown.is_set():
            #     self.running = False
            #     if defaults.debug:
            #         print(status.DEBUG + self.name + "@run: shutdown process")

    def shutdown(self):
        global running
        if defaults.debug:
            print(status.DEBUG + self.name + "@shutdown: shutdown process")
        running = False

    def checkShutdown(self):
        if shutdown.is_set():
            self.shutdown()

    def getScreen(self):
        self.screen = np.array(ImageGrab.grab(bbox=self.Gamecoords))

    def checkLava(self):
        self.lava_mask = cv2.inRange(self.screen, self.color_range.lava_lower, self.color_range.lava_upper)
        if (self.lava_mask > defaults.lowest_light_level).any():
            print(status.CRITICAL + "==> LAVA FOUND!")
            print(status.CRITICAL + "==> Sending notification to MineBot!")
            lava.set()
            sleep(timings.sec_lava_rescue)
            print(status.WARNING + "Trying to shutdown all processes!")
            shutdown.set()
            self.shutdown()

        else:
            print(status.GOOD + "==> No lava found!")
            lava.clear()


class oreScanner(multiprocessing.Process):
    def __init__(self, ores_dict, ore_pipe, Gamecoords=defaults.Gamecoords):
        multiprocessing.Process.__init__(self)
        self.name = "oreScanner"
        self.color_range = ColorRange()
        self.Gamecoords = Gamecoords
        self.ores = ores_dict
        self.ore_pipe = ore_pipe
        global shutdown, pause, running, ore_time, dig_time
        # new_ores = []
        running = True

    def run(self):
        global running
        while running:
            if defaults.debug: # debugging
                self.start_ore_time = time.time()
            # not for debugging
            self.ore_time_start = time.time()

            self.getScreen()
            self.checkOres() # check for ores on screen

            self.ore_pipe.send(self.new_ores)

            pause.wait() # if set, pause scanner
            # sleep(timings.ore_scanner_wait)

            if defaults.debug:
                print(status.DEBUG + "Ore scan took {0:.4f}s".format(time.time() - self.start_ore_time))

            if not self.new_ores: # if no new ores detected
                print(status.STATUS + "==> No new ores!")
            self.displayOres() # always print status list about all ores
            self.checkShutdown()
            with ore_time.get_lock():
                ore_time.value = time.time() - self.ore_time_start
            if defaults.debug:
                print(status.WARNING + "dig_time.value:", dig_time.value)
                print(status.WARNING + "ore_time.value:", ore_time.value)
            sleep(dig_time.value)

            # sleep(timings.sleep_run)

    def shutdown(self):
        global running
        if defaults.debug:
            print(status.DEBUG + self.name + "@shutdown: shutdown process")
        running = False

    def checkShutdown(self):
        if shutdown.is_set():
            self.shutdown()


    def displayOres(self):
        print(status.STATUS + "Ores found:")
        for ore, num in self.ores.items():
            if len(ore) >= 7:
                print("\t\t\t{}:\t{}".format(ore, num))
            else:
                print("\t\t\t{}:\t\t{}".format(ore, num))

    def getScreen(self):
        self.screen = np.array(ImageGrab.grab(bbox=self.Gamecoords))

    def checkOres(self):
        # new empty list for new oreprocesss
        self.new_ores = []

        ## redstone/emeralds/gold:
        self.reg_mask = cv2.inRange(self.screen, self.color_range.reg_lower, self.color_range.reg_upper)
        if (self.reg_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Redstone/Emeralds/Gold found!")
            self.ores["reg"] += 1
            self.new_ores.append("reg")

        ## stone/andeside/diorite/granite:
        self.sadg_mask = cv2.inRange(self.screen, self.color_range.sadg_lower, self.color_range.sadg_upper)
        if (self.sadg_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Stone/Andeside/Diorite/Granite found!")
            self.ores["sadg"] += 1
            self.new_ores.append("sadg")

        ## dirt:
        self.dirt_mask = cv2.inRange(self.screen, self.color_range.dirt_lower, self.color_range.dirt_upper)
        if (self.dirt_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Dirt found!")
            self.ores["dirt"] += 1
            self.new_ores.append("dirt")

        ## gravel:
        self.gravel_mask = cv2.inRange(self.screen, self.color_range.gravel_lower, self.color_range.gravel_upper)
        if (self.gravel_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Gravel found!")
            self.ores["gravel"] += 1
            self.new_ores.append("gravel")

        ## diamonds
        self.diamond_mask = cv2.inRange(self.screen, self.color_range.diamond_lower, self.color_range.diamond_upper)
        if (self.diamond_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Diamonds found!")
            self.ores["diamond"] += 1
            self.new_ores.append("diamond")

        ## iron
        self.iron_mask = cv2.inRange(self.screen, self.color_range.iron_lower, self.color_range.iron_upper)
        if (self.iron_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Iron found!")
            self.ores["iron"] += 1
            self.new_ores.append("iron")

        ## coal
        self.coal_mask = cv2.inRange(self.screen, self.color_range.coal_lower, self.color_range.coal_upper)
        if (self.coal_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Coal found!")
            self.ores["coal"] += 1
            self.new_ores.append("coal")

        ## lapis
        self.lapis_mask = cv2.inRange(self.screen, self.color_range.lapis_lower, self.color_range.lapis_upper)
        if (self.lapis_mask > defaults.lowest_light_level).any():
            print(status.GOOD + "==> Lapis found!")
            self.ores["lapis"] += 1
            self.new_ores.append("lapis")


class MineBot(multiprocessing.Process):
    def __init__(self, ore_pipe):
        multiprocessing.Process.__init__(self)
        self.name = "MineBot"
        self.ore_pipe = ore_pipe
        self.total_way = 0
        self.torch_way = 0
        self.torches = defaults.torches
        self.torch_interval = defaults.torches
        self.default_pickaxe_health = defaults.default_pickaxe_health_game
        self.iron_pickaxe_health = defaults.iron_pickaxe_health_game
        self.default_shovel_health = defaults.default_shovel_health_game
        self.default_pickaxe_num = defaults.default_pickaxe_num
        self.iron_pickaxe_num = defaults.iron_pickaxe_num
        self.default_shovel_num = defaults.default_shovel_num
        self.default_pickaxe_used = 1 # how many pickaxes/shovels are already swapped/used
        self.iron_pickaxe_used = 1    # '1' cause one is already in use
        self.default_shovel_used = 1
        global lava, shutdown, pause, running
        running = True

    def shutdown(self):
        global running
        if defaults.debug:
            print(status.DEBUG + self.name + "@shutdown: shutdown process")
        running = False

    def checkShutdown(self):
        if shutdown.is_set():
            self.shutdown()

    def displayStatus(self):
        print(status.STATUS + "Total way:",self.total_way)
        print(status.STATUS + "Blocks to next torch:",self.torch_interval - self.torch_way)
        print(status.STATUS + "Torches left:",self.torches)
        print(status.STATUS + "Default pickaxe health left:",self.default_pickaxe_health)
        print(status.STATUS + "Iron pickaxe health left:",self.iron_pickaxe_health)
        print() # newline

    def lavaRescue(self, sec=timings.sec_lava_rescue):
        pag.keyDown(defaults.move_back_key)
        pag.keyDown(defaults.jump_key)
        print(status.CRITICAL + "RUNNING AWAY FROM LAVA!")
        sleep(sec)
        pag.keyUp(defaults.move_back_key)
        pag.keyUp(defaults.jump_key)
        self.shutdown()

    def checkLava(self):
        if defaults.debug:
            print(status.DEBUG + "Minebot is checking for lava!")
        if lava.is_set():
            self.lavaRescue()

    def checkOres(self):
        self.new_ores = self.ore_pipe.recv()
        if defaults.debug:
            print(status.DEBUG + "reciving new ores:\n\n\n\t\t" + colors.BOLD, self.new_ores, "\n\n\n" + colors.END)
        if self.new_ores:
            return True

    def checkOresNeedIron(self):
        if set(self.new_ores) & set(defaults.ores_need_iron_pickaxe):
            return True
        else:
            return False

    def moveItem(self, from_slot, to_slot):
        pag.moveTo(from_slot)
        pag.click()
        pag.moveTo(to_slot)
        pag.click()

    def swapTool(self, tool="default"): # n is which pickaxe
        if tool == "default pickaxe":
            num = self.default_pickaxe_num - self.default_pickaxe_used
            self.selectDefaultPickaxe()
            self.dropSelectedItem()
            self.switchInventory()
            self.moveItem(coords.slot_1[num], defaults.default_pickaxe_slot_coords)
            print(status.ACTION + "Swapped default pickaxe")
            self.default_pickaxe_health = defaults.default_default_pickaxe_health # reset, cause new pickaxe
            self.default_pickaxe_used += 1 # add one used pickaxe
            self.switchInventory()
            self.selectDefaultPickaxe()
        elif tool == "iron pickaxe":
            num = self.iron_pickaxe_num - self.iron_pickaxe_used
            self.selectIronPickaxe()
            self.dropSelectedItem()
            self.switchInventory()
            self.moveItem(coords.slot_2[num], defaults.iron_pickaxe_slot_coords)
            print(status.ACTION + "Swapped iron pickaxe")
            self.iron_pickaxe_health = defaults.default_iron_pickaxe_health # reset, cause new pickaxe
            self.iron_pickaxe_used += 1
            self.switchInventory()
            self.selectIronPickaxe()
        elif tool == "default shovel":
            num = self.default_shovel_num - self.default_shovel_used
            self.selectDefaultShovel()
            self.dropSelectedItem()
            self.switchInventory()
            self.moveItem(coords.slot_3[num], defaults.default_shovel_slot_coords)
        else:
            print(status.WARNING + "Couldn't find {} tool!".format(pickaxe))

    def checkDefautlShovelHealth(self):
        if self.default_pickaxe_health < 2:
            self.swapTool("default shovel")

    def checkDefaultPickaxeHealth(self):
        if self.default_pickaxe_health < 2:
            self.swapTool("default pickaxe")

    def checkIronPickaxeHealth(self):
        if self.iron_pickaxe_health < 2:
            self.swapTool("iron pickaxe")

    def selectDefaultShovel(self):
        if defaults.debug:
            print(status.DEBUG + "Selecting default shovel!")
        pag.press(defaults.default_shovel_slot)

    def selectDefaultPickaxe(self):
        if defaults.debug:
            print(status.DEBUG + "Selecting default pickaxe!")
        pag.press(defaults.default_pickaxe_slot)

    def selectIronPickaxe(self):
        if defaults.debug:
            print(status.DEBUG + "Selecting iron pickaxe!")
        pag.press(defaults.iron_pickaxe_slot)

    def selectTorch(self):
        pag.press(defaults.torch_slot)

    def digBlock(self):
        if set(defaults.ores_need_default_pickaxe) & set(self.new_ores):
            self.selectDefaultPickaxe()
            self.holdMouse(sec=timings.default_pickaxe_ore)
            self.default_pickaxe_health -= 1
        elif set(defaults.ores_need_default_shovel) & set(self.new_ores):
            self.selectDefaultShovel()
            if "dirt" in self.new_ores:
                self.holdMouse(sec=timings.default_shovel_dirt)
                self.default_shovel_health -= 1
            elif "gravel" in self.new_ores:
                self.holdMouse(sec=timings.default_shovel_gravel)
            else:
                self.default_shovel_health -= 1
                self.holdMouse(sec=timings.default_shovel)
        else:
            self.selectDefaultPickaxe()
            self.holdMouse(sec=timings.default_pickaxe)
            self.default_pickaxe_health -= 1
            self.checkDefaultPickaxeHealth()

    def digOreNeedIron(self):
        self.selectIronPickaxe()
        if set(defaults.ores_need_iron_pickaxe) & set(self.new_ores):
            self.holdMouse(sec=timings.iron_pickaxe_ore)
        else:
            self.holdMouse(sec=timings.iron_pickaxe)
        self.iron_pickaxe_health -= 1
        self.checkIronPickaxeHealth()

    def switchInventory(self): # open/close
        pag.press(defaults.inventory_key)

    def dropSelectedItem(self):
        pag.press(defaults.drop_key)

    def turnRight(self, range=defaults.turn_right_range):
        pag.move(range, None)

    def turnLeft(self, range=defaults.turn_left_range):
        pag.move(range, None)

    def moveBack(self, sec=timings.sec_move_backward, jump=defaults.jump_key):
        pag.keyDown(defaults.move_back_key)
        sleep(sec)
        pag.keyUp(defaults.move_back_key)

    def moveForward(self, sec=timings.sec_move_forward):
        pag.keyDown(defaults.move_forward_key)
        sleep(sec)
        pag.keyUp(defaults.move_forward_key)

    def moveFaceOneBlockDown(self, range=defaults.turn_one_block_down_range):
        pag.move(None, range) # move mouse down

    def moveFaceOneBlockUp(self, range=defaults.turn_one_block_up_range):
        pag.move(None, range) # move mouse up

    def holdMouse(self, sec=timings.hold_mouse):
        pag.mouseDown()
        sleep(sec)
        pag.mouseUp()

    def placeSelectedItem(self):
        pag.click(button="right")

    def placeTorch(self):
        self.turnRight()
        sleep(0.1)
        self.selectTorch()
        self.placeSelectedItem()
        self.torch_way = 0
        self.torches -= 1
        sleep(0.1)
        self.turnLeft()
        self.selectDefaultPickaxe()
        print(status.ACTION + "Placed torch")

    def checkTorch(self):
        if self.torch_way == defaults.torch_interval:
            self.placeTorch()

    def run(self): # mine
        global running
        while running:
            self.dig_time_start = time.time()
            # top block
            self.displayStatus()
            self.checkLava()
            if self.checkOres():
                if defaults.debug:
                    print(status.DEBUG + colors.BOLD + "new ores!" + colors.END)
                if self.checkOresNeedIron():
                    if defaults.debug:
                        print(status.DEBUG + colors.BOLD + "ores need iron!" + colors.END)
                    self.digOreNeedIron()
                else:
                    self.digBlock()
            else: # no ores, just stone
                self.digBlock()
            self.checkLava()
            # pause
            pause.wait()
            self.checkLava()
            self.checkTorch()
            self.checkLava()
            self.checkShutdown()
            pause.wait()
            self.checkLava()
            with dig_time.get_lock(): # only time from first block
                dig_time.value = time.time() - self.dig_time_start
            # bottom block
            self.moveFaceOneBlockDown() # set focus to bottom block
            self.displayStatus()
            self.checkLava()
            if self.checkOres():
                if self.checkOresNeedIron():
                    self.digOreNeedIron()
                else:
                    self.digBlock()
            else: # no ores, just stone
                self.digBlock()
            self.checkLava()
            self.moveForward()
            self.torch_way += 1
            self.total_way += 1
            # pause
            self.checkShutdown()
            pause.wait()
            self.checkLava()
            with dig_time.get_lock(): # only time from first block
                dig_time.value = time.time() - self.dig_time_start
            sleep(ore_time.value)
            self.moveFaceOneBlockUp() # set focus to top block
            # sleep(timings.sleep_run)

def getInfo():
    # global defaults

    ## getting info about ingame stuff
    pickaxe_health_new = str(input(status.INPUT + "How much health has the default pickaxe left: "))
    if pickaxe_health_new:
        defaults.default_pickaxe_health_game = int(pickaxe_health_new)

    iron_pickaxe_health_new = str(input(status.INPUT + "How much health has the iron pickaxe left: "))
    if iron_pickaxe_health_new:
        defaults.iron_pickaxe_health_game = int(iron_pickaxe_health_new)

    torches_new = str(input(status.INPUT + "How much torches left: "))
    if torches_new:
        if torches_new in ["full", "f", "F"]:
            defaults.torches = 64
        else:
            defaults.torches = int(torches_new)
    else:
        defaults.torches = 64

def countdown(sec=timings.start_countdown):
    for i in reversed(range(sec)):
        print(colors.BOLD + "Starting in " + colors.END + colors.YELLOW + colors.BOLD + "{}".format(i) + colors.END + colors.BOLD + " seconds!" + colors.END)
        sleep(1)

def main():
    print(colors.GREEN + colors.BOLD + colors.UNDERLINE + "Starting MineBot!\n\n" + colors.END)
    getInfo()
    ## globals
    global shutdown, pause, lava, dig_time, ore_time
    ## set globals
    pause = multiprocessing.Event()
    pause.set()
    shutdown = multiprocessing.Event()
    shutdown.clear()
    ore_recver, ore_sender = multiprocessing.Pipe()
    dig_time = multiprocessing.Value('d', 0.1) # just to set a value (random)
    ore_time = multiprocessing.Value('d', 0.1) # just to set a value (random)
    lava = multiprocessing.Event()
    lava.clear()
    lavascanner = lavaScanner() # initialize lava scanner process
    orescanner = oreScanner(ores_dict=defaults.ores.copy(), ore_pipe=ore_sender) # initialize ore scanner process
    keylistener = keyListener()
    minebot = MineBot(ore_pipe=ore_recver) # initialize minebot class

    countdown() # starting countdown

    lavascanner.start() # starting lava scanner
    orescanner.start() # starting ore scanner
    minebot.start() # starting minebot
    val = keylistener.listen()

    if val == True:
        print(status.WARNING + "Shutting down Minebot!\n")
        if defaults.debug:
            print(status.DEBUG + "Waiting for lavaScanner to exit...\n")
        lavascanner.join()
        if defaults.debug:
            print(status.DEBUG + "lavaScanner joined successfully!\n")
            print(status.DEBUG + "Waiting for oreScanner to exit...\n")
        orescanner.join()
        if defaults.debug:
            print(status.DEBUG + "oreScanner joined successfully!\n")
            print(status.DEBUG + "Waiting for MineBot to exit...\n")
        minebot.join()
        if defaults.debug:
            print(status.DEBUG + "MineBot joined successfully!\n")
        # lavascanner.kill()
        # orescanner.kill()
        # minebot.kill()

        # lavascanner.terminate()
        # orescanner.terminate()
        # minebot.terminate()

        # keyListener().resetKeys()
        if defaults.debug:
            print(status.DEBUG + "Shutdown successfull!")

    else: # something went terrible wrong
        if defaults.debug:
            print(status.DEBUG + "Problems in main thread! Terminating processes!")
        lavascanner.termintate()
        orescanner.termintate()
        minebot.termintate()

if __name__ == "__main__":
    main()
    if defaults.debug:
        print(status.DEBUG + "Exiting main process!")
    sys.exit()
