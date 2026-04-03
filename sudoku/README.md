# Sudoku Lab

Sudoku Lab is a small C++ terminal project focused on the core mechanics of Sudoku. It generates playable puzzles, keeps each generated board uniquely solvable, and lets the player interact with the puzzle directly from the command line.

The project is split into clear modules: a board representation responsible for validation and candidate checking, a backtracking solver used internally to solve and verify boards, a generator that creates full solutions and removes clues while preserving uniqueness, and a simple CLI layer that turns everything into a playable game loop.

The main goal of the project is to practice clean multi-file C++ design around a classic logic game. It combines state representation, recursive search, puzzle generation, and user interaction in a compact but expandable codebase.
