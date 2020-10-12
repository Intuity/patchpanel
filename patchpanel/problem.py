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

from .connectivity import Connectivity

class Problem(Connectivity):
    """ Extends Connectivity to provide storage and solving of constraints """

    def __init__(self, sources=None, sinks=None, matrix=None):
        """ Initialise the problem

        Args:
            sources: List of sources (must provide sinks & matrix)
            sinks  : List of sinks (must provide sources & matrix)
            matrix : Connectivity matrix (must provide sources & sinks)
        """
        # Call to super to initialise
        super().__init__(sources=sources, sinks=sinks, matrix=matrix)
        # Collect constraints
        self.constraints = []
        # Collect isolated subsets of the connectivity to solve
        self.subsets = []

    def constrain(self, sources, sinks, inverse=False):
        """ Apply a constraint that only certain sources and sinks can be linked

        Args:
            sources: Single source or list of sources
            sinks  : Single sink or list of sinks
            inverse: Add an inverse constraint (ban certain links)
        """
        # Ensure sources & sinks are lists
        if not isinstance(sources, list): sources = [sources]
        if not isinstance(sinks,   list): sinks   = [sinks]
        # Check all sinks and sources are known
        u_srcs  = [x for x in sources if x not in self.src_to_row]
        if len(u_srcs) > 0:
            raise Exception(f"Applying constaint to unknown sources: {u_srcs}")
        u_sinks = [x for x in sinks if x not in self.sink_to_col]
        if len(u_sinks) > 0:
            raise Exception(f"Applying constraint to unknown sinks: {u_sinks}")
        # Append the constraint to the list
        # NOTE: We don't apply immediately as we may still be in construction
        self.constraints.append((not inverse, sources, sinks))

    def prohibit(self, sources, sinks):
        """
        Apply an inverse constraint that prevents certain sources and sinks from
        being linked together. (Alias to constrain(..., inverse=True))

        Args:
            sources: Single source or list of sources
            sinks  : Sink sink or list of sinks
        """
        return self.constrain(sources, sinks, inverse=True)

    def populate(self):
        """ Populate the matrix with constraints """
        for allow, sources, sinks in self.constraints:
            for src in sources:
                for snk in sinks:
                    self.matrix.set(
                        self.src_to_row[src],  # Row index
                        self.sink_to_col[snk], # Column index
                        (1 if allow else 0)    # Value to set (1 -> allow)
                    )

    def separate(self):
        """ Split the problem into subsections. """
        # Perform a separate operation on the matrix - will identify submatrices
        self.subsets = []
        for submatrix, rows, cols in self.matrix.separate():
            self.subsets.append(Problem(
                sources=[self.row_to_src[x] for x in sorted(rows)],
                sinks  =[self.col_to_sink[x] for x in sorted(cols)],
                matrix =submatrix,
            ))
        return self.subsets

    def weight(self):
        """
        Apply weightings to each source connection based on the number of possible
        sinks it can drive
        """
        for r_idx in range(self.matrix.rows):
            row   = self.matrix.row(r_idx)
            r_sum = sum(row)
            for c_idx in range(len(row)):
                self.matrix.set(r_idx, c_idx, row[c_idx] / r_sum)

    def assign(self, single_source=True, single_sink=True):
        """ Assign connections between sources & sinks based on weights

        Args:
            single_source: Only allow source to connect to one sink
            single_sink  : Only allow sink to connect to one source
        """
        # Flatten all cells with non-zero value into a list
        all_cells = []
        for r_idx, row in enumerate(self.matrix.data):
            for c_idx, val in enumerate(row):
                if val == 0: continue
                all_cells.append((r_idx, c_idx, val))
        # Order by the weighting (descending)
        all_cells = sorted(all_cells, key=lambda x: x[2], reverse=True)
        # Build connections
        while len(all_cells) > 0:
            # Pickup the first cell
            row, col, _weight = all_cells[0]
            # Form the connection
            self.connections.append((self.row_to_src[row], self.col_to_sink[col]))
            # Filter out all cells that have this same source
            if single_source: all_cells = [x for x in all_cells if x[0] != row]
            # Filter out all cells that have this same sink
            if single_sink: all_cells = [x for x in all_cells if x[1] != col]
            # If multi-source and multi-sink, just remove the first cell
            if not single_source and not single_sink: all_cells.pop(0)
        # Return the constructed connections
        return self.connections

    def solve(self, single_source=True, single_sink=True):
        """
        Solve the connectivity based on constraints and return each connection
        that is formed.

        Args:
            single_source: Only allow source to connect to one sink
            single_sink  : Only allow sink to connect to one source
        """
        # First populate the matrix with constraints
        self.populate()
        # Prune the matrix - this will store unconnectable sinks & sources
        self.prune()
        # Separate into isolated problems
        connections = []
        u_sub_src   = []
        u_sub_sink  = []
        for subproblem in self.separate():
            # Calculate for each SINK->SOURCE assignment
            self.weight()
            # Gather the connections
            sub_cons = subproblem.assign(
                single_source=single_source, single_sink=single_sink
            )
            connections += sub_cons
            # Extract sources & sinks that were connected
            c_sub_src, c_sub_sink = [], []
            for src, sink in sub_cons:
                c_sub_src.append(src)
                c_sub_sink.append(sink)
            # Pickup any unconnected sources & sinks
            u_sub_src  += [x for x in subproblem.sources if x not in c_sub_src]
            u_sub_sink += [x for x in subproblem.sinks   if x not in c_sub_sink]
        # Return connections and unconnected ports
        return (
            connections,
            list(set(u_sub_src + self.unconnected_source)),
            list(set(u_sub_sink + self.unconnected_sink)),
        )

