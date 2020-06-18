import tcod

# ######################################################################
# Global Game Settings
# ######################################################################
# Size of window
FULLSCREEN = False
SCREEN_WIDTH = 80  # characters wide
SCREEN_HEIGHT = 50  # characters tall
LIMIT_FPS = 20 # FPS limit
# Game Controls
TURN_BASED = True  # turn-based game


# ######################################################################
# Classes
# ######################################################################
class Object:
#this is a generic object: the player, monster or an item
#it's always represented by a charakter on screen
 def __init__(self, x, y, char, color):
    self.x = x
    self.y = y
    self.char = char        
    self.color = color

 def move(self, dx, dy):
    #move by the given amount
    self.x += dx
    self.y += dy

 def draw(self):
    #set the color and then draw the character that represents this object at its position
    tcod.console_set_default_foreground(cuck, self.color)
    tcod.console_put_char(cuck, self.x, self.y, self.char, tcod.BKGND_NONE)

 def clear(self):
    #erase the character taht represents this object
    tcod.console_put_char(cuck, self.x, self.y, ' ', tcod.BKGND_NONE)
  
# ######################################################################
# User Input
# ######################################################################
def get_key_event(turn_based=None):
    if turn_based:
        #Turn-based game play; wait for a key stroke
        key = tcod.console_wait_for_keypress(True)
    else:
        #Real-time game play; don't wait for a player's key stroke
        key = tcod.console_check_for_keypress()
    return key
 
 
def handle_keys():
 
    key = get_key_event(TURN_BASED)
 
    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
 
    elif key.vk == tcod.KEY_ESCAPE:
        return True  # exit game
 
    # movement keys
    if tcod.console_is_key_pressed(tcod.KEY_UP):
        player.move(0,-1)
 
    elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
        player.move(0,1)
 
    elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
        player.move(-1,0)
 
    elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
        player.move(1,0)
 

#############################################
# Initialization & Main Game Loop
#############################################
 # Setup Font
font_filename = 'd:/Python/RougeLike/project/arial10x10.png'
tcod.console_set_custom_font(font_filename, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
# Initialize screen
title = 'Python 3 + Libtcod tutorial'
tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, title, FULLSCREEN)
cuck = tcod.console_new(SCREEN_WIDTH,SCREEN_HEIGHT) #temporary work screen
# Set FPS
tcod.sys_set_fps(LIMIT_FPS)

#Create player
player = Object(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@', tcod.lighter_azure)
#Create npc
npc = Object(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT // 2, '#', tcod.yellow)
#Create list of objects
objects = [npc, player]
 
 
exit_game = False
while not tcod.console_is_window_closed() and not exit_game:

    #draw all objects in the list
    for object in objects:
        object.draw()

    #blit the contents of "cuck" to the root console and present it
    tcod.console_blit(cuck, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    tcod.console_flush()

    #erase all objects at thier old locations, before they move
    for object in objects:
        object.clear()
        
    exit_game = handle_keys()
 

main()