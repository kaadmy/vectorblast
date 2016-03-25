from OpenGL.GL import *
import pygame
import texture
import options

fonts={}

options.set("text_fontname", "monospace", False)
options.set("text_fontsize", 64, False)

def load_font(bold=False, italic=False):
    id_=options.get("text_fontname", str)+"-%s-%s" % (bold, italic)
    if id_ not in fonts:
        fonts[id_]=pygame.font.SysFont(options.get("text_fontname", str), options.get("text_fontsize", int), bold=bold, italic=italic)

def draw_text(text, color, pos, offset, size, bold=False, italic=False):
    load_font(bold=bold, italic=italic)

    id_="text-%s-%s-%s-%s" % (text, color, bold, italic)

    fontid=options.get("text_fontname", str)+"-%s-%s" % (bold, italic)
    
    def render():
        surf=fonts[fontid].render(text, True, color)
        return surf

    texture.bind_with_func(render, id_)

    texwidth, texheight=texture.surfaces[id_][0].get_size()

    texwidth/=float(options.get("text_fontsize", int))
    texheight/=float(options.get("text_fontsize", int))

    texwidth*=size
    texheight*=size

    glEnable(GL_TEXTURE_2D)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(pos[0]+(texwidth*offset[0]), pos[1]+(texheight*offset[1]))
    glTexCoord2f(0, 1)
    glVertex2f(pos[0]+(texwidth*offset[0]), pos[1]+texheight+(texheight*offset[1]))
    glTexCoord2f(1, 1)
    glVertex2f(pos[0]+texwidth+(texwidth*offset[0]), pos[1]+texheight+(texheight*offset[1]))
    glTexCoord2f(1, 0)
    glVertex2f(pos[0]+texwidth+(texwidth*offset[0]), pos[1]+(texheight*offset[1]))
    glEnd()
