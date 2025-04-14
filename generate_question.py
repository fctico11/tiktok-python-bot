import os
import random
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize openai client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# hardcoded fallback list
fallback_questions = [
    {
        "day": "Day - 1",
        "difficulty": "easy",
        "question": "What is the output of the following Python code?\n\nmy_dict = {'a': 1, 'b': 2, 'c': 3}\nresult = my_dict.values()\nprint(result)",
        "options": ["A) {1, 2, 3}", "B) [1, 2, 3]", "C) {'a': 1, 'b': 2, 'c': 3}", "D) dict_values([1, 2, 3])"],
        "answer": "D",
        "explanation": "`dict.values()` returns a dict_values object, not a list or set."
    },
    {
        "day": "Day - 2",
        "difficulty": "easy",
        "question": "What is the output of the following Python code?\n\ndef uppercase_text(text):\n    return text.upper()\n\nresult = uppercase_text(\"Hello, world!\")\nprint(result)",
        "options": ["A) \"Hello, world!\"", "B) \"HELLO, WORLD!\"", "C) \"hello, world!\"", "D) Error"],
        "answer": "B",
        "explanation": "The `upper()` method converts all characters to uppercase."
    },
]

def fetch_from_openai():
    prompt = (
        "Create a short Python multiple-choice question (MCQ) with 4 options (A-D), one correct answer, "
        "a brief explanation, and a difficulty tag (easy, medium, or hard). It should test Python knowledge "
        "at any level and be suitable for TikTok-style graphic slides.\n\n"
        "Format:\n"
        "Difficulty:\n"
        "Question:\n"
        "Options:\n"
        "Answer:\n"
        "Explanation:"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    content = response.choices[0].message.content
    content = content.replace("```python", "").replace("```", "").replace("`", "")
    return content

def parse_gpt_output(raw):
    try:
        lines = raw.strip().replace("```", "").split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        question_lines = []
        options = []
        answer = ""
        explanation = ""
        difficulty = ""

        print("\n\U0001F9EA Raw lines:")
        for line in lines:
            print(f"> {line}")

        mode = "question"
        for i, line in enumerate(lines):
            if line.lower().startswith("difficulty"):
                difficulty = line.split(":")[-1].strip().lower()
                mode = "question"
            elif re.match(r"^[ABCD][\.\)]\s?.+", line) and mode != "answer":
                print(f"✅ Matched option: {line}")
                options.append(line)
                mode = "options"
            elif line.lower().startswith("answer"):
                answer_line = line.split("Answer:")[-1].strip()
                answer_line = answer_line.replace(")", "").replace(".", "").strip()
                match_letter = re.match(r"^([ABCD])", answer_line)
                if match_letter:
                    answer = match_letter.group(1)
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    match_letter = re.match(r"^([ABCD])", next_line)
                    if match_letter:
                        answer = match_letter.group(1)
                mode = "answer"
            elif line.lower().startswith("explanation"):
                explanation = line.split("Explanation:")[-1].strip()
                mode = "explanation"
            elif mode == "explanation":
                explanation += " " + line
            elif mode == "question":
                question_lines.append(line)

        if not question_lines:
            raise ValueError("Missing question")
        if len(options) != 4:
            raise ValueError(f"Expected 4 options, got {len(options)}: {options}")
        if not answer:
            raise ValueError("Missing answer")
        if not explanation:
            raise ValueError("Missing explanation")

        print("\n✅ Parsed result:")
        print("Difficulty:", difficulty)
        print("Question:", "\n".join(question_lines))
        print("Options:", options)
        print("Answer:", answer)
        print("Explanation:", explanation)

        question_text = "\n".join(question_lines).replace("Question:", "").replace("Options:", "").strip()

        return {
            "difficulty": difficulty,
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": explanation
        }

    except Exception as e:
        print(f"❌ Failed to parse GPT output: {e}")
        return random.choice(fallback_questions)

def generate_question():
    try:
        raw = fetch_from_openai()
        print("\U0001F4E6 GPT raw response:\n", raw)
        return parse_gpt_output(raw)
    except Exception as e:
        print(f"❌ Error calling OpenAI: {e}")
        return random.choice(fallback_questions)

if __name__ == "__main__":
    from pprint import pprint
    print("\u26A1 Running question generator...")
    pprint(generate_question())
