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
# Map dimension
MAP_WIDTH = 80
MAP_HEIGHT = 45
# Generator constants
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
#FOV
FOV_ALGO = 0 #deflault FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10


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
    #move by the given amount if the destination is not blocked
    if not map[self.x + dx][self.y + dy].blocked:
        self.x += dx
        self.y += dy

 def draw(self):
    #set the color and then draw the character that represents this object at its position
    tcod.console_set_default_foreground(cuck, self.color)
    tcod.console_put_char(cuck, self.x, self.y, self.char, tcod.BKGND_NONE)

 def clear(self):
    #erase the character taht represents this object
    tcod.console_put_char(cuck, self.x, self.y, ' ', tcod.BKGND_NONE)

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        #all tiles starts unexplored
        self.explored = False

        #by default, if a tile is blocked it blocks the sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    #a rectangle on the map, used to characterize a room
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
    
    def center(self):
        #find center cordinates (all tunnels will be connected there)
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersecs with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and 
        self.y1 <= other.y2 and self.y2 >= other.y1)

# ######################################################################
# Map
# ######################################################################
def make_map():
    global map

    #fill map with "blocked" tiles
    #Using list comprehension
    map = [
        [Tile(True) for y in range (MAP_HEIGHT)]
        for x in range (MAP_WIDTH)
    ]

    #ROOM GENERATOR
    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random width and height
        w = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going of the boundaries of the map
        x = tcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = tcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
        
        #makes rooms
        new_room = Rect(x, y, w, h)

        #check if the other rooms intersect with the new one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
        if not failed:
            #the room is valid, so it can be created
            create_room(new_room)

            #save the new room's center cordinates
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                #all rooms afther the first one
                #connect it to the previous room with a tunnel

                #center coords of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                #draw a coin (random number that is either 0 or 1)
                if tcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, new_x)
                    create_h_tunnel(prev_x, new_x, prev_y)

            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1



def create_room(room):
    global map

    #go through the tiles in the rectangle and make them passable
    for x in range (room.x1 + 1, room.x2): #+1 to make walls and separete rooms
        for y in range (room.y1 +1 , room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map

    #create horizontal tunnel
    for x in range(min(x1, x2), max(x1, x2) + 1): #min/max used to determine smaller x cord, +1 to prevent exclusion of the last loop element
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map

    #create horizontal tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1): #min/max used to determine smaller x cord, +1 to prevent exclusion of the last loop element
        map[x][y].blocked = False
        map[x][y].block_sight = False

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
    global fov_recompute

    key = get_key_event(TURN_BASED)
 
    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
 
    elif key.vk == tcod.KEY_ESCAPE:
        return True  # exit game
 
    # movement keys
    if tcod.console_is_key_pressed(tcod.KEY_UP):
        player.move(0,-1)
        fov_recompute = True
 
    elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
        player.move(0,1)
        fov_recompute = True
 
    elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
        player.move(-1,0)
        fov_recompute = True
 
    elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
        player.move(1,0)
        fov_recompute = True

# ######################################################################
# Logic
# ######################################################################
def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    if fov_recompute:
        #recompute FOV if needed (Pleyer moves etc.)   
        fov_recompute = False
        tcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #draw map, according to the FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if map[x][y].explored:
                        if wall:
                            tcod.console_set_char_background(cuck, x, y, color_dark_wall, tcod.BKGND_SET)
                        else:
                            tcod.console_set_char_background(cuck, x, y, color_dark_ground, tcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        tcod.console_set_char_background(cuck, x, y, color_light_wall, tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(cuck, x, y, color_light_ground, tcod.BKGND_SET)
                    #since it's visible, explore it
                    map[x][y].explored = True

    #draw all objects in the list
    for object in objects:
        object.draw()

    #blit the contents of "cuck" to the root console and present it
    tcod.console_blit(cuck, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def clear_all():
    #erase all objects on the map
    for object in objects:
        object.clear()


# ############################################
# Initialization & Main Game Loop
# ############################################
# Setup Font
font_filename = 'd:/Python/RougeLike/project/arial10x10.png'
tcod.console_set_custom_font(font_filename, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
# Initialize screen
title = 'RLPY'
tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, title, FULLSCREEN)
cuck = tcod.console_new(SCREEN_WIDTH,SCREEN_HEIGHT) #temporary work screen
# Set FPS
tcod.sys_set_fps(LIMIT_FPS)

#Set map colors
color_dark_wall = tcod.Color(0, 0, 100)
color_light_wall = tcod.Color(130, 110, 50)
color_dark_ground = tcod.Color(50,50,150)
color_light_ground = tcod.Color(200, 180, 50)

#Create player
player = Object(0, 0, '@', tcod.white)
#Create npc
npc = Object(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT // 2, '#', tcod.yellow)
#Create list of objects
objects = [npc, player]
 
#Generate map
make_map()
 
#FOV
fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        tcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True

# #########
# MAIN LOOP
# #########

exit_game = False
while not tcod.console_is_window_closed() and not exit_game:

    #draw all objects in the list
    render_all()

    tcod.console_flush()

    #erase all objects at thier old locations, before they move
    clear_all()
        
    exit_game = handle_keys()
 