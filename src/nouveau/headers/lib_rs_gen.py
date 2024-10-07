#! /usr/bin/env python3
#
# Copyright © 2024 Collabora Ltd. and Red Hat Inc.
# SPDX-License-Identifier: MIT

# This script takes a list of Rust files, each of the form nvh_path_to_mod.rs
# and constructs a lib.rs which puts each of them in ::path::to::mod.

import argparse
import os.path
import re
import sys

from mako.template import Template

TEMPLATE_RS = Template("""\
// Copyright © 2024 Collabora Ltd. and Red Hat Inc.
// SPDX-License-Identifier: MIT

// This file is generated by lib_rs_gen.py. DO NOT EDIT!

#![allow(unused_imports)]

<%def name="import_mod(m, path)">
% if m.present:
mod nvh_${'_'.join(path)};
% endif
% for name in sorted(m.children):
${import_mod(m.children[name], path + [name])}
% endfor
</%def>
${import_mod(root, [])}

<%def name="decl_mod(m, path)">
% if path:
pub mod ${path[-1]} {
% endif

% if m.present:
pub use crate::nvh_${'_'.join(path)}::*;
% endif

% for name in sorted(m.children):
${decl_mod(m.children[name], path + [name])}
% endfor

% if path:
}
% endif
</%def>
${decl_mod(root, [])}
""")

class Mod(object):
    def __init__(self):
        self.present = False;
        self.children = {}

    def add_child(self, path):
        mod = self
        for p in path:
            if p not in mod.children:
                mod.children[p] = Mod()
            mod = mod.children[p]

        # Once we've found the child, mark it present
        assert not mod.present
        mod.present = True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-rs', required=True, help='Output Rust file.')
    parser.add_argument('class_files', metavar='FILE', nargs='*',
                        action='append',
                        help='Input class Rust filename')
    args = parser.parse_args()

    root = Mod()
    for f in args.class_files[0]:
        f = os.path.basename(f)
        assert f.endswith('.rs')
        f = f.removesuffix('.rs')

        mod_path = f.split('_')
        assert mod_path[0] == 'nvh'
        root.add_child(mod_path[1:])

    try:
        with open(args.out_rs, 'w', encoding='utf-8') as f:
            f.write(TEMPLATE_RS.render(root=root))

    except Exception:
        # In the event there's an error, this imports some helpers from mako
        # to print a useful stack trace and prints it, then exits with
        # status 1, if python is run with debug; otherwise it just raises
        # the exception
        import sys
        from mako import exceptions
        print(exceptions.text_error_template().render(), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
