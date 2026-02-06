class Level:
    def __init__(self, grid, start_room: tuple, upgrades: dict):
        self.grid = grid
        # 7x9 map, room = RGB tuple(rrr,ggg,bbb). supposed to be temporal, but then I liked it
        # last number is a flag (it doesn't make the difference for the actual color)
        # bb1 == room is discovered, visible on the map
        # gg1 == is a secret room
        # rr1 == room is cleared, no need to do some things upon entering etc.

        self.start_room = start_room
        self.upgrades = upgrades

    def rgb(self, room: tuple) -> tuple:    # converts room (x,y)->(r,g,b)
        return self.grid[room[0]][room[1]]

    def set_rgb(self, room: tuple, rgb: tuple) -> None: # set new rgb value for (x,y) room
        self.grid[room[0]][room[1]] = rgb

    def flag(self, room: tuple, flag: int) -> bool:     # flag position: 0 or 1 or 2
        return str(self.rgb(room)[flag])[-1] == "1"     # True if flag == 1

    def set_flag(self, room, flag) -> None:        # set flag to 1
        rgb = list(self.rgb(room))
        s = str(rgb[flag])
        rgb[flag] = int(s[:-1] + "1")
        self.set_rgb(room, tuple(rgb))

    def neighbors(self, room: tuple) -> list:  # (x,y) -> i[(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        return [(room[0] + 1, room[1]), (room[0] - 1, room[1]),
                (room[0], room[1] + 1), (room[0], room[1] - 1)]

    def in_bounds(self, r:tuple)->bool:
        return r[0] > 6 or r[0] < 0 or r[1] > 8 or r[1] < 0

    # TODO: get_upgrade(room) and consume_upgrade(room) move here?
