#!/usr/bin/env python3
"""Build the release zip: the three MSE packages, the sample set and INSTRUCTIONS.md, all at the top level.

    python3 mse/tools/make_release.py [output.zip]

The default output is mse/dist/mood-swings-mse.zip. The release workflow (.github/workflows/release.yml)
runs this and attaches the zip to a GitHub release.
"""
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
MSE = os.path.dirname(HERE)
ITEMS = ["mood-swings.mse-game", "mood-swings-edition1.mse-style", "mood-swings-dice.mse-symbol-font",
         "examples", "INSTRUCTIONS.md"]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(MSE, "dist", "mood-swings-mse.zip")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for item in ITEMS:
            src = os.path.join(MSE, item)
            if os.path.isfile(src):
                z.write(src, item)
                continue
            for folder, _, files in os.walk(src):
                for name in sorted(files):
                    full = os.path.join(folder, name)
                    z.write(full, os.path.relpath(full, MSE))
    print("wrote", out)


if __name__ == "__main__":
    main()
