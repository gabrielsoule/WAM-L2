# WAM-L2

This is a Python implementation of a Warren Abstract Machine without backtracking. It does not include a compiler.

It's pretty simple. I made it to supplement my WAM research project I did over the winter, during my first year of CS @ UCSB College of Creative Studies. With that in mind, I've also included the final presentation pdf in the repo. It's way cooler than the actual code and I think you chould check it out instead.

Anyway.

Given a set of well-formed WAM instructions, the machine will attempt to unify the query with the specified program clause, following subgoals to their conclusion. If unification fails even once, it will not backtrack to the nearest choice point; instead, it will terminate in failure. 

A full WAM is coming soon, when I have actual free time. 
