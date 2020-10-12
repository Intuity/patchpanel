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

from .matrix import Matrix2D

class Connectivity(object):
    """ Collate the connectivity matrix and constraints """

    def __init__(self, sources=None, sinks=None, matrix=None):
        """ Initialise the connectivity instance

        Args:
            sources: List of sources (must provide sinks & matrix)
            sinks  : List of sinks (must provide sources & matrix)
            matrix : Connectivity matrix (must provide sources & sinks)
        """
        # Check if one of sources, sinks, or matrix is provided - all three are!
        if matrix and None in (sources, sinks):
            raise Exception("If providing matrix, sources & sinks must be given")
        # Create lookup tables for the matrix
        self.src_to_row  = {}
        self.row_to_src  = {}
        self.sink_to_col = {}
        self.col_to_sink = {}
        # If a matrix is provided, adopt it
        if matrix:
            self.matrix = matrix
            for idx, src in enumerate(sources):
                self.src_to_row[src] = idx
                self.row_to_src[idx] = src
            for idx, sink in enumerate(sinks):
                self.sink_to_col[sink] = idx
                self.col_to_sink[idx]  = sink
        # Otherwise construct an empty matrix
        else:
            self.matrix = Matrix2D(default=0)
            if isinstance(sources, list):
                for src in sources: self.add_source(src)
            if isinstance(sinks, list):
                for sink in sinks: self.add_sink(sink)
        # Collect connections & unconnected ports
        self.connections        = []
        self.unconnected_source = []
        self.unconnected_sink   = []

    @property
    def sources(self): return self.src_to_row.keys()

    @property
    def sinks(self): return self.sink_to_col.keys()

    def add_source(self, source):
        """ Add a new source to the connectivity problem.

        Args:
            source: Any object that represents the source, should be unique
        """
        # Check the source is unique
        if source in self.src_to_row:
            raise Exception(f"Source '{source}' is not unique")
        # Add a new row to the matrix
        row_idx = self.matrix.add_row()
        # Update lookup tables
        self.src_to_row[source]  = row_idx
        self.row_to_src[row_idx] = source

    def add_sink(self, sink):
        """ Add a new sink to the connectivity problem.

        Args:
            sink: Any object that represents the sink, should be unique
        """
        # Check that the sink is unique
        if sink in self.sink_to_col:
            raise Exception(f"Sink '{sink}' is not unique")
        # Add a new column to the matrix
        col_idx = self.matrix.add_column()
        # Update lookup tables
        self.sink_to_col[sink]    = col_idx
        self.col_to_sink[col_idx] = sink

    def isolated_sources(self):
        """ Identify sources within a populated matrix that have no solution.

        Returns: List of sources
        """
        return [self.row_to_src[x] for x in self.matrix.empty_rows()]

    def isolated_sinks(self):
        """ Identify sinks within a populated matrix that have no solution.

        Returns: List of sinks
        """
        return [self.col_to_sink[x] for x in self.matrix.empty_columns()]

    def prune(self):
        """ Prune unconnectable sources and sinks from the problem """
        # Run a matrix prune to remove empty rows and columns
        e_rows, e_cols = self.matrix.prune()
        # Store the unconnected sources and sinks & remove from lookups
        for idx in e_rows:
            self.unconnected_source.append(self.row_to_src[idx])
            del self.src_to_row[self.row_to_src[idx]]
            del self.row_to_src[idx]
        for idx in e_cols:
            self.unconnected_sink.append(self.col_to_sink[idx])
            del self.sink_to_col[self.col_to_sink[idx]]
            del self.col_to_sink[idx]
        # Update the indexes to match
        for idx in sorted(self.row_to_src.keys()):
            # Identify the source, and calculate the new row
            src     = self.row_to_src[idx]
            new_idx = idx - sum((1 for x in e_rows if idx > x))
            # Remove existing lookup entry
            del self.row_to_src[idx]
            # Insert the new positions
            self.src_to_row[src]     = new_idx
            self.row_to_src[new_idx] = src
        for idx in sorted(self.col_to_sink.keys()):
            # Identify the sink, and calculate the new column
            sink    = self.col_to_sink[idx]
            new_idx = idx - sum((1 for x in e_cols if idx > x))
            # Remove existing lookup entry
            del self.col_to_sink[idx]
            # Insert the new positions
            self.sink_to_col[sink]    = new_idx
            self.col_to_sink[new_idx] = sink

