import os
import importlib.util
from PIL import Image, ImageDraw, ImageFont

# Dynamic import
spec = importlib.util.spec_from_file_location("generate_question", "generate_question.py")
generate_question_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_question_module)
generate_question = generate_question_module.generate_question

# Generate question
question_data = generate_question()

# Output
output_dir = "output/answers"
os.makedirs(output_dir, exist_ok=True)
existing_files = [f for f in os.listdir(output_dir) if f.endswith(".png")]
day_number = len(existing_files) + 1
question_data["day"] = f"Day {day_number}"

# paths
bg_path = "assets/backgrounds/bg.png"
python_logo_path = "assets/pythonlogo.png"
snake_path = "assets/snake.png"
bulb_path = "assets/lightbulb.png"
difficulty_icon_paths = {
    "easy": "assets/green.png",
    "medium": "assets/yellow.png",
    "hard": "assets/red.png"
}

# Fonts
title_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 80)
section_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 48)
code_font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 44)
answer_font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 46)
footer_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 52)

# Rounded Corners
def add_rounded_corners(im, radius):
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, *im.size), radius=radius, fill=255)
    im.putalpha(mask)
    return im

# text wrapping
def wrap_lines(text_lines, font, max_width):
    wrapped = []
    for line in text_lines:
        words = line.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if font.getlength(trial) <= max_width:
                current = trial
            else:
                wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)
    return wrapped

# Layout Calculation
card_width = 1000
max_text_width = card_width - 100
question_lines = wrap_lines(question_data["question"].split("\n"), code_font, max_text_width)
# Use full answer line
full_answer = next((opt for opt in question_data["options"] if opt.startswith(question_data["answer"])), question_data["answer"])
answer_line = f"Answer: {full_answer}"
explanation_lines = wrap_lines([question_data["explanation"]], code_font, max_text_width)

# Estimate card height
line_height = 60
card_height = max(950, 200 + (len(question_lines) + len(explanation_lines) + 2) * line_height)

# Create Base Image
background = Image.new("RGB", (1080, 1920), "white")
draw = ImageDraw.Draw(background)

# Header
draw.text((60, 130), "Daily Python Questions", font=title_font, fill="black")
draw.text((60, 300), "Answer & Explanation", font=section_font, fill="#1f2937")
if os.path.exists(python_logo_path):
    logo = Image.open(python_logo_path).resize((100, 100)).convert("RGBA")
    background.paste(logo, (920, 110), logo)

# Code card
card_x, card_y = 40, 520
code_card = Image.open(bg_path).resize((card_width, card_height)).convert("RGBA")
code_card = add_rounded_corners(code_card, 60)
background.paste(code_card, (card_x, card_y), code_card)

card_draw = ImageDraw.Draw(background)
code_x = card_x + 50
current_y = card_y + 50

# Difficulty Icon
difficulty = question_data.get("difficulty", "easy").lower()
icon_path = difficulty_icon_paths.get(difficulty)
if icon_path and os.path.exists(icon_path):
    icon = Image.open(icon_path).resize((60, 60)).convert("RGBA")
    background.paste(icon, (code_x, current_y), icon)

# Day
day_label = question_data["day"]
day_w = card_draw.textlength(day_label, font=title_font)
card_draw.text((card_x + (card_width - day_w) // 2, current_y + 8), day_label, font=title_font, fill="white")

# Divider
current_y += 100
card_draw.line((code_x, current_y, card_x + card_width - 50, current_y), fill="white", width=2)
current_y += 40

# Question
for line in question_lines:
    card_draw.text((code_x, current_y), line, font=code_font, fill="white")
    current_y += line_height

# Answer (green)
current_y += 20
card_draw.text((code_x, current_y), answer_line, font=answer_font, fill="#22c55e")
current_y += 70

# Explanation
for line in explanation_lines:
    card_draw.text((code_x, current_y), line, font=code_font, fill="white")
    current_y += line_height

# footer and icons
footer_y = card_y + card_height + 100  # Enough spacing but not too low
footer_lines = [
    ("Want more Python gems?", snake_path),
    ("Follow for daily insights and tips", bulb_path)
]

for text, icon_path in footer_lines:
    icon = Image.open(icon_path).resize((70, 70)).convert("RGBA") if os.path.exists(icon_path) else None
    text_w = draw.textlength(text, font=footer_font)
    text_x = (1080 - text_w) // 2
    icon_x = text_x - 80  # Icon sits before text
    text_height = footer_font.getbbox(text)[3]

    if icon:
        icon_y = footer_y + (text_height // 2) - 35  # Vertically center 70px icon
        background.paste(icon, (int(icon_x), int(icon_y)), icon)

    draw.text((text_x, footer_y), text, font=footer_font, fill="#1f2937")
    footer_y += 90  # Spacing between lines

# save
output_path = os.path.join(output_dir, f"day_{day_number}_answer.png")
background.save(output_path)
print(f"✅ Explanation slide saved to: {output_path}")
