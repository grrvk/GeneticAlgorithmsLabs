# Lab 3 — Binary ↔ Gray Code Converter

## Problem

Implement a converter between standard binary and reflected binary **Gray code**, in both directions.

## Algorithm

For an `n`-bit string `bits`, indexed left to right:

- **binary → gray**: `gray[0] = bits[0]`, and `gray[i] = bits[i-1] XOR bits[i]` for `i > 0`.
- **gray → binary**: `binary[0] = bits[0]`, and `binary[i] = binary[i-1] XOR bits[i]` for `i > 0` (running XOR — the inverse of the above).

## Running it

```bash
uv run python main.py
```

Prints a table of all 4-bit values (binary, Gray code, decoded-back binary) and confirms every consecutive pair of Gray codes differs by exactly one bit.

```bash
uv run pytest
```

Runs unit tests: round-trip correctness over random bit strings, exact values against the canonical 3-bit Gray sequence, and the single-bit-difference property between consecutive codes.