import os

paths={
    "base": [
        [".", "data"],
        ],
    "map": [["maps"]],
    "image": [["textures"], ["textures", "skydome"]],
    "model": [["models"]],
    "mapmodel": [["models", "mapmodels"]],
    "sound": [["sounds"]],
    }

suffix={
    "map": [".cmap"],
    "image": [".png", ".jpg", ".gif"], 
    "model": [".smf"],
    "mapmodel": [".smf"],
    "sound": [".wav", ".ogg"],
    }

def get_paths(type_, file_):
    out=[]
    for basepath in paths["base"]:
        for path in paths[type_]:
            for suf in suffix[type_]:
                out.append(os.path.join(*(basepath+path+[file_+suf])))
    return out

def path(type_, file_):
    valid=get_paths(type_, file_)
    for path in valid:
        if os.path.exists(path):
            return path
    raise ValueError, "%s with type %s does not exist, checked\n\t%s" % (file_, type_, "\n\t".join(valid))
