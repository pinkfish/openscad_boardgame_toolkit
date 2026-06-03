from os import path
from hyperpack import HyperPack
import re
import argparse

pattern_single = re.compile(
    r"([A-Za-z0-9_]+) = object\(width=([0-9.]+), length=([0-9.]+)\);", re.IGNORECASE
)
pattern_num = re.compile(
    r"([A-Za-z0-9_]+) = object\(width=([0-9.]+), length=([0-9.]+), num=([0-9]+)\);",
    re.IGNORECASE,
)

pattern_spacing = re.compile(r"\/\/ spacing = ([0-9.]+)")
pattern_container = re.compile(
    r"\/\/ container\(width = ([0-9.]+), length = ([0-9.]+)\)"
)


def ReadItemsFromOpenScad(filename: str) -> dict:
    with open(filename, "r") as file:
        items = {}
        container = {}
        metadata = {}
        spacing = 0
        for line in file:
            match = pattern_spacing.match(line)
            if match:
                spacing = float(match.group(1))
            match_container = pattern_container.match(line)
            if match_container:
                metadata["container" + str(len(container))] = {"spacing": spacing * 10}
                container["container" + str(len(container))] = {
                    "W": int((float(match_container.group(1)) - spacing) * 10),
                    "L": int((float(match_container.group(2)) - spacing) * 10),
                }
            match = pattern_single.match(line)
            if match:
                items[match.group(1)] = {
                    "w": int((float(match.group(2)) + spacing / 2) * 10),
                    "l": int((float(match.group(3)) + spacing / 2) * 10),
                }
                metadata[match.group(1)] = {
                    "spacing": spacing * 10,
                    "num": 1,
                    "w": float(match.group(2)) * 10,
                    "l": float(match.group(3)) * 10,
                }
            match_num = pattern_num.match(line)
            if match_num:
                items[match_num.group(1)] = {
                    "w": int((float(match_num.group(2)) + spacing / 2) * 10),
                    "l": int(
                        (
                            float(match_num.group(3))
                            * (int(match_num.group(4)) + spacing / 2)
                        )
                        * 10
                    ),
                }
                metadata[match_num.group(1)] = {
                    "spacing": spacing * 10,
                    "num": int(match_num.group(4)),
                    "w": float(match_num.group(2)) * 10,
                    "l": float(match_num.group(3)) * 10,
                    "ltotal": items[match_num.group(1)]["l"],
                }
        return items, container, metadata
    return {}


def RunBinpack(items: dict, containers: dict):
    settings = {"rotation": True}
    problem = HyperPack(containers=containers, items=items, settings=settings)
    problem.hypersearch()
    print(problem.log_solution())
    # problem.create_figure()
    return problem.solution


def CreateOpenScadLayout(fname: str, solution: dict, metadata: dict):
    with open(fname, "w") as file:
        for c_name, container in solution.items():
            spacing = metadata[c_name]["spacing"]
            print("module Layout_" + c_name + "(height) {", file=file)
            for name, item in container.items():
                print(
                    "    back("
                    + str(item[1] / 10 + spacing / 20 + item[3] / 20)
                    + ") right("
                    + str(item[0] / 10 + spacing / 20 + item[2] / 20)
                    + ") {",
                    file=file,
                )
                if metadata[name]["num"] > 1:
                    for i in range(metadata[name]["num"]):
                        if item[2] == metadata[name]["ltotal"]:
                            print(
                                "       right("
                                + str(
                                    (i - metadata[name]["num"] / 2 + 0.5)
                                    * (
                                        (
                                            metadata[name]["l"]
                                            + metadata[name]["spacing"]
                                        )
                                        / 10
                                    )
                                )
                                + ")",
                                file=file,
                            )
                            print(
                                "         cuboid(["
                                + str(metadata[name]["l"] / 10)
                                + ", "
                                + str(metadata[name]["w"] / 10)
                                + ", height],",
                                file=file,
                            )
                        else:
                            print(
                                "       back("
                                + str(
                                    (i - metadata[name]["num"] / 2 + 0.5)
                                    * (
                                        (
                                            metadata[name]["l"]
                                            + metadata[name]["spacing"]
                                        )
                                        / 10
                                    )
                                )
                                + ")",
                                file=file,
                            )
                            print(
                                "         cuboid(["
                                + str(metadata[name]["w"] / 10)
                                + ", "
                                + str(metadata[name]["l"] / 10)
                                + ", height],",
                                file=file,
                            )
                        print("        rounding=1,", file=file)
                        print(
                            "        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],",
                            file=file,
                        )
                        print("        anchor=BOTTOM);", file=file)
                else:
                    print(
                        "       cuboid(["
                        + str(item[2] / 10 - spacing / 10)
                        + ", "
                        + str(item[3] / 10 - spacing / 10)
                        + ", height],",
                        file=file,
                    )
                    print("        rounding=1,", file=file)
                    print(
                        "        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],",
                        file=file,
                    )
                    print("        anchor=BOTTOM);", file=file)
                print("    }", file=file)
            print("}", file=file)
            # Make a module to make text for the spot.
            print("module Layout_Text_" + c_name + "(height, max_size=15) {", file=file)
            for name, item in container.items():
                print(
                    "    back("
                    + str(item[1] / 10 + spacing / 20 + item[3] / 20)
                    + ") right("
                    + str(item[0] / 10 + spacing / 20 + item[2] / 20)
                    + ") {",
                    file=file,
                )
                if metadata[name]["num"] > 1:
                    for i in range(metadata[name]["num"]):
                        if item[2] == metadata[name]["ltotal"]:
                            print(
                                "       right("
                                + str(
                                    (i - metadata[name]["num"] / 2 + 0.5)
                                    * (
                                        (
                                            metadata[name]["l"]
                                            + metadata[name]["spacing"]
                                        )
                                        / 10
                                    )
                                )
                                + ")",
                                file=file,
                            )
                            print(
                                "         linear_extrude(h=height) resize(["
                                + "min(max_size, "
                                + str(metadata[name]["l"] / 10)
                                + '), 0], auto=true) text("'
                                + name.replace("_", " ").title()
                                + '", valign="center", halign="center");',
                                file=file,
                            )
                        else:
                            print(
                                "       back("
                                + str(
                                    (i - metadata[name]["num"] / 2 + 0.5)
                                    * (
                                        (
                                            metadata[name]["l"]
                                            + metadata[name]["spacing"]
                                        )
                                        / 10
                                    )
                                )
                                + ")",
                                file=file,
                            )
                            print(
                                "         linear_extrude(h=height) resize([0, "
                                + "min(max_size, "
                                + str(metadata[name]["l"] / 10)
                                + ')], auto=true) rotate(90) text("'
                                + name.replace("_", " ").title()
                                + '", valign="center", halign="center");',
                                file=file,
                            )
                else:
                    if item[2] > item[3]:
                        print(
                            "         linear_extrude(h=height) resize([min(max_size, "
                            + str((item[2] - metadata[name]["spacing"]) / 10)
                            + '), 0], auto=true) text("'
                            + name.replace("_", " ").title()
                            + '", valign="center", halign="center");',
                            file=file,
                        )
                    else:
                        print(
                            "         linear_extrude(h=height) resize([0, "
                            + "min(max_size, "
                            + str((item[3] - metadata[name]["spacing"]) / 10)
                            + ')], auto=true) rotate(90) text("'
                            + name.replace("_", " ").title()
                            + '", valign="center", halign="center");',
                            file=file,
                        )
                print("    }", file=file)
            print("}", file=file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run binpack algorithm on items from an OpenSCAD file."
    )
    parser.add_argument(
        "-i",
        "--items",
        type=str,
        required=True,
        help="Path to OpenSCAD file containing items.",
    )
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="Path to output file."
    )
    args = parser.parse_args()
    items, containers, metadata = ReadItemsFromOpenScad(args.items)
    solution = RunBinpack(items, containers)
    CreateOpenScadLayout(args.output, solution, metadata)
