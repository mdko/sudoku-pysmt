#!/usr/bin/env python3
from pysmt.shortcuts import Symbol, LE, GE, Int, And, Not, is_sat, AllDifferent, get_model
from pysmt.typing import INT
import string
import sys
import argparse
import termcolor

def read_in_grid(f):
    """ expects f to have been opened """
    def parse(c):
        return None if c == '-' else int(c)

    grid = []
    while True:
        line = f.readline().strip().replace(" ", "")
        if not line:
            break
        if len(line) != 9:
            raise Exception("invalid puzzle: must have 9 elements per line")
        row = [parse(c) for c in line]
        grid.append(row)

    if len(grid) != 9:
        raise Exception("not enough rows")
    return grid

def tosym(e, row, col):
    if e:
        return Int(e)
    else:
        return Symbol(row+col, INT)

def constrain(e):
    return And(LE(Int(1), e), GE(Int(9), e))

def region(grid_smt, i):
    res = []
    for row in grid_smt[(i//3)*3:((i//3)+1)*3]:
        for c in range((i%3)*3, ((i%3)+1)*3):
            res.append(row[c])
    return res

def column(grid_smt, i):
    col = []
    for r in range(len(grid_smt)):
        col.append(grid_smt[r][i])
    return col

def print_grid(grid, printer=lambda r, c, x: x):
    for rix, row in enumerate(grid):
        if rix % 3 == 0:
            print('-------------------')
        for cix, el in enumerate(row):
            if cix % 3 == 0:
                print('|', end='')
            else:
                print(' ', end='')
            print(printer(rix, cix, el) if el else ' ', end='')
        print('|', end='')
        print()
    print('-------------------')

if __name__ == "__main__":
    
    # Parsing
    parser = argparse.ArgumentParser(description="Sudoku solver via SMT")
    parser.add_argument("puzzle", type=argparse.FileType("r"))
    parser.add_argument("--solution", type=argparse.FileType("r"))
    args = parser.parse_args()

    # Read in puzzle, possibly expected solution
    puzzle = read_in_grid(args.puzzle)
    solution_user = None
    if args.solution:
        solution_user = read_in_grid(args.solution)

    # Convert puzzle to SMT domain
    puzzle_smt = [
        [tosym(e, r, str(c)) for (c, e) in enumerate(row, start=1)] for (r, row) in zip(string.ascii_lowercase[:9], puzzle)
    ]

    # Get all the constraints (rows, columns, regions all contain unique)
    domains = And([And([constrain(n) for n in row]) for row in puzzle_smt])

    rows_unique = And([AllDifferent(r) for r in puzzle_smt])
    cols_unique = And([AllDifferent(column(puzzle_smt, i)) for i in range(9)])
    regions_unique = And([AllDifferent(region(puzzle_smt, i)) for i in range(9)])

    problem = And(rows_unique, cols_unique, regions_unique)
    formula = And(domains, problem)

    # Solve it!
    print("Solvable? ", is_sat(formula))
    model = get_model(formula)
    solution_smt = [[model.get_py_value(e) for e in row] for row in puzzle_smt]

    # Print the results
    print("Problem")
    print_grid(puzzle)
    print("Solution")
    print_grid(solution_smt)

    if solution_user:
        if solution_smt != solution_user:
            def compare(rix, cix, v):
                if solution_smt[rix][cix] != v:
                    return termcolor.colored(v, 'red')
                else:
                    return v
            print("Your solution's errors:")
            print_grid(solution_user, compare)
        else:
            print("You got it right!")
