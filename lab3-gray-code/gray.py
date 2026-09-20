def binary_to_gray(bits: str) -> str:
    gray = [bits[0]]
    for prev, cur in zip(bits, bits[1:]):
        gray.append("1" if prev != cur else "0")
    return "".join(gray)


def gray_to_binary(bits: str) -> str:
    binary = [bits[0]]
    for cur in bits[1:]:
        binary.append("1" if cur != binary[-1] else "0")
    return "".join(binary)
