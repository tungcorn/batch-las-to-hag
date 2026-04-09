# -*- coding: utf-8 -*-
r"""
Batch ground classification using CSF (Cloth Simulation Filter).

Output: each input LAS -> new LAS with Classification reassigned
by CSF (ground=2, non-ground=0).

Requires: pip install laspy cloth-simulation-filter

Usage:
  python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf"
  python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r
  python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r --cloth-resolution 1.0 --rigidness 3
"""

import argparse
import sys
import time
from pathlib import Path

import laspy
import numpy as np

try:
    import CSF
except ImportError:
    print("ERROR: Missing 'CSF' package. Install: pip install cloth-simulation-filter")
    sys.exit(1)


def classify_ground_csf(
    input_path,
    output_path,
    cloth_resolution=2.0,
    rigidness=2,
    slope_smooth=True,
    class_threshold=0.5,
):
    """Run CSF on a single LAS file, write new LAS with ground classification."""
    las = laspy.read(str(input_path))

    xyz = np.column_stack((np.asarray(las.x), np.asarray(las.y), np.asarray(las.z)))

    csf = CSF.CSF()
    csf.setPointCloud(xyz)
    csf.params.bSloopSmooth = slope_smooth
    csf.params.cloth_resolution = cloth_resolution
    csf.params.rigidness = rigidness
    csf.params.class_threshold = class_threshold

    ground = CSF.VecInt()
    non_ground = CSF.VecInt()
    csf.do_filtering(ground, non_ground)

    classification = np.zeros(len(xyz), dtype=np.uint8)
    classification[list(ground)] = 2  # ground = class 2

    las.classification = classification

    output_path.parent.mkdir(parents=True, exist_ok=True)
    las.write(str(output_path))

    return len(las.x), len(ground)


def main():
    parser = argparse.ArgumentParser(
        description="Batch ground classification using CSF (Cloth Simulation Filter)"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Input directory containing .las files"
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output directory for CSF classified .las files",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search subdirectories for .las files",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already have a non-empty output",
    )
    parser.add_argument(
        "--cloth-resolution",
        type=float,
        default=2.0,
        help="CSF cloth resolution (default: 2.0). Smaller = more detail",
    )
    parser.add_argument(
        "--rigidness",
        type=int,
        default=2,
        choices=[1, 2, 3],
        help="CSF rigidness 1=mountain, 2=complex, 3=flat (default: 2)",
    )
    parser.add_argument(
        "--slope-smooth",
        action="store_true",
        default=True,
        help="Enable slope post-processing (default: True)",
    )
    parser.add_argument(
        "--no-slope-smooth", action="store_true", help="Disable slope post-processing"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="CSF class threshold (default: 0.5). Distance to cloth for ground/non-ground classification",
    )
    args = parser.parse_args()

    slope_smooth = not args.no_slope_smooth

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.is_dir():
        print(f"ERROR: Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.recursive:
        las_files = sorted(input_dir.rglob("*.las"))
        las_upper = sorted(f for f in input_dir.rglob("*.LAS") if f not in las_files)
        las_files.extend(las_upper)
    else:
        las_files = sorted(f for f in input_dir.iterdir() if f.suffix.lower() == ".las")

    if not las_files:
        print(f"No .las files found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(las_files)} .las file(s)")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print(
        f"CSF params: cloth_resolution={args.cloth_resolution}, rigidness={args.rigidness}, slope_smooth={slope_smooth}, threshold={args.threshold}"
    )
    if args.recursive:
        print("Mode: recursive")
    print()

    start = time.time()
    ok = 0
    fail = 0
    skipped = 0

    for i, f in enumerate(las_files, 1):
        if args.recursive:
            rel = f.relative_to(input_dir)
            out_path = output_dir / rel.parent / (f.stem + "_csf" + f.suffix)
        else:
            out_path = output_dir / (f.stem + "_csf" + f.suffix)

        rel_name = f.relative_to(input_dir) if args.recursive else f.name
        print(f"[{i}/{len(las_files)}] {rel_name}")

        if args.skip_existing and out_path.exists() and out_path.stat().st_size > 0:
            print(f"  SKIP (already exists): {out_path.name}")
            skipped += 1
            continue

        try:
            total_pts, ground_pts = classify_ground_csf(
                f,
                out_path,
                cloth_resolution=args.cloth_resolution,
                rigidness=args.rigidness,
                slope_smooth=slope_smooth,
                class_threshold=args.threshold,
            )
            pct = ground_pts / total_pts * 100 if total_pts > 0 else 0
            print(f"  OK: {total_pts:,} pts, ground: {ground_pts:,} ({pct:.1f}%)")
            ok += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            fail += 1

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s: {ok} converted, {fail} failed, {skipped} skipped")


if __name__ == "__main__":
    main()
