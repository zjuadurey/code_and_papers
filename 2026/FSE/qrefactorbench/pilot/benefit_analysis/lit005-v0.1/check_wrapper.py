"""Run the existing wrapper tests with only complete replaced by local lex-DPLL."""
import sys
import pytest
from analysis import lex_dpll
from run import CASE

sys.path.insert(0, str(CASE))
import program

program.complete = lex_dpll
raise SystemExit(pytest.main([str(CASE / "test_program.py"), "-q", "-p", "no:cacheprovider"]))
