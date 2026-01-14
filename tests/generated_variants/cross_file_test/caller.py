import vulnerable_lib

def main():
    user_input = input("Enter something: ")
    # Calling vulnerable functions from another module
    vulnerable_lib.run_command(user_input)
    vulnerable_lib.unsafe_eval(user_input)

if __name__ == "__main__":
    main()
