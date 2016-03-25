import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import resource

images={}

surfaces={}

def load_image(img):
    if img in surfaces:
        return surfaces[img]
    i=pygame.image.load(resource.path("image", img))
    dat=i, pygame.image.tostring(i, "RGBA")
    surfaces[img]=dat
    return dat

def get(img, mipmap=True):
    id_="%s-%s" % (img, mipmap)
    if id_ not in images:
        if img in surfaces:
            i=surfaces[img]
        else:
            i=load_image(img)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        
        o=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, o)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        if mipmap:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, i[0].get_rect().w, i[0].get_rect().h, 
                              GL_RGBA, GL_UNSIGNED_BYTE, i[1])
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, i[0].get_rect().w, i[0].get_rect().h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, i[1])
        images[id_]=o
    return images[id_]

def get_with_func(func, img, mipmap=False):
    id_="%s-%s" % (img, mipmap)
    if id_ not in images:
        if img in surfaces:
            i=surfaces[img]
        else:
            surf=func()
            i=[surf, pygame.image.tostring(surf, "RGBA")]
            surfaces[img]=i

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        
        o=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, o)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        if mipmap:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, i[0].get_rect().w, i[0].get_rect().h, 
                              GL_RGBA, GL_UNSIGNED_BYTE, i[1])
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, i[0].get_rect().w, i[0].get_rect().h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, i[1])
        images[id_]=o
    return images[id_]

def bind(img):
    glBindTexture(GL_TEXTURE_2D, get(img))

def bind_with_func(func, img):
    glBindTexture(GL_TEXTURE_2D, get_with_func(func, img))

def precache(img):
    get(img)
