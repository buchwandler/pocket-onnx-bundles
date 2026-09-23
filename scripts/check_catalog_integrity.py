#!/usr/bin/env python3
"""Reject incomplete integrity metadata in the committed Pocket catalog."""

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "catalog" / "bundles.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors = []
    null_size = 0
    null_sha256 = 0
    artifact_count = 0

    for bundle_id, bundle in catalog["bundles"].items():
        for index, artifact in enumerate(bundle["artifacts"]):
            artifact_count += 1
            label = f"{bundle_id}.artifacts[{index}]"
            fmt = artifact.get("format")
            if not isinstance(fmt, str) or not fmt.strip():
                errors.append(f"{label}: format must be a non-empty string")

            size = artifact.get("size")
            if size is None:
                null_size += 1
            if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
                errors.append(f"{label}: size must be a positive integer")

            sha256 = artifact.get("sha256")
            if sha256 is None:
                null_sha256 += 1
            if not isinstance(sha256, str) or SHA256_RE.fullmatch(sha256) is None:
                errors.append(f"{label}: sha256 must be 64 lowercase hexadecimal characters")

    if errors:
        print("Catalog integrity check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Catalog integrity check passed: artifacts={artifact_count} "
        f"null_size={null_size} null_sha256={null_sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
