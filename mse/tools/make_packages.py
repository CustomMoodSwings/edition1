#!/usr/bin/env python3
"""Zip the three Magic Set Editor packages into mse/dist/ so they can be double-clicked or dropped
into MSE's data folder. A zipped package needs its data file (game, style or symbol-font) at the top
of the zip, so the zip is built from inside each package folder.

    python3 mse/tools/make_packages.py
"""
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
MSE = os.path.dirname(HERE)
DIST = os.path.join(MSE, "dist")
PACKAGES = ["mood-swings.mse-game", "mood-swings-edition1.mse-style", "mood-swings-dice.mse-symbol-font"]
SAMPLES = ["examples/edition1-sample.mse-set"]


def zip_package(rel):
    src = os.path.join(MSE, rel)
    out = os.path.join(DIST, os.path.basename(rel))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, _, files in os.walk(src):
            for name in sorted(files):
                full = os.path.join(folder, name)
                z.write(full, os.path.relpath(full, src))
    print("wrote", os.path.relpath(out, MSE))


def main():
    os.makedirs(DIST, exist_ok=True)
    for rel in PACKAGES + SAMPLES:
        zip_package(rel)


if __name__ == "__main__":
    main()
