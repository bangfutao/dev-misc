#include <iostream>

using namespace std;

/**
 * Implementation of class EightQueens
 * 
 * Solve eight Queens on 8x8 chess board without attacking each other.
 * Author: Bangfu Tao
 */

class EightQueens {
 public:
    EightQueens() {
        memset(matrix_, 0, sizeof(matrix_));
    }

    virtual ~EightQueens() {

    }

    int solutions() {
        solve(0);
        return num_solutions_;
    }

  private:
     static const int M = 8;
     int num_solutions_ = 0;
     int matrix_[M][M] = { 0 };

     // Solve the problem by recursively checking row by row, column by column
     // keep traces in 8x8 matrix and print out matrix when a solution found.
     void solve(int row) {
         if (row >= M) {
             num_solutions_++;
             print_solution();
             return;
         }
         for (int col = 0; col < M; col++) {
             // cout << row << ", " << col << endl;
             if (is_safe(row, col)) {
                 set_board(row, col);
                 solve(row + 1);
             }
         }
     }

     // Check if the square is safe to put a new Queen 
     bool is_safe(int row, int col) {
         for (int r = 0; r < row; r++) {
             if (matrix_[r][col]) {
                 return false;  // attack from same column
             }
             if ((col + r - row) >= 0 && (col + r - row) < M
                 && matrix_[r][col + r - row]) {
                 return false;  // attack from upper-left
             }
             if ((col + row - r) >= 0 && (col + row - r) < M
                 && matrix_[r][col + row -r]) {
                 return false;  // attack from upper-right
             }
         }
         return true;
     }

     void clear_row(int r) {
         for (int c = 0; c < M; c++) {
             matrix_[r][c] = 0;
         }
     }

     void set_board(int r, int c) {
         clear_row(r);
         matrix_[r][c] = 1;
     }

     void print_solution() {
         cout << "\nsolution " << num_solutions_ << ":" << endl;
         for (int i = 0; i < M; i++) {
             for (int j = 0; j < M; j++) {
                 cout << ((matrix_[i][j] == 0) ? "-" : "Q") << " ";
             }
             cout << endl;
         }
     }
};


int main()
{
    EightQueens check;
    int numSolutions = check.solutions();
    std::cout << "\nTotal " << numSolutions << " solutions found" << endl;
}