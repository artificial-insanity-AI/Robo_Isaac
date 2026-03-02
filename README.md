game project for Python Programming MOOC 2024 examination (https://programming-24.mooc.fi/)

prerequisites:
 - install python
 - install pygame: pip install pygame


BUGS (those are only the latest ones out of many or current bugs)
- [fixed]      secret room sometimes can generate near the boss room
- [fixed]       secret door spawned without being hit
- [fixed]    coins spawn after boss fight
- [fixed]       coins can spawn in starting room of a new lvl
- [fixed]  tear is drawn after robot respawn losing the extra life
- [fixed]  sometimes no items in the shop/item room
- [fixed]   sometimes no enemies in the room

POTENTIAL FUTURE IMPROVEMENTS

- [mostly  done] rewrite code to OOP and split into multiple files and in accordance with good practices
- prevent next-level door spawning right under the robot (teleport robot away or make the door inactive)
- balance power-level of the enemies and the player at higher levels
- add super enemies with flushy colors and various size
- [done] boss shoots huge lasers from time to time
- [done] darker color of unexplored rooms on the minimap
- [done] do not allow to buy HP if at maximum already
- [done] boss hp bar
- [done] increase the safe zone near the doors
  |-> from 100 to 150 pixels
- add HP up chance to secret rooms
- add a chance for devil deal / angel room to spawn after boss
    - devil deal - two random upgrades one HP price each
    - angel room - two random upgrades (choose only one)

new test line alex

new line ksu(note: resolved conflict)