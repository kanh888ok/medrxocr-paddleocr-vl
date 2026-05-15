#!/usr/bin/env python3
"""Print availability of optional PaddleOCR-VL training dependencies."""

import importlib.util


def main():
    for name in ["erniekit", "paddlenlp", "visualdl"]:
        print(f"{name}: {bool(importlib.util.find_spec(name))}")


if __name__ == "__main__":
    main()
