# 🎉 Personal Introduction Program
### TDA Internship | Week 1: Python Basics | Ankit Dash

---

## 📌 Project Overview

A beginner-friendly Python program that interactively collects user information (name, age, city, hobby, dream job) and displays a personalized, formatted welcome message. This project demonstrates core Python fundamentals including variables, input/output, functions, and f-strings.

---

## 🎯 Objectives

- Understand and use Python's `input()` and `print()` functions
- Store user data using variables
- Format output using f-strings
- Organize code using functions
- Create an interactive, user-friendly CLI program

---

## 🗂️ Project Structure

```
TDA-Week1-Python-Basics/
│
├── personal_intro.py      # Main program file
├── requirements.txt       # Dependencies (none external)
├── screenshot.png         # Program output screenshot
└── README.md              # Project documentation
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8 or higher installed
- Any terminal / command prompt

### Steps to Run

```bash
# Step 1: Clone the repository
git clone https://github.com/YOUR_USERNAME/TDA-Week1-Python-Basics.git

# Step 2: Navigate to the project folder
cd TDA-Week1-Python-Basics

# Step 3: Run the program
python personal_intro.py
```

> **No external libraries needed!** This project uses only Python built-ins.

---

## 💻 Sample Output

```
==================================================
   🎉 PERSONAL INTRODUCTION PROGRAM 🎉
==================================================

Hello! Let's get to know you better.
--------------------------------------------------
👤 What is your name? Ankit
🎂 How old are you? 21
🏙️  Which city are you from? Bhubaneswar
🎯 What is your favorite hobby? Gaming
🌟 What is your dream job? AI Engineer

==================================================
   ✨ WELCOME, ANKIT! ✨
==================================================

  👤 Name    : Ankit
  🎂 Age     : 21 years old
  🏙️  City    : Bhubaneswar
  🎯 Hobby   : Gaming
  🌟 Dream   : AI Engineer

--------------------------------------------------
  Great to meet you, Ankit!
  A 21-year-old from Bhubaneswar who loves Gaming.
  Keep chasing your dream of becoming a AI Engineer! 💪
--------------------------------------------------

  Thank you for using this program! 🚀
==================================================
```

---

## 🧠 Code Structure & Technical Details

### Functions Used

| Function | Purpose |
|----------|---------|
| `display_welcome_banner()` | Prints decorative header banner |
| `get_user_info()` | Collects 5 inputs from user, returns as tuple |
| `display_intro()` | Formats and displays personalized welcome message |
| `main()` | Orchestrates program flow |

### Key Python Concepts Applied

- **Variables** — Store user inputs (name, age, city, hobby, dream)
- **`input()`** — Capture user data from terminal
- **`print()`** — Display formatted output
- **f-strings** — Dynamic string formatting with variables
- **Functions** — Reusable, modular code blocks
- **`if __name__ == "__main__"`** — Proper Python entry point

---

## ✅ Technical Requirements Met

- [x] Used `input()` to get user information (5 questions)
- [x] Used variables to store all answers
- [x] Used `print()` to display the welcome message
- [x] Added at least 3 questions (added 5)
- [x] Output is friendly and welcoming with emojis and formatting

---

## 🧪 Test Cases

| Input | Expected Output |
|-------|----------------|
| Name: Alex, Age: 20, City: Delhi, Hobby: Reading, Dream: Doctor | Welcome banner with all details formatted correctly |
| Name: Priya, Age: 25, City: Mumbai, Hobby: Singing, Dream: Singer | Personalized message with Priya's details |
| Empty name input | Program accepts and displays empty string (no crash) |

---

## 💡 What I Learned

- How Python programs execute line by line
- How to use `input()` to make programs interactive
- How f-strings make string formatting clean and readable
- How to organize code into functions for reusability
- The importance of comments for code readability
- Using `if __name__ == "__main__"` as proper entry point

---

## 👨‍💻 Author

**Ankit Dash**
- 📧 005ankitdash@gmail.com
- 🏫 Centurion University of Technology & Management, Bhubaneswar
- 🎓 B.Tech - Data Analytics & Machine Learning (2027)
- 🏢 TDA Internship | Data Science Domain | May 2026 Batch

---

*Submitted as part of The Developers Arena (TDA) Internship Program — Week 1 Task*
