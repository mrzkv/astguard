import pickle, yaml
def cwe502_variant_9(user_input):
    yaml.load(user_input, Loader=yaml.Loader)

if __name__ == '__main__':
    cwe502_variant_9(input())
