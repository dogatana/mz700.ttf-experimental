"""紅茶羊羹氏のページからディスプレイコードとユニコードとのマップを取得する"""

import io
import json
import re
import sys


def main():
    with open("page.html", encoding="utf-8") as fp:
        text = fp.read()

    codes = re.findall(r"<td>.*?u\+([0-9a-fA-F]+)\s*</td>", text, flags=re.IGNORECASE)

    if len(codes) != 256:
        print("** the number of definitios should be 512", len(codes))

    # change stdout encoding to utf-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    map = {}
    used = set()
    print("# ATB=0")
    print_plane(0, map, used, codes[:256])
    print()
    print("# ATB=1")
    print_plane(1, map, used, codes[256:])

    with open("map.json", "w") as fp:
        json.dump(map, fp)


def print_plane(atb, map, used, codes):
    for hi in range(16):
        for lo in range(16):
            value = int(codes[lo * 16 + hi], 16)
            char = f"\\u{value:04x}".encode().decode("unicode-escape")
            print(f"U+{value:04X} # {hi * 16 + lo:02x} {char}", end="")
            if value in used:
                print(" used")
            else:
                map[hi * 16 + lo + atb * 256] = value
                print()
            used.add(value)


main()
