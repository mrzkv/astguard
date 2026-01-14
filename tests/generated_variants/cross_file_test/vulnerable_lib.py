import os

def run_command(command):
    """Vulnerable function that executes a command."""
    os.system(command)

def unsafe_eval(code):
    """Vulnerable function that evaluates code."""
    eval(code)
