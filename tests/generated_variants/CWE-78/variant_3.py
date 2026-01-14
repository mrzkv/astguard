import os, subprocess
def cwe78_variant_3(user_input):
    subprocess.Popen(user_input, shell=True)

if __name__ == '__main__':
    cwe78_variant_3(input())
