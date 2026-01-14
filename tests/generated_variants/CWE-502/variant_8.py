import pickle, yaml
def cwe502_variant_8(user_input):
    pickle.loads(user_input)

if __name__ == '__main__':
    cwe502_variant_8(input())
