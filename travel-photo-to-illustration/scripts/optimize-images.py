#!/usr/bin/env python3
"""Resize/encode approved images; never perform generative visual edits. Requires Pillow."""

import argparse
import hashlib
import io
import json
import math
import re
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener
except ImportError:
    pass
else:
    register_heif_opener()


def load_pixels(path):
    with Image.open(path) as image:
        if getattr(image, "n_frames", 1) != 1:
            raise ValueError("Animated inputs are unsupported; select an approved still image")
        upright = ImageOps.exif_transpose(image)
        alpha = "A" in upright.getbands() or "transparency" in upright.info
        converted = upright.convert("RGBA" if alpha else "RGB")
        clean = Image.new(converted.mode, converted.size)
        clean.paste(converted)
        return clean


def size_of(path):
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).size


def validate_webp(raw, size):
    if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
        raise ValueError("Invalid WebP container")
    if int.from_bytes(raw[4:8], "little") + 8 != len(raw):
        raise ValueError("Incomplete WebP payload")
    offset = 12
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise ValueError("Truncated WebP chunk")
        if raw[offset:offset + 4] in (b"EXIF", b"XMP ", b"ICCP"):
            raise ValueError("Private metadata retained")
        length = int.from_bytes(raw[offset + 4:offset + 8], "little")
        offset += 8 + length + length % 2
    if offset != len(raw):
        raise ValueError("Invalid WebP chunk boundaries")
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        if image.size != size or image.format != "WEBP":
            raise ValueError("Decoded dimensions differ")
        if any(key in image.info for key in ("exif", "xmp", "icc_profile")):
            raise ValueError("Private metadata retained")


def optimize(args):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.id):
        raise ValueError("--id must be lowercase hyphen-case")
    if not 1 <= args.min_quality <= args.quality <= 100:
        raise ValueError("Require 1 <= min-quality <= quality <= 100")
    if args.max_bytes <= 0 or any(width <= 0 for width in args.widths):
        raise ValueError("Byte budget and widths must be positive")
    if not 1 <= len(set(args.widths)) <= 3:
        raise ValueError("Specify one to three distinct responsive width candidates")
    image = load_pixels(args.input)
    source_size = size_of(args.source)
    edit_size = size_of(args.edit_input) if args.edit_input else None
    limits = [source_size, image.size] + ([edit_size] if edit_size else [])
    ratio = image.width / image.height
    if args.framing == "preserve" and abs(ratio / (source_size[0] / source_size[1]) - 1) >= .003:
        raise ValueError("Aspect ratio changed; inspect the result or explicitly request crop/outpaint")
    max_width = min(size[0] for size in limits)
    max_height = min(size[1] for size in limits)
    cap = min(max_width, math.floor(max_height * ratio))
    while cap > 0 and round(cap / ratio) > max_height:
        cap -= 1
    if cap < 1:
        raise ValueError("No size fits all source/edit/generated dimension limits")
    widths = sorted({min(width, cap) for width in args.widths})
    targets = [(width, max(1, round(width / ratio))) for width in widths]
    outputs = [(args.out_dir / f"{args.id}-{width}.webp", (width, height))
               for width, height in targets]
    if not args.overwrite and any(path.exists() for path, _ in outputs):
        raise ValueError("Output exists; use a sibling ID or explicitly approve --overwrite")
    forbidden = {p.resolve() for p in (args.input, args.source, args.edit_input) if p}
    if any(path.resolve() in forbidden for path, _ in outputs):
        raise ValueError("Refusing to overwrite an input image")

    # Encode every variant before publishing any, so a budget failure leaves no partial batch.
    payloads = []
    variants = []
    hashes = {}
    qualities = list(range(args.quality, args.min_quality - 1, -4))
    if args.min_quality not in qualities:
        qualities.append(args.min_quality)
    for path, size in outputs:
        resized = image.resize(size, Image.Resampling.LANCZOS)
        for quality in qualities:
            buffer = io.BytesIO()
            resized.save(buffer, "WEBP", quality=quality, method=6)
            raw = buffer.getvalue()
            if len(raw) <= args.max_bytes:
                break
        else:
            raise ValueError(f"{path.name} exceeds {args.max_bytes} bytes at quality floor; reduce widths or revise the budget explicitly")
        validate_webp(raw, size)
        payloads.append((path, raw))
        variants.append(dict(width=size[0], height=size[1], bytes=len(raw),
                             quality=quality, file=path.name))
        hashes[path.name] = hashlib.sha256(raw).hexdigest()
    if len(set(hashes.values())) != len(hashes):
        raise ValueError("Duplicate variant hashes")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".optimize-", dir=args.out_dir) as temp:
        for path, raw in payloads:
            (Path(temp) / path.name).write_bytes(raw)
        for path, _ in payloads:
            staged = Path(temp) / path.name
            if args.overwrite:
                staged.replace(path)
            else:
                # Exclusive creation also protects against a concurrent writer.
                with path.open("xb") as output:
                    output.write(staged.read_bytes())

    result = dict(id=args.id, original=args.source.name, style=args.style,
                  sourceWidth=source_size[0], sourceHeight=source_size[1],
                  width=variants[-1]["width"], height=variants[-1]["height"],
                  variants=variants)
    if args.style != "documentary-photo":
        result.update(generatedWidth=image.width, generatedHeight=image.height)
    if edit_size:
        result.update(editInputWidth=edit_size[0], editInputHeight=edit_size[1])
    if args.framing != "preserve":
        result["framingEdit"] = args.framing
    result["audit"] = dict(inputWidth=image.width, inputHeight=image.height,
                           framing=args.framing, maxBytes=args.max_bytes,
                           metadataFree=True, sha256=hashes)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Approved final image")
    parser.add_argument("--source", type=Path, required=True, help="Original, for real size limits")
    parser.add_argument("--edit-input", type=Path, help="Previous edit, if re-editing")
    parser.add_argument("--id", required=True)
    parser.add_argument("--style", choices=["watercolor", "colored-pencil", "documentary-photo"], default="watercolor")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--widths", nargs="+", type=int, default=[480, 800, 1200])
    parser.add_argument("--framing", choices=["preserve", "crop", "outpaint"], default="preserve")
    parser.add_argument("--max-bytes", type=int, default=250_000)
    parser.add_argument("--quality", type=int, default=88)
    parser.add_argument("--min-quality", type=int, default=48)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        result = optimize(args)
    except (ValueError, OSError) as error:
        parser.exit(1, f"error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
