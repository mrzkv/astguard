import pickle, yaml
def cwe502_variant_3(user_input):
    yaml.load(user_input, Loader=yaml.Loader)

if __name__ == '__main__':
    cwe502_variant_3(input())
