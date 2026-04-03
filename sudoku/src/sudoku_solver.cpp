#include "sudoku_solver.h"

#include <limits>
#include <utility>
#include <vector>

bool SudokuSolver::solve(SudokuBoard& board) const {
    return solveRecursive(board);
}

int SudokuSolver::countSolutions(SudokuBoard board, int limit) const {
    int count = 0;
    countRecursive(board, limit, count);
    return count;
}

bool SudokuSolver::solveRecursive(SudokuBoard& board) const {
    int bestRow = -1;
    int bestCol = -1;
    std::vector<int> bestCandidates;
    int bestSize = std::numeric_limits<int>::max();

    for (int row = 0; row < 9; ++row) {
        for (int col = 0; col < 9; ++col) {
            if (board.get(row, col) != 0) {
                continue;
            }

            std::vector<int> options = board.candidates(row, col);
            if (options.empty()) {
                return false;
            }
            if (static_cast<int>(options.size()) < bestSize) {
                bestSize = static_cast<int>(options.size());
                bestRow = row;
                bestCol = col;
                bestCandidates = std::move(options);
                if (bestSize == 1) {
                    break;
                }
            }
        }
        if (bestSize == 1) {
            break;
        }
    }

    if (bestRow == -1) {
        return board.isSolved();
    }

    for (int value : bestCandidates) {
        board.set(bestRow, bestCol, value);
        if (solveRecursive(board)) {
            return true;
        }
        board.set(bestRow, bestCol, 0);
    }

    return false;
}

void SudokuSolver::countRecursive(SudokuBoard& board, int limit, int& count) const {
    if (count >= limit) {
        return;
    }

    int bestRow = -1;
    int bestCol = -1;
    std::vector<int> bestCandidates;
    int bestSize = std::numeric_limits<int>::max();

    for (int row = 0; row < 9; ++row) {
        for (int col = 0; col < 9; ++col) {
            if (board.get(row, col) != 0) {
                continue;
            }

            std::vector<int> options = board.candidates(row, col);
            if (options.empty()) {
                return;
            }
            if (static_cast<int>(options.size()) < bestSize) {
                bestSize = static_cast<int>(options.size());
                bestRow = row;
                bestCol = col;
                bestCandidates = std::move(options);
                if (bestSize == 1) {
                    break;
                }
            }
        }
        if (bestSize == 1) {
            break;
        }
    }

    if (bestRow == -1) {
        ++count;
        return;
    }

    for (int value : bestCandidates) {
        board.set(bestRow, bestCol, value);
        countRecursive(board, limit, count);
        board.set(bestRow, bestCol, 0);
        if (count >= limit) {
            return;
        }
    }
}
