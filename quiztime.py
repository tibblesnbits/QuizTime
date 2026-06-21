"""
CompTia Practice Quiz
-----------------------
Reads multiple-choice questions from questions.json and quizzes you
one at a time in the terminal. Tells you right/wrong immediately,
shows an explanation, then shows your running score.

Supports both single-answer and "select all that apply" (multi-select)
questions. The required number of selections is automatically the length of the
"answer" list, no extra field needed. In questions.json:

Usage:
    python quiz.py
    python quiz.py --shuffle      (randomize question order)
    python quiz.py --file myquiz.json   (use a different question file)
"""

import json
import random
import argparse
import sys
import string
import re

DIVIDER = "~*" * 26


def load_questions(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Could not find '{filepath}'. Make sure it's in the same folder as this script.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error reading '{filepath}': {e}")
        sys.exit(1)


def get_multi_choice(prompt, valid_letters, required_count):
    """Ask for exactly `required_count` letters. Accepts any mix of
    separators ('A,C', 'A C', 'A, C') AND no separator at all ('AC').
    Re-prompts on invalid letters or on selecting the wrong number of letters."""
    while True:
        raw = input(prompt).strip().upper()
        chosen = re.findall(r"[A-Z]", raw)
        chosen = list(dict.fromkeys(chosen))  # de-dupe, preserve order

        if not chosen:
            print("  Please enter at least one letter.")
            continue

        invalid = [c for c in chosen if c not in valid_letters]
        if invalid:
            print(f"  Invalid letter(s): {', '.join(invalid)}. Valid options are A-{valid_letters[-1]}.")
            continue

        if len(chosen) != required_count:
            word = "letter" if required_count == 1 else "letters"
            print(f"  Please select exactly {required_count} {word} (you entered {len(chosen)}).")
            continue

        return chosen


def ask_question(q_num, total, q, correct_count):
    print(f"\n  Question {q_num} of {total}")
    print(f"\n  {q['question']}\n")

    is_multi = isinstance(q["answer"], list)
    required_count = len(q["answer"]) if is_multi else 1
    if is_multi:
        print(f"  (Choose {required_count})\n")

    # Shuffle the displayed order of options so memorizing positions doesn't help
    options = q["options"][:]
    random.shuffle(options)

    letters = list(string.ascii_uppercase)[: len(options)]
    for letter, option in zip(letters, options):
        print(f"    {letter}.  {option}")

    if is_multi:
        prompt = f"\n  Your answers: "
    else:
        prompt = "\n  Your answer: "
    chosen_letters = get_multi_choice(prompt, letters, required_count)

    selected = {options[letters.index(c)] for c in chosen_letters}
    correct_set = set(q["answer"]) if is_multi else {q["answer"]}

    print()
    if selected == correct_set:
        print("  ✅  Correct! (っ◕‿◕)っ")
        is_correct = True
        correct_count += 1
    else:
        is_correct = False
        if is_multi:
            print(f"  ❌  Incorrect. (╥﹏╥)")
            print(f"  💡  Correct answers: {', '.join(sorted(correct_set))}")
        else:
            correct_text = q["answer"]
            print(f"  ❌  Incorrect. (╥﹏╥)")
            print(f"  💡  Correct answer: {correct_text}")

    if q.get("explanation"):
        print(f"\n  📝  {q['explanation']}")

    # Running score
    pct = (correct_count / q_num) * 100
    print(f"\n  📊  Score so far: {correct_count}/{q_num} ({pct:.1f}%)")
    print(f"\n{DIVIDER}")

    return is_correct, correct_count


def main():
    parser = argparse.ArgumentParser(description="Interactive multiple-choice quiz.")
    parser.add_argument("--file", default="questions.json", help="Path to questions JSON file")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle question order")
    args = parser.parse_args()

    questions = load_questions(args.file)

    if not questions:
        print("No questions found in the file.")
        return

    if args.shuffle:
        random.shuffle(questions)

    total = len(questions)
    correct_count = 0

    header = r"""
    ██████                ███
  ███░░░░███             ░░░
 ███    ░░███ █████ ████ ████   █████████
░███     ░███░░███ ░███ ░░███  ░█░░░░███
░███   ██░███ ░███ ░███  ░███  ░   ███░
░░███ ░░████  ░███ ░███  ░███    ███░   █
 ░░░██████░██ ░░████████ █████  █████████
   ░░░░░░ ░░   ░░░░░░░░ ░░░░░  ░░░░░░░░░


 ███████████  ███
░█░░░███░░░█ ░░░
░   ░███  ░  ████  █████████████    ██████
    ░███    ░░███ ░░███░░███░░███  ███░░███
    ░███     ░███  ░███ ░███ ░███ ░███████
    ░███     ░███  ░███ ░███ ░███ ░███░░░
    █████    █████ █████░███ █████░░██████
   ░░░░░    ░░░░░ ░░░░░ ░░░ ░░░░░  ░░░░░░

                       by Tibbles & Claude
"""
    print(header)
    print(f"\n{DIVIDER}")
    print(f"  {total} questions")
    print(DIVIDER)

    for i, q in enumerate(questions, start=1):
        _, correct_count = ask_question(i, total, q, correct_count)

    score_pct = (correct_count / total) * 100
    print(f"\n  Final score: {correct_count}/{total} ({score_pct:.1f}%)")

    if score_pct >= 90:
        grade = "Excellent! Exam ready!"
    elif score_pct >= 80:
        grade = "Good! Review your missed questions."
    elif score_pct >= 70:
        grade = "Passing, but keep studying!"
    else:
        grade = "Keep at it, you'll get there."

    print(f"  {grade}")
    print(f"\n{DIVIDER}\n")


if __name__ == "__main__":
    main()
