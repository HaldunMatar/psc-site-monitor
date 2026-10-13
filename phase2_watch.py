"""المرحلة 2: python phase2_watch.py"""
import sys
sys.argv.insert(1, "watch")
import runpy
runpy.run_module("psc_monitor", run_name="__main__")
