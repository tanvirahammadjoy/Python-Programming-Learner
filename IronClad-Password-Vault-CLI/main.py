from utils import generate_password, password_strength
from datetime import datetime


def get_bool_input(prompt):
    while True:
        val = input(prompt + " (y/n): ").lower()
        if val in ["y", "n"]:
            return val == "y"
        print("⚠️ Please enter 'y' or 'n'")


def get_length():
    while True:
        try:
            length = int(input("Enter password length: "))
            if length < 4:
                print("⚠️ Minimum length is 4")
                continue
            return length
        except ValueError:
            print("❌ Please enter a valid number")


def save_to_file(password):
    with open("vault.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} -> {password}\n")
    print("💾 Saved to vault.txt")


def main():
    print("🔐 Welcome to IronClad Password Vault")

    length = get_length()
    use_upper = get_bool_input("Include Uppercase?")
    use_lower = get_bool_input("Include Lowercase?")
    use_digits = get_bool_input("Include Numbers?")
    use_symbols = get_bool_input("Include Symbols?")

    try:
        password = generate_password(
            length, use_upper, use_lower, use_digits, use_symbols
        )

        print(f"\n🔑 Generated Password: {password}")
        print(f"📊 Strength: {password_strength(password)}")

        if get_bool_input("Save to file?"):
            save_to_file(password)

    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()