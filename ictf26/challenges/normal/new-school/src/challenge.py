import hashlib
import secrets

secret = secrets.token_bytes(16)
with open('/flag.txt') as f:
    flag = f.read().strip()

class_size = 20

def return_to_office():
    print(f"""
You found them! Good job!
...wow...that is a weird name...
*the secretary turns to the student*
Is your name really {flag}? I don't remember you registering here.
    """)
    exit()

def main():
    print("""
It's your first day at a new school.
You need to register at the main office.
I've heard they have a really advanced method of assigning IDs...
    """)
    name  = input('Enter your name: ')
    grade = input('Enter your grade: ')
    dob   = input('Enter your date of birth: ')
    print("Using state-of-the-art post-quantum agentic workflow to compute student ID....")
    new_id = hashlib.sha256((name + grade + dob).encode()).hexdigest()[:7]
    print(f"""
*the secretary seems surprised*
It looks like there is an error in our database!!! :O
I thought we designed these to be unique.
Go find the student you are matching with.
Your ID: {new_id}
""")

    while True:
        print("Choose your next action:\n1) Check classroom\n2) Go home :(")
        choice = int(input("Action: "))

        if choice == 1:
            class_num = int(input("Check a classroom: "))
            if class_num < 1:
                raise Exception("Invalid classroom!")
            for student_num in range(class_size):
                stu_index = class_num * class_size + student_num
                stu_id = hashlib.sha256(secret + (str(stu_index)).encode()).hexdigest()[:7]
                if stu_id == new_id:
                    return_to_office()
                print(f"Student {student_num}'s ID: {stu_id} ")
        elif choice == 2:
            exit()
        else:
            print("Try again...")

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception:
            continue
