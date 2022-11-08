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


LHEX_DIGITS = "0l23456789fgjkqw"
LHEX_DIGIT_LOOKUP = {LHEX_DIGITS[i]: i for i in range(0, 16)}

def parse_lhex_digit(d):
    """
        >>> parse_lhex_digit("g")
        11
    """
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


OPCODES = {
    '0': "STOP", ## z 
    'l': "BRNG", ## b 
    '2': "STOR", ## y
    '3': "CALL", ## r 
    '4': "INPT", ## i 
    '5': "DIV ", ## d 
    '6': "NULT", ## n
    '7': "MULT", ## m 
    '8': "PRNT", ## p 
    '9': "MASK", ## e 
    'f': "JUMP", ## u 
    'g': "TEST", ## t 
    'j': "HOLD", ## h 
    'k': "CLER", ## c 
    'q': "ADD ", ## a 
    'w': "SUB ", ## s
}


def decode_word(word):
    """
        >>> decode_word("")
        'EMPTY'
        >>> decode_word("f3lj4")
        'JUMP 31 C4'
        >>> decode_word("k2w8j")
        'CLER 2F 8C'
        >>> decode_word("l2k94")
        'BRNG 2D 94'
    """
    if not word:
        return "EMPTY"
    
    if len(word) == 5:
        opcode = word[0]

        if opcode in OPCODES:
            op = OPCODES[opcode]
            location_value = parse_lhex_word(word[1:5])
            location = format_hword_in_hex(location_value)
            return "%s %s" % (op, location)

    value = parse_lhex_word(word) 

    return "CONSTANT %s" % (format_word_in_hex(value), )


def decode_line(line):
    """
        >>> decode_line("k2w8j'k3278'f3lj4'q2k98'22k78'q2qwj'22k54'22k58'")
        ['CLER 2F 8C', 'CLER 32 78', 'JUMP 31 C4', 'ADD  2D 98', 'STOR 2D 78', 'ADD  2E FC', 'STOR 2D 54', 'STOR 2D 58']
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


def gen_format_block(block):
    yield block[0]
    for i in range(1, 9):
        yield ""
        for line in block[i]:
            yield line
    yield ""
    yield block[9]
    yield ""
    yield ""


def format_block(block):
    """
        >>> print(format_block(
        ... ['LOCATION 2D 00', 
        ... ['CLER 2F 8C', 'CLER 32 78', 'JUMP 31 C4', 'ADD  2D 98', 'STOR 2D 78', 'ADD  2E FC', 'STOR 2D 54', 'STOR 2D 58'], 
        ... ['STOR 2D 6C', 'CALL 32 F0', 'JUMP 32 D8', 'MASK 31 F0', 'SUB  31 E0', 'TEST 2D 24', 'ADD  2E 8C', 'HOLD 2D 94'], 
        ... ['ADD  2D 0C', 'STOR 2D 68', 'STOR 2D 70', 'STOR 2D 50', 'CONSTANT 00 01  2D A8', 'MASK 2D E4', 'SUB  2D E4', 'TEST 2D 68'], 
        ... ['JUMP 2E 68', 'CONSTANT 00 01  2D D0', 'CONSTANT 00 01  2D A8', 'ADD  2D E4', 'HOLD 2D A8', 'CLER 2D 88', 'CONSTANT 00 01  2D D4', 'CLER 2D 8C'], 
        ... ['CALL 33 00', 'JUMP 33 00', 'CONSTANT 56 A4  06 56', 'CONSTANT 0E 06  62 7E', 'JUMP 2E 00', 'CONSTANT 00 00  00 18', 'CONSTANT 00 00  2D D0', 'CONSTANT 11 F2  08 06'], 
        ... ['CONSTANT 56 14  06 56', 'CONSTANT 56 1C  06 56', 'CONSTANT 56 A4  06 56', 'CONSTANT 57 2C  06 56', 'CONSTANT 56 34  06 56', 'CONSTANT 56 3C  06 56', 'CONSTANT 56 44  06 56', 'CONSTANT 56 4C  06 56'], 
        ... ['CONSTANT 28 0C  04 06', 'CONSTANT 10 64  08 06', 'CONSTANT 10 75  08 06', 'CONSTANT 10 6C  08 06', 'CONSTANT 0E 06  7A 7E', 'CONSTANT 0E 06  62 7E', 'CONSTANT 0E 06  2A 7E', 'CONSTANT 0E 06  6A 7E'], 
        ... ['CONSTANT 01 00  00 00', 'CONSTANT 00 80  00 00', 'CONSTANT 00 01  00 00', 'CONSTANT 00 00  80 00', 'CONSTANT 80 00  00 04', 'CONSTANT 7E 7E  7E 7E', 'CONSTANT 7F FF  FF FC', 'CONSTANT 00 40  00 00'], 
        ... 'FOOTER 3C 6F  C5 4C (????)']
        ... ))
        LOCATION 2D 00
        <BLANKLINE>
        CLER 2F 8C
        CLER 32 78
        JUMP 31 C4
        ADD  2D 98
        STOR 2D 78
        ADD  2E FC
        STOR 2D 54
        STOR 2D 58
        <BLANKLINE>
        STOR 2D 6C
        CALL 32 F0
        JUMP 32 D8
        MASK 31 F0
        SUB  31 E0
        TEST 2D 24
        ADD  2E 8C
        HOLD 2D 94
        <BLANKLINE>
        ADD  2D 0C
        STOR 2D 68
        STOR 2D 70
        STOR 2D 50
        CONSTANT 00 01  2D A8
        MASK 2D E4
        SUB  2D E4
        TEST 2D 68
        <BLANKLINE>
        JUMP 2E 68
        CONSTANT 00 01  2D D0
        CONSTANT 00 01  2D A8
        ADD  2D E4
        HOLD 2D A8
        CLER 2D 88
        CONSTANT 00 01  2D D4
        CLER 2D 8C
        <BLANKLINE>
        CALL 33 00
        JUMP 33 00
        CONSTANT 56 A4  06 56
        CONSTANT 0E 06  62 7E
        JUMP 2E 00
        CONSTANT 00 00  00 18
        CONSTANT 00 00  2D D0
        CONSTANT 11 F2  08 06
        <BLANKLINE>
        CONSTANT 56 14  06 56
        CONSTANT 56 1C  06 56
        CONSTANT 56 A4  06 56
        CONSTANT 57 2C  06 56
        CONSTANT 56 34  06 56
        CONSTANT 56 3C  06 56
        CONSTANT 56 44  06 56
        CONSTANT 56 4C  06 56
        <BLANKLINE>
        CONSTANT 28 0C  04 06
        CONSTANT 10 64  08 06
        CONSTANT 10 75  08 06
        CONSTANT 10 6C  08 06
        CONSTANT 0E 06  7A 7E
        CONSTANT 0E 06  62 7E
        CONSTANT 0E 06  2A 7E
        CONSTANT 0E 06  6A 7E
        <BLANKLINE>
        CONSTANT 01 00  00 00
        CONSTANT 00 80  00 00
        CONSTANT 00 01  00 00
        CONSTANT 00 00  80 00
        CONSTANT 80 00  00 04
        CONSTANT 7E 7E  7E 7E
        CONSTANT 7F FF  FF FC
        CONSTANT 00 40  00 00
        <BLANKLINE>
        FOOTER 3C 6F  C5 4C (????)
        <BLANKLINE>
        <BLANKLINE>
    """
    return "\n".join(gen_format_block(block))


if __name__ == '__main__':
    filename = "bkjck.tx"
    data = read_file(filename)
    for block in data:
        print(format_block(block))
