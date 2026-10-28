"""Render the proposed lesson's roster with exact, deliberately uneven alignment.

Run: uv run --with pillow build_roster_preview.py
The proposed surname is local to this lesson, not a character canon change.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = Path('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc')
BOLD = Path('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc')
ROWS = [
    ('佐藤 健一', 'left'),
    ('鈴木 美咲', 'left'),
    ('二八 そば屋', 'right'),
    ('高橋 直人', 'left'),
    ('田中 彩', 'left'),
    ('無職 やめ太郎', 'right'),
    ('渡辺 誠', 'left'),
    ('伊藤 遥', 'left'),
]


def main():
    image = Image.new('RGB', (1280, 720), '#ffffff')
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype(str(FONT), 32)
    small = ImageFont.truetype(str(FONT), 22)
    heading = ImageFont.truetype(str(BOLD), 40)
    column_heading = ImageFont.truetype(str(BOLD), 25)
    ink, rule = '#222222', '#707070'

    draw.text((88, 68), '社員名簿', font=heading, fill=ink, anchor='lm')
    draw.text((1192, 76), 'ACCIDENCHUA', font=small, fill='#555555', anchor='rm')
    draw.line((88, 110, 1192, 110), fill=ink, width=2)

    left, split, right, top = 88, 184, 1192, 145
    header, row_height = 48, 56
    bottom = top + header + len(ROWS) * row_height
    draw.rectangle((left, top, right, top + header), fill='#e8e8e8')
    draw.rectangle((left, top, right, bottom), outline=rule, width=2)
    draw.line((split, top, split, bottom), fill=rule, width=2)
    draw.text(((left + split) / 2, top + header / 2), 'No.', font=column_heading, fill=ink, anchor='mm')
    draw.text((split + 24, top + header / 2), '氏名', font=column_heading, fill=ink, anchor='lm')

    for index, (name, align) in enumerate(ROWS):
        y = top + header + index * row_height
        draw.line((left, y, right, y), fill=rule, width=1)
        center = y + row_height / 2
        draw.text(((left + split) / 2, center), str(index + 1), font=small, fill=ink, anchor='mm')
        x, anchor = (right - 24, 'rm') if align == 'right' else (split + 24, 'lm')
        draw.text((x, center), name, font=regular, fill=ink, anchor=anchor)

    output = ROOT / 'roster_right_aligned_preview.png'
    image.save(output)
    print(output)


if __name__ == '__main__':
    main()
