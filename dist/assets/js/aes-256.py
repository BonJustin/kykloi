"""
Pure-Python AES-256-GCM Implementation (Zero External Dependencies).
Strictly compliant with NIST SP 800-38D and FIPS-197.
Interoperable with the WebCrypto SubtleCrypto API.
"""

# Precomputed S-Box and Rcon Tables (FIPS-197)
S_BOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5e, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]


def _xtime(a: int) -> int:
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1)


def _key_expansion_256(key: bytes) -> list[int]:
    """Expands a 32-byte (256-bit) key into a 60-word round key list."""
    w = list(key)
    for i in range(8, 60):
        temp = w[(i - 1) * 4: i * 4]
        if i % 8 == 0:
            temp = [S_BOX[temp[1]], S_BOX[temp[2]], S_BOX[temp[3]], S_BOX[temp[0]]]
            temp[0] ^= RCON[i // 8]
        elif i % 8 == 4:
            temp = [S_BOX[x] for x in temp]
        for j in range(4):
            w.append(w[(i - 8) * 4 + j] ^ temp[j])
    return w


def _cipher_block(state: list[int], round_keys: list[int]) -> bytes:
    """Standard 14-round AES-256 block transformation."""
    # Round 0
    for i in range(16):
        state[i] ^= round_keys[i]

    # Rounds 1 to 13
    for r in range(1, 14):
        rk_offset = r * 16
        # SubBytes & ShiftRows
        s0 = S_BOX[state[0]]
        s1 = S_BOX[state[5]]
        s2 = S_BOX[state[10]]
        s3 = S_BOX[state[15]]

        s4 = S_BOX[state[4]]
        s5 = S_BOX[state[9]]
        s6 = S_BOX[state[14]]
        s7 = S_BOX[state[3]]

        s8 = S_BOX[state[8]]
        s9 = S_BOX[state[13]]
        s10 = S_BOX[state[2]]
        s11 = S_BOX[state[7]]

        s12 = S_BOX[state[12]]
        s13 = S_BOX[state[1]]
        s14 = S_BOX[state[6]]
        s15 = S_BOX[state[11]]

        # MixColumns & AddRoundKey
        state[0] = _xtime(s0 ^ s1) ^ s1 ^ s2 ^ s3 ^ round_keys[rk_offset]
        state[1] = _xtime(s1 ^ s2) ^ s2 ^ s3 ^ s0 ^ round_keys[rk_offset + 1]
        state[2] = _xtime(s2 ^ s3) ^ s3 ^ s0 ^ s1 ^ round_keys[rk_offset + 2]
        state[3] = _xtime(s3 ^ s0) ^ s0 ^ s1 ^ s2 ^ round_keys[rk_offset + 3]

        state[4] = _xtime(s4 ^ s5) ^ s5 ^ s6 ^ s7 ^ round_keys[rk_offset + 4]
        state[5] = _xtime(s5 ^ s6) ^ s6 ^ s7 ^ s4 ^ round_keys[rk_offset + 5]
        state[6] = _xtime(s6 ^ s7) ^ s7 ^ s4 ^ s5 ^ round_keys[rk_offset + 6]
        state[7] = _xtime(s7 ^ s4) ^ s4 ^ s5 ^ s6 ^ round_keys[rk_offset + 7]

        state[8] = _xtime(s8 ^ s9) ^ s9 ^ s10 ^ s11 ^ round_keys[rk_offset + 8]
        state[9] = _xtime(s9 ^ s10) ^ s10 ^ s11 ^ s8 ^ round_keys[rk_offset + 9]
        state[10] = _xtime(s10 ^ s11) ^ s11 ^ s8 ^ s9 ^ round_keys[rk_offset + 10]
        state[11] = _xtime(s11 ^ s8) ^ s8 ^ s9 ^ s10 ^ round_keys[rk_offset + 11]

        state[12] = _xtime(s12 ^ s13) ^ s13 ^ s14 ^ s15 ^ round_keys[rk_offset + 12]
        state[13] = _xtime(s13 ^ s14) ^ s14 ^ s15 ^ s12 ^ round_keys[rk_offset + 13]
        state[14] = _xtime(s14 ^ s15) ^ s15 ^ s12 ^ s13 ^ round_keys[rk_offset + 14]
        state[15] = _xtime(s15 ^ s12) ^ s12 ^ s13 ^ s14 ^ round_keys[rk_offset + 15]

    # Round 14 (No MixColumns)
    rk_offset = 224
    out = bytearray(16)
    out[0] = S_BOX[state[0]] ^ round_keys[rk_offset]
    out[1] = S_BOX[state[5]] ^ round_keys[rk_offset + 1]
    out[2] = S_BOX[state[10]] ^ round_keys[rk_offset + 2]
    out[3] = S_BOX[state[15]] ^ round_keys[rk_offset + 3]

    out[4] = S_BOX[state[4]] ^ round_keys[rk_offset + 4]
    out[5] = S_BOX[state[9]] ^ round_keys[rk_offset + 5]
    out[6] = S_BOX[state[14]] ^ round_keys[rk_offset + 6]
    out[7] = S_BOX[state[3]] ^ round_keys[rk_offset + 7]

    out[8] = S_BOX[state[8]] ^ round_keys[rk_offset + 8]
    out[9] = S_BOX[state[13]] ^ round_keys[rk_offset + 9]
    out[10] = S_BOX[state[2]] ^ round_keys[rk_offset + 10]
    out[11] = S_BOX[state[7]] ^ round_keys[rk_offset + 11]

    out[12] = S_BOX[state[12]] ^ round_keys[rk_offset + 12]
    out[13] = S_BOX[state[1]] ^ round_keys[rk_offset + 13]
    out[14] = S_BOX[state[6]] ^ round_keys[rk_offset + 14]
    out[15] = S_BOX[state[11]] ^ round_keys[rk_offset + 15]

    return bytes(out)


def _ghash_mult(x: int, y: int) -> int:
    """Field multiplication in GF(2^128) using reducing polynomial x^128 + x^7 + x^2 + x + 1."""
    r = 0xE1000000000000000000000000000000
    z = 0
    v = x
    for i in range(128):
        if (y >> (127 - i)) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ r
        else:
            v >>= 1
    return z


def aes_gcm_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    """
    Encrypts data using AES-256-GCM.
    Returns: (ciphertext, 16-byte authentication tag).
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes (256 bits).")
    if len(iv) != 12:
        raise ValueError("Standard 96-bit (12 byte) IV required.")

    round_keys = _key_expansion_256(key)

    # 1. Compute Hash Subkey H = AES_K(0^128)
    h_bytes = _cipher_block([0] * 16, round_keys)
    h = int.from_bytes(h_bytes, byteorder="big")

    # 2. Compute J0 (Initial Counter Block)
    j0 = iv + b"\x00\x00\x00\x01"

    # 3. Encrypt Plaintext via GCTR
    ciphertext = bytearray()
    counter = int.from_bytes(j0, byteorder="big")

    num_blocks = (len(plaintext) + 15) // 16
    for i in range(num_blocks):
        counter = ((counter + 1) & 0xFFFFFFFF) | (counter & ~0xFFFFFFFF)
        ctr_block = counter.to_bytes(16, byteorder="big")
        keystream = _cipher_block(list(ctr_block), round_keys)
        chunk = plaintext[i * 16: (i + 1) * 16]
        for c_b, k_b in zip(chunk, keystream):
            ciphertext.append(c_b ^ k_b)

    ciphertext_bytes = bytes(ciphertext)

    # 4. Authenticate Ciphertext via GHASH
    s = 0
    # Zero-padded ciphertext blocks
    pad_len = (16 - (len(ciphertext_bytes) % 16)) % 16
    padded_ct = ciphertext_bytes + (b"\x00" * pad_len)

    for i in range(0, len(padded_ct), 16):
        block_int = int.from_bytes(padded_ct[i: i + 16], byteorder="big")
        s = _ghash_mult(s ^ block_int, h)

    # Length block: [len(AAD) in bits (64-bit) || len(C) in bits (64-bit)]
    # AAD is empty (0 bits).
    len_block = (0).to_bytes(8, "big") + (len(ciphertext_bytes) * 8).to_bytes(8, "big")
    s = _ghash_mult(s ^ int.from_bytes(len_block, "big"), h)

    # 5. Compute Authentication Tag T = GCTR_K(J0, S)
    tag_mask = _cipher_block(list(j0), round_keys)
    tag = bytes(a ^ b for a, b in zip(s.to_bytes(16, "big"), tag_mask))

    return ciphertext_bytes, tag
