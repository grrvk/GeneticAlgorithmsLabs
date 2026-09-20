import random

from gray import binary_to_gray, gray_to_binary

KNOWN_3BIT_GRAY = [
    "000",
    "001",
    "011",
    "010",
    "110",
    "111",
    "101",
    "100",
]


def test_binary_to_gray_matches_known_3bit_sequence():
    for value, expected_gray in enumerate(KNOWN_3BIT_GRAY):
        binary = format(value, "03b")
        assert binary_to_gray(binary) == expected_gray


def test_gray_to_binary_matches_known_3bit_sequence():
    for value, gray in enumerate(KNOWN_3BIT_GRAY):
        expected_binary = format(value, "03b")
        assert gray_to_binary(gray) == expected_binary


def test_round_trip_binary_to_gray_to_binary():
    random.seed(0)
    for _ in range(200):
        length = random.randint(1, 20)
        binary = "".join(random.choice("01") for _ in range(length))
        assert gray_to_binary(binary_to_gray(binary)) == binary


def test_consecutive_gray_codes_differ_by_one_bit():
    for value in range(len(KNOWN_3BIT_GRAY) - 1):
        a = KNOWN_3BIT_GRAY[value]
        b = KNOWN_3BIT_GRAY[value + 1]
        differing_bits = sum(1 for x, y in zip(a, b) if x != y)
        assert differing_bits == 1
