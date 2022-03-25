"""
summle.py target a,b,c,d,e,f

Example:
    $ python3 summle.py 268 2,2,7,50,100
    Target=268
    Numbers=[2, 2, 7, 50, 100]
    Found solution: (7+2=9, 100+9=109, 109*2=218, 218+50=268)
    Found solution: (50-2=48, 48*7=336, 336/2=168, 168+100=268)
    Found solution: (50-2=48, 48/2=24, 24*7=168, 168+100=268)
    Found solution: (100+2=102, 102+7=109, 109*2=218, 218+50=268)
    Found solution: (100+7=107, 107+2=109, 109*2=218, 218+50=268)
    N solutions = 5

"""
import sys
from typing import List, NamedTuple


operators = {
    "+": lambda a, b: (a + b, True),
    "-": lambda a, b: (a - b, a >= b),
    "*": lambda a, b: (a * b, True),
    "/": lambda a, b: ((0 if b == 0 else a // b), (b != 0 and (a % b == 0))),
}

identity = {
    "+": lambda a, b: a == 0 or b == 0,
    "-": lambda a, b: b == 0,
    "*": lambda a, b: a == 1 or b == 1,
    "/": lambda a, b: b == 1,
}


class Operation(NamedTuple):
    a: int
    op: str
    b: int

    def __repr__(self):
        result, _ = operators[self.op](self.a, self.b)
        return f"{self.a}{self.op}{self.b}={result}"


commutative = { op: op in ("+", "*") for op in operators }

def calc_step(target, numbers, i, j, op):
    numbers = numbers[:]
    a = numbers[i]
    b = numbers[j]
    partial, valid = operators[op](a, b)
    if not valid:
        return partial, []
    if i > j:
        i, j = j, i
    numbers.pop(j)
    numbers.pop(i)
    numbers.append(partial)
    return partial, numbers


solutions = []
solutions_set = set()


def ignore_commutative(numbers, op, i, j):
    a, b = numbers[i], numbers[j]
    if not commutative[op]:
        return a == b and i > j
    return a < b or (a == b and i > j)


def solve(target, numbers, curr_steps):

    if not numbers:
        return

    for i in range(len(numbers)):
        for op in operators:
            for j in range(len(numbers)):
                a, b = numbers[i], numbers[j]
                if (
                    i == j 
                    or ignore_commutative(numbers, op, i, j) 
                    or identity[op](a, b)
                ):
                    continue

                result, new_numbers = calc_step(target, numbers, i, j, op)
                step = Operation(a, op, b)
                if not new_numbers:
                    continue
                new_steps = curr_steps + (step,)
                new_steps_set = frozenset(new_steps)
                if result == target and new_steps_set not in solutions_set:
                    print(f"Found solution: {new_steps}")
                    solutions.append(new_steps)
                    solutions_set.add(new_steps_set)
                elif len(new_numbers) >= 2:
                    solve(target, new_numbers, new_steps)

    return solutions


def main():
    if len(sys.argv) != 3:
        print(f"{sys.argv[0]} target a,b,c,d,e,f")
        exit(1)

    target = int(sys.argv[1])
    numbers = [int(s) for s in sys.argv[2].split(",")]

    print(f"Target={target}")
    print(f"Numbers={numbers}")

    solutions = solve(target, numbers, ())
    print(f"N solutions = {len(solutions)}")


if __name__ == "__main__":
    main()
