#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser
from collections import deque, OrderedDict
from json import dumps as dump_json
from pathlib import Path

try:
    from yaml import load as _load, CLoader
    load = lambda f: _load(f, Loader=CLoader)
except ImportError:
    from yaml import load


BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "template.js"
PLACEHOLDER = "@@ANIMATIONS@"
LINE_FMT = "{prefix}JSVEE.animations['{name}'] = {data};\n"

assert TEMPLATE.exists(), "Internal template is not accessible!"


def exit(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def stdout_debug(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    print(msg)

def noop_debug(*args, **kwargs):
    pass


def traverse(path, test, max_depth=3):
    todo = deque()
    todo.append((0, path))
    while todo:
        depth, current = todo.popleft()
        for child in current.iterdir():
            if child.is_dir():
                if depth < max_depth:
                    todo.append((depth + 1, child))
            elif child.match(test):
                yield child


def collect(args):
    debug = noop_debug if args.silent else stdout_debug

    source = Path(args.source) if args.source else Path.cwd()
    if not source.exists() or not source.is_dir():
        exit("Source {} doesn't exist or isn't a directory".format(source))
    
    dest = Path(args.destination)
    if dest.exists() and not args.force:
        exit("Destination {} exists.".format(dest))

    animations = OrderedDict()
    for file_ in traverse(source, args.test, args.depth):
        with file_.open() as f:
            data = load(f)
            name = file_.name if not args.usedir else file_.parent.name
            basename = name.split('.', 1)[0].replace("'", "")
            animations[basename] = data
            debug("Found animation: {}", name)

    with TEMPLATE.open() as f:
        template = f.readlines()

    os.makedirs(str(dest.parent))
    with dest.open('w') as f:
        for line in template:
            s = line.find(PLACEHOLDER)
            if s < 0:
                f.write(line)
                continue

            prefix = line[:s]
            for name, data in animations.items():
                f.write(LINE_FMT.format(prefix=prefix, name=name, data=dump_json(data)))

    debug("Animations script written to: {}", dest)


def main():
    parser = ArgumentParser()

    parser.add_argument('destination')
    parser.add_argument('--source', '-s',
        help="Source path to be searched")
    parser.add_argument('--test', '-t',
        default="*.animation",
        help="Test path against pattern (e.g. *.animation/*.json)")
    parser.add_argument('--name-from-dir', dest='usedir', action='store_true',
        help="Bt default, we take the animation name from the filename, but it this flag is true, then we use the name of the directory.")
    parser.add_argument("--search-depth", dest='depth', type=int, default=3,
        help="Maximum search depth")
    parser.add_argument('--silent', '-q', action="store_true",
        help="Do not print info")
    parser.add_argument('--force', '-f', action="store_true",
        help="Overwrite existing destination")

    collect(parser.parse_args())


if __name__ == '__main__':
    main()
