import random

from entities.upgrade import Upgrade
from systems.level import Level


class LevelGenerator:
    def __init__(self, level):
        self.level = level

    # @staticmethod
    # def get_n(i:tuple)->list: # returns *n*eighbours (x,y) -> [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    #     return [(i[0]+1,i[1]),(i[0]-1,i[1]),(i[0],i[1]+1),(i[0],i[1]-1)]

    # @staticmethod
    # def check_b(n:tuple)->bool: # check if outside the mab *b*orders
    #     return n[0] > 6 or n[0] < 0 or n[1] > 8 or n[1] < 0

    def generate(self): # generate current level map

        #7x9 map, room = RGB tuple(rrr,ggg,bbb). supposed to be temporal but then I liked it
        grid = [[(0,0,0) for _ in range(9)] for _ in range(7)]
            #bb1 == room discovered, visible on the map
            #gg1 == is a secret room
            #rr1 == room is cleared, no need to do some things upon entering
        start_room=(3,4)
        upgrades = {          # pre-generate upgrade objects for each room
            (0, 255, 1):Upgrade(),    # green room upgrade
            (250, 255, 1):Upgrade(),  # yellow room upgrade
            (250, 0, 1): Upgrade()    # red room upgrade
        }
        level = Level(grid, start_room, upgrades)

        def how_many_n(target_room:tuple)->int: # how many neighbours exists (helper function)
            neighbour_rooms = level.neighbors(target_room)                         # get neighbour cells
            return sum(el in rooms_created for el in neighbour_rooms)  # how many of them are rooms

        how_many_rooms = random.randint(1,2) + 6 + min(self.level, 8) * 2   # how many rooms to generate
        rooms_created = [(3,4)] # currently existing rooms ((3,4) is always starting room)
        ends = []          # list of the dead end rooms

        while len(rooms_created) < how_many_rooms:    ### generate rooms
            for room in rooms_created:
                if how_many_n(room) < 2:   # check there is no 2 adjacent rooms already
                    for n in level.neighbors(room):
                        if len(rooms_created) == how_many_rooms: break # already have enough rooms
                        if n in rooms_created: continue  # already existing room
                        if level.out_bounds(n):continue      # out of the map range
                        if how_many_n(n) >= 2: continue  # there are 2 adjacent to "n" rooms
                        if random.choice([True, False]): continue # 50% to give up
                        rooms_created.append(n)          # room added to the list

        #                               *** test generated map***
        many_n = False   # clusters helper flag
        for r in rooms_created:
            if how_many_n(r) == 1 and r != (3,4):  # look for dead ends excluding starting room
                ends.append(r)                     # add it to the list of dead ends
            if how_many_n(r) > 3: many_n = True    # if a room somehow got too many neighbours

        #     incorrect amount of rooms?            not enough "ends"?   clusters?
        if how_many_rooms != len(set(rooms_created)) or len(ends) < 3 or many_n:
            return self.generate()             # generate the level anew

        #                    *** passed tests. generate map layout ***
        for r in rooms_created:                 # mark all created rooms
            level.set_rgb(r, (0,222,220))        # with the "regular room" color

        #                            ***SPECIAL ROOMS***
        level.set_rgb((3,4), (251, 255, 251))  # **STARTING** room is white, visible from spawn
        for i in range(-1, -len(ends)-1, -1):      # reverse: should be less likely to get one near the start
            if (3,4) not in level.neighbors(ends[i]):   # **BOSS** room can not be adjacent to start room
                level.set_rgb((ends[i]),(250,0,0))   # boss room created = red
                break

        s = random.choice([i for i in ends if level.rgb(i) == (0,222,220)])   # random unused dead end room
        level.set_rgb(s, (250, 255, 0))             # **SHOP** room = yellow

        i = random.choice([i for i in ends if level.rgb(i) == (0,222,220)])
        level.set_rgb(i, (0, 255, 0))               # **UPGRADE** room = green

        #**SECRET ROOM** = random non-existing room among those that have most existing neighbours
        # NOTE: undiscovered secret room will not have a visible door or minimap visibility
        ##      to find it shoot the wall
        candidates = [] # [(n,(x,y)),...] where n is how many non-boss neighbours
        for room in rooms_created:
            for n in level.neighbors(room):
                if level.out_bounds(n): continue        # square is outside the map
                if level.rgb(n) != (0,0,0): continue      # square is occupied
                if (250,0,0) in [level.rgb(i) for i in level.neighbors(n) if not level.out_bounds(i)]:
                    continue                             # the boss room is neighbour
                rgb_in_range = [level.rgb(i) for i in level.neighbors(n) if not level.out_bounds(i)]
                r = len(rgb_in_range) - rgb_in_range.count((0,0,0)) # how many adjacent non-boss rooms
                candidates.append((r, n)) # candidate found

        for i in range(4,0,-1): # i = how many existing neighbours, start with maximum 4, then 3...
            roms = [r[1] for r in candidates if r[0] == i] # list all rooms with "i" neighbours
            if roms: # if none with "i" neighbours go look with "i-1" in the next loop
                s = random.choice(roms) # pick random location
                level.set_rgb(s, (0,1,60)) # **secret** room created
                break                     ## 1 == secret room flag

        return Level(grid, start_room, upgrades)

        #########---for testing purposes---########
        # for i in candidates: ### for testing possible secret locations
        # #     self.map[i[1][0]][i[1][1]] = (0,0,251)
        # for i in rooms_created: # turn on visibility for all rooms
        #     self.set_flag(i,2)  ## secret room visibility? edit flag at creation

