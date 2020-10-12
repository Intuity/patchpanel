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

from patchpanel.problem import Problem

from .common import Port

# Create input ports on top-level module
clk_in    = Port("clk_in")
rst_in    = Port("rst_in")
misc_a_in = Port("misc_a_in")

# Create output ports on top-level module
clk_out    = Port("clk_out")
rst_out    = Port("rst_out")
misc_b_out = Port("misc_b_out")

# Create I/O on child module A
clk_in_child_a  = Port("clk_in_child_a")
rst_in_child_a  = Port("rst_in_child_a")
rst_out_child_a = Port("rst_out_child_a")

# Create I/O on child module B
clk_in_child_b  = Port("clk_in_child_b")
rst_in_child_b  = Port("rst_in_child_b")
clk_out_child_b = Port("clk_out_child_b")

# Create a connectivity problem
problem = Problem()

# Add sources
problem.add_source(clk_in)
problem.add_source(rst_in)
problem.add_source(misc_a_in)
problem.add_source(rst_out_child_a)
problem.add_source(clk_out_child_b)

# Add sinks
problem.add_sink(clk_out)
problem.add_sink(rst_out)
problem.add_sink(misc_b_out)
problem.add_sink(clk_in_child_a)
problem.add_sink(rst_in_child_a)
problem.add_sink(clk_in_child_b)
problem.add_sink(rst_in_child_b)

# Associate types (misc A & B are left unassociated)
problem.constrain([clk_in, clk_out_child_b], [clk_in_child_a, clk_in_child_b, clk_out])
problem.constrain([rst_in, rst_out_child_a], [rst_in_child_a, rst_in_child_b, rst_out])

# Prevent straight passthrough
problem.prohibit([clk_in], [clk_out])
problem.prohibit([rst_in], [rst_out])

# Solve the problem
conns, u_src, u_sink = problem.solve()

print("Connections:")
for src, sink in conns:
    print(f" - Connecting: {src.name} -> {sink.name}")

print("Unconnected sources:")
for src in u_src: print(f" - {src.name}")

print("Unconnected sinks:")
for sink in u_sink: print(f" - {sink.name}")
