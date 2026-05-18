# 📊 Student Grade Calculator
### TDA Internship | Week 2: Making Decisions & Repeating Tasks | Ankit Dash

---

## 📌 Project Overview

A Python command-line program that takes a student's name and marks as input, then calculates and displays their grade (A, B, C, D, or F) along with an encouraging message. The program uses if-elif-else logic, input validation with while loops, and modular functions.

---

## 🎯 Objectives

- Use if-elif-else statements for grading logic
- Add input validation (marks 0-100 only) using while loop
- Create reusable functions for clean code structure
- Add encouraging messages for each grade
- Handle invalid inputs gracefully using error handling

---

## 🗂️ Project Structure

```
Week-2-Grade-Calculator/
│
├── grade_calculator.py    # Main program file
├── test_cases.txt         # All test cases with results
├── requirements.txt       # Dependencies (none external)
├── screenshots/           # Program output screenshots
└── README.md              # Project documentation
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8 or higher
- Terminal / Command Prompt

### Steps to Run

```bash
# Step 1: Clone the repository
git clone https://github.com/Ankit-builds1/TDA-DataScience-Internship.git

# Step 2: Navigate to Week 2 folder
cd TDA-DataScience-Internship/Week-2-Grade-Calculator

# Step 3: Run the program
python grade_calculator.py
```

> No external libraries needed!

---

## 💻 Sample Output

```
=======================================================
       📊 STUDENT GRADE CALCULATOR 📊
=======================================================

Hello! Let's calculate your grade.
-------------------------------------------------------
Enter student name: Priya
Enter marks (0-100): 85

=======================================================
📊 RESULT FOR PRIYA:
=======================================================
  Marks   : 85.0/100
  Grade   : B
  Message : Very Good! Keep it up! 👍
=======================================================
```

---

## 📝 Grading Logic

| Marks Range | Grade | Message |
|-------------|-------|---------|
| 90 - 100 | A | Outstanding! You're a star! 🌟 |
| 80 - 89 | B | Very Good! Keep it up! 👍 |
| 70 - 79 | C | Good effort! You can do better! 💪 |
| 60 - 69 | D | Keep trying! Practice makes perfect! 📚 |
| 0 - 59 | F | Don't give up! Seek help and try again! 🙏 |

---

## 🧠 Code Structure & Technical Details

### Functions Used

| Function | Purpose |
|----------|---------|
| `display_banner()` | Prints decorative header |
| `calculate_grade(marks)` | if-elif-else logic, returns grade & message |
| `get_valid_marks()` | while loop with try-except for validation |
| `display_result(name, marks, grade, message)` | Formatted output |
| `main()` | Controls overall program flow |

### Key Python Concepts Applied

- **if-elif-else** — Grading logic based on mark ranges
- **while loop** — Repeats input prompt until valid marks entered
- **try-except** — Handles non-numeric input errors
- **Functions** — Modular, reusable code blocks
- **Comparison operators** — `>=`, `<=`, `==` used in conditions
- **f-strings** — Dynamic formatted output

---

## ✅ Technical Requirements Met

- [x] Used if-elif-else statements for grading logic
- [x] Added input validation (marks 0-100 only)
- [x] Created multiple functions (exceeded requirement of 1)
- [x] Added encouraging messages for each grade
- [x] Used while loop to handle invalid inputs

---

## 🧪 Testing Evidence

See `test_cases.txt` for all 11 test cases including:
- Normal inputs for all 5 grades (A, B, C, D, F)
- Boundary values (0, 90, 100)
- Invalid inputs (>100, negative, text)

---

## 💡 What I Learned

- How if-elif-else works for multiple conditions
- How while loops keep asking until valid input is given
- How try-except handles unexpected errors
- How to break a program into small, clean functions
- Comparison operators and how Python evaluates conditions

---

## 👨‍💻 Author

**Ankit Dash**
- 📧 005ankitdash@gmail.com
- 🏫 Centurion University of Technology & Management, Bhubaneswar
- 🎓 B.Tech - Data Analytics & Machine Learning (2027)
- 🏢 TDA Internship | Data Science Domain | May 2026 Batch

---

*Submitted as part of The Developers Arena (TDA) Internship Program — Week 2 Task*
