# let's code somthing
# print somthing on console
print("hello world")

# let's take some input from user
name = input("enter your name: ")

def helloto(name):
    print("hello how are you " + name)
    if name == "john":
        print("welcome back john")
    elif name != "john":
        print("i don't know you but welcome " + name)

helloto(name)

# randome number generator
import random
def random_number():
    number = random.randint(1, 100)
    print("your random number is: " + str(number))

random_number()

words = ['cat', 'window', 'defenestrate']
print(words)
for w in words:
    print(w, len(w))

# Create a sample collection
users = {'Hans': 'active', 'Éléonore': 'inactive', '景太郎': 'active'}

# Strategy:  Iterate over a copy
for user, status in users.copy().items():
    if status == 'inactive':
        del users[user]

print(users)

# Strategy:  Create a new collection
active_users = {}
for user, status in users.items():
    if status == 'active':
        active_users[user] = status

print(active_users)
