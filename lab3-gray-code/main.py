import random

from gray import binary_to_gray, gray_to_binary

BITS = 4
RANDOM_EXAMPLES = 5
RANDOM_SEED = 3


def hamming_distance(a: str, b: str) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def main() -> None:
    print(f"{'decimal':>7}  {'binary':>{BITS}}  {'gray':>{BITS}}  {'decoded':>{BITS}}")

    prev_gray = None
    for value in range(2**BITS):
        binary = format(value, f"0{BITS}b")
        gray = binary_to_gray(binary)
        decoded = gray_to_binary(gray)
        assert decoded == binary

        print(f"{value:>7}  {binary:>{BITS}}  {gray:>{BITS}}  {decoded:>{BITS}}")

        if prev_gray is not None:
            assert hamming_distance(prev_gray, gray) == 1
        prev_gray = gray

    print(f"\nRandom round-trip examples (bit-strings of arbitrary length, seed={RANDOM_SEED}):")
    random.seed(RANDOM_SEED)
    for _ in range(RANDOM_EXAMPLES):
        length = random.randint(1, 20)
        binary = "".join(random.choice("01") for _ in range(length))
        gray = binary_to_gray(binary)
        decoded = gray_to_binary(gray)
        assert decoded == binary
        decimal = int(binary, 2)
        print(
            f"decimal={decimal:<7} binary={binary!r:22} gray={gray!r:22} "
            f"decoded={decoded!r:22} match={decoded == binary}"
        )


if __name__ == "__main__":
    main()
