import hashlib
def cwe327_variant_1():
    hashlib.sha1(b'test')

if __name__ == '__main__':
    cwe327_variant_1()
