import cPickle
import os

options={}
binds={}

config_enable=False # enabling has problems with persistence
config_path=".vectorblast"

def add_bind(key, action):
    binds[key]=action

def remove(key):
    del binds[key]

def get_bind(key):
    return binds.get(key, None)

def get_key(action):
    out=[]
    for b in binds:
        if binds[b] == action:
            out.append(b)
    return out

def get_string():
    out=""
    for opt in options:
        out+=opt+" "+str(options[opt])
        out+="\n"
    for b in binds:
        bind=binds[b]
        out+="bind "+str(b)+" "+bind+"\n"
    return out

def from_string(s):
    s=s.split("\n")
    for opt in s:
        opt=opt.strip()
        if opt == "":
            continue
        opt=opt.split(" ", 1)
        if opt[0] == "bind":
            key, action=opt[1].split(" ")
            binds[key]=action
        else:
            options[opt[0]]=opt[1]

def get(name, type_):
    try:
        val=type_(options[name])
    except:
        val=type_()
    return val

def set(name, value, important):
    if important or options.get(name) == None:
        options[name]=value

def save():
    if config_enable:
        f=open(os.path.join(os.path.expanduser("~"), config_path), "w")
        f.write(get_string())
        f.close()

def load():
    global options
    
    if config_enable:
        try:
            f=open(os.path.join(os.path.expanduser("~"), config_path), "r")
        except:
            return True
        from_string(f.read())
        f.close()
    else:
        return True
