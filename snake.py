import libtcodpy as tcod
import random


class Obj:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def snackxy(grid, w, h):
    for x in range(w):
        for y in range(h):
            if tcod.map_is_transparent(grid, x, y):
                return True, x, y
    return False, 0, 0

demo = True     # toggle to play as human or bot
RW = 80         # root width
RH = 50         # root height
W0 = 8
H0 = 5
CW = RW - 2*W0  # console width
CH = RH - 2*H0  # console height
FPS = 25
CON = tcod.console_new(CW, CH)
init = True
restart = True
chance = 10     # percent chance of a snack/bait
tcod.console_init_root(RW, RH, 'snake - hit ESC to quit')
tcod.sys_set_fps(FPS)
tcod.console_set_default_background(None, tcod.gold)
key = tcod.Key()
mouse = tcod.Mouse()
while not tcod.console_is_window_closed():
    tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key,
                             mouse)
    if init:
        init = False
        hearts = 5
        alive = True
        score = 0
    if restart:
        punish = False
        restart = False
        speed = [1, 0]
        snake = []
        snack = []
        bait = []
        grow = False
        growth = 0
        grid = tcod.map_new(CW, CH)
        tcod.map_clear(grid, False, True)
        found = False
        for x in range(5):
            o = Obj(CW / 2 - x, CH / 2)
            snake.append(o)
            tcod.map_set_properties(grid, CW / 2 - x, CH / 2, False, False)
    if alive:
        # render snack
        tcod.console_set_default_foreground(CON, tcod.green)
        for s in snack:
            # collision
            if s.x == snake[0].x and s.y == snake[0].y:
                snack.remove(s)
                grow = True
                score += len(snake)
                found = False
                #tcod.map_set_properties(grid, s.x, s.y, False, True)
            tcod.console_put_char(CON, s.x, s.y, chr(5))
        # render bait
        tcod.console_set_default_foreground(CON, tcod.gold)
        for b in bait:
            # collision
            if b.x == snake[0].x and b.y == snake[0].y:
                punish = True
                break
            tcod.console_put_char(CON, b.x, b.y, chr(219))
        # render snake
        tcod.console_set_default_foreground(CON, tcod.red)
        for i, s in enumerate(snake):
            if i > 0:
                if s.x == snake[0].x and s.y == snake[0].y:
                    punish = True
            else:
                if s.x == CW or s.x == -1 or s.y == CH or s.y == -1:
                    punish = True
                    break
            tcod.console_put_char(CON, s.x, s.y, chr(219))
        if punish:
            hearts -= 1
            if hearts < 1:
                alive = False
            else:
                restart = True
        # gen snake
        x = snake[0].x + speed[0]
        y = snake[0].y + speed[1]
        o = Obj(x, y)
        snake.insert(0, o)
        tcod.map_set_properties(grid, x, y, False, False)
        if grow:
            growth += 1
            if growth == 5:
                growth = 0
                grow = False
        else:
            tcod.map_set_properties(grid, snake[-1].x, snake[-1].y, False, True)
            snake.pop()
        # gen snack/bait
        if random.randint(0, 100) < chance:
            x = random.randint(0, CW)
            y = random.randint(0, CH)
            o = Obj(x, y)
            if random.randint(0, 100) < 50:
                bait.append(o)
                tcod.map_set_properties(grid, x, y, False, False)
            else:
                snack.append(o)
                tcod.map_set_properties(grid, x, y, True, True)
    else:
        msg = 'game over man!'
        tcod.console_print(CON, (CW - len(msg)) / 2, CH / 2, msg)
        msg = 'hit ESC to restart'
        tcod.console_print(CON, (CW - len(msg)) / 2, CH / 2 + 2, msg)
    # blit console
    tcod.console_blit(CON, 0, 0, 0, 0, None, W0, H0)
    tcod.console_clear(CON)
    # render score
    tcod.console_set_default_foreground(None, tcod.red)
    for x in range(hearts):
        tcod.console_put_char(None, x + 1, RH - 2, chr(3))
    tcod.console_set_default_foreground(None, tcod.blue)
    msg = str(score)
    tcod.console_print(None, (RW - len(msg)) / 2, RH - 2, msg)
    # key handler
    if key.vk == tcod.KEY_DOWN:
        if speed[1] != -1:
            speed = [0, 1]
    elif key.vk == tcod.KEY_UP:
        if speed[1] != 1:
            speed = [0, -1]
    elif key.vk == tcod.KEY_LEFT:
        if speed[0] != 1:
            speed = [-1, 0]
    elif key.vk == tcod.KEY_RIGHT:
        if speed[0] != -1:
            speed = [1, 0]
    elif key.vk == tcod.KEY_ESCAPE:
        if not alive:
            init = True
            restart = True
        else:
            break
    if demo:
        # find a snack (snacks are transparent)
        if not found:
            found, pathx, pathy = snackxy(grid, CW, CH)
        if found:
            path = tcod.path_new_using_map(grid, 0)
            if tcod.path_compute(path, snake[0].x, snake[0].y, pathx, pathy):
                #x, y = tcod.path_get(path, 0)
                x, y = tcod.path_walk(path, True)
                if x is not None:
                    speed = [x - snake[0].x, y - snake[0].y]
            # no path
            else:
                # you're fucked
                found = False
        else:
            # no snack on grid (yet?)
            x = snake[0].x + speed[0]
            y = snake[0].y + speed[1]
            if not tcod.map_is_walkable(grid, x, y):
                # try up
                speed = [0, -1]
                x = snake[0].x + speed[0]
                y = snake[0].y + speed[1]
                if not tcod.map_is_walkable(grid, x, y):
                    # try down
                    speed = [0, 1]
                    x = snake[0].x + speed[0]
                    y = snake[0].y + speed[1]
                    if not tcod.map_is_walkable(grid, x, y):
                        # try left
                        speed = [-1, 0]
                        x = snake[0].x + speed[0]
                        y = snake[0].y + speed[1]
                        if not tcod.map_is_walkable(grid, x, y):
                            # try right
                            speed = [1, 0]
                            x = snake[0].x + speed[0]
                            y = snake[0].y + speed[1]
                            if not tcod.map_is_walkable(grid, x, y):
                                #you're fucked
                                pass
    tcod.console_flush()
    tcod.console_clear(None)
    # fps
    tcod.console_print_ex(None, RW - 2, RH - 2, tcod.BKGND_NONE, tcod.RIGHT,
                          '%3d fps' % tcod.sys_get_fps())
