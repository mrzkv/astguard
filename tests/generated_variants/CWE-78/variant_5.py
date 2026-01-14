import os, subprocess
def cwe78_variant_5(user_input):
    subprocess.run(user_input, shell=True)

if __name__ == '__main__':
    cwe78_variant_5(input())
