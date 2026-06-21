"""
convert.py
----------
Converts a raw copy/pasted LMS test export into questions.json for quiztime.py.

(Copying from a Canvas test- you just need to manually mark the correct answer(s) with a ***)

EXPECTED INPUT FORMAT (this is what you paste/save into raw_questions.txt):

    Question 28
    6 / 6 pts
    How does Blockchain use cryptography to ensure the integrity of data?

      It uses cryptographic hash algorithms to encrypt transactions.
      It uses cryptographic hash algorithms to record transactions.
      It uses symmetric cryptographic algorithms to record transactions.
      It uses asymmetric cryptographic algorithms to record transactions.

    Blockchain relies heavily on cryptographic hash algorithms, most notably
    SHA-256, to record its transactions. This makes it computationally
    infeasible to try to replace a block or insert a new block of information
    without the approval of all entities involved.

    Correct answer
    Question 29
    ...

HOW TO MARK THE CORRECT ANSWER:
    Add *** immediately after the correct option's text. 
      Example:
      The key(s) used by algorithms must be securely guarded.***

    For "Choose 2" style questions, just mark
    every correct option with *** the same way. The converter automatically
    detects multiple *** marks and saves the answer as a multi-select
    question for quiztime.py:
      Bad cables or connectors***
      VLAN configuration
      dB loss***
      Port security

WHAT GETS IGNORED AUTOMATICALLY (no need to delete these yourself):
    - "Question N" lines           -> used only as a block separator
    - "X / Y pts" lines             -> discarded
    - blank lines / single-space lines -> discarded
    - "Wrong answer" / "Correct answer" lines -> discarded

WHAT GETS KEPT:
    - The question text (the first non-indented line(s) after the pts line)
    - The options (the indented lines)
    - The explanation (the paragraph after the options, before the next
      "Question N" or "Wrong/Correct answer" line)

Usage:
    python convert.py
    python convert.py --file raw_questions.txt --out questions.json
"""

import json
import re
import argparse
import sys

QUESTION_HEADER_RE = re.compile(r"^question\s+\d+\s*$", re.IGNORECASE)
PTS_LINE_RE = re.compile(r"^\d+\s*/\s*\d+\s*pts?\s*$", re.IGNORECASE)
RESULT_LINE_RE = re.compile(r"^(wrong answer|correct answer)\s*$", re.IGNORECASE)
CORRECT_MARKER = "***"


def split_blocks(text):
    """Split the raw text into a list of (question_number, lines) blocks,
    using 'Question N' lines as the boundary."""
    lines = text.splitlines()
    blocks = []
    current_lines = []
    current_num = None

    for line in lines:
        m = re.match(r"^question\s+(\d+)\s*$", line.strip(), re.IGNORECASE)
        if m:
            if current_lines and current_num is not None:
                blocks.append((current_num, current_lines))
            current_num = m.group(1)
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines and current_num is not None:
        blocks.append((current_num, current_lines))

    return blocks


def is_indented(line):
    """True if the line has leading whitespace (i.e. it's an option line)."""
    return line != line.lstrip() and line.strip() != ""


def parse_block(q_num, lines):
    idx = 0
    n = len(lines)

    def skip_blanks():
        nonlocal idx
        while idx < n and lines[idx].strip() == "":
            idx += 1

    # 1. Skip the "X / Y pts" line if present
    skip_blanks()
    if idx < n and PTS_LINE_RE.match(lines[idx].strip()):
        idx += 1

    # 2. Question text: consecutive non-blank, non-indented lines
    skip_blanks()
    question_parts = []
    while idx < n:
        line = lines[idx]
        if line.strip() == "":
            break
        if is_indented(line):
            break
        question_parts.append(line.strip())
        idx += 1
    question_text = " ".join(question_parts).strip()

    # 3. Options: consecutive indented lines (blank lines between are skipped)
    skip_blanks()
    options = []
    correct_answers = []
    while idx < n:
        line = lines[idx]
        if line.strip() == "":
            idx += 1
            continue
        if not is_indented(line):
            break
        opt_raw = line.strip()
        is_correct = opt_raw.endswith(CORRECT_MARKER)
        opt_text = opt_raw[: -len(CORRECT_MARKER)].strip() if is_correct else opt_raw
        options.append(opt_text)
        if is_correct:
            correct_answers.append(opt_text)
        idx += 1

    # 4. Explanation: remaining non-blank lines, stopping at "Wrong/Correct answer"
    explanation_parts = []
    while idx < n:
        line = lines[idx]
        stripped = line.strip()
        if stripped == "":
            idx += 1
            continue
        if RESULT_LINE_RE.match(stripped):
            idx += 1
            continue
        explanation_parts.append(stripped)
        idx += 1
    explanation = " ".join(explanation_parts).strip()

    # Validation
    if not question_text:
        print(f"  Skipped Question {q_num}: no question text found.")
        return None
    if len(options) < 2:
        print(f"  Skipped Question {q_num} ('{question_text[:50]}...'): fewer than 2 options found.")
        return None
    if not correct_answers:
        print(f"  Skipped Question {q_num} ('{question_text[:50]}...'): no answer marked with {CORRECT_MARKER}.")
        return None

    # Single *** -> answer is a plain string. Multiple *** -> answer is a list (multi-select).
    answer_value = correct_answers[0] if len(correct_answers) == 1 else correct_answers

    result = {
        "question": question_text,
        "options": options,
        "answer": answer_value,
    }
    if explanation:
        result["explanation"] = explanation

    return result


def convert(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    blocks = split_blocks(text)
    questions = []
    for q_num, lines in blocks:
        parsed = parse_block(q_num, lines)
        if parsed:
            questions.append(parsed)

    return questions, len(blocks)


def main():
    parser = argparse.ArgumentParser(
        description="Convert raw LMS test export (with *** marking correct answers) into quiz JSON."
    )
    parser.add_argument("--file", default="raw_questions.txt", help="Input raw text file")
    parser.add_argument("--out", default="questions.json", help="Output JSON file")
    args = parser.parse_args()

    try:
        questions, total_blocks = convert(args.file)
    except FileNotFoundError:
        print(f"Could not find '{args.file}'.")
        sys.exit(1)

    if not questions:
        print("No valid questions parsed. Check your formatting and *** markers.")
        sys.exit(1)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)

    skipped = total_blocks - len(questions)
    print(f"\nConverted {len(questions)} of {total_blocks} questions into '{args.out}'.")
    if skipped:
        print(f"{skipped} question(s) were skipped — see warnings above.")


if __name__ == "__main__":
    main()
