# Historical implementation

`WFM4Cities_2.6_original.py` is an unmodified copy of the single-file script
published before the 3.0 refactor. It is retained only for provenance and
comparison.

It is excluded from the installed wheel, source distribution, linting, and
tests. Do not use it as the maintained entry point because importing it creates
Tk windows and depends on module-level global state.
