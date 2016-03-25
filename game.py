from OpenGL.GL import *
from util import *
import texture
import model
import random
import resource
import sound
import options

class WeaponDef:
    def __init__(self, maxammo, refire, spread, bulletspeed, bullets, knockback, spin, name):
        self.maxammo=maxammo
        self.refire=refire
        self.name=name
        self.spread=spread
        self.bulletspeed=bulletspeed
        self.bullets=bullets
        self.knockback=knockback
        self.spin=spin

class Weapon:
    def __init__(self, parent, wepdef):
        self.parent=parent
        self.wepdef=wepdef
        self.name=wepdef.name
        self.ammo=wepdef.maxammo
        self.refire=0
        
    def update(self, d):
        self.refire+=d

    def fire(self):
        if self.refire > self.wepdef.refire:
            sound.play_sound(self.name+"_fire")

            self.refire=0

            xm, zm=rotate([1, 0], radians(self.parent.gun_rot[0]))

            x_offset=self.parent.gun_offset[0]
            y_offset=self.parent.gun_offset[1]*xm+self.parent.gun_offset[2]*zm
            z_offset=self.parent.gun_offset[2]*xm-self.parent.gun_offset[1]*zm

            x_offset, y_offset=rotate([x_offset, y_offset], -radians(self.parent.gun_rot[2]))

#            gun_rot=[self.parent.gun_rot[0], self.parent.gun_rot[2]]
            gun_rot=self.parent.rot

            for i in range(self.wepdef.bullets):
                world.spawn_bullet(Bullet(self.parent.pos[0]+x_offset, self.parent.pos[1]+y_offset, self.parent.pos[2]+1.8+z_offset, [gun_rot[0], gun_rot[1]], [crange(0, random.random(), 1, -self.wepdef.spread, self.wepdef.spread), crange(0, random.random(), 1, -self.wepdef.spread, self.wepdef.spread), crange(0, random.random(), 1, -self.wepdef.spread, self.wepdef.spread)], self.wepdef.bulletspeed))

            return True
        return False

wepdefs=[
    WeaponDef(120, 0.083, 0.04, 50, 1, 0.5, True, "chaingun"),
    WeaponDef(20, 0.9, 0.06, 90, 14, 5.0, False, "shotgun"),
    ]

class Player:
    def __init__(self):
        self.pos=[0, 0, 1]
        self.vel=[0, 0, 0]
        self.rot=[0, 0]

        self.height=Lowpass(self.pos[2], 16) # camera height alignment speed(view smoothing from landings, stairs

        self.step_height=options.get("player_step_height", float)

        self.hit=[0, 0, 0]

        self.recoil=Lowpass(0, 3)

        self.jump=0

        self.controls={}
        self.damping=[ # Air damping, ground damping: it takes that many seconds to get to zero velocity
            options.get("player_damping_air", float),
            options.get("player_damping_ground", float)
            ]
        self.speed=[ # Air speed, ground speed: acceleration per second
            options.get("player_accel_air", float),
            options.get("player_accel_ground", float)
            ]
        
        self.gun_rot=[0, 0, 0]
        self.gun_offset=[0, 0, 0]
        self.gun_mult=0
        self.gun_spin=0

        self.gun_rotation_speed=Lowpass(0, 5)

        self.gun_sway=[
            Lowpass(0, options.get("view_gun_stiffness", float)),
            Lowpass(0, options.get("view_gun_stiffness", float)),
            Lowpass(0, options.get("view_gun_stiffness", float))
            ]

        self.time=0

        self.zoom=0
        
        self.weapon=0
        self.weapons=[]
        for w in wepdefs:
            self.weapons.append(Weapon(self, w))

        for w in self.weapons:
            model.precache("weapon_"+w.name, {"body": [1.0, 1.0, 1.0, 1.0, w.name], "muzzleflash": [1.0, 1.0, 1.0, 0.0, "muzzleflash"]})
            model.precache("weapon_"+w.name, {"body": [1.0, 1.0, 1.0, 1.0, w.name], "muzzleflash": [1.0, 1.0, 1.0, 1.0, "muzzleflash"]})
            if w.wepdef.spin:
                glRotatef(self.gun_spin, 0, 1, 0)
                model.precache("weapon_"+w.name+"_spin", {"spin": [1.0, 1.0, 1.0, 1.0, w.name+"_spin"], "muzzleflash": [1.0, 1.0, 1.0, 0.0, "muzzleflash"]})
                model.precache("weapon_"+w.name+"_spin", {"spin": [1.0, 1.0, 1.0, 1.0, w.name+"_spin"], "muzzleflash": [1.0, 1.0, 1.0, 1.0, "muzzleflash"]})

    def get_zoom(self):
        return self.zoom
    
    def get_pos(self):
        return [self.pos[0], self.pos[1], self.height.value+1.8]

    def get_rot(self):
        return [self.rot[0], 0, self.rot[1]]

    def turn(self, x, y):
        self.rot[1]+=x
        self.rot[0]+=y

    def pre_world_draw(self):
        glPushMatrix()
        glDisable(GL_CULL_FACE)
        glDisable(GL_DEPTH_TEST)
        glTranslatef(self.pos[0], self.pos[1], self.height.value+1.8)
        draw_cube_scaled(-1, -1, -1, 2, 2, 2,
                          ["sky_nx", "sky_px", "sky_py", "sky_ny", "sky_pz", "sky_nz"],
                          [1.0, 1.0, 1.0])
        glEnable(GL_DEPTH_TEST)
        
        glPopMatrix()


    def draw(self):
        glEnable(GL_TEXTURE_2D)

        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.height.value+1.8)
        glTranslatef(self.gun_sway[0].value*1, self.gun_sway[1].value*1, self.gun_sway[2].value*1)
        glRotatef(-self.gun_rot[2], 0, 0, 1)
        glRotatef(-self.gun_rot[0], 1, 0, 0)
        glTranslatef(self.gun_offset[0], self.gun_offset[1], self.gun_offset[2])
        glRotatef(self.gun_rot[1], 0, 1, 0)
        glClear(GL_DEPTH_BUFFER_BIT)
        model.draw("weapon_"+self.weapons[self.weapon].name, {"body": [1.0, 1.0, 1.0, 1.0, self.weapons[self.weapon].name], "muzzleflash": [1.0, 1.0, 1.0, round(self.recoil.value), "muzzleflash"]})
        if self.weapons[self.weapon].wepdef.spin:
            glRotatef(self.gun_spin, 0, 1, 0)
            model.draw("weapon_"+self.weapons[self.weapon].name+"_spin", {"spin": [1.0, 1.0, 1.0, 1.0, self.weapons[self.weapon].name+"_spin"], "muzzleflash": [1.0, 1.0, 1.0, round(self.recoil.value), "muzzleflash"]})
        glPopMatrix()

    def update(self, d):
        for w in self.weapons:
            w.update(d)

        self.recoil.update(d, 0)

        if self.get_control("shoot"):
            if self.weapons[self.weapon].fire():
                self.recoil.value=1

                l=-self.weapons[self.weapon].wepdef.knockback

                xm=cos(radians(self.rot[0]))
                zm=-sin(radians(self.rot[0]))
                self.vel[0]+=sin(radians(self.rot[1]))*xm*l
                self.vel[1]+=cos(radians(self.rot[1]))*xm*l
                self.vel[2]+=zm*l

        self.time+=d

        self.rot[0]=clamp(-90, self.rot[0], 90)
        speed=d*self.get_speed()

        walking=False

        if self.get_control("weapon_next"):
            self.weapon+=1
            self.recoil.value=0.4
        if self.get_control("weapon_prev"):
            self.weapon-=1
            self.recoil.value=0.4
            
        if self.weapon < 0:
            self.weapon+=len(self.weapons)
        elif self.weapon >= len(self.weapons):
            self.weapon-=len(self.weapons)

        if self.get_control("walk_forward"):
            self.vel[0]+=sin(radians(self.rot[1]))*speed
            self.vel[1]+=cos(radians(self.rot[1]))*speed
            walking=True

        if self.get_control("walk_backward"):
            self.vel[0]-=sin(radians(self.rot[1]))*speed
            self.vel[1]-=cos(radians(self.rot[1]))*speed
            walking=True

        if self.get_control("strafe_left"):
            self.vel[0]-=sin(radians(self.rot[1]+90))*speed
            self.vel[1]-=cos(radians(self.rot[1]+90))*speed
            walking=True

        if self.get_control("strafe_right"):
            self.vel[0]+=sin(radians(self.rot[1]+90))*speed
            self.vel[1]+=cos(radians(self.rot[1]+90))*speed
            walking=True

        self.vel[2]-=options.get("gravity", float)*d

        if self.hit[2]:
            self.jump=1
            
        if self.get_control("jump") and self.jump > 0:
            if options.get("player_superjump", bool) and not self.hit[2]:
                l=((self.vel[0]**2)+(self.vel[1]**2)+(self.vel[2]**2))**0.5
                l*=0.5
                xm=cos(radians(self.rot[0]))
                zm=-sin(radians(self.rot[0]))
                self.vel[0]+=sin(radians(self.rot[1]))*xm*l
                self.vel[1]+=cos(radians(self.rot[1]))*xm*l
                self.vel[2]+=zm*l
                self.vel[2]+=options.get("player_jump_force", float)*0.75
                self.jump-=1
            else:
                self.vel[2]+=options.get("player_jump_force", float)

        if world != None:
            boxes=world.hit([-0.5+self.pos[0], -0.5+self.pos[1], self.pos[2]+self.vel[2]*d, 1, 1, 2.0])
            self.hit[2]=False
            hit=False
            jump=False
            for b in boxes:
                if self.vel[2] > 0:
                    if self.pos[2] > b[3]-2:
                        self.pos[2]=b[3]-2
                else:
                    if b[0] == "jumppad":
                        self.vel=[b[7], b[8], b[9]]
                        sound.play_sound("jumppad")
                        jump=True
                    else:
                        if self.pos[2] < b[3]+b[6]:
                            self.pos[2]=b[3]+b[6]
                        self.hit[2]=True
                hit=True

            if hit and not jump:
                self.vel[2]=0

            boxes=world.hit([-0.5+self.pos[0]+self.vel[0]*d, -0.5+self.pos[1], self.pos[2], 1, 1, 2.0])

            height=-float("inf")
            self.hit[0]=False
            for b in boxes:
                if self.vel[0] > 0:
                    if self.pos[0] > b[1]-0.5:
                        self.pos[0]=b[1]-0.5
                else:
                    if self.pos[0] < b[1]+b[4]+0.5:
                        self.pos[0]=b[1]+b[4]+0.5
                if height < b[3]+b[6]:
                    height=b[3]+b[6]
                self.hit[0]=True

            boxes=world.hit([-0.5+self.pos[0], -0.5+self.pos[1]+self.vel[1]*d, self.pos[2], 1, 1, 2.0])

            if height < self.pos[2]+self.step_height and height > self.pos[2]:
                self.pos[2]=height
                self.hit[0]=False
                if self.vel[2] < 0:
                    self.vel[2]=0

            height=0

            self.hit[1]=False
            for b in boxes:
                if self.vel[1] > 0:
                    if self.pos[1] > b[2]-0.5:
                        self.pos[1]=b[2]-0.5
                else:
                    if self.pos[1] < b[2]+b[5]+0.5:
                        self.pos[1]=b[2]+b[5]+0.5
                if height < b[3]+b[6]:
                    height=b[3]+b[6]
                self.hit[1]=True

            if height < self.pos[2]+self.step_height and height > self.pos[2]:
                self.pos[2]=height
                self.hit[1]=False
                if self.vel[2] < 0:
                    self.vel[2]=0

            if self.hit[0]:
                self.vel[0]=0

            if self.hit[1]:
                self.vel[1]=0

        self.height.update(d, self.pos[2])

        self.pos[0]+=self.vel[0]*d
        self.pos[1]+=self.vel[1]*d
        self.pos[2]+=self.vel[2]*d

        self.gun_rotation_speed.update(d, 0)

        if self.get_control("shoot"):
            self.gun_rotation_speed.value=720

        self.vel[0]*=crange(0, d, self.damping[int(self.hit[2])], 1, 0)
        self.vel[1]*=crange(0, d, self.damping[int(self.hit[2])], 1, 0)
        self.vel[2]*=crange(0, d, self.damping[0], 1, 0)

        self.gun_rot[0]-=crange(0, d, 0.1, 0, self.gun_rot[0]-self.rot[0])
        self.gun_spin+=d*self.gun_rotation_speed.value
        self.gun_rot[2]-=crange(0, d, 0.1, 0, self.gun_rot[2]-self.rot[1])

        sway_clamp=5

        self.gun_rot[0]=clamp(self.rot[0]-sway_clamp, self.gun_rot[0], self.rot[0]+sway_clamp)
        self.gun_rot[2]=clamp(self.rot[1]-sway_clamp, self.gun_rot[2], self.rot[1]+sway_clamp)

        self.gun_rot[0]-=self.recoil.value*4
        self.gun_rot[1]=self.recoil.value*8

        self.gun_offset[0]=0.21*(1-self.get_zoom())
        self.gun_offset[1]=0.2-(self.recoil.value*0.08)
        self.gun_offset[2]=-0.24-(self.recoil.value*0.12)

        rot=sin(self.time*10)

        if not self.hit[2]:
            walking=0

        if self.gun_mult < walking:
            self.gun_mult+=d*10
        elif self.gun_mult > walking:
            self.gun_mult-=d*10

        self.gun_mult=clamp(0, self.gun_mult, 1)

        if self.zoom < self.get_control("scope"):
            self.zoom+=d*5
        elif self.zoom > self.get_control("scope"):
            self.zoom-=d*5

        self.zoom=clamp(0, self.zoom, 1)

        self.gun_offset[0]-=self.gun_mult*(sin(rot)*0.02)
        self.gun_offset[2]-=self.gun_mult*((cos(rot)*0.02)-0.02)

        sway_clamp=0.1
        sway_mult=0.004

        self.gun_sway[0].update(d, clamp(-sway_clamp, -self.vel[0]*sway_mult, sway_clamp))
        self.gun_sway[1].update(d, clamp(-sway_clamp, -self.vel[1]*sway_mult, sway_clamp))
        self.gun_sway[2].update(d, clamp(-sway_clamp, -self.vel[2]*sway_mult, sway_clamp))

    def get_speed(self):
        return self.speed[int(self.hit[2])]

    def set_controls(self, controls):
        self.controls=controls
        
    def get_control(self, name):
        return self.controls.get(name, False)
    
class Bullet:
    def __init__(self, x, y, z, r, offset, speed):
        self.x=x
        self.y=y
        self.z=z
        self.r=r
        self.offset=offset
        self.dead=False
        self.deadtimer=0
        self.remove=False
        self.time=0
        self.speed=speed
        self.spinspeed=crange(0, random.random(), 1, -2000, 2000)
        self.spin=random.random()*360
        self.length=0.5
        self.scale=1

        self.vel=[0, 0, 0]
        xm=cos(radians(self.r[0]))
        zm=-sin(radians(self.r[0]))
        rotated=rotate([xm, 0], -radians(self.r[1]+270))
        self.vel[0]=(self.offset[0]+rotated[0])*self.speed
        self.vel[1]=(self.offset[1]+rotated[1])*self.speed
        self.vel[2]=(self.offset[2]+zm)*self.speed

        self.hitdir=None

        self.cooldown=crange(0, random.random(), 1, 0.5, 1.5)

    def _update(self, d):
        if self.time > 3:
            self.remove=True
        if self.dead:
            self.deadtimer+=d
            self.length=crange(0, self.deadtimer, 1, 1.0, 0)
            self.scale=crange(0, self.deadtimer, 1, 1, 4)
            if self.deadtimer > 3:
                self.remove=True
        else:
            self.time+=d
            
            self.x+=self.vel[0]*d
            self.y+=self.vel[1]*d
            self.z+=self.vel[2]*d

        if not self.dead:
            boxes=world.hit([self.x, self.y, self.z, 0, 0, 0])
            if boxes:
                if not world.hit([self.x-self.vel[0]*d, self.y, self.z, 0, 0, 0]):
                    self.hitdir="x"
                if not world.hit([self.x, self.y-self.vel[1]*d, self.z, 0, 0, 0]):
                    self.hitdir="y"
                if not world.hit([self.x, self.y, self.z-self.vel[2]*d, 0, 0, 0]):
                    self.hitdir="z"
                if self.hitdir == "x":
                    if self.vel[0] < 0:
                        self.x=boxes[0][1]+boxes[0][4]+0.01
                    else:
                        self.x=boxes[0][1]-0.01
                elif self.hitdir == "y":
                    if self.vel[1] < 0:
                        self.y=boxes[0][2]+boxes[0][5]+0.01
                    else:
                        self.y=boxes[0][2]-0.01
                elif self.hitdir == "z":
                    if self.vel[2] < 0:
                        self.z=boxes[0][3]+boxes[0][6]+0.01
                    else:
                        self.z=boxes[0][3]-0.01
                self.dead=True

    def update(self, d):
        for i in range(10):
            self._update(d*0.1)

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        if self.hitdir != None:
            c=crange(0, self.deadtimer, self.cooldown, 1, 0)
            glColor4f(0.0, 1.0*c, 1.0*c, crange(2, self.deadtimer, 3, 1, 0))
            glBegin(GL_QUADS)
            if self.hitdir == "x":
                glTexCoord2f(0, 0)
                glVertex3f(self.x, self.y-0.1, self.z-0.1)
                glTexCoord2f(0, 1)
                glVertex3f(self.x, self.y-0.1, self.z+0.1)
                glTexCoord2f(1, 1)
                glVertex3f(self.x, self.y+0.1, self.z+0.1)
                glTexCoord2f(1, 0)
                glVertex3f(self.x, self.y+0.1, self.z-0.1)
            elif self.hitdir == "y":
                glTexCoord2f(0, 0)
                glVertex3f(self.x-0.1, self.y, self.z-0.1)
                glTexCoord2f(0, 1)
                glVertex3f(self.x-0.1, self.y, self.z+0.1)
                glTexCoord2f(1, 1)
                glVertex3f(self.x+0.1, self.y, self.z+0.1)
                glTexCoord2f(1, 0)
                glVertex3f(self.x+0.1, self.y, self.z-0.1)
            elif self.hitdir == "z":
                glTexCoord2f(0, 0)
                glVertex3f(self.x-0.1, self.y-0.1, self.z)
                glTexCoord2f(0, 1)
                glVertex3f(self.x+0.1, self.y-0.1, self.z)
                glTexCoord2f(1, 1)
                glVertex3f(self.x+0.1, self.y+0.1, self.z)
                glTexCoord2f(1, 0)
                glVertex3f(self.x-0.1, self.y+0.1, self.z)
            glEnd()
        glDisable(GL_TEXTURE_2D)

        if self.length < 0:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(-self.r[1], 0, 0, 1)
        glRotatef(-self.r[0], 1, 0, 0)
        glRotatef(self.spin+self.time*self.spinspeed, 0, 1, 0)
        glScalef(self.scale, self.length, self.scale)

        glBegin(GL_LINES)

        glColor4f(0.0, 1.0, 1.0, 1.0)
        glVertex3f(0, 0, 0)
        glColor4f(0.0, 1.0, 1.0, 0.0)
        glVertex3f(0, -1, 0)

        # glColor4f(0.0, 1.0, 1.0, 1.0)
        # glVertex3f(0.06, 0, 0)
        # glColor4f(0.0, 1.0, 1.0, 0.0)
        # glVertex3f(0, -1, 0)

        # glColor4f(0.0, 1.0, 1.0, 1.0)
        # glVertex3f(-0.06, 0, 0)
        # glColor4f(0.0, 1.0, 1.0, 0.0)
        # glVertex3f(0, -1, 0)

        # glColor4f(0.0, 1.0, 1.0, 1.0)
        # glVertex3f(0, 0, 0.06)
        # glColor4f(0.0, 1.0, 1.0, 0.0)
        # glVertex3f(0, -1, 0)

        # glColor4f(0.0, 1.0, 1.0, 1.0)
        # glVertex3f(0, 0, -0.06)
        # glColor4f(0.0, 1.0, 1.0, 0.0)
        # glVertex3f(0, -1, 0)

        glEnd()

        glPopMatrix()

def draw_cube(x, y, z, w, h, d, tex=None, scale=0.5, col=[1.0, 1.0, 1.0, 1.0]):
    t=["wall01", "wall01", "wall01", "wall01", "floor01", "ceil01"]

    # tex: string or list
    # list: [all sides], [top/bottom, sides], [top, bottom, sides], [+x, -x, +y, -y, +z, -z]

    if type(tex) == list:
        if len(tex) == 1:
            t[0]=tex[0]
            t[1]=tex[0]
            t[2]=tex[0]
            t[3]=tex[0]
            t[4]=tex[0]
            t[5]=tex[0]
        elif len(tex) == 2:
            t[0]=tex[1]
            t[1]=tex[1]
            t[2]=tex[1]
            t[3]=tex[1]
            t[4]=tex[0]
            t[5]=tex[0]
        elif len(tex) == 3:
            t[0]=tex[2]
            t[1]=tex[2]
            t[2]=tex[2]
            t[3]=tex[2]
            t[4]=tex[1]
            t[5]=tex[0]
        elif len(tex) == 6:
            t=tex[:]
    elif type(tex) == str:
        t=[tex, tex, tex, tex, tex, tex]

    def texCoord2f(x, y):
        glTexCoord2f(x*scale, y*scale)

    texture.bind(t[0])
    glBegin(GL_QUADS)

    glColor4f(*[i*0.6 for i in col[:3]]+[col[3]])

    texCoord2f(y, z)
    glVertex3f(x+w, y, z)
    texCoord2f(y+h, z)
    glVertex3f(x+w, y+h, z)
    texCoord2f(y+h, z+d)
    glVertex3f(x+w, y+h, z+d)
    texCoord2f(y, z+d)
    glVertex3f(x+w, y, z+d)

    glEnd()
    texture.bind(t[1])
    glBegin(GL_QUADS)

    glColor4f(*[i*0.8 for i in col[:3]]+[col[3]])

    texCoord2f(y+h, z)
    glVertex3f(x, y+h, z)
    texCoord2f(y, z)
    glVertex3f(x, y, z)
    texCoord2f(y, z+d)
    glVertex3f(x, y, z+d)
    texCoord2f(y+h, z+d)
    glVertex3f(x, y+h, z+d)

    glEnd()
    texture.bind(t[2])
    glBegin(GL_QUADS)

    glColor4f(*[i*0.6 for i in col[:3]]+[col[3]])

    texCoord2f(x, z)
    glVertex3f(x, y+h, z)
    texCoord2f(x, z+d)
    glVertex3f(x, y+h, z+d)
    texCoord2f(x+w, z+d)
    glVertex3f(x+w, y+h, z+d)
    texCoord2f(x+w, z)
    glVertex3f(x+w, y+h, z)

    glEnd()
    texture.bind(t[3])
    glBegin(GL_QUADS)

    glColor4f(*[i*0.8 for i in col[:3]]+[col[3]])

    texCoord2f(x+w, z)
    glVertex3f(x+w, y, z)
    texCoord2f(x+w, z+d)
    glVertex3f(x+w, y, z+d)
    texCoord2f(x, z+d)
    glVertex3f(x, y, z+d)
    texCoord2f(x, z)
    glVertex3f(x, y, z)

    glEnd()
    texture.bind(t[4])
    glBegin(GL_QUADS)

    glColor4f(*col)

    texCoord2f(x, y)
    glVertex3f(x, y, z+d)
    texCoord2f(x+w, y)
    glVertex3f(x+w, y, z+d)
    texCoord2f(x+w, y+h)
    glVertex3f(x+w, y+h, z+d)
    texCoord2f(x, y+h)
    glVertex3f(x, y+h, z+d)

    glEnd()
    texture.bind(t[5])
    glBegin(GL_QUADS)

    glColor4f(*[i*0.5 for i in col[:3]]+[col[3]])

    texCoord2f(x, y+h)
    glVertex3f(x, y+h, z)
    texCoord2f(x+w, y+h)
    glVertex3f(x+w, y+h, z)
    texCoord2f(x+w, y)
    glVertex3f(x+w, y, z)
    texCoord2f(x, y)
    glVertex3f(x, y, z)

    glEnd()

def draw_cube_scaled(x, y, z, w, h, d, tex=None, col=[1.0, 1.0, 1.0]):
    t=["blank", "blank", "blank", "blank", "blank", "blank"]

    # tex: string or list
    # list: [all sides], [top/bottom, sides], [top, bottom, sides], [+x, -x, +y, -y, +z, -z]

    if type(tex) == list:
        if len(tex) == 1:
            t[0]=tex[0]
            t[1]=tex[0]
            t[2]=tex[0]
            t[3]=tex[0]
            t[4]=tex[0]
            t[5]=tex[0]
        elif len(tex) == 2:
            t[0]=tex[1]
            t[1]=tex[1]
            t[2]=tex[1]
            t[3]=tex[1]
            t[4]=tex[0]
            t[5]=tex[0]
        elif len(tex) == 3:
            t[0]=tex[2]
            t[1]=tex[2]
            t[2]=tex[2]
            t[3]=tex[2]
            t[4]=tex[1]
            t[5]=tex[0]
        elif len(tex) == 6:
            t=tex[:]
    elif type(tex) == str:
        t=[tex, tex, tex, tex, tex, tex]

    glColor3f(*col)

    texture.bind(t[0])
    glBegin(GL_QUADS)

    glTexCoord2f(1, 1)
    glVertex3f(x+w, y, z)
    glTexCoord2f(0, 1)
    glVertex3f(x+w, y+h, z)
    glTexCoord2f(0, 0)
    glVertex3f(x+w, y+h, z+d)
    glTexCoord2f(1, 0)
    glVertex3f(x+w, y, z+d)

    glEnd()
    texture.bind(t[1])
    glBegin(GL_QUADS)

    glTexCoord2f(1, 1)
    glVertex3f(x, y+h, z)
    glTexCoord2f(0, 1)
    glVertex3f(x, y, z)
    glTexCoord2f(0, 0)
    glVertex3f(x, y, z+d)
    glTexCoord2f(1, 0)
    glVertex3f(x, y+h, z+d)

    glEnd()
    texture.bind(t[2])
    glBegin(GL_QUADS)

    glTexCoord2f(0, 1)
    glVertex3f(x, y+h, z)
    glTexCoord2f(0, 0)
    glVertex3f(x, y+h, z+d)
    glTexCoord2f(1, 0)
    glVertex3f(x+w, y+h, z+d)
    glTexCoord2f(1, 1)
    glVertex3f(x+w, y+h, z)

    glEnd()
    texture.bind(t[3])
    glBegin(GL_QUADS)

    glTexCoord2f(0, 1)
    glVertex3f(x+w, y, z)
    glTexCoord2f(0, 0)
    glVertex3f(x+w, y, z+d)
    glTexCoord2f(1, 0)
    glVertex3f(x, y, z+d)
    glTexCoord2f(1, 1)
    glVertex3f(x, y, z)

    glEnd()
    texture.bind(t[4])
    glBegin(GL_QUADS)

    glTexCoord2f(0, 1)
    glVertex3f(x, y, z+d)
    glTexCoord2f(0, 0)
    glVertex3f(x+w, y, z+d)
    glTexCoord2f(1, 0)
    glVertex3f(x+w, y+h, z+d)
    glTexCoord2f(1, 1)
    glVertex3f(x, y+h, z+d)

    glEnd()
    texture.bind(t[5])
    glBegin(GL_QUADS)

    glTexCoord2f(1, 0)
    glVertex3f(x, y+h, z)
    glTexCoord2f(1, 1)
    glVertex3f(x+w, y+h, z)
    glTexCoord2f(0, 1)
    glVertex3f(x+w, y, z)
    glTexCoord2f(0, 0)
    glVertex3f(x, y, z)

    glEnd()

class World:
    def __init__(self, entities, mdls):
        self.entities=entities
        self.mdls=mdls

        self.bullets=[]

        self.time=0
        self.cache=None
        
        self.collision=[]
        for c in entities:
            if c[0] in ["glasscube", "cube"]:
                if c[10]:
                    self.collision.append(c)
            elif c[0] == "jumppad":
                self.collision.append(c)


    def precache(self):
        for c in self.entities:
            if c[0] in ["cube", "glasscube"]:
                if c[7]:
                    texture.precache(c[7])

    def draw(self):
        glEnable(GL_CULL_FACE)
        glEnable(GL_TEXTURE_2D)

        if not self.cache:
            self.cache=glGenLists(1)

            glNewList(self.cache, GL_COMPILE)

            for mdl in self.mdls:
                glPushMatrix()

                glTranslatef(mdl[0], mdl[1], mdl[2])
                glRotatef(mdl[3], 0, 0, 1)

                model.draw(mdl[4], {}, mm=True, gl_list=False)

                glPopMatrix()

            for e in self.entities:
                if e[0] == "cube" and e[9]:
                    draw_cube(
                        e[1], e[2], e[3],
                        e[4], e[5], e[6],
                        e[7], e[8]
                        )
                elif e[0] == "glasscube" and e[9]:
                    glDepthMask(False)
                    draw_cube(
                        e[1], e[2], e[3],
                        e[4], e[5], e[6],
                        e[7], e[8], [1.0, 1.0, 1.0, 0.5]
                        )
                    glDepthMask(True)

            glEndList()

        glCallList(self.cache)

        glDisable(GL_CULL_FACE)
        texture.bind("bullethole")
        glDepthMask(False)
        for b in self.bullets:
            b.draw()
        glDepthMask(True)
        glEnable(GL_CULL_FACE)

    def spawn_bullet(self, b):
        self.bullets.append(b)

    def update(self, d):
        self.time+=d
        for b in self.bullets:
            b.update(d)

        for b in self.bullets:
            if b.remove:
                self.bullets.remove(b)

    def hit(self, box):
        out=[]
        for c in self.collision:
            if in_box_3d(c[1:], box):
                out.append(c)
        return out

player=None
world=None

def init_player():
    global player
    player=Player()
    return player

def load_world(name):
    path=resource.path("map", name)

    f=open(path, "r")

    data=f.read()
    f.close()

    data=data.split("\n")

    entities=[]
    mdls=[]

    for line in data:
        while " \t" in line:
            line=line.replace("\t", " ")
        while "  " in line:
            line=line.replace("  ", " ")

        line=line.replace(" ", "")
        
        line=line.split(",")

        if line == []: continue
        
        if line[0] == "jumppad" and len(line) >= 10:
            line[1]=float(line[1])
            line[2]=float(line[2])
            line[3]=float(line[3])
            line[4]=float(line[4])
            line[5]=float(line[5])
            line[6]=float(line[6])
            line[7]=float(line[7])
            line[8]=float(line[8])
            line[9]=float(line[9])

            entities.append([
                    "jumppad",
                    line[1], line[2], line[3],
                    line[4], line[5], line[6],
                    line[7], line[8], line[9]])
        elif line[0] in ["glasscube", "physcube", "gfxcube", "cube"] and len(line) >= 7:
            line[1]=float(line[1])
            line[2]=float(line[2])
            line[3]=float(line[3])
            line[4]=float(line[4])
            line[5]=float(line[5])
            line[6]=float(line[6])

            tex=None
            scale=0.5
            gfx=True
            phys=True

            if len(line) >= 8:
                try:
                    scale=float(line[7])
                except:
                    tex=line[7]

            if len(line) >= 9:
                tex=line[8]

            name="cube"

            if line[0] == "physcube":
                gfx=False
            elif line[0] == "gfxcube":
                phys=False
            elif line[0] == "glasscube":
                name="glasscube"

            entities.append([name, line[1], line[2], line[3], line[4], line[5], line[6], tex, scale, gfx, phys])
        elif line[0] == "model" and len(line) >= 6:
            line[1]=float(line[1])
            line[2]=float(line[2])
            line[3]=float(line[3])
            line[4]=float(line[4])
            
            mdl=line[5]

            mdls.append([line[1], line[2], line[3], line[4], mdl])

    entities.sort(lambda a, b: cmp(a[0], b[0]))

    return World(entities, mdls)

def init_world():
    global world
    world=load_world("debug")
    return world
