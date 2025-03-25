import json
import os.path
import sys
from argparse import ArgumentParser

BDF_HEADER = """STARTFONT 2.1
FONT -mz700-Fixed-Medium-R-Normal--8-80-75-75-M-80-ISO10646-1
SIZE 8 75 75
FONTBOUNDINGBOX 8 8 0 0
STARTPROPERTIES 21
FACE_NAME "mz700"
FONT_VERSION "1.0"
FONT_ASCENT 8
FONT_DESCENT 0
DEFAULT_CHAR 32
COPYRIGHT ""
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
