import os
def cwe22_variant_7(user_input):
    os.path.join('/base/', user_input)

if __name__ == '__main__':
    cwe22_variant_7(input())
