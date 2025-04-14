import os
import importlib.util
from PIL import Image, ImageDraw, ImageFont

# Dynamic import
spec = importlib.util.spec_from_file_location("generate_question", "generate_question.py")
generate_question_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_question_module)
generate_question = generate_question_module.generate_question

# Shared Vars
question_data = generate_question()
day_number = len([f for f in os.listdir("output/slides") if f.endswith(".png")]) + 1
question_data["day"] = f"Day {day_number}"

bg_path = "assets/backgrounds/bg.png"
python_logo_path = "assets/pythonlogo.png"
arrow_path = "assets/rightarrow.png"
snake_path = "assets/snake.png"
bulb_path = "assets/lightbulb.png"
difficulty_icon_paths = {
    "easy": "assets/green.png",
    "medium": "assets/yellow.png",
    "hard": "assets/red.png"
}

# Fonts (Fallbacks included)
def load_font(path_list, size):
    for path in path_list:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

title_font = load_font(["/System/Library/Fonts/SFNS.ttf", "/Library/Fonts/Arial.ttf"], 80)
section_font = load_font(["/System/Library/Fonts/SFNS.ttf", "/Library/Fonts/Arial.ttf"], 48)
code_font = load_font(["/System/Library/Fonts/SFNSMono.ttf", "/Library/Fonts/Menlo.ttc"], 44)
answer_font = load_font(["/System/Library/Fonts/SFNSMono.ttf", "/Library/Fonts/Menlo.ttc"], 46)
footer_font = load_font(["/System/Library/Fonts/SFNS.ttf", "/Library/Fonts/Arial.ttf"], 52)

# Helpers
def add_rounded_corners(im, radius):
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, *im.size), radius=radius, fill=255)
    im.putalpha(mask)
    return im

def wrap_lines(text_lines, font, max_width):
    wrapped = []
    for line in text_lines:
        line = line.replace("\t", "    ")  # Replace tab with spaces
        words = line.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if font.getlength(trial) <= max_width:
                current = trial
            else:
                if current:
                    wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)
    return wrapped

def preprocess_code(text):
    """Ensure indented code retains tab structure."""
    lines = text.split("\n")
    return [line.replace("\t", "    ") for line in lines]

def get_card_height(*sections, base=950, line_height=60):
    total_lines = sum(len(s) for s in sections)
    return max(base, 200 + total_lines * line_height + 150)

def paste_icon(draw, bg, icon_path, x, y, size=60):
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).resize((size, size)).convert("RGBA")
        bg.paste(icon, (x, y), icon)

# Generate Question Slide
def generate_question_slide(data):
    os.makedirs("output/slides", exist_ok=True)
    output_path = f"output/slides/day_{day_number}.png"

    q_lines = wrap_lines(preprocess_code(data["question"]), code_font, 900)
    o_lines = [l for opt in data["options"] for l in wrap_lines([opt], code_font, 900)]
    card_height = get_card_height(q_lines, o_lines)

    bg = Image.new("RGB", (1080, 1920), "white")
    draw = ImageDraw.Draw(bg)

    # Header
    draw.text((60, 130), "Daily Python Questions", font=title_font, fill="black")
    draw.text((60, 300), "Practice makes Python. Here's your daily question:", font=section_font, fill="#1f2937")
    paste_icon(draw, bg, python_logo_path, 920, 110)

    # Card
    card = Image.open(bg_path).resize((1000, card_height)).convert("RGBA")
    card = add_rounded_corners(card, 60)
    card_x, card_y = 40, 520
    bg.paste(card, (card_x, card_y), card)
    cd = ImageDraw.Draw(bg)
    cx, cy = card_x + 50, card_y + 50

    paste_icon(draw, bg, difficulty_icon_paths[data["difficulty"].lower()], cx, cy)

    cd.text((card_x + 500 - draw.textlength(data["day"], title_font) // 2, cy + 8), data["day"], font=title_font, fill="white")
    cy += 100
    cd.line((cx, cy, card_x + 950, cy), fill="white", width=2)
    cy += 40

    for line in q_lines:
        cd.text((cx, cy), line, font=code_font, fill="white")
        cy += 60

    cy += 30
    for line in o_lines:
        cd.text((cx, cy), line, font=code_font, fill="white")
        cy += 60

    # Swipe Arrow
    swipe_text = "Swipe for answer and explanation"
    swipe_font = footer_font
    swipe_width = draw.textlength(swipe_text, font=swipe_font)
    swipe_x = (1080 - swipe_width - 80) // 2
    swipe_y = card_y + card_height + 80
    draw.text((swipe_x, swipe_y), swipe_text, font=swipe_font, fill="#1f2937")
    paste_icon(draw, bg, arrow_path, int(swipe_x + swipe_width + 20), int(swipe_y + 10))

    bg.save(output_path)
    print(f"✅ Question slide saved to: {output_path}")
    return card_height

# Generate Answer Slide
def generate_answer_slide(data, card_height):
    os.makedirs("output/answers", exist_ok=True)
    output_path = f"output/answers/day_{day_number}_answer.png"

    q_lines = wrap_lines(preprocess_code(data["question"]), code_font, 900)
    full_answer = next((opt for opt in data["options"] if opt.startswith(data["answer"])), data["answer"])
    answer_lines = wrap_lines([f"Answer: {full_answer}"], answer_font, 900)
    explanation_lines = wrap_lines([data["explanation"]], code_font, 900)

    card_height = get_card_height(q_lines, answer_lines, explanation_lines)

    bg = Image.new("RGB", (1080, 1920), "white")
    draw = ImageDraw.Draw(bg)

    draw.text((60, 130), "Daily Python Questions", font=title_font, fill="black")
    draw.text((60, 300), "Answer & Explanation", font=section_font, fill="#1f2937")
    paste_icon(draw, bg, python_logo_path, 920, 110)

    card = Image.open(bg_path).resize((1000, card_height)).convert("RGBA")
    card = add_rounded_corners(card, 60)
    card_x, card_y = 40, 520
    bg.paste(card, (card_x, card_y), card)
    cd = ImageDraw.Draw(bg)
    cx, cy = card_x + 50, card_y + 50

    paste_icon(draw, bg, difficulty_icon_paths[data["difficulty"].lower()], cx, cy)
    cd.text((card_x + 500 - draw.textlength(data["day"], title_font) // 2, cy + 8), data["day"], font=title_font, fill="white")

    cy += 100
    cd.line((cx, cy, card_x + 950, cy), fill="white", width=2)
    cy += 40

    for line in q_lines:
        cd.text((cx, cy), line, font=code_font, fill="white")
        cy += 60

    cy += 20
    for line in answer_lines:
        cd.text((cx, cy), line, font=answer_font, fill="#22c55e")
        cy += 60

    cy += 10
    for line in explanation_lines:
        cd.text((cx, cy), line, font=code_font, fill="white")
        cy += 60

    # Footer lines
    footer_y = card_y + card_height + 100
    footer_lines = [("Want more Python gems?", snake_path), ("Follow for daily insights and tips", bulb_path)]

    for text, icon_path in footer_lines:
        icon = Image.open(icon_path).resize((70, 70)).convert("RGBA") if os.path.exists(icon_path) else None
        text_w = draw.textlength(text, font=footer_font)
        text_x = (1080 - text_w) // 2
        text_height = footer_font.getbbox(text)[3]
        icon_x = text_x - 80
        icon_y = footer_y + (text_height // 2) - 35
        if icon:
            bg.paste(icon, (int(icon_x), int(icon_y)), icon)
        draw.text((text_x, footer_y), text, font=footer_font, fill="#1f2937")
        footer_y += 90

    bg.save(output_path)
    print(f"✅ Explanation slide saved to: {output_path}")

# Main Call
card_height = generate_question_slide(question_data)
generate_answer_slide(question_data, card_height)
