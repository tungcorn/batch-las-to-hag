# -*- coding: utf-8 -*-
"""
Batch convert .LAS -> HAG (Height Above Ground) .LAS using PDAL.

Default pipeline per file (for input LAS that does NOT already have ground classification):
  readers.las -> filters.smrf (ground classification)
               -> filters.hag_delaunay (compute HAG)
               -> writers.las (with extra_dims HeightAboveGround=float32)

If --no-smrf is used, the tool skips ground re-classification and computes HAG
from the existing Classification values in the input LAS.

Requires: pdal (pip install pdal) or pdal CLI on PATH.

Usage:
  python batch_las_to_hag.py -i "E:\\input" -o "E:\\output"
  python batch_las_to_hag.py -i "E:\\input" -r
  python batch_las_to_hag.py -b batch.txt --skip-existing
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _pdal_available():
    try:
        import pdal  # noqa: F401

        return True
    except ImportError:
        return False


def _pdal_cli_available():
    try:
        subprocess.run(
            ["pdal", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def build_pipeline_json(input_path, output_path, skip_smrf=False):
    pipeline = [
        {"type": "readers.las", "filename": str(input_path)},
    ]
    if not skip_smrf:
        pipeline.append(
            {"type": "filters.smrf", "returns": "first,intermediate,last,only"}
        )
    pipeline.append({"type": "filters.hag_delaunay"})
    pipeline.append(
        {
            "type": "writers.las",
            "filename": str(output_path),
            "extra_dims": "HeightAboveGround=float32",
        },
    )
    return json.dumps(pipeline, indent=2)


def convert_one_file_python(input_path, output_path, skip_smrf):
    import pdal

    pipeline_json = build_pipeline_json(input_path, output_path, skip_smrf)
    pipeline = pdal.Pipeline(pipeline_json)
    count = pipeline.execute()
    return count


def convert_one_file_cli(input_path, output_path, skip_smrf):
    pipeline_json = build_pipeline_json(input_path, output_path, skip_smrf)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(pipeline_json)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["pdal", "pipeline", tmp_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"pdal pipeline failed (exit {result.returncode}): {result.stderr.strip()}"
            )
    finally:
        os.unlink(tmp_path)


def convert_one_file(input_path, output_path, use_python_bindings, skip_smrf):
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not input_path.exists():
            print(f"  SKIP: file not found {input_path}")
            return False

        file_size = input_path.stat().st_size
        if file_size == 0:
            print(f"  SKIP: empty file {input_path.name}")
            return False

        if use_python_bindings:
            count = convert_one_file_python(input_path, output_path, skip_smrf)
            out_size_mb = output_path.stat().st_size / 1024 / 1024
            print(
                f"  OK: {input_path.name} -> {output_path.name} ({count:,} pts, {out_size_mb:.1f} MB)"
            )
        else:
            convert_one_file_cli(input_path, output_path, skip_smrf)
            out_size_mb = output_path.stat().st_size / 1024 / 1024
            print(
                f"  OK: {input_path.name} -> {output_path.name} ({out_size_mb:.1f} MB)"
            )

        return True

    except Exception as e:
        print(f"  ERROR: {input_path.name}: {e}")
        if output_path.exists():
            try:
                output_path.unlink()
            except OSError:
                pass
        return False


def _resolve_output_path(las_path, input_root, output_root, recursive):
    hag_name = las_path.stem + "_hag" + las_path.suffix
    if recursive:
        rel = las_path.relative_to(input_root)
        return output_root / rel.parent / hag_name
    return output_root / hag_name


def parse_batch_file(batch_path):
    pairs = []
    with open(batch_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "->" not in line:
                print(f"WARNING: line {line_num} skipped (no '->'): {line}")
                continue
            parts = line.split("->", 1)
            input_dir = parts[0].strip().strip('"')
            output_dir = parts[1].strip().strip('"')
            if not input_dir or not output_dir:
                print(f"WARNING: line {line_num} skipped (empty path): {line}")
                continue
            pairs.append((Path(input_dir), Path(output_dir)))
    return pairs


def batch_convert(
    input_path, output_path, recursive, skip_existing, use_python_bindings, skip_smrf
):
    if not input_path.is_dir():
        print(f"ERROR: Input directory not found: {input_path}")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    if recursive:
        las_files = sorted(input_path.rglob("*.las"))
        las_upper = sorted(f for f in input_path.rglob("*.LAS") if f not in las_files)
        las_files.extend(las_upper)
    else:
        las_files = sorted(
            f for f in input_path.iterdir() if f.suffix.lower() == ".las"
        )

    if not las_files:
        print(f"No .las files found in {input_path}")
        return 0, 0

    print(f"Found {len(las_files)} .las file(s)")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    if recursive:
        print("Mode: recursive (directory structure mirrored)")
    if skip_smrf:
        print(
            "Mode: --no-smrf (skip ground classification, use existing classification; input must already have valid ground class)"
        )
    print()

    start = time.time()
    ok = 0
    fail = 0
    skipped = 0

    for i, f in enumerate(las_files, 1):
        out_path = _resolve_output_path(f, input_path, output_path, recursive)
        rel = f.relative_to(input_path) if recursive else f.name
        print(f"[{i}/{len(las_files)}] {rel}")

        if skip_existing and out_path.exists() and out_path.stat().st_size > 0:
            print(f"  SKIP (already exists): {out_path.name}")
            skipped += 1
            continue

        if convert_one_file(f, out_path, use_python_bindings, skip_smrf):
            ok += 1
        else:
            fail += 1

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s: {ok} converted, {fail} failed, {skipped} skipped")
    return ok, fail


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert .LAS files to HAG (Height Above Ground) .LAS using PDAL. Default mode runs SMRF first; use --no-smrf only when input LAS already has valid ground classification."
    )
    parser.add_argument(
        "-i", "--input", default=None, help="Input directory containing .las files"
    )
    parser.add_argument(
        "-o", "--output", default=None, help="Output directory for HAG .las files"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search subdirectories for .las files",
    )
    parser.add_argument(
        "-b",
        "--batch",
        default=None,
        metavar="FILE",
        help="Text file with 'input_dir -> output_dir' pairs, one per line",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already have a non-empty .las output",
    )
    parser.add_argument(
        "--no-smrf",
        action="store_true",
        help="Skip ground classification and use existing Classification to compute HAG (use ONLY when input already has valid ground classification)",
    )
    args = parser.parse_args()

    has_single_mode = args.input is not None
    has_batch_mode = args.batch is not None

    if not has_single_mode and not has_batch_mode:
        print("ERROR: Specify -i <input_dir> or -b <batch_file>")
        sys.exit(1)

    if has_single_mode and not args.output:
        if args.recursive:
            inp = Path(args.input)
            args.output = str(inp.parent / (inp.name + "_hag"))
            print(f"Auto output: {args.output}")
        else:
            print("ERROR: With -i, specify -o <output_dir> or use -r (auto output)")
            sys.exit(1)

    use_python = _pdal_available()
    use_cli = _pdal_cli_available()

    if not use_python and not use_cli:
        print("ERROR: PDAL not found.")
        print("  Install Python bindings: pip install pdal")
        print("  Or install PDAL CLI: https://pdal.io/en/latest/download.html")
        sys.exit(1)

    if use_python:
        print("PDAL backend: Python bindings")
    else:
        print("PDAL backend: CLI subprocess")
    print()

    if has_batch_mode:
        pairs = parse_batch_file(args.batch)
        if not pairs:
            print(f"ERROR: No valid pairs found in {args.batch}")
            sys.exit(1)
        print(f"Batch file: {args.batch} ({len(pairs)} pairs)\n")
        total_ok = 0
        total_fail = 0
        for idx, (inp, outp) in enumerate(pairs, 1):
            print(f"{'=' * 60}")
            print(f"Pair {idx}/{len(pairs)}: {inp} -> {outp}")
            print(f"{'=' * 60}")
            ok, fail = batch_convert(
                inp,
                outp,
                recursive=False,
                skip_existing=args.skip_existing,
                use_python_bindings=use_python,
                skip_smrf=args.no_smrf,
            )
            total_ok += ok
            total_fail += fail
        print(f"\n{'=' * 60}")
        print(
            f"ALL DONE: {total_ok} converted, {total_fail} failed across {len(pairs)} pairs"
        )
    else:
        batch_convert(
            Path(args.input),
            Path(args.output),
            args.recursive,
            args.skip_existing,
            use_python,
            args.no_smrf,
        )


if __name__ == "__main__":
    main()
