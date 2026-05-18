# ============================================================
# Student Grade Calculator
# TDA Internship - Week 2: Making Decisions & Repeating Tasks
# Author: Ankit Dash
# ============================================================

def display_banner():
    """Display a decorative banner."""
    print("=" * 55)
    print("       📊 STUDENT GRADE CALCULATOR 📊")
    print("=" * 55)
    print()

def calculate_grade(marks):
    """Calculate grade based on marks using if-elif-else."""
    if marks >= 90:
        grade = "A"
        message = "Outstanding! You're a star! 🌟"
    elif marks >= 80:
        grade = "B"
        message = "Very Good! Keep it up! 👍"
    elif marks >= 70:
        grade = "C"
        message = "Good effort! You can do better! 💪"
    elif marks >= 60:
        grade = "D"
        message = "Keep trying! Practice makes perfect! 📚"
    else:
        grade = "F"
        message = "Don't give up! Seek help and try again! 🙏"
    return grade, message

def get_valid_marks():
    """Get valid marks using while loop for input validation."""
    while True:
        try:
            marks = float(input("Enter marks (0-100): "))
            if 0 <= marks <= 100:
                return marks
            else:
                print("⚠️  Invalid! Please enter marks between 0 and 100.")
        except ValueError:
            print("⚠️  Invalid! Please enter a number.")

def display_result(name, marks, grade, message):
    """Display the result in a formatted way."""
    print()
    print("=" * 55)
    print(f"       📋 RESULT FOR {name.upper()}")
    print("=" * 55)
    print(f"  👤 Student  : {name}")
    print(f"  📝 Marks    : {marks}/100")
    print(f"  🎯 Grade    : {grade}")
    print(f"  💬 Message  : {message}")
    print("=" * 55)
    print()

def main():
    """Main function to run the grade calculator."""
    display_banner()

    print("Hello! Let's calculate your grade.")
    print("-" * 55)

    # Get student name
    name = input("Enter student name: ")

    # Get valid marks using while loop
    marks = get_valid_marks()

    # Calculate grade using if-elif-else
    grade, message = calculate_grade(marks)

    # Display result
    display_result(name, marks, grade, message)

    # Ask if user wants to calculate another
    while True:
        another = input("Calculate another student? (yes/no): ").lower()
        if another == "yes":
            print()
            name = input("Enter student name: ")
            marks = get_valid_marks()
            grade, message = calculate_grade(marks)
            display_result(name, marks, grade, message)
        elif another == "no":
            print()
            print("  Thank you for using Grade Calculator! 🚀")
            print("=" * 55)
            break
        else:
            print("⚠️  Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()
