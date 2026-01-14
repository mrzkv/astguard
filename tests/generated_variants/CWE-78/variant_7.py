import os, subprocess
def cwe78_variant_7(user_input):
    subprocess.Popen(user_input, shell=True)

if __name__ == '__main__':
    cwe78_variant_7(input())
