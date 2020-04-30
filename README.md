# sudoku-smt

A sudoku solver via PySMT (a quick experiment to get my feet wet using PySMT):

Run it like so:

    python3 pysmt_sudoku.py puzzle1.sk --solution puzzle1.sk.sol

Including a user solution file (`*.sk.sol`) allows you to use this as the backend for a game
script; it will compare the user's solution agains the actual solution and show the errors,
if any.
