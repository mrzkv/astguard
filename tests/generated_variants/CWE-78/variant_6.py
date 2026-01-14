import os, subprocess
def cwe78_variant_6(user_input):
    subprocess.call(user_input, shell=True)

if __name__ == '__main__':
    cwe78_variant_6(input())
