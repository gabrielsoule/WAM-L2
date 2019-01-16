# WAM-L2

This is a Python implementation of a Warren Abstract Machine without backtracking. 

It does not include a compiler.

Given a set of well-formed WAM instructions, it will attempt to unify the query with the specified program clause, following subgoals to their conclusion. If unification fails, it will not backtrack to the nearest choice point; instead, it will terminate in failure.

A full WAM is coming soon.
