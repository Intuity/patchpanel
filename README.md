# Patch Panel
Patch Panel is a Python library for solving constrained connectivity between sources and sinks. The sources and sinks can be any arbitrary (hashable) object, and connectivity is returned as a simple list of tuples. This library does not guarantee a unique solution, it simply returns the first legal solution that satisfies all constraints.

## Installing
Easiest way to install Patch Panel is to grab it from PyPI:

```bash
$> pip install patchpanel
```

Alternatively you can install it manually:

```bash
$> git clone git@github.com:Intuity/patchpanel
$> cd patchpanel
$> python3 setup.py install
```

## Example
```python
from patchpanel.problem import Problem
# Create I/O
sources = [f"src_{x}" for x in range(2)]
sinks   = [f"snk_{x}" for x in range(2)]
# Create the problem
problem = Problem(sources, sinks)
# Constrain to allow any-to-any
problem.constrain(sources, sinks)
# Solve
conns, u_src, u_sink = problem.solve()
# Display
print(f"Connections: {conns}")
print(f"Uncon. src : {u_src}")
print(f"Uncon. sink: {u_sink}")
```

## Running Tests
Patch Panel comes with a basic suite of tests, which use `pytest` for regression:

```
$> git clone git@github.com:Intuity/patchpanel
$> cd patchpanel
$> python3 setup.py test
```
