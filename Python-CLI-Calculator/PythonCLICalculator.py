#!/usr/bin/env python3
"""
CLI Calculator - A command-line calculator with basic arithmetic operations.
"""

def add(a, b):
    """Return the sum of a and b."""
    return a + b

def subtract(a, b):
    """Return the difference of a and b."""
    return a - b

def multiply(a, b):
    """Return the product of a and b."""
    return a * b

def divide(a, b):
    """Return the quotient of a and b."""
    if b == 0:
        return None
    return a / b

def get_number(prompt):
    """Get a valid number from the user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Invalid input! Please enter a number.\n")

def display_menu():
    """Display the calculator menu."""
    print("\n" + "═" * 40)
    print("        CLI CALCULATOR".center(40))
    print("═" * 40)
    print("  [1]  Add (+)")
    print("  [2]  Subtract (-)")
    print("  [3]  Multiply (*)")
    print("  [4]  Divide (/)")
    print("  [5]  Exit")
    print("═" * 40)

def get_choice():
    """Get user's menu choice."""
    while True:
        try:
            choice = int(input("\nYour choice: "))
            if 1 <= choice <= 5:
                return choice
            print("❌ Please select 1, 2, 3, 4, or 5.")
        except ValueError:
            print("❌ Invalid input! Please enter a number (1-5).")

def main():
    """Main program loop."""
    print("\n🎉 Welcome to the Python CLI Calculator! 🎉")
    print("Type numbers and choose operations to calculate.\n")
    
    while True:
        display_menu()
        choice = get_choice()
        
        if choice == 5:
            print("\n👋 Goodbye! Thanks for using the calculator.\n")
            break
        
        print("\n" + "─" * 40)
        num1 = get_number("  Enter first number: ")
        num2 = get_number("  Enter second number: ")
        print("─" * 40)
        
        if choice == 1:
            result = add(num1, num2)
            print(f"\n  {num1} + {num2} = {result}")
        elif choice == 2:
            result = subtract(num1, num2)
            print(f"\n  {num1} - {num2} = {result}")
        elif choice == 3:
            result = multiply(num1, num2)
            print(f"\n  {num1} × {num2} = {result}")
        elif choice == 4:
            result = divide(num1, num2)
            if result is None:
                print("\n  ❌ ERROR: Cannot divide by zero!")
            else:
                print(f"\n  {num1} ÷ {num2} = {result}")
        
        input("\n  Press Enter to continue...")

if __name__ == "__main__":
    main()