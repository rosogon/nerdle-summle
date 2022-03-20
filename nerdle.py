"""
nerdle.py [-e] {template}+ [discarded]
    - e: only evaluate the template
    template: list of digis and operators;
        On classic mode, more than one template can appear
        Without -e, is a template to find available expressions that match
        Guesses are prefixed by _
        Unknown values are represented by ? (only valid on classic nerdle)
    discarded: digits or operators not in the matching expressions

Playing instant nerdle (https://instant.nerdlegame.com):

    Pass the hint as parameter, prefixing the guessed green squares with '_'

    $ python nerdle.py 14=+6_78/
    Template:
         _
    14=+678/

    Solutions:
    6+14/7=8


Playing classic nerdle (https://nerdlegame.com):

    Enter an initial guess in the game (e.g.: 12+35=47)
    Then pass the result as parameter, replacing the failed squares for '?',
    and prefixing the guesses with '_'.
    The last argument is the set of discarded values (at the bottom)

    You will get 5 results at most. Only 100 results are calculated and then sorted
    by the number of different used characters.

    Run nerdle.py again passing the new try as nth parameter and the new set 
    of discarded values as last parameter, until you win the game.

    Example:

    $ python nerdle.py 12+??=?? 3547
    Tries:
    12+??=??

    Solutions:
    0+16/8=2    <-- entered
    0+16/2=8
    0+18/2=9
    0+18/9=2
    0/61+2=2

    $ python nerdle.py 12+??=?? ?_+_16?_8_=2 35470/
    Tries:
    12+??=??
     __  __
    ?+16?8=2

    Solutions:
    2+12-8=6

"""

import sys
from typing import List, NamedTuple, Union, Optional, Set, Dict
from collections import deque


GREEN = "\033[1;32m"
BLUE = "\033[1;44m"
REV_GREEN = "\033[97;42m"
REV_BLUE = "\033[97;104m"
REV_BLACK = "\033[97;40m"
NORMAL = "\033[1;0m"

CUT=100

UNKNOWN = "?"
digits = set(str(n) for n in range(0, 10))
operators = set(["+", "-", "*", "/", "="])
operations = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: div(a, b),
    "=": lambda a, b: a == b,
}
precedence = {
    "+": 1,
    "-": 1,
    "*": 10,
    "/": 10,
    "=": 0,
}
EOF = "EOF"


def div(a, b):
    if b == 0:
        raise SyntaxError("division by zero")
    return a / b


class Try(NamedTuple):
    template: List[str]
    guessed: List[bool]


class Node(NamedTuple):
    op: str
    left: Union["Node", int]
    right: Optional[Union["Node", int]] = None

    def __repr__(self):
        if not self.op:
            return str(self.left)
        return f"({self.op}, {self.left}, {self.right})"


def evaluate(expression):
    # Using shunting yard algorithm
    # I wanted to evaluate myself, instead of using eval()
    # I tried to make a recursive descent parser, but was not suitable due to right
    # associativity (I had forgotten about this :) )
    # Not sure it is bulletproof, but it seems enough for the kind of expressions
    # used here.
    # See https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm

    def nextchar():
        nonlocal index
        if index >= len(expression):
            result = EOF
        else:
            result = expression[index]
            index += 1
        return result

    def nexttoken():
        nonlocal ch

        if ch in operators or ch == EOF:
            result = ch
            ch = nextchar()
            return result
        elif ch.isdigit():
            n = 0
            while ch.isdigit():
                n = 10*n + int(ch)
                ch = nextchar()
            return n
        else:
            raise SyntaxError(f"Unexpected character {ch}")

    def reduce():
        op = op_stack.pop()
        try:
            right, left = output_stack.pop(), output_stack.pop()
        except IndexError:
            raise SyntaxError()
        node = Node(op, left, right)
        output_stack.append(node)

    def value(node):
        if isinstance(node, int):
            return node
        return operations[node.op](value(node.left), value(node.right))

    index = 0
    ch = nextchar()
    token = nexttoken()

    output_stack = deque()
    op_stack = deque()
    while token != EOF:
        if isinstance(token, int):
            output_stack.append(token)
        else:
            while op_stack and precedence[op_stack[-1]] >= precedence[token]:
                reduce()
            op_stack.append(token)
        token = nexttoken()

    while op_stack:
        reduce()

    return value(output_stack[0])


def find(ch, l):
    i = -1
    while True:
        try:
            i = l.index(ch, i + 1)
        except ValueError:
            return
        yield i


def valid_character(ch, pos, available, template, semi_guessed):

    n = len(template)
    if ch in operators and pos in (0, n - 1):
        return False
    if ch == "=" and template[0:pos].count("=") > 0:
        return False
    return pos not in semi_guessed.get(ch, [])


def check_semi_guessed(solution, semi_guessed):
    checked = set()
    for i, ch in enumerate(solution):
        if ch in semi_guessed:
            if i in semi_guessed[ch]:
                return False
            checked.add(ch)
    return len(semi_guessed.keys()) - len(checked) == 0


def initial_solution(tries):
    solution = None
    for try_ in tries:
        if not solution:
            solution = [UNKNOWN] * len(try_.template)
        for i, ch in enumerate(try_.template):
            if try_.guessed[i]:
                solution[i] = ch
    return solution


def build_semi_guessed(tries, initial) -> Dict[int, Set[int]]:
    semi_guesses = set(
        ch
        for try_ in tries
        for i, ch in enumerate(try_.template)
        if ch != UNKNOWN and not try_.guessed[i]
    )
    result = {}
    guessed_pos = set(i for i, _ in enumerate(initial) if initial[i] != UNKNOWN)
    for n in semi_guesses:
        result[n] = set()
        for try_ in tries:
            result[n] |= set(find(n, try_.template)) - guessed_pos
    return result


def solve(classic_mode, tries, discarded):

    def build_available_classic(tries, discarded):
        return (digits | operators) - discarded

    def build_available_instant(tries, discarded):
        template = tries[0].template
        guessed = tries[0].guessed
        available = set(
            template[i] for i in range(len(template)) if not guessed[i]
        )
        return available

    def next_available_classic(available, ch):
        return available - operators if ch == "=" else available

    def next_available_instant(available, ch):
        aux = available - operators if ch == "=" else available
        return aux - {ch}

    def step(i, solution, available):
        if i == n_steps:
            try:
                if "=" not in solution:
                    return
                if not check_semi_guessed(solution, semi_guessed):
                    return
                if evaluate(solution):
                    solutions.append(solution[:])
            except SyntaxError:
                pass
            return

        if initial[i] != UNKNOWN:
            step(i + 1, solution, available)
            return

        for ch in available:
            if len(solutions) > CUT:
                break
            if not valid_character(ch, i, available, solution, semi_guessed):
                continue
            solution[i] = ch
            step(i + 1, solution, next_available(available, ch))

    if classic_mode:
        next_available = next_available_classic
        build_available = build_available_classic
    else:
        next_available = next_available_instant
        build_available = build_available_instant

    available = build_available(tries, discarded)
    initial = initial_solution(tries)
    semi_guessed = build_semi_guessed(tries, initial)
    n_steps = len(initial)
    solutions = []
    step(0, initial[:], available)
    return solutions


def parse_template(input_):
    guessed = [False] * len(input_)
    i = 0
    template = []
    for ch in input_:
        if ch == "_":
            guessed[i] = True
        elif ch in operators or ch.isdigit():
            template.append(ch)
            i += 1
        elif ch == UNKNOWN:
            # silently ignore previous '_'
            if guessed[i]:
                guessed[i] = False
            template.append(ch)
            i += 1
        else:
            raise ValueError(f"Character {ch} is not valid in template")
    return Try(template=template, guessed=guessed)


def parse_discarded(input_):
    discarded = set()
    for ch in input_:
        if not ch.isdigit() and ch not in operators:
            raise ValueError(f"Character {ch} is not valid in discarded")
        discarded.add(ch)
    return discarded


def colored(s, color):
    return color + s + NORMAL


def print_try(try_):
    def ch_color(ch):
        if ch == UNKNOWN:
            return REV_BLACK
        if guessed[i]:
            return REV_GREEN
        return REV_BLUE

    template, guessed = try_[:]
    for i, ch in enumerate(template):
        color = ch_color(ch)
        print(f"{colored(ch, color)}", end="")
    print()


def usage():
    print(__doc__)
    exit(1)


def main():
    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] == "-e":
        if len(sys.argv) != 3:
            usage()
        expression, _ = parse_template(sys.argv[2])
        print(f"{''.join(expression)} --> {evaluate(expression)}")
        return

    classic_mode = len(sys.argv) > 2

    # parse
    if classic_mode:
        tries = []
        for i in range(1, len(sys.argv) - 1):
            tries.append(parse_template(sys.argv[i]))
        discarded = parse_discarded(sys.argv[i + 1])
    else:
        tries = [ parse_template(sys.argv[1]) ]
        discarded = set()

    # intro
    print("Tries:" if classic_mode else "Template:")
    for try_ in tries:
        print_try(try_)
    print()

    # solve
    solutions = solve(classic_mode, tries, discarded)
    if classic_mode:
        # Order by most different characters
        solutions = sorted(
            solutions, reverse=True, key=lambda item: len(set(item))
        )
        solutions = solutions[:5]

    # print solutions
    print("Solutions:")
    color = REV_GREEN if len(solutions) == 1 else NORMAL
    for solution in solutions:
        print(colored("".join(solution), color))
    if len(solutions) == 5:
        print("...")
    print()


if __name__ == "__main__":
    main()
