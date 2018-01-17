#!/usr/bin/env python3
"""
This script takes a list of makefiles as argument and prints help texts
for each target found.

Any comments on the first lines of a target are considered documentation
for the target.

With the following Makefile:

help:
    @# Print help text
    @./make-help.py $(MAKEFILE_LIST)

mytarget:
    @# Description of this target
    @# and the args used.
    do_stuff

Running:

$ make help

Would yield the following output:

help        Print help text
mytarget    Description of this target
            and the args used
"""
import sys
import re


def main():
    if len(sys.argv) < 2:
        print('Usage: {}: $(MAKEFILE_LIST)'.format(sys.argv[0]))

    makefiles = sys.argv[1:]

    for makefile in makefiles:
        print_help(makefile)


def print_help(makefile):
    with open(makefile, 'r') as f:
        states = parse_makefile(f)

    targets = [state for state in states
               if type(state) is StateTargetDefinition]
    col_width = max(len(t.name) for t in targets) + 2
    for target in sorted(targets, key=lambda t: t.name):
        print(target.format(col_width))


def parse_makefile(makefile):
    states = []
    curr_state = StateNoTarget()

    for line in makefile:
        next_state = curr_state.next(line)
        if next_state is not curr_state:
            states.append(next_state)
        curr_state = next_state

    return states


class StateNoTarget:
    """Indicates that the parser isn't at a line that indicates anything
    interesting with the regards to targets"""

    def next(self, line):
        """Parse the line and change the parser's state if necessary"""
        target_def = parse_target_def(line)
        if target_def:
            return StateTargetDefinition(target_def)

        return self


class StateTargetDefinition:
    """Indicates that the parser has found a target definition and possibly
    it's descriptive comments"""
    def __init__(self, name):
        self.name = name
        self.comments = []

    def next(self, line):
        """Parse the line and change the parser's state if necessary"""
        target_def = parse_target_def(line)
        if target_def == self.name:
            return self

        if target_def:
            return StateTargetDefinition(target_def)

        comment = parse_comment(line)
        if comment:
            self.comments.append(comment)
            return self

        return StateNoTarget()

    def format(self, col_width):
        return ('{}{}'.format(self.name.ljust(col_width),
                              self.format_comments(col_width)))

    def format_comments(self, col_width):
        if self.comments:
            return '\n{}'.format(''.ljust(col_width)).join(self.comments)
        else:
            return ' <no description>'


def parse_target_def(line):
    match = re.match(r'^([\w-]+):', line)
    if match:
        return match.group(1)


def parse_comment(line):
    match = re.match(r'\s*@?#(.*)', line)
    if match:
        return match.group(1)


if __name__ == '__main__':
    sys.exit(main())
