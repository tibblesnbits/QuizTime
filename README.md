
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


An interactive terminal-based multiple choice quiz I made while studying for cert exams.
Built in Python. Questions stored in a simple JSON file, easy to add your own.

~*~*~*~

## Features

~ Multiple choice questions with shuffled answer order every run
~ Immediate right/wrong feedback with explanation after each question
~ Running score shown after every question
~ Support for "choose all that apply"
~ Final score with grade label at the end
~ Shuffle mode to randomize question order
~ Easy to add your own questions via JSON or plain text converter

~*~*~*~

## Files

 `quiztime.py`		  | Main quiz script 
 `convert.py` 		  | Convert questions to .json 
 `raw_questions.txt`| Paste questions here for convert.py
 `questions.json`   | Question bank 

~*~*~*~

## Requirements

Python 3.6+

~*~*~*~

## Usage

**Run the quiz:**
python quiztime.py

**Shuffle question order:**
python quiztime.py --shuffle

**Use a different question file:**
python quiztime.py --file myquestions.json

~*~*~*~

## Adding Your Own Questions

Each question follows this format:

json
{
  "question": "Your question text here?",
  "options": ["Choice A", "Choice B", "Choice C", "Choice D"],
  "answer": "Choice B",
  "explanation": "Why this is the correct answer."
}


The `answer` field must match one of the strings in `options` exactly.
The `explanation` field is optional.


~*~*~*~

## License

MIT, go nuts

~*~*~*~

