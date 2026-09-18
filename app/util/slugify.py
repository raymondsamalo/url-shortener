import hashlib


def base62_encode(num: int) -> str:
    """Encodes an integer into a Base62 string."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return chars[0]

    arr = []
    while num:
        num, rem = divmod(num, 62)
        arr.append(chars[rem])
    arr.reverse()
    return "".join(arr)


def slugify_md5_base62(text: str, length: int = 11) -> str:
    """
    Hashes text with MD5, converts it to an integer, encodes to Base62, 
    and truncates to the desired length for a short slug.
    """
    # 1. Generate MD5 hash
    md5_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

    # 2. Convert hex string to a large integer
    hash_int = int(md5_hash, 16)

    # 3. Encode integer to Base62
    base62_slug = base62_encode(hash_int)

    # 4. Return truncated slug (Standard MD5 in Base62 is max 22 chars)
    return base62_slug[:length]
