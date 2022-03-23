# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2019 Intel Corporation.  All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#

"""
Download the repo of WAMR from Github. The script will `git checkout` to the
latest commit ID of the main branch unless it receives a specific ID from the
command line.
"""

import argparse
import os
import pathlib
import shlex
import subprocess
import sys


def clone(workplace):
    """
    $ git clone https://github.com/bytecodealliance/wasm-micro-runtime.git
    $ #or
    $ git fetch origin && git checkout main && git reset --hard origin/main

    Suppose the source code will not be modified
    """
    WAMR_DIR = workplace.joinpath("wasm-micro-runtime").resolve()
    if WAMR_DIR.exists():
        CMDS = ["git fetch origin", "git checkout main", "git reset --hard origin/main"]
        for cmd in CMDS:
            subprocess.check_output(shlex.split(cmd), cwd=WAMR_DIR)
    else:
        CMD = "git clone https://github.com/bytecodealliance/wasm-micro-runtime.git"
        subprocess.check_output(shlex.split(CMD), cwd=workplace)


def checkout(workplace, commit_id=None):
    """
    $ git checkout -b commit_id commit_id
    """
    if not commit_id:
        return

    WAMR_DIR = workplace.joinpath("wasm-micro-runtime").resolve()

    cmd = f"git branch --list {commit_id}"
    if subprocess.check_output(shlex.split(cmd), cwd=WAMR_DIR):
        return

    cmd = f"git checkout -b {commit_id} {commit_id}"
    subprocess.check_output(shlex.split(cmd), cwd=WAMR_DIR)


def main():
    parser = argparse.ArgumentParser(
        description="download wasm-micro-runtime from github"
    )
    parser.add_argument(
        "--commit",
        type=str,
        default="",
        help="identify a specific commit id to checkout, or use the latest commit on main branch",
    )
    options = parser.parse_args()
    print(f"options={options}")

    current_file = pathlib.Path(__file__)
    if current_file.is_symlink():
        current_file = pathlib.Path(os.readlink(current_file))

    current_dir = current_file.parent.resolve()
    root_dir = current_dir.joinpath("..").resolve()

    try:
        clone(root_dir)
        checkout(root_dir, options.commit)
        return True
    except subprocess.CalledProcessError:
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
