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

# Output Setup
output_dir = "output/slides"
os.makedirs(output_dir, exist_ok=True)
existing_files = [f for f in os.listdir(output_dir) if f.endswith(".png")]
day_number = len(existing_files) + 1
question_data["day"] = f"Day {day_number}"

# Paths
bg_path = "assets/backgrounds/bg.png"
python_logo_path = "assets/pythonlogo.png"
arrow_path = "assets/rightarrow.png"
difficulty_icon_paths = {
    "easy": "assets/green.png",
    "medium": "assets/yellow.png",
    "hard": "assets/red.png"
}

# Fonts
default_font = ImageFont.load_default()
title_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 80)
question_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 48)
code_font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 44)
arrow_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 42)

# Rounded Corners
def add_rounded_corners(im, radius):
    rounded = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(rounded)
    draw.rounded_rectangle((0, 0, *im.size), radius=radius, fill=255)
    im.putalpha(rounded)
    return im

# Pixel text wrapper
def wrap_lines(text_lines, font, max_width):
    wrapped = []
    for line in text_lines:
        words = line.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    wrapped.append(current_line)
                current_line = word
        if current_line:
            wrapped.append(current_line)
    return wrapped

def estimate_card_height(q_lines, opt_lines, line_height=60):
    total_lines = len(q_lines) + len(opt_lines)
    return max(950, 200 + (total_lines * line_height) + 150)

# Prepare lines
card_width = 1000
max_text_width = card_width - 100
question_lines = wrap_lines(question_data["question"].split("\n"), code_font, max_text_width)
option_lines = [l for opt in question_data["options"] for l in wrap_lines([opt], code_font, max_text_width)]
card_height = estimate_card_height(question_lines, option_lines)

# Create background canvas
background = Image.new("RGB", (1080, 1920), "white")
draw = ImageDraw.Draw(background)

# Header title + logo 
draw.text((60, 130), "Daily Python Questions", font=title_font, fill="black")
draw.text((60, 300), "Practice makes Python. Here's your daily question:", font=question_font, fill="#1f2937")
if os.path.exists(python_logo_path):
    logo = Image.open(python_logo_path).resize((100, 100)).convert("RGBA")
    background.paste(logo, (920, 110), logo)

# Code card
card_x, card_y = 40, 520
code_card = Image.open(bg_path).resize((card_width, card_height)).convert("RGBA")
code_card = add_rounded_corners(code_card, 60)
background.paste(code_card, (card_x, card_y), code_card)

# Inside card drawing
card_draw = ImageDraw.Draw(background)
code_x = card_x + 50
current_y = card_y + 50

# Icon
difficulty = question_data.get("difficulty", "easy").lower()
icon_path = difficulty_icon_paths.get(difficulty)
if icon_path and os.path.exists(icon_path):
    icon = Image.open(icon_path).resize((60, 60)).convert("RGBA")
    background.paste(icon, (code_x, current_y), icon)

# Day label
day_label = question_data["day"]
day_width = card_draw.textlength(day_label, font=title_font)
day_x = card_x + (card_width - day_width) // 2
card_draw.text((day_x, current_y + 8), day_label, font=title_font, fill="white")

# Divider
current_y += 100
card_draw.line((code_x, current_y, card_x + card_width - 50, current_y), fill="white", width=2)
current_y += 40

# Question
for line in question_lines:
    card_draw.text((code_x, current_y), line, font=code_font, fill="white")
    current_y += 60

current_y += 30

# Options
for line in option_lines:
    card_draw.text((code_x, current_y), line, font=code_font, fill="white")
    current_y += 60

# === Swipe Prompt Below Card ===
swipe_text = "Swipe for answer and explanation"
swipe_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 60)
swipe_y = int(card_y + card_height + 80)  # increased spacing below the card

swipe_text_width = draw.textlength(swipe_text, font=swipe_font)
swipe_x = int((1080 - swipe_text_width - 60 - 20) // 2)

draw.text((swipe_x, swipe_y), swipe_text, font=swipe_font, fill="#1f2937")

# Draw right arrow aligned vertically with text
if os.path.exists(arrow_path):
    arrow = Image.open(arrow_path).resize((60, 60)).convert("RGBA")
    text_height = swipe_font.getbbox(swipe_text)[3]
    arrow_y = swipe_y + (text_height // 2) - (60 // 2)  # center arrow
    background.paste(arrow, (int(swipe_x + swipe_text_width + 20), int(arrow_y)), arrow)


# Save slide
output_path = os.path.join(output_dir, f"day_{day_number}.png")
background.save(output_path)
print(f"✅ Slide saved to: {output_path}")
