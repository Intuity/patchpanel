# Copyright 2020, Peter Birch, mailto:peter@lightlogic.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from itertools import count

class Matrix2D(object):
    """ Represent a 2D matrix """

    def __init__(self, rows=0, cols=0, default=0, state=None, debug=False):
        """ Initialise the 2D matrix

        Args:
            rows   : Initial number of rows
            cols   : Initial number of columns
            default: Default value to populate the matrix with
            state  : An existing matrix to adopt
            debug  : Enable debug messages
        """
        self.default = default
        self.debug   = debug
        # If state provided, adopt it
        self.data    = [[
            (state[r][c] if state and len(state) > r and len(state[r]) > c else self.default)
            for c in range(cols)
        ] for r in range(rows)]

    @property
    def rows(self): return len(self.data)

    @property
    def cols(self):
        return max((len(x) for x in self.data)) if len(self.data) > 0 else 0

    @property
    def min(self):
        return max((
            max((cell for cell in row)) for row in self.data
        ))

    @property
    def max(self):
        return max((
            max((cell for cell in row)) for row in self.data
        ))

    @property
    def abs_max(self):
        return max((
            max((abs(cell) for cell in row)) for row in self.data
        ))

    def row(self, row): return self.data[row]

    def column(self, col): return [x[col] for x in self.data]

    def get(self, row, col): return self.data[row][col]

    def set(self, row, col, val): self.data[row][col] = val

    def add_row(self):
        """ Extend the matrix by adding a new row

        Returns: The index of the newly added row
        """
        self.data.append([self.default for _x in range(self.cols)])
        return len(self.data) - 1

    def add_column(self):
        """ Extend the matrix by adding a new column

        Returns: The index of the newly added column
        """
        num_cols = self.cols
        for row in self.data:
            row += [self.default for _x in range(num_cols + 1 - len(row))]
        return num_cols

    def remove_row(self, idx):
        """ Remove a row from the matrix.

        Args:
            idx: Index of the row to remove
        """
        self.data.pop(idx)

    def remove_column(self, idx):
        """ Remove a column from the matrix.

        Args:
            idx: Index of the column to remove
        """
        for row in self.data: row.pop(idx)

    def display(self):
        """ Print out the matrix """
        max_val_len = min(max((len(str(self.max)), len(str(self.min)))), 5)
        for row in self.data:
            line = ""
            for cell in row:
                line += f"%{max_val_len}f " % cell
            print(line)

    def empty_rows(self):
        """ Identify empty rows (all 0) within the matrix

        Returns: A list of rows which are empty
        """
        empty = []
        for idx, row in enumerate(self.data):
            if not any((x for x in row if x != 0)):
                empty.append(idx)
        return empty

    def empty_columns(self):
        """ Identify empty columns (all 0) within the matrix

        Returns: A list of columns which are empty
        """
        empty = []
        for idx in range(self.cols):
            if not any((x for x in self.data if x[idx] != 0)):
                empty.append(idx)
        return empty

    def prune(self):
        """ Remove empty rows and columns and return the modifications.

        Returns: Tuple of list of removed rows and list of removed columns.
        """
        # Sort rows and columns in descending order
        # NOTE: This means they don't destroy state as they are removed
        e_rows = sorted(self.empty_rows(), reverse=True)
        e_cols = sorted(self.empty_columns(), reverse=True)
        # Remove identified rows and columns
        for row in e_rows: self.remove_row(row)
        for col in e_cols: self.remove_column(col)
        # Return the dropped rows & columns
        return (e_rows, e_cols)

    def extract(self, rows, columns):
        """ Extract a submatrix from this larger matrix.

        Args:
            rows: List of rows to extract
            cols: List of columns to extract
        """
        submatrix = []
        for r_idx in sorted(rows):
            row = []
            for c_idx in sorted(columns):
                row.append(self.data[r_idx][c_idx])
            submatrix.append(row)
        return Matrix2D(
            rows=len(rows), cols=len(columns), default=self.default, state=submatrix
        )

    def separate(self):
        """ Identify and split out independent submatrices. """
        r_separated, c_separated, m_separated = [], [], []
        for i_pass in count():
            # Identify non-separated rows and columns
            a_rows = [x for x in range(self.rows) if x not in r_separated]
            a_cols = [x for x in range(self.cols) if x not in c_separated]
            # If either non-separated rows or columns falls to zero, stop
            if len(a_rows) == 0 or len(a_cols) == 0: break
            # Start with the first row not yet separated
            r_focus, c_focus = [a_rows[0]], []
            r_last,  c_last  = 0, 0
            for i_refine in count():
                # Identify all non-empty columns in each row of interest
                for r_idx in r_focus:
                    c_focus += [x for x in a_cols if self.data[r_idx][x] != 0]
                c_focus = list(set(c_focus))
                # Identify all non-empty rows in each column of interest
                for c_idx in c_focus:
                    r_focus += [x for x in a_rows if self.data[x][c_idx] != 0]
                r_focus = list(set(r_focus))
                # Check if we haven't advanced
                if len(r_focus) == r_last and len(c_focus) == c_last: break
                r_last = len(r_focus)
                c_last = len(c_focus)
            # Print out identified rows & columns
            if self.debug:
                print(f"Separation pass {i_pass} (took {i_refine} steps):")
                print(f" - Rows: {r_focus}")
                print(f" - Cols: {c_focus}")
            # Keep track of the separated rows & columns
            r_separated += r_focus
            c_separated += c_focus
            # Store the submatrix
            m_separated.append(
                (self.extract(r_focus, c_focus), r_focus, c_focus)
            )
        # Return the collected submatrices
        return m_separated