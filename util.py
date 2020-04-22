import configparser
from os import path


def read_config(cfg_files):
    if cfg_files is not None:
        config = configparser.RawConfigParser()

        # merges all files into a single config
        for i, cfg_file in enumerate(cfg_files):
            if path.exists(cfg_file):
                config.read(cfg_file)

        return config
