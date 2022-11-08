# Notes on the blackjack code

This was the first single piece of code I was able to understand in detail, although it still holds some mysteries.

```
SUB  2F C4      # 32 80
TEST 32 A0
SUB  2F C4
TEST 32 BC
SUB  2F C4
TEST 32 C4
PRNT 00 0E '3'
STOP 00 24      # 32 9C

ADD  2F C4      # 32 A0
NULT 31 0C
ADD  32 B4
STOR 32 B0
PRNT 00 1A '6'  # 32 B0
STOP 02 00      # 32 B4
JUMP 31 B0
PRNT 00 06 '1'

JUMP 32 9C
PRNT 00 0A '2'
JUMP 32 9C      # 32 C8
```

This is a subroutine, which is called from other places, using the return code op to store a return code at 32 B8. For example it is called at lines 31 28 / 31 2C.  

```
CALL 32 B8      # 31 28
JUMP 32 80      # 31 2C
```

The value in the accumulator when the routine is called is tested, and depending on its value we branch to 4 different places. Most of these are just a single PRNT and then another jump, but one of them is a PRNT which requires several calculations to determine the appropriate value.

This is the PRNT at 32 60 - note that the line before is STOR 32 B0, in other words writing to the location that is going to be used as the operand to PRNT.

```
ADD  2F C4      # 32 A0
NULT 31 0C
ADD  32 B4
STOR 32 B0
PRNT 00 1A '6'  # 32 B0
STOP 02 00      # 32 B4
JUMP 31 B0
```

There are three memory locations used as arithmetic inputs here. The initial values at these locations are:

- 2F C4: 00 00 00 28
- 31 0C: 00 00 01 00
- 32 B4: 00 00 02 00

Suppose that we start with x in the accumulator at the start of the subroutine. 40 (0x28) was subtracted from the acc before we reached this branch, as part of the test, and we add it back first. Then we multiply by 256 and add 2. When we print the result, we take the high nybble as the character to be printed, and this is x + 2.

If we start with x = 4d in the accumulator, then we will print 4d + 2, which corresponds to the decimal digit d.

This part of the subroutine serves to print numbers, where the number is a single digit, stored as a multiple of 4.

So the other branches seem to print the first digit of a two digit number, after checking whether the number (still stored in multiplied-by-4 form) is bigger than 40, 80 and 120 respectively. In other words numbers 10 or above are prefixed by 1, 20 or above by 2, 30 or above by 3. So we can display any decimal number up to 39 (probably only 30 for blackjack values or 31 for dates are needed).

I originally got confused by the 3 extra branches because I guessed that the served to print 'J', 'Q' and 'K' for the card values.
