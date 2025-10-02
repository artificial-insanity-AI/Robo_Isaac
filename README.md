game project for Python Programming MOOC 2024 examination (https://programming-24.mooc.fi/)

prerequisites:
 - install python
 - install pygame: pip install pygame


BUGS (those are only the latest ones out of many or current bugs)
- [fixed?]      secret room sometimes can generate near the boss room
  reason: typo
- [fixed]       secret door spawned without being hit
  reason: one of the "dead" tears from previous room(s) that was not overwritten yet
  match the direction of the secret door in the current room
  fix:    delete all tears instead of setting tear.is_dead=True on entering new room
- [fixed ? ]    coins spawn after boss fight
- [fixed]       coins can spawn in starting room of a new lvl
- [non issue?]  tear is drawn after robot respawn losing the extra life
- [fix later?]  sometimes no items in the shop/item room
- [won't fix]   sometimes no enemies in the room
  |-> reason: doesn't happen too often, and it is ok if some rooms do not have enemies
  [update] - likely first room after defeating a boss (on this or next floor, not counting start) - need to fix

POTENTIAL FUTURE IMPROVEMENTS

- rewrite code to OOP and split into multiple files and in accordance with good practices
- prevent next-level door spawning right under the robot (teleport robot away or make the door inactive)
- balance power-level of the enemies and the player at higher levels
- add super enemies with flushy colors and various size
- boss shoots huge lasers from time to time
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
- new line ksu(note: resolved conflict)