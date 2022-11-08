def decode_header(header):
    r"""
        >>> decode_header("v0402k00'" )
        'LOCATION 2D 00'
    """
    location = parse_lhex_word(header[4:8])
    hex_location = format_hword_in_hex(location)
    return "LOCATION %s" % (hex_location, )


CHARS = r"?z0 ?b1-?y2+?r3;?i4/?d5.?n6,?m7v'p8o?e9x?uf??tg??hj??ck??aq??sw?"

def print_char(char):
    if char > 63:
        return '?'
    else:
        return CHARS[char]


HEX_DIGITS = "0123456789ABCDEF"

def print_nybble(nybble):
    return HEX_DIGITS[nybble]


def print_byte(byte):
    return "%s%s" % (print_nybble(byte // 16), print_nybble(byte % 16))


def format_word_in_text(word):
    """
        >>> format_word_in_text(0x000B31C4)
        '?+h?'
    """
    digits = []
    x = word
    for i in range(0, 4):
        digits.append(x % 256)
        x = x // 256
    return "".join(print_char(d) for d in digits[::-1])


def format_hword_in_hex(hword):
    """
        >>> format_hword_in_hex(0x31C4)
        '31 C4'
    """
    return "%s %s" % (print_byte(hword // 256), print_byte(hword % 256))


def format_word_in_hex(word):
    """
        >>> format_word_in_hex(0x000B31C4)
        '00 0B  31 C4'
        >>> format_word_in_hex(0x31C4)
        '00 00  31 C4'
    """
    return "%s  %s" % (
        format_hword_in_hex(word // 65536),
        format_hword_in_hex(word % 65536)
    )


LHEX_DIGITS = "0l23456789dfjkqw"
LHEX_DIGIT_LOOKUP = {LHEX_DIGITS[i]: i for i in range(0, 16)}

def parse_lhex_digit(d):
    return LHEX_DIGIT_LOOKUP[d]


def parse_lhex_word(ws):
    """
        >>> parse_lhex_word("")
        0
        >>> parse_lhex_word("j")
        12
        >>> parse_lhex_word("lj")
        28
    """
    a = 0
    for d in ws:
        x = parse_lhex_digit(d)
        a = a * 16 + x
    return a


def decode_footer(footer):
    r"""
        >>> decode_footer("22l6w45q'                    ")
        'FOOTER 22 16  F4 5E (85??)'
    """
    word_s = footer[:8]
    word = parse_lhex_word(word_s)
    hex_word = format_word_in_hex(word)
    text_word = format_word_in_text(word)
    return "FOOTER %s (%s)" % (hex_word, text_word)


def decode_word(word):
    """
        >>> decode_word("")
        'EMPTY'
        >>> decode_word("f3lj4")
        'CONSTANT 00 0B  31 C4'
        >>> decode_word("k2w8j")
        'CALL 2F 8C'
    """
    if not word:
        return "EMPTY"
    
    value = parse_lhex_word(word) 
    return "CONSTANT %s" % (format_word_in_hex(value), )


def decode_line(line):
    """
        >>> decode_line("k2w8j'k3278'f3lj4'q2k98'22k78'q2qwj'22k54'22k58'")
        ["CALL 2F 8C", ... ]
        >>> decode_line("''''''''")
        ['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY']
    """
    return [decode_word(word) for word in line.split("'")[:-1]]


def translate_block(block):
    if len(block) < 10:
        raise Exception("Bad block: %s" % (repr(block), ))
    return (
        [ decode_header(block[0]) ] +
        [ decode_line(line) for line in block[1:9] ] +
        [ decode_footer(block[9]) ]
    )


def read_file(filename):
    data = []
    with open(filename, 'r') as f:
        line = f.readline()
        eof = False
        while not eof:
            block = []
            for i in range(0, 10):
                line = f.readline().strip()
                if not line:
                    eof = True
                    continue
                block.append(line)
            if block:
                data.append(translate_block(block))
    return data


if __name__ == '__main__':
    filename = "bkjck.tx"
    data = read_file(filename)
    print(data)
