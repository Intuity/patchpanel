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

def test_single():
    """ Test forming a single connection between two points """
    # Create an input and output
    p_in  = Port("input")
    p_out = Port("output")
    # Create a connectivity problem and add the ports
    problem = Problem()
    problem.add_source(p_in)
    problem.add_sink(p_out)
    # Create a constraint to allow connectivity between the ports
    problem.constrain([p_in], [p_out])
    # Solve the problem
    conns, u_src, u_sink = problem.solve()
    # Check
    assert len(conns) == 1
    assert conns[0][0] == p_in and conns[0][1] == p_out
    assert len(u_src) == 0
    assert len(u_sink) == 0

def test_double():
    """ Test cross connection of four ports """
    # Create I/O
    sources = [Port(f"source_{x}") for x in range(2)]
    sinks   = [Port(f"sink_{x}") for x in range(2)]
    # Setup the problem
    problem = Problem(sources=sources, sinks=sinks)
    # Create cross constraints
    problem.constrain(sources[0], sinks[1])
    problem.constrain(sources[1], sinks[0])
    # Solve the problem
    conns, u_src, u_sink = problem.solve()
    assert len(conns) == 2 and len(u_src) == 0 and len(u_sink) == 0
    assert conns[0][0] == sources[0] and conns[0][1] == sinks[1]
    assert conns[1][0] == sources[1] and conns[1][1] == sinks[0]

def test_unconnected():
    """ Test unconnected ports aren't solved """
    # Create I/O
    sources = [Port(f"source_{x}") for x in range(2)]
    sinks   = [Port(f"sink_{x}") for x in range(2)]
    # Setup the problem
    problem = Problem(sources=sources, sinks=sinks)
    # NOTE: Not adding constraints - so all unconnected
    # Solve the problem
    conns, u_src, u_sink = problem.solve()
    # Check the solution
    assert len(conns) == 0 and len(u_src) == 2 and len(u_sink) == 2
    assert len([x for x in sources if x not in u_src ]) == 0
    assert len([x for x in sinks   if x not in u_sink]) == 0

def test_partial():
    """ Test solving a mix of connected and unconnected ports """
    # Create I/O
    sources = [Port(f"source_{x}") for x in range(4)]
    sinks   = [Port(f"sink_{x}") for x in range(4)]
    # Setup the problem
    problem = Problem()
    for src in sources: problem.add_source(src)
    for sink in sinks: problem.add_sink(sink)
    # Create some constraints
    problem.constrain([sources[0], sources[1]], [sinks[2], sinks[3]])
    # Solve the problem
    conns, u_src, u_sink = problem.solve()
    # Check the solution
    assert len(conns) == 2 and len(u_src) == 2 and len(u_sink) == 2
    for src, sink in conns:
        assert src in [sources[0], sources[1]]
        assert sink in [sinks[2], sinks[3]]
    assert len([x for x in sources if x not in u_src ]) == 2
    assert len([x for x in sinks   if x not in u_sink]) == 2

def test_prohibit():
    """ Test that prohibiting certain pathways stops connectivity """
    # Create I/O
    sources = [Port(f"source_{x}") for x in range(4)]
    sinks   = [Port(f"sink_{x}") for x in range(4)]
    # Setup the problem
    problem = Problem()
    for src in sources: problem.add_source(src)
    for sink in sinks: problem.add_sink(sink)
    # Allow all sources to connect to all sinks
    problem.constrain(sources, sinks)
    # Now prohibit SRC[0] and SRC[1] connecting to SINK[1] and SINK[2]
    problem.prohibit([sources[0], sources[1]], [sinks[1], sinks[2]])
    # Solve the problem
    conns, u_src, u_sink = problem.solve()
    # Check the solution
    assert len(conns) == 4 and len(u_src) == 0 and len(u_sink) == 0
    for src, sink in conns:
        if src in [sources[0], sources[1]]:
            assert sink in [sinks[0], sinks[3]]
        else:
            assert sink in [sinks[1], sinks[2]]

def test_simple_type():
    """ Test a string can be used as the object """
    # Create I/O
    sources = [f"src_{x}" for x in range(2)]
    sinks   = [f"snk_{x}" for x in range(2)]
    # Create the problem
    problem = Problem(sources, sinks)
    # Constrain to allow any-to-any
    problem.constrain(sources, sinks)
    # Solve
    conns, u_src, u_sink = problem.solve()
    # Check the solution
    assert len(conns) == 2 and len(u_src) == 0 and len(u_sink) == 0
    for src, sink in conns:
        assert src in sources
        assert sink in sinks

