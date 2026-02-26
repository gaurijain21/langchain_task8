% -------- FACTS (15) --------
parent(john, mary).
parent(mary, sue).
parent(john, alex).
parent(alex, david).
parent(david, lily).

male(john).
male(alex).
male(david).

female(mary).
female(sue).
female(lily).
female(anna).

married(john, anna).
married(anna, john).

% -------- RULES (8) --------
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

grandparent(X, Y) :- parent(X, Z), parent(Z, Y).

sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.

mother(X, Y) :- parent(X, Y), female(X).
father(X, Y) :- parent(X, Y), male(X).

spouse(X, Y) :- married(X, Y).

brother(X, Y) :- sibling(X, Y), male(X).
