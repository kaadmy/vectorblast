import json
import texture
from OpenGL.GL import *
from OpenGL.GLU import *
from util import *
import resource

cache={}

def load(name, mm=False):
    mtype="model"
    if mm:
        mtype="mapmodel"

    path=resource.path(mtype, name)
    out=[]
    try:
        f=open(path, "r")
        data=f.read().strip().split("\n")
        f.close()

        faces=[]

        vertices=[]

        texcoords=[]

        for l in data:
            l=l.split(" ")
            if l[0] == "vertex":
                vertices.append([float(x) for x in l[1:]])
            elif l[0] == "texcoord":
                texcoords.append([float(x) for x in l[1:]])
            elif l[0] == "face":
                faces.append([[int(x) for x in l[1:7]], l[7]])

        out=[vertices, texcoords, faces]
    except:
        pass
    return out

def get(name, materials={}, shading=True, mm=False):
    id_=name
    id_+=str(mm)
    for m in materials:
        id_+=m
        id_+=str(materials[m])
    id_+=str(shading)
    if id_ in cache:
        return cache[id_]

    verts, tex, faces=load(name, mm)

    cache[id_]=glGenLists(1)
    glNewList(cache[id_], GL_COMPILE)
    
    ccol=None
    ctex=None

    for face in faces:
        if materials.get(face[1]):
            if ccol != materials[face[1]][:4]:
                glColor4fv(materials[face[1]][:4])
                ccol=materials[face[1]][:4]
            if ctex != materials[face[1]][4]:
                texture.bind(materials[face[1]][4])
                ctex=materials[face[1]][4]
        else:
            if ccol != [1.0, 1.0, 1.0]:
                ccol=[1.0, 1.0, 1.0]
                glColor3f(1.0, 1.0, 1.0)
            if ctex != face[1]:
                texture.bind(face[1])
                ctex=face[1]

        glBegin(GL_TRIANGLES)

        for i in range(3):
            glTexCoord2f(tex[face[0][i+3]][0], 1-tex[face[0][i+3]][1])
            glVertex3fv(verts[face[0][i]])

        glEnd()

    glEndList()
    
    return cache[id_]

def draw_model(name, materials={}, shading=True, mm=False, gl_list=True):
    verts, tex, faces=load(name, mm)

    ccol=None
    ctex=None

    for face in faces:
        if materials.get(face[1]):
            if ccol != materials[face[1]][:4]:
                glColor4fv(materials[face[1]][:4])
                ccol=materials[face[1]][:4]
            if ctex != materials[face[1]][4]:
                texture.bind(materials[face[1]][4])
                ctex=materials[face[1]][4]
        else:
            if ccol != [1.0, 1.0, 1.0]:
                ccol=[1.0, 1.0, 1.0]
                glColor3f(1.0, 1.0, 1.0)
            if ctex != face[1]:
                texture.bind(face[1])
                ctex=face[1]

        glBegin(GL_TRIANGLES)

        for i in range(3):
            glTexCoord2f(tex[face[0][i+3]][0], 1-tex[face[0][i+3]][1])
            glVertex3fv(verts[face[0][i]])

        glEnd()

def draw(name, materials, shading=True, mm=False, gl_list=True):
    if gl_list:
        glCallList(get(name, materials, shading, mm))
    else:
        draw_model(name, materials, shading, mm)

def precache(name, materials, shading=True, mm=False):
    get(name, materials, shading, mm)
