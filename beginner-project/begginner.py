# python variables
name = "John"
age = 30
height = 1.75

print("Name:", name)
print("Age:", age)
print("Height:", height)

# pthon data types
string_var = "Hello, World!"
integer_var = 42
float_var = 3.14
boolean_var = True
list_var = [1, 2, 3, 4, 5]
tuple_var = (1, 2, 3)
set_var = {1, 2, 3}
dict_var = {"name": "Alice", "age": 25}

print("String:", string_var)
print("Integer:", integer_var)
print("Float:", float_var)
print("Boolean:", boolean_var)
print("List:", list_var)
print("Tuple:", tuple_var)
print("Set:", set_var)
print("Dictionary:", dict_var)

# pythons operators
a = 10
b = 5
# Arithmetic operators
print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
print("Floor Division:", a // b)
print("Modulus:", a % b)
print("Exponentiation:", a ** b) 

# Comparison operators
print("Equal:", a == b)
print("Not Equal:", a != b)
print("Greater Than:", a > b)
print("Less Than:", a < b)
print("Greater Than or Equal:", a >= b)
print("Less Than or Equal:", a <= b)

# Logical operators
x = True
y = False
print("Logical AND:", x and y)
print("Logical OR:", x or y)
print("Logical NOT:", not x)

# Bitwise operators
a = 10
b = 5
print("Bitwise AND:", a & b)
print("Bitwise OR:", a | b)
print("Bitwise XOR:", a ^ b)
print("Bitwise NOT:", ~a)
print("Left Shift:", a << 2)
print("Right Shift:", a >> 2)

# Assignment operators
c = 10
c += 5  # c = c + 5
print("Addition Assignment:", c)
c -= 3  # c = c - 3
print("Subtraction Assignment:", c)
c *= 2  # c = c * 2
print("Multiplication Assignment:", c)
c /= 4  # c = c / 4
print("Division Assignment:", c)
c //= 2  # c = c // 2
print("Floor Division Assignment:", c)
c %= 3  # c = c % 3
print("Modulus Assignment:", c)
c **= 2  # c = c ** 2
print("Exponentiation Assignment:", c)

# Membership operators
list_var = [1, 2, 3, 4, 5]
tuple_var = (1, 2, 3)
set_var = {1, 2, 3}
dict_var = {"name": "Alice", "age": 25}

print("In List:", 3 in list_var)
print("In Tuple:", 3 in tuple_var)
print("In Set:", 3 in set_var)
print("In Dictionary:", "age" in dict_var)

# Identity operators
a = 10
b = 10
print("Identity Equal:", a is b)
print("Identity Not Equal:", a is not b)

# functions and modules
# defining a function
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))

# importing a module
import math

print(math.pi)

# classes and objects in python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, my name is {self.name} and I am {self.age} years old."

person = Person("Alice", 25)
print(person.greet())

# exception handling
try:
    result = 10 / 0
    print(result)
except ZeroDivisionError:
    print("Cannot divide by zero.")

# file handling
# creating a file and writing to it
with open("file.txt", "w") as file:
    file.write("Hello, world!")

# reading from the file
with open("file.txt", "r") as file:
    content = file.read()
    print(content)
