#!/usr/bin/env python3
"""Summarize a HAR file without printing URLs, headers, or body data."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys


# ponytail: cap parsing at 32 MiB; add streaming JSON only if larger HAR exports matter.
MAX_INPUT_BYTES = 32 * 1024 * 1024
METHODS = ("CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "TRACE", "OTHER")
STATUS_CLASSES = ("1xx", "2xx", "3xx", "4xx", "5xx", "other")
MEDIA_TYPES = ("application", "audio", "font", "image", "message", "model", "multipart", "text", "video", "other")


def reject_constant(_value):
    raise ValueError("non-standard JSON number")


def method_bucket(value):
    if not isinstance(value, str) or not value.isascii() or not value.isalpha() or len(value) > 20:
        return "OTHER", False
    method = value.upper()
    return (method if method in METHODS else "OTHER"), True


def status_bucket(value):
    if type(value) is not int or not 100 <= value <= 599:
        return "other", False
    return f"{value // 100}xx", True


def media_bucket(value):
    if isinstance(value, str) and "/" in value:
        major = value.partition("/")[0].strip().lower()
        if major in MEDIA_TYPES:
            return major
    return "other"


def summarize(entries):
    methods = Counter()
    statuses = Counter()
    media_types = Counter()
    incomplete = 0

    for entry in entries:
        valid = isinstance(entry, dict)
        request = entry.get("request") if valid else None
        response = entry.get("response") if valid else None

        method, method_valid = method_bucket(request.get("method") if isinstance(request, dict) else None)
        status, status_valid = status_bucket(response.get("status") if isinstance(response, dict) else None)
        content = response.get("content") if isinstance(response, dict) else None
        media = media_bucket(content.get("mimeType") if isinstance(content, dict) else None)

        methods[method] += 1
        statuses[status] += 1
        media_types[media] += 1
        if not isinstance(request, dict) or not isinstance(response, dict) or not method_valid or not status_valid:
            incomplete += 1

    return incomplete, methods, statuses, media_types


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Summarize HAR request methods, response classes, and media types without showing request data."
    )
    parser.add_argument("file", type=Path, help="UTF-8 HAR file")
    args = parser.parse_args(argv)

    try:
        with args.file.expanduser().open("rb") as source:
            raw = source.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("input exceeds the 32 MiB limit")
        document = json.loads(raw.decode("utf-8-sig"), parse_constant=reject_constant)
    except OSError as error:
        print(f"har-tally: cannot read input ({type(error).__name__})", file=sys.stderr)
        return 2
    except UnicodeError:
        print("har-tally: input is not valid UTF-8", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"har-tally: invalid JSON at line {error.lineno}, column {error.colno}", file=sys.stderr)
        return 2
    except ValueError as error:
        # The only messages here are fixed parser/size errors, never file content.
        print(f"har-tally: {error}", file=sys.stderr)
        return 2

    log = document.get("log") if isinstance(document, dict) else None
    entries = log.get("entries") if isinstance(log, dict) else None
    if not isinstance(entries, list):
        print("har-tally: expected a HAR object with a log.entries array", file=sys.stderr)
        return 2

    incomplete, methods, statuses, media_types = summarize(entries)
    print(f"entries={len(entries)} incomplete={incomplete}")
    print("methods: " + " ".join(f"{key}={methods[key]}" for key in METHODS if methods[key]))
    print("status: " + " ".join(f"{key}={statuses[key]}" for key in STATUS_CLASSES if statuses[key]))
    print("media: " + " ".join(f"{key}={media_types[key]}" for key in MEDIA_TYPES if media_types[key]))
    return 1 if incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
