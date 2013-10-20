import libtcodpy as tcod
import random

RW = 80         # root width
RH = 50         # root height
W0 = 8
H0 = 5
CW = RW - 2*W0  # console width
CH = RH - 2*H0  # console height
FPS = 25
CON = tcod.console_new(CW, CH)


class Obj:
    def __init__(self, x, y):
        self.x = x
        self.y = y

init = True
restart = True
punish = False
chance = 5      # percent chance of a snack/bait
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
        x0 = CW / 2
        y0 = CH / 2
        speed = [1, 0]
        snake = []
        snack = []
        bait = []
        grow = False
        growth = 0
        for i in range(5):
            o = Obj(x0 - i, y0)
            snake.append(o)
    if alive:
        # render snack
        tcod.console_set_default_foreground(CON, tcod.green)
        for s in snack:
            # collision
            if s.x == snake[0].x and s.y == snake[0].y:
                snack.remove(s)
                grow = True
                score += len(snake)
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
        x0 = snake[0].x + speed[0]
        y0 = snake[0].y + speed[1]
        o = Obj(x0, y0)
        snake.insert(0, o)
        if grow:
            growth += 1
            if growth == 5:
                growth = 0
                grow = False
        else:
            snake.pop()
        # gen snack/bait
        if random.randint(0, 100) < chance:
            x = random.randint(0, CW)
            y = random.randint(0, CH)
            o = Obj(x, y)
            if random.randint(0, 100) < 50:
                bait.append(o)
            else:
                snack.append(o)

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
    tcod.console_flush()
    tcod.console_clear(None)
    # fps
    tcod.console_print_ex(None, RW - 2, RH - 2, tcod.BKGND_NONE, tcod.RIGHT,
                          '%3d fps' % tcod.sys_get_fps())
