"""المرحلة 1: python phase1_baseline.py"""
import sys
sys.argv.insert(1, "baseline")
import runpy
runpy.run_module("psc_monitor", run_name="__main__")
