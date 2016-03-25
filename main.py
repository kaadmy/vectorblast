#!/usr/bin/python2.7

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from util import *
import options
import pygame
import view
import game
import text
import sound

sound.init()
pygame.init()

def reopen():
    global win

    dpysize=[options.get("dpy_width", int), options.get("dpy_height", int)]

    win=pygame.display.set_mode(dpysize, RESIZABLE | OPENGL | DOUBLEBUF)
    pygame.display.set_caption("Vectorblast")
    glViewport(0, 0, *dpysize)

reopen()

glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glEnable(GL_TEXTURE_2D)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

timers={"start": 0}

clock=pygame.time.Clock()

if options.load():
    options.add_bind("W", "walk_forward")
    options.add_bind("S", "walk_backward")
    options.add_bind("A", "strafe_left")
    options.add_bind("D", "strafe_right")

    options.add_bind("Space_Tap", "jump")

    options.add_bind("Mouse1", "shoot")
    options.add_bind("Left_Control", "shoot")

    options.add_bind("Mouse4_Tap", "weapon_next")
    options.add_bind("Mouse5_Tap", "weapon_prev")

    options.add_bind("Mouse3", "scope")

    options.add_bind("Escape", "quit")

options.set("gravity", 16, False)
options.set("player_superjump", True, False)
options.set("player_jump_force", 7, False)
options.set("player_step_height", 0.5, False)
options.set("player_damping_air", 1.0, False)
options.set("player_damping_ground", 0.15, False)
options.set("player_accel_air", 6, False)
options.set("player_accel_ground", 50, False)

options.set("view_gun_stiffness", 10, False)

options.set("dpy_width", 1024, False)
options.set("dpy_height", 600, False)
options.set("dpy_fov", 90, False)
options.set("dpy_fov_scope", 35, False)

options.set("mouse_sensitivity", 0.1, False)

options.set("slowmo", 1.0, True)

pygame.mouse.set_pos([options.get("dpy_width", int)/2, options.get("dpy_height", int)/2])

pygame.mouse.set_visible(False)

keys=[]
key_press=[]
key_release=[]

mouse=[]
mouse_press=[]
mouse_release=[]
mouse_pos=[0, 0]

glLineWidth(2)

player=game.init_player()

world=game.init_world()

view.set(player)

state = "game"

player.draw()

world.draw()

binds={
    K_LCTRL: "left control",
    K_RCTRL: "right control",
    K_ESCAPE: "escape"
    }

world.precache()

clock.tick(60)

try:
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                raise ValueError("window close")
            
            elif e.type == VIDEORESIZE:
                options.set("dpy_width", e.w, True)
                options.set("dpy_height", e.h, True)

                reopen()

            elif e.type == MOUSEMOTION:
                if state == "game":
                    player.turn((e.pos[0]-(options.get("dpy_width", int)/2))*options.get("mouse_sensitivity", float), (e.pos[1]-(options.get("dpy_height", int)/2))*options.get("mouse_sensitivity", float))
                    pygame.mouse.set_pos([options.get("dpy_width", int)/2, options.get("dpy_height", int)/2])
                else:
                    mouse_pos=e.pos

            elif e.type == KEYDOWN:
                key_press.append(e.key)
                if e.key not in keys:
                    keys.append(e.key)

            elif e.type == KEYUP:
                key_release.append(e.key)
                if e.key in keys:
                    keys.remove(e.key)

            elif e.type == MOUSEBUTTONDOWN:
                mouse_press.append(e.button)
                if e.button not in mouse:
                    mouse.append(e.button)

            elif e.type == MOUSEBUTTONUP:
                mouse_release.append(e.button)
                if e.button in mouse:
                    mouse.remove(e.button)

        actions={}

        for k in keys:
            action=options.get_bind(pygame.key.name(k).title().replace(" ", "_"))
            if action:
                actions[action]=True

            action=options.get_bind(binds.get(k, "").title().replace(" ", "_"))
            if action:
                actions[action]=True

        for k in key_press:
            action=options.get_bind((pygame.key.name(k)+" tap").title().replace(" ", "_"))
            if action:
                actions[action]=True

            action=options.get_bind((binds.get(k, "")+" tap").title().replace(" ", "_"))
            if action:
                actions[action]=True

        for m in mouse:
            action=options.get_bind("Mouse"+str(m))
            if action:
                actions[action]=True

        for m in mouse_press:
            action=options.get_bind("Mouse"+str(m) + "_Tap")
            if action:
                actions[action]=True

        player.set_controls(actions)

        if "quit" in actions:
            raise SystemExit

        clock.tick(0)
        d=(clock.get_time()/1000.0)*options.get("slowmo", float)

        for t in timers:
            timers[t]+=d

        glClear(GL_DEPTH_BUFFER_BIT)

        if state == "game":
            world.update(d)

            player.update(d)
            
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            fov=lerp(options.get("dpy_fov", int), options.get("dpy_fov_scope", int), view.get_zoom())
            gluPerspective(fov, options.get("dpy_width", int)/options.get("dpy_height", float), 0.1, 500.0)
            gluLookAt(0, 0, 0,
                      0, 1, 0,
                      0, 0, 1)

            glRotatef(view.get_rot()[0], 1, 0, 0)
            glRotatef(view.get_rot()[1], 0, 1, 0)
            glRotatef(view.get_rot()[2], 0, 0, 1)
            glTranslatef(-view.get_pos()[0], -view.get_pos()[1], -view.get_pos()[2])

            glMatrixMode(GL_MODELVIEW)

            glEnable(GL_DEPTH_TEST)

            player.pre_world_draw()

            world.draw()

            player.draw()

            glDisable(GL_DEPTH_TEST)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0, options.get("dpy_width", int), options.get("dpy_height", int), 0, -1, 1)

            glColor3f(1.0, 1.0, 1.0)
            
            text.draw_text(str(round(clock.get_fps(), 2)), (255, 120, 120), (0, 0), (0, 0), 20, False, False)

        elif state == "menu":
            glDisable(GL_DEPTH_TEST)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0, options.get("dpy_width", int), options.get("dpy_height", int), 0, -1, 1)

        pygame.display.flip()

        key_press=[]
        key_release=[]

        mouse_press=[]
        mouse_release=[]

except BaseException as e:
    options.save()
    if e.message != "window close":
        raise
