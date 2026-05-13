# Personal Introduction Program
# TDA Internship - Week 1: Python Basics
# Author: Ankit Dash


def display_welcome_banner():
    """Display a decorative welcome banner."""
    print("=" * 50)
    print("   🎉 PERSONAL INTRODUCTION PROGRAM 🎉")
    print("=" * 50)
    print()

def get_user_info():
    """Collect user information using input() function."""
    print("Hello! Let's get to know you better.")
    print("-" * 50)

    name = input("👤 What is your name? ")
    age = input("🎂 How old are you? ")
    city = input("🏙️  Which city are you from? ")
    hobby = input("🎯 What is your favorite hobby? ")
    dream = input("🌟 What is your dream job? ")

    return name, age, city, hobby, dream

def display_intro(name, age, city, hobby, dream):
    """Display a friendly welcome message with user's information."""
    print()
    print("=" * 50)
    print(f"   ✨ WELCOME, {name.upper()}! ✨")
    print("=" * 50)
    print()
    print(f"  👤 Name    : {name}")
    print(f"  🎂 Age     : {age} years old")
    print(f"  🏙️  City    : {city}")
    print(f"  🎯 Hobby   : {hobby}")
    print(f"  🌟 Dream   : {dream}")
    print()
    print("-" * 50)
    print(f"  Great to meet you, {name}!")
    print(f"  A {age}-year-old from {city} who loves {hobby}.")
    print(f"  Keep chasing your dream of becoming a {dream}! 💪")
    print("-" * 50)
    print()

def main():
    """Main function to run the program."""
    display_welcome_banner()
    name, age, city, hobby, dream = get_user_info()
    display_intro(name, age, city, hobby, dream)
    print("  Thank you for using this program! 🚀")
    print("=" * 50)

if __name__ == "__main__":
    main()
