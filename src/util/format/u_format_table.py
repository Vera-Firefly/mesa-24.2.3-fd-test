CopyRight = '''
/**************************************************************************
 *
 * Copyright 2010 VMware, Inc.
 * All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sub license, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice (including the
 * next paragraph) shall be included in all copies or substantial portions
 * of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
 * IN NO EVENT SHALL VMWARE AND/OR ITS SUPPLIERS BE LIABLE FOR
 * ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 **************************************************************************/
'''


import sys, os

from u_format_parse import *
import u_format_pack


def layout_map(layout):
    return 'UTIL_FORMAT_LAYOUT_' + str(layout).upper()


def colorspace_map(colorspace):
    return 'UTIL_FORMAT_COLORSPACE_' + str(colorspace).upper()

colorspace_channels_map = {
    'RGB': ['r', 'g', 'b', 'a'],
    'SRGB': ['sr', 'sg', 'sb', 'a'],
    'ZS': ['z', 's'],
    'YUV': ['y', 'u', 'v'],
}


type_map = {
    VOID:     "UTIL_FORMAT_TYPE_VOID",
    UNSIGNED: "UTIL_FORMAT_TYPE_UNSIGNED",
    SIGNED:   "UTIL_FORMAT_TYPE_SIGNED",
    FIXED:    "UTIL_FORMAT_TYPE_FIXED",
    FLOAT:    "UTIL_FORMAT_TYPE_FLOAT",
}


def bool_map(value):
    if value:
        return "true"
    else:
        return "false"


swizzle_map = {
    SWIZZLE_X:    "PIPE_SWIZZLE_X",
    SWIZZLE_Y:    "PIPE_SWIZZLE_Y",
    SWIZZLE_Z:    "PIPE_SWIZZLE_Z",
    SWIZZLE_W:    "PIPE_SWIZZLE_W",
    SWIZZLE_0:    "PIPE_SWIZZLE_0",
    SWIZZLE_1:    "PIPE_SWIZZLE_1",
    SWIZZLE_NONE: "PIPE_SWIZZLE_NONE",
}

def has_access(format):
    # We don't generate code for YUV formats, and many of the new ones lack
    # pack/unpack functions for softpipe/llvmpipe.
    noaccess_formats = [
        'r1_unorm',
        'yv12',
        'yv16',
        'iyuv',
        'nv12',
        'nv16',
        'nv21',
        'p010',
        'p012',
        'p016',
        'p030',
        'y210',
        'y212',
        'y216',
        'y410',
        'y412',
        'y416',
        'xyuv',
        'ayuv',
        'r8g8_r8b8_unorm',
        'r8b8_r8g8_unorm',
        'g8r8_b8r8_unorm',
        'b8r8_g8r8_unorm',
        'g8r8_g8b8_unorm',
        'g8b8_g8r8_unorm',
        'b8g8_r8g8_unorm',
        'y8_400_unorm',
        'y8_u8_v8_422_unorm',
        'y8_u8v8_422_unorm',
        'y8_u8_v8_444_unorm',
        'y8_u8_v8_440_unorm',
        'y16_u16_v16_420_unorm',
        'y16_u16_v16_422_unorm',
        'y16_u16v16_422_unorm',
        'y16_u16_v16_444_unorm',
        'r8_g8b8_420_unorm',
        'r8_b8g8_420_unorm',
        'g8_b8r8_420_unorm',
        'r8_g8_b8_420_unorm',
        'r8_b8_g8_420_unorm',
        'g8_b8_r8_420_unorm',
        'r8_g8_b8_unorm',
        'y8_unorm',
    ]
    if format.short_name() in noaccess_formats:
        return False
    if format.layout in ('astc', 'atc'):
        return False
    if format.layout == 'etc' and format.short_name() != 'etc1_rgb8':
        return False
    return True

def write_format_table_header(file):
    print('/* This file is autogenerated by u_format_table.py from u_format.yaml. Do not edit directly. */', file=file)
    print(file=file)
    # This will print the copyright message on the top of this file
    print(CopyRight.strip(), file=file)
    print(file=file)

def write_format_aliases(formats):
    print("#if UTIL_ARCH_LITTLE_ENDIAN", file=sys.stdout3)
    for f in formats:
        if f.le_alias:
            print("#define %s %s" % (f.le_alias, f.name), file=sys.stdout3)
    print("#elif UTIL_ARCH_BIG_ENDIAN", file=sys.stdout3)
    for f in formats:
        if f.be_alias:
            print("#define %s %s" % (f.be_alias, f.name), file=sys.stdout3)
    print("#endif", file=sys.stdout3)


def write_format_table(formats):
    write_format_table_header(sys.stdout)
    print('#include "util/format/u_format.h"')
    print('#include "u_format_bptc.h"')
    print('#include "u_format_fxt1.h"')
    print('#include "u_format_s3tc.h"')
    print('#include "u_format_rgtc.h"')
    print('#include "u_format_latc.h"')
    print('#include "u_format_etc.h"')
    print()

    write_format_table_header(sys.stdout2)

    print('#ifdef __cplusplus', file=sys.stdout2)
    print('extern "C" {', file=sys.stdout2)
    print('#endif', file=sys.stdout2)
    print('#include "util/format/u_format.h"', file=sys.stdout2)
    print(file=sys.stdout2)

    u_format_pack.generate(formats)

    print('#ifdef __cplusplus', file=sys.stdout2)
    print('} /* extern "C" */', file=sys.stdout2)
    print('#endif', file=sys.stdout2)


    write_format_table_header(sys.stdout3)

    print('#ifdef __cplusplus', file=sys.stdout3)
    print('extern "C" {', file=sys.stdout3)
    print('#endif', file=sys.stdout3)
    print(file=sys.stdout3)

    write_format_aliases(formats)

    print('#ifdef __cplusplus', file=sys.stdout3)
    print('} /* extern "C" */', file=sys.stdout3)
    print('#endif', file=sys.stdout3)

    def do_channel_array(channels, swizzles):
        print("   {")
        for i in range(4):
            channel = channels[i]
            if i < 3:
                sep = ","
            else:
                sep = ""
            if channel.size:
                print("      {%s, %s, %s, %u, %u}%s\t/* %s = %s */" % (type_map[channel.type], bool_map(channel.norm), bool_map(channel.pure), channel.size, channel.shift, sep, "xyzw"[i], channel.name))
            else:
                print("      {0, 0, 0, 0, 0}%s" % (sep,))
        print("   },")

    def do_swizzle_array(channels, swizzles):
        print("   {")
        for i in range(4):
            swizzle = swizzles[i]
            if i < 3:
                sep = ","
            else:
                sep = ""
            try:
                comment = colorspace_channels_map[format.colorspace][i]
            except (KeyError, IndexError):
                comment = 'ignored'
            print("      %s%s\t/* %s */" % (swizzle_map[swizzle], sep, comment))
        print("   },")

    def generate_table_getter(type):
        suffix = ""
        if type == "unpack_":
            suffix = "_generic"
        print("ATTRIBUTE_RETURNS_NONNULL const struct util_format_%sdescription *" % type)
        print("util_format_%sdescription%s(enum pipe_format format)" % (type, suffix))
        print("{")
        print("   assert(format < PIPE_FORMAT_COUNT);")
        print("   return &util_format_%sdescriptions[format];" % (type))
        print("}")
        print()

    def generate_function_getter(func):
        print("util_format_%s_func_ptr" % func)
        print("util_format_%s_func(enum pipe_format format)" % (func))
        print("{")
        print("   assert(format < PIPE_FORMAT_COUNT);")
        print("   return util_format_%s_table[format];" % (func))
        print("}")
        print()

    print('static const struct util_format_description')
    print('util_format_descriptions[PIPE_FORMAT_COUNT] = {')
    for format in formats:
        sn = format.short_name()

        print("   [%s] = {" % (format.name,))
        print("      .format = %s," % (format.name,))
        print("      .name = \"%s\"," % (format.name,))
        print("      .short_name = \"%s\"," % (sn,))
        print("      .block = {%u, %u, %u, %u},\t/* block */" % (format.block_width, format.block_height, format.block_depth, format.block_size()))
        print("      .layout = %s," % (layout_map(format.layout),))
        print("      .nr_channels = %u,\t/* nr_channels */" % (format.nr_channels(),))
        print("      .is_array = %s,\t/* is_array */" % (bool_map(format.is_array()),))
        print("      .is_bitmask = %s,\t/* is_bitmask */" % (bool_map(format.is_bitmask()),))
        print("      .is_mixed = %s,\t/* is_mixed */" % (bool_map(format.is_mixed()),))
        print("      .is_unorm = %s,\t/* is_unorm */" % (bool_map(format.is_unorm()),))
        print("      .is_snorm = %s,\t/* is_snorm */" % (bool_map(format.is_snorm()),))
        u_format_pack.print_channels(format, do_channel_array)
        u_format_pack.print_channels(format, do_swizzle_array)
        print("      .colorspace = %s," % (colorspace_map(format.colorspace),))
        if format.srgb_equivalent:
            print("      .srgb_equivalent = %s,\t/* srgb_equivalent */" % format.srgb_equivalent.name)
        elif format.linear_equivalent:
            print("      .linear_equivalent = %s,\t/* linear_equivalent */" % format.linear_equivalent.name)
        else:
            print("      .srgb_equivalent = PIPE_FORMAT_NONE,\t/* srgb_equivalent */")
        print("   },")
        print()
    print("};")
    print()
    generate_table_getter("")

    print('static const struct util_format_pack_description')
    print('util_format_pack_descriptions[PIPE_FORMAT_COUNT] = {')
    for format in formats:
        sn = format.short_name()

        if not has_access(format):
            print("   [%s] = { 0 }," % (format.name,))
            continue

        print("   [%s] = {" % (format.name,))
        if format.colorspace != ZS and not format.is_pure_color():
            print("      .pack_rgba_8unorm = &util_format_%s_pack_rgba_8unorm," % sn)
            print("      .pack_rgba_float = &util_format_%s_pack_rgba_float," % sn)

        if format.has_depth():
            print("      .pack_z_32unorm = &util_format_%s_pack_z_32unorm," % sn)
            print("      .pack_z_float = &util_format_%s_pack_z_float," % sn)

        if format.has_stencil():
            print("      .pack_s_8uint = &util_format_%s_pack_s_8uint," % sn)

        if format.is_pure_unsigned() or format.is_pure_signed():
            print("      .pack_rgba_uint = &util_format_%s_pack_unsigned," % sn)
            print("      .pack_rgba_sint = &util_format_%s_pack_signed," % sn)
        print("   },")
        print()
    print("};")
    print()
    generate_table_getter("pack_")
    print('static const struct util_format_unpack_description')
    print('util_format_unpack_descriptions[PIPE_FORMAT_COUNT] = {')
    for format in formats:
        sn = format.short_name()

        if not has_access(format):
            print("   [%s] = { 0 }," % (format.name,))
            continue

        print("   [%s] = {" % (format.name,))

        if format.colorspace != ZS and not format.is_pure_color():
            if format.layout == 's3tc' or format.layout == 'rgtc':
                print("      .fetch_rgba_8unorm = &util_format_%s_fetch_rgba_8unorm," % sn)
            if format.block_width > 1:
                print(
                    "      .unpack_rgba_8unorm_rect = &util_format_%s_unpack_rgba_8unorm," % sn)
                print(
                    "      .unpack_rgba_rect = &util_format_%s_unpack_rgba_float," % sn)
            else:
                print(
                    "      .unpack_rgba_8unorm = &util_format_%s_unpack_rgba_8unorm," % sn)
                print("      .unpack_rgba = &util_format_%s_unpack_rgba_float," % sn)

        if format.has_depth():
            print("      .unpack_z_32unorm = &util_format_%s_unpack_z_32unorm," % sn)
            print("      .unpack_z_float = &util_format_%s_unpack_z_float," % sn)

        if format.has_stencil():
            print("      .unpack_s_8uint = &util_format_%s_unpack_s_8uint," % sn)

        if format.is_pure_unsigned():
            print("      .unpack_rgba = &util_format_%s_unpack_unsigned," % sn)
        elif format.is_pure_signed():
            print("      .unpack_rgba = &util_format_%s_unpack_signed," % sn)
        print("   },")
    print("};")
    print()

    generate_table_getter("unpack_")

    print('static const util_format_fetch_rgba_func_ptr util_format_fetch_rgba_table[PIPE_FORMAT_COUNT] = {')
    for format in formats:
        sn = format.short_name()

        if format.colorspace != ZS and has_access(format):
            print("  [%s] = &util_format_%s_fetch_rgba," % (format.name, sn))
        else:
            print("  [%s] = NULL," % format.name)

    print("};")
    print()

    generate_function_getter("fetch_rgba")

def main():
    formats = {}

    sys.stdout2 = open(os.devnull, "w")
    sys.stdout3 = open(os.devnull, "w")

    for arg in sys.argv[1:]:
        if arg == '--header':
            sys.stdout2 = sys.stdout
            sys.stdout = open(os.devnull, "w")
            sys.stdout3 = sys.stdout
            continue
        elif arg == '--enums':
            sys.stdout3 = sys.stdout
            sys.stdout = open(os.devnull, "w")
            sys.stdout2 = sys.stdout
            continue

        to_add = parse(arg)
        duplicates = [x.name for x in to_add if x.name in formats]
        if len(duplicates):
            raise RuntimeError(f"Duplicate format entries {', '.join(duplicates)}")
        formats.update({ x.name: x for x in to_add })

    write_format_table(formats.values())

if __name__ == '__main__':
    main()
