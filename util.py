import configparser
from os import path
from pathlib import Path
import os
import shutil
import stat


def read_config(cfg_files):
    if cfg_files is not None:
        config = configparser.RawConfigParser()

        # merges all files into a single config
        for i, cfg_file in enumerate(cfg_files):
            if path.exists(cfg_file):
                config.read(cfg_file)

        return config


def get_project_root() -> Path:
    return Path(__file__).parent


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
