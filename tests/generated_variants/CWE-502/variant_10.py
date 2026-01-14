import pickle, yaml
def cwe502_variant_10(user_input):
    pickle.loads(user_input)

if __name__ == '__main__':
    cwe502_variant_10(input())
