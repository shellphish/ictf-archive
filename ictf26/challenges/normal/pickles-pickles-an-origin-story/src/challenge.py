import pickle
import base64

with open('/flag.txt') as f:
    flag = f.read().strip()

class PickleJar:
    def __init__(self, pickle_flavor : str, pickle_quantity : int):
        self.pickle_flavor   : str = pickle_flavor
        self.pickle_quantity : int = pickle_quantity

    def __repr__(self):
        return f"Jar of {self.pickle_flavor} pickles ({self.pickle_quantity})"

def pickle_pickles() -> str:
    pickle_flavor = input("Pickle flavor: ")
    pickle_qty    = int(input("Number of pickles: "))
    pickle_jar    = PickleJar(pickle_flavor, pickle_qty)
    pickle_data   = pickle.dumps(pickle_jar)

    return base64.b64encode(pickle_data).decode()

def open_pickled_pickles() -> PickleJar:
    pickle_data = input("Paste pickled pickle jar (base64): ")
    pickle_raw  = base64.b64decode(pickle_data)
    pickle_jar  = pickle.loads(pickle_raw)

    return pickle_jar

def main():
    print("🥒 Welcome to Pickle's Pickles!!! 🥒")
    while True:
        print("1) Pickle Pickle's pickles")
        print("2) Open a pickled pickle jar")
        print("3) Leave :(")

        choice = input("> ")

        if choice == "1":
            print("\nYour pickled pickles:\n", pickle_pickles())
        elif choice == "2":
            print("\nYour unpickled pickles:\n", open_pickled_pickles())
        elif choice == "3":
            break
            print(flag) # oops

if __name__ == '__main__':
    main()
