#pragma once

#include "sudoku_board.h"

class SudokuSolver {
public:
    bool solve(SudokuBoard& board) const;
    int countSolutions(SudokuBoard board, int limit = 2) const;

private:
    bool solveRecursive(SudokuBoard& board) const;
    void countRecursive(SudokuBoard& board, int limit, int& count) const;
};
