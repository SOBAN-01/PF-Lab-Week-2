
import time

# =========================
# CONSTANTS & CREDENTIALS
# =========================

ADMIN_USER = "ecat_admin"
ADMIN_PASS = "ecat@2024"

STUDENT_USER = "student"
STUDENT_PASS = "student123"

CORRECT_MARKS = 4
WRONG_MARKS = -1
SKIP_MARKS = 0

all_results = []

# =========================
# QUESTION BANK (10 MCQs)
# =========================

questions = [
    {"id":1,"subject":"Math","question":"What is 2 + 2?","choices":{"A":"3","B":"4","C":"5","D":"6"},"answer":"B"},
    {"id":2,"subject":"Math","question":"What is 5 x 6?","choices":{"A":"30","B":"25","C":"35","D":"40"},"answer":"A"},
    {"id":3,"subject":"Physics","question":"SI unit of Force is?","choices":{"A":"Joule","B":"Pascal","C":"Newton","D":"Watt"},"answer":"C"},
    {"id":4,"subject":"Physics","question":"Speed of light is approximately?","choices":{"A":"3 x 10^8 m/s","B":"3 x 10^6 m/s","C":"3 x 10^4 m/s","D":"300 m/s"},"answer":"A"},
    {"id":5,"subject":"Chemistry","question":"Chemical symbol of Oxygen is?","choices":{"A":"Ox","B":"O","C":"Og","D":"On"},"answer":"B"},
    {"id":6,"subject":"Chemistry","question":"Water formula is?","choices":{"A":"CO2","B":"NaCl","C":"H2O","D":"O2"},"answer":"C"},
    {"id":7,"subject":"Computer","question":"CPU stands for?","choices":{"A":"Central Process Unit","B":"Central Processing Unit","C":"Computer Processing Unit","D":"Control Processing Unit"},"answer":"B"},
    {"id":8,"subject":"Computer","question":"Python is a?","choices":{"A":"Programming Language","B":"Database","C":"Browser","D":"Operating System"},"answer":"A"},
    {"id":9,"subject":"GK","question":"Capital of Pakistan is?","choices":{"A":"Lahore","B":"Karachi","C":"Islamabad","D":"Peshawar"},"answer":"C"},
    {"id":10,"subject":"GK","question":"How many continents are there?","choices":{"A":"5","B":"6","C":"7","D":"8"},"answer":"C"}
]

def print_header(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)

# =========================
# LOGIN FUNCTIONS
# =========================

def admin_login():
    attempts = 0
    while attempts < 3:
        print_header("ADMIN LOGIN")
        u = input("Username: ").strip()
        p = input("Password: ").strip()

        if u == ADMIN_USER and p == ADMIN_PASS:
            return True

        attempts += 1
        print("Invalid Login")
    return False

def student_login():
    attempts = 0
    while attempts < 3:
        print_header("STUDENT LOGIN")
        u = input("Username: ").strip()
        p = input("Password: ").strip()

        if u == STUDENT_USER and p == STUDENT_PASS:
            name = input("Full Name: ")
            roll = input("Roll Number: ")
            return name, roll

        attempts += 1
        print("Invalid Login")

    return None, None

# =========================
# ADMIN FUNCTIONS
# =========================

def view_questions():
    if len(questions) == 0:
        print("No Questions Available")
        return

    for i in range(len(questions)):
        q = questions[i]
        print(f"\nQuestion {i+1}")
        print("Subject:", q["subject"])
        print(q["question"])

        for k, v in q["choices"].items():
            print(k + ")", v)

        print("Correct Answer:", q["answer"])

def add_question():
    subject = input("Subject: ")
    question = input("Question: ")
    a = input("Option A: ")
    b = input("Option B: ")
    c = input("Option C: ")
    d = input("Option D: ")
    answer = input("Correct Answer: ").upper()

    questions.append({
        "id": len(questions)+1,
        "subject": subject,
        "question": question,
        "choices": {"A":a,"B":b,"C":c,"D":d},
        "answer": answer
    })

    print("Question Added")

def delete_question():
    view_questions()

    num = int(input("Question Number To Delete: "))

    if 1 <= num <= len(questions):
        questions.pop(num-1)
        print("Question Deleted")
    else:
        print("Invalid Number")

def question_bank_statistics():
    subjects = {}

    for q in questions:
        s = q["subject"]
        subjects[s] = subjects.get(s, 0) + 1

    print("Total Questions:", len(questions))

    for s, c in subjects.items():
        print(s, ":", c)

def view_all_results():
    if len(all_results) == 0:
        print("No Results Available")
        return

    for r in all_results:
        print("\nName:", r["name"])
        print("Roll:", r["roll"])
        print("Score:", r["score"])
        print("Percentage:", r["percentage"])
        print("Grade:", r["grade"])
        print("Time:", r["time"])

def view_detailed_result():
    if len(all_results) == 0:
        print("No Results Available")
        return

    for i in range(len(all_results)):
        print(i+1, "-", all_results[i]["name"])

    n = int(input("Select Student: "))

    if not (1 <= n <= len(all_results)):
        return

    result = all_results[n-1]

    for item in result["review"]:
        print("\nQuestion:", item["question"])
        print("Student Answer:", item["student_answer"])
        print("Correct Answer:", item["correct_answer"])

def class_statistics():
    if len(all_results) == 0:
        print("No Results Available")
        return

    scores = [r["score"] for r in all_results]

    print("Highest Score:", max(scores))
    print("Lowest Score:", min(scores))
    print("Average Score:", round(sum(scores)/len(scores),2))

# =========================
# STUDENT FUNCTIONS
# =========================

def view_exam_rules():
    print_header("EXAM RULES")
    print("+4 Correct")
    print("-1 Wrong")
    print("0 Skip")
    print("Type S to Skip")
    print("Type SUBMIT to End Exam")

def start_exam(name, roll):
    correct = 0
    wrong = 0
    skipped = 0
    review = []

    for q in questions:
        print("\n" + q["question"])

        for k,v in q["choices"].items():
            print(k + ")", v)

        ans = input("A/B/C/D/S/SUBMIT: ").upper()

        if ans == "SUBMIT":
            break

        if ans == "S":
            skipped += 1
        elif ans == q["answer"]:
            correct += 1
        else:
            wrong += 1

        review.append({
            "question": q["question"],
            "student_answer": ans,
            "correct_answer": q["answer"]
        })

    score = (correct * CORRECT_MARKS) + (wrong * WRONG_MARKS)
    percentage = (score / (len(questions)*4)) * 100

    if percentage >= 80:
        grade = "EXCELLENT"
    elif percentage >= 65:
        grade = "GOOD"
    elif percentage >= 50:
        grade = "AVERAGE"
    else:
        grade = "BELOW AVERAGE"

    print_header("RESULT")
    print("Name:", name)
    print("Roll:", roll)
    print("Score:", score)
    print("Percentage:", round(percentage,2))
    print("Grade:", grade)

    for item in review:
        print("\nQuestion:", item["question"])
        print("Your Answer:", item["student_answer"])
        print("Correct:", item["correct_answer"])

    all_results.append({
        "name": name,
        "roll": roll,
        "score": score,
        "percentage": round(percentage,2),
        "grade": grade,
        "review": review,
        "time": time.strftime("%d-%m-%Y %H:%M:%S")
    })

def student_menu(name, roll):
    while True:
        print_header("STUDENT PORTAL")
        print("1. Review Official Examination Guidelines Rules")
        print("2. Initialize Standardized Core Test Engine Execution")
        print("3. Logoff Student Session Access Tunnel")

        ch = input("Choice: ")

        if ch == "1":
            view_exam_rules()
        elif ch == "2":
            start_exam(name, roll)
        elif ch == "3":
            break

# =========================
# ADMIN MENU
# =========================

def admin_menu():
    while True:
        print_header("ADMIN PORTAL")

        print("1. View Active Question Bank Inventory")
        print("2. Add New MCQ Blueprint Structure")
        print("3. Delete Target Question Object")
        print("4. Review Question Bank Distribution Metrics")
        print("5. View Global Results Overview Summary")
        print("6. Drill Detailed Question-by-Question Result Record")
        print("7. Calculate Aggregate Class Performance Analytics")
        print("8. Terminate Admin Portal Session Link")

        ch = input("Choice: ")

        if ch == "1":
            view_questions()
        elif ch == "2":
            add_question()
        elif ch == "3":
            delete_question()
        elif ch == "4":
            question_bank_statistics()
        elif ch == "5":
            view_all_results()
        elif ch == "6":
            view_detailed_result()
        elif ch == "7":
            class_statistics()
        elif ch == "8":
            break

# =========================
# MAIN MENU
# =========================

while True:
    print_header("ECAT EXAM APPLICATION")

    print("1. Admin Portal")
    print("2. Student Portal")
    print("3. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        if admin_login():
            admin_menu()

    elif choice == "2":
        name, roll = student_login()

        if name is not None:
            student_menu(name, roll)

    elif choice == "3":
        print("Good Bye")
        break

    else:
        print("Invalid Choice")
