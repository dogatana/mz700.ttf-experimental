import json
import os.path
import sys
from argparse import ArgumentParser

BDF_HEADER = """STARTFONT 2.1
FONT -mz700-Fixed-Medium-R-Normal--8-80-75-75-M-80-ISO10646-1
COMMENT 
COMMENT This fils is based on MZ700FON.JP that is included in mz700win release file
COMMENT 
COMMENT Following is the content of mz700win.txt
COMMENT ---------------------------------------------------------------------------------
COMMENT mz700win - an MZ-700 emulator 'mz700win.exe' for Win32 version 0.53 (maintenance)
COMMENT 
COMMENT (C) 1998-2000 Takeshi Maruyama (marukun)
COMMENT I can't write English well. Please forgive me my poor English.
COMMENT 
COMMENT mz700win by Takeshi Maruyama, based on Russell Marks's 'mz700em'.
COMMENT MZ700 emulator 'mz700em' for VGA PCs running Linux (C) 1996 Russell Marks.
COMMENT 
COMMENT In Primary version, I ported Linux version to Win32 directly. But it was slow.
COMMENT This version of MZ700WIN was rewritten newly by me.
COMMENT 
COMMENT Z80 emulation from 'Z80em' Copyright (C) Marcel de Kogel 1996,1997
COMMENT ---------------------------------------------------------------------------------
COMMENT * CG-ROM             MZ700FON.DAT or MZ700FON.JP (4096bytes)
COMMENT 
COMMENT 'MZ700FON.DAT' is the image file of Character-ROM.
COMMENT In order to get it, You can use the tool called 'mkfnt.exe' and
COMMENT Its data file.
COMMENT 
COMMENT This data file 'MZ700FON.JP' is the character font data. This is not from
COMMENT the MZ700, but put together by hand.
COMMENT It is Japanese font file.
COMMENT
SIZE 8 75 75
FONTBOUNDINGBOX 8 8 0 0
STARTPROPERTIES 21
FACE_NAME "mz700"
FONT_VERSION "1.0"
FONT_ASCENT 8
FONT_DESCENT 0
DEFAULT_CHAR 32
COPYRIGHT "Copyright (C) Takeshi Maruyama (marukun)"
FONTNAME_REGISTRY ""
FOUNDRY ""
FAMILY_NAME "mz700"
WEIGHT_NAME "Medium"
SLANT "R"
SETWIDTH_NAME "Normal"
ADD_STYLE_NAME ""
PIXEL_SIZE 8
POINT_SIZE 8
RESOLUTION_X 75
RESOLUTION_Y 75
SPACING "M"
AVERAGE_WIDTH 8
CHARSET_REGISTRY "ISO10646"
CHARSET_ENCODING "1"
ENDPROPERTIES
"""


def main(args):
    map = load_map(args.MAP)
    chars = load_font(args.FONT)

    font_data = {}
    for code, bits in enumerate(chars):
        if code in map:
            font_data[map[code]] = bits

    with open(args.BDF, "w") as fp:
        write_bdf(fp, font_data)


def load_map(file):
    with open(file) as fp:
        map = json.load(fp)
    return {int(k): v for k, v in map.items()}


def load_font(file):
    chars = []
    with open(file, "rb") as fp:
        for _ in range(512):
            chars.append(fp.read(8))
    return chars


def write_bdf(fp, font_data):
    print(BDF_HEADER, file=fp)
    print(f"CHARS {len(font_data)}", file=fp)

    for code in sorted(font_data.keys()):
        print(
            "\n".join(
                [
                    f"STARTCHAR u+{code:04x}",
                    f"ENCODING {code}",
                    "SWIDTH 500 0",
                    "DWIDTH 8 0",
                    "BBX 8 8 0 0",
                    "BITMAP",
                ]
            ),
            file=fp,
        )
        for b in font_data[code]:
            print(f"{b:02x}", file=fp)
        print("ENDCHAR", file=fp)

    print("ENDFONT", file=fp)


def check_duped(chars):
    for i in range(len(chars) - 1):
        char = chars[i]
        print(f"{i:03x}", end="")
        if char is None:
            print(" # used")
            continue
        print()
        for j in range(i + 1, len(chars)):
            if char == chars[j]:
                chars[j] = None
    print(f"{len(chars) - 1: 03x}", end="")
    if chars[-1] is None:
        print(" # used")
    else:
        print()
    print("duped", len([char for char in chars if char is None]))


def parse_args():
    parser = ArgumentParser(description="build BDF from FONT and MAP")
    parser.add_argument("FONT", help="input font file")
    parser.add_argument("MAP", help="code mapping json file")
    parser.add_argument("BDF", help="output bdf file")
    parser.add_argument("--name", "-n", help="font name. default basename of FONT)")
    args = parser.parse_args(sys.argv[1:])

    if not os.path.isfile(args.FONT):
        print("**", args.FONT, "not found")
        exit()
    if not os.path.isfile(args.MAP):
        print("**", args.MAP, "not found")
        exit()
    if args.name is None:
        args.name, _ = os.path.splitext(os.path.basename(args.BDF))
    return args


if __name__ == "__main__":
    args = parse_args()
    print(args)
    main(args)
