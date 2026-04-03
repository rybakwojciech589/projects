#include "sudoku_board.h"

#include <algorithm>
#include <cctype>
#include <iostream>
#include <string>

SudokuBoard::SudokuBoard() : cells_{} {}

std::optional<SudokuBoard> SudokuBoard::fromString(const std::string& raw) {
    std::string cleaned;
    cleaned.reserve(raw.size());

    for (char ch : raw) {
        if (std::isspace(static_cast<unsigned char>(ch))) {
            continue;
        }
        cleaned += ch;
    }

    if (cleaned.size() != 81) {
        return std::nullopt;
    }

    SudokuBoard board;
    for (std::size_t i = 0; i < cleaned.size(); ++i) {
        const char ch = cleaned[i];
        if (ch == '.' || ch == '_' || ch == '0') {
            board.cells_[i] = 0;
            continue;
        }
        if (ch < '1' || ch > '9') {
            return std::nullopt;
        }
        board.cells_[i] = ch - '0';
    }

    if (!board.isConsistent()) {
        return std::nullopt;
    }

    return board;
}

int SudokuBoard::get(int row, int col) const {
    return cells_[index(row, col)];
}

void SudokuBoard::set(int row, int col, int value) {
    cells_[index(row, col)] = value;
}

bool SudokuBoard::isValidPlacement(int row, int col, int value) const {
    if (value < 1 || value > 9) {
        return false;
    }

    for (int c = 0; c < 9; ++c) {
        if (c != col && get(row, c) == value) {
            return false;
        }
    }

    for (int r = 0; r < 9; ++r) {
        if (r != row && get(r, col) == value) {
            return false;
        }
    }

    const int boxRow = (row / 3) * 3;
    const int boxCol = (col / 3) * 3;
    for (int r = boxRow; r < boxRow + 3; ++r) {
        for (int c = boxCol; c < boxCol + 3; ++c) {
            if ((r != row || c != col) && get(r, c) == value) {
                return false;
            }
        }
    }

    return true;
}

bool SudokuBoard::isConsistent() const {
    for (int row = 0; row < 9; ++row) {
        for (int col = 0; col < 9; ++col) {
            const int value = get(row, col);
            if (value == 0) {
                continue;
            }
            if (!isValidPlacement(row, col, value)) {
                return false;
            }
        }
    }
    return true;
}

bool SudokuBoard::isSolved() const {
    return emptyCount() == 0 && isConsistent();
}

int SudokuBoard::emptyCount() const {
    return static_cast<int>(std::count(cells_.begin(), cells_.end(), 0));
}

int SudokuBoard::clueCount() const {
    return 81 - emptyCount();
}

std::vector<int> SudokuBoard::candidates(int row, int col) const {
    if (get(row, col) != 0) {
        return {};
    }

    std::vector<int> out;
    for (int value = 1; value <= 9; ++value) {
        if (isValidPlacement(row, col, value)) {
            out.push_back(value);
        }
    }
    return out;
}

std::string SudokuBoard::toString() const {
    std::string out;
    out.reserve(81);
    for (int value : cells_) {
        out += static_cast<char>(value == 0 ? '0' : ('0' + value));
    }
    return out;
}

void SudokuBoard::print(std::ostream& out, const std::optional<std::array<bool, 81>>& fixed) const {
    out << "    1 2 3   4 5 6   7 8 9\n";
    out << "  +-------+-------+-------+\n";

    for (int row = 0; row < 9; ++row) {
        out << row + 1 << " | ";
        for (int col = 0; col < 9; ++col) {
            const int idx = index(row, col);
            const int value = cells_[idx];
            const bool isFixed = fixed.has_value() ? (*fixed)[idx] : false;

            if (value == 0) {
                out << ".";
            } else if (isFixed) {
                out << value;
            } else {
                out << value;
            }

            out << ' ';
            if ((col + 1) % 3 == 0) {
                out << "| ";
            }
        }
        out << "\n";
        if ((row + 1) % 3 == 0) {
            out << "  +-------+-------+-------+\n";
        }
    }
}

int SudokuBoard::index(int row, int col) {
    return row * 9 + col;
}
