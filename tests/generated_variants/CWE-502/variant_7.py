import pickle, yaml
def cwe502_variant_7(user_input):
    yaml.load(user_input, Loader=yaml.Loader)

if __name__ == '__main__':
    cwe502_variant_7(input())
