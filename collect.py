#!/usr/bin/env python3

import os
import sys
import string
from shutil import copy2
from argparse import ArgumentParser, Namespace
from collections import deque, OrderedDict
from pathlib import Path

from json import dumps as _dump_json
dump_json = lambda d: _dump_json(d, sort_keys=True)

try:
    from yaml import load as _load, CLoader
    load = lambda f: _load(f, Loader=CLoader)
except ImportError:
    from yaml import load


BASE = Path(__file__).resolve().parent
CONF = BASE / 'config.yml'


def exit(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def warning(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    print("Warning:", msg)


def stdout_debug(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    print(msg)

def noop(*args, **kwargs):
    pass

debug = stdout_debug


def load_config():
    if not CONF.exists():
        raise RuntimeError("Configuration {} doesn't exist".format(CONF))

    with CONF.open() as f:
        conf = load(f)

    config = Namespace(
        destination_fn = conf['destination'],
        template = BASE / conf['template'],
        placeholder = conf['placeholder'],
        line_template = conf['line_template'],
        default_test = conf['default_test'],
        copy_files = [],
    )

    if not config.template.exists():
        raise RuntimeError("Template {} doesn't exist".format(config.template))

    for copy in conf.get('copy', []):
        src = Path(copy['source'])
        config.copy_files.append((src, copy['files']))

    return config


class PathIterator:
    @classmethod
    def wrap(cls, func):
        def wrapped(*args, **kwargs):
            return cls(func(*args, **kwargs))
        return wrapped

    def __init__(self, it):
        self._iter = it

    def __iter__(self):
        return self._iter

    def matching(self, test):
        return self.__class__(x for x in self._iter if x.match(test))


@PathIterator.wrap
def traverse(path, max_depth=0):
    todo = deque()
    todo.append((0, path))
    while todo:
        depth, current = todo.popleft()
        for child in current.iterdir():
            if child.is_dir():
                if not max_depth or depth < max_depth:
                    todo.append((depth + 1, child))
            else:
                yield child


def collect(config):
    src = config.source
    dst = config.destination_file
    placeholder = config.placeholder
    line_fmt = config.line_template

    if config.usedir:
        get_name = lambda f: f.parent.name.split('.', 1)[0]
    else:
        get_name = lambda f: f.name.split('.', 1)[0]

    # clean invalid names
    map_from = " "
    map_to = "_"
    valid = set(ord(x) for x in string.ascii_letters+map_from+map_to)
    nonvalid = "".join(chr(x) for x in range(255) if x not in valid)
    replace_table = str.maketrans(map_from, map_to, nonvalid)
    clean_name = lambda fn: fn.translate(replace_table)

    collected = OrderedDict()

    for file_ in traverse(src, config.depth).matching(config.test):
        with file_.open() as f:
            raw_name = get_name(file_)
            name = clean_name(raw_name)
            if raw_name != name:
                warning("collected file had name {!r}, but it was renamed to {!r}", raw_name, name)
            if name in collected:
                warning("multiple definitions for name {!r}", name)
            collected[name] = load(f)
            debug("Included {} from {}", name, file_)

    with config.template.open() as f:
        template = f.readlines()

    with dst.open('w') as f:
        for line in template:
            s = line.find(placeholder)
            if s < 0:
                f.write(line)
            else:
                prefix = line[:s]
                for name, data in collected.items():
                    f.write(line_fmt.format(prefix=prefix, name=name, data=dump_json(data)))

    debug("Destination {} created with {} entries.", dst, len(collected))


def copy(config):
    dst_base = config.destination

    all_files = []
    for src, files in config.copy_files:
        if not src.exists():
            raise RuntimeError("Expected data path {} is missing.".format(src))

        for fn in files:
            path = src / fn
            if path.is_dir():
                for fpath in traverse(path):
                    all_files.append((fpath, dst_base / fpath.relative_to(src)))
            else:
                all_files.append((path, dst_base / fn))

    for src, dst in all_files:
        if not dst.parent.exists():
            os.makedirs(str(dst.parent))
        dste = dst.exists()
        src_s, dst_s = str(src), str(dst)
        if not dste or os.path.getmtime(src_s) > os.path.getmtime(dst_s):
            if dste:
                dst.unlink()
            copy2(src_s, dst_s)
            debug("Copied {} -> {}", src, dst)


def main():
    parser = ArgumentParser()

    parser.add_argument('destination',
        help="Destination path within build directory. Collected files will be merged using template into a file in this path. Configured extra files will be copied into this path too.")
    parser.add_argument('--source', '-s',
        help="Source path to be searched")
    parser.add_argument('--test', '-t',
        help="Test path against pattern (e.g. *.custom.json)")
    parser.add_argument('--name-from-dir', dest='usedir', action='store_true',
        help="By default, we take the name from the filename, but it this flag is true, then we use the name of the directory.")
    parser.add_argument("--search-depth", dest='depth', type=int, default=3,
        help="Maximum search depth")
    parser.add_argument('--silent', '-q', action="store_true",
        help="Do not print info")
    parser.add_argument('--force', '-f', action="store_true",
        help="Overwrite existing destination")

    config = load_config()
    parser.set_defaults(test=config.default_test)

    config = parser.parse_args(namespace=config)
    config.destination = Path('build/') / Path(config.destination)
    config.destination_file = config.destination / config.destination_fn
    if config.source:
        config.source = Path('src/') / config.source
    else:
        config.source = Path('src/')

    if config.silent:
        global debug
        debug = noop

    if not config.source.exists() or not config.source.is_dir():
        exit("Source {} doesn't exist or isn't a directory".format(config.source))

    if config.destination_file.exists() and not config.force:
        exit("Destination {} exists.".format(config.destination_file))

    if not config.destination.exists():
        os.makedirs(str(config.destination))

    collect(config)
    copy(config)


if __name__ == '__main__':
    main()
