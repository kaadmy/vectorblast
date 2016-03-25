import math

PI=math.pi
TWO_PI=math.pi*2
HALF_PI=math.pi*0.5
SIN_CACHE={}

def in_box(a, b):
    if b[0] < a[0]+a[2] and b[0]+b[2] > a[0]:
        if b[1] < a[1]+a[3] and b[1]+b[3] > a[1]:
            return True

def in_box_3d(a, b):
    if b[2] < a[2]+a[5] and b[2]+b[5] > a[2]:
        if b[0] < a[0]+a[3] and b[0]+b[3] > a[0]:
            if b[1] < a[1]+a[4] and b[1]+b[4] > a[1]:
                return True

def radians(a):
    return math.radians(a)

def degrees(a):
    return math.degrees(a)

def clamp(a, n, b):
    a, b=sorted([a, b])
    if n < a: return a
    if n > b: return b
    return n

def within(a, n, b):
    if n < a: return False
    if n > b: return False
    return True

def trange(il,i,ih,ol,oh):
    return ol+(oh-ol)*(i-il)/(ih-il)

def crange(il,i,ih,ol,oh):
    return clamp(ol,ol+(oh-ol)*(i-il)/(ih-il),oh)

def srange(il, i, ih, ol, oh):
    return trange(1, math.cos(crange(il, i, ih, 0, math.pi)), -1, ol, oh)

def lerp(a, b, n):
    return a+((b-a)*n)

def lerpcolor(a, b, n):
    out=[]
    for i in range(len(a)):
        out.append(a[i]+((b[i]-a[i])*n))
    return out

def sin(n):
    n=round(n, 2)
    if(n in SIN_CACHE):
        return SIN_CACHE[n]
    SIN_CACHE[n]=math.sin(n)
    return SIN_CACHE[n]

def cos(n):
    return sin(n+HALF_PI)

def dist(x1, y1, x2, y2):
    return math.hypot(x1-x2, y1-y2)

def rotate(pt, ang):
    s, c=sin(ang), cos(ang)
    
    return [pt[0]*c-pt[1]*s, pt[1]*c+pt[0]*s]

def angle(x1, y1, x2, y2):
    return math.atan2(y1-y2, x1-x2)

class Lowpass:
    def __init__(self, value, mixin):
        self.value=value
        self.mixin=mixin
        self.target=value
    
    def update(self, d, value=None):
        if value == None:
            value=self.target
        self.value=lerp(self.value, value, clamp(0, self.mixin*d, 1))
        return self.value
