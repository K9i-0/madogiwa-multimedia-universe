"""Export LINE animated main and static tab from the approved drawn poses."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import build as b

ROOT = b.ROOT
SOURCE = ROOT / 'source/animation/02_hataraiteruka/poses'
ORDER = [0, 1, 3, 4, 5]
DURATIONS = [450, 150, 170, 200, 2030]


def fitted(art, size, padding):
    out = Image.new('RGBA', size)
    art = b.outline(art)
    scale = min((size[0] - 2 * padding) / art.width,
                (size[1] - 2 * padding) / art.height)
    art = art.resize((round(art.width * scale), round(art.height * scale)),
                     Image.Resampling.LANCZOS)
    out.alpha_composite(art, ((size[0] - art.width) // 2,
                             (size[1] - art.height) // 2))
    return out


def main():
    poses = [Image.open(SOURCE / f'{i:02d}.png').convert('RGBA') for i in ORDER]
    # A single crop and scale across every frame keeps the approved motion intact.
    boxes = [im.getbbox() for im in poses]
    box = (max(0, min(v[0] for v in boxes) - 5),
           max(0, min(v[1] for v in boxes) - 5),
           min(512, max(v[2] for v in boxes) + 5),
           min(512, max(v[3] for v in boxes) + 5))
    frames = [fitted(im.crop(box), (240, 240), 8) for im in poses]
    frames[0].save(ROOT / 'main.png', save_all=True, append_images=frames[1:],
                   duration=DURATIONS, loop=1, disposal=0, blend=0,
                   optimize=True, compress_level=9, dpi=(72, 72))
    frames[0].save(ROOT / 'main-still.png', dpi=(72, 72))
    # Small chat icon: retain the mask, mug and gripping hand; omit tiny lettering.
    tab_box = (10, 32, 378, 315)
    tab = fitted(poses[0].crop(tab_box), (96, 74), 3)
    tab.save(ROOT / 'tab.png', optimize=True, dpi=(72, 72))
    for bg in ['white', 'black']:
        previews = []
        for frame in frames:
            panel = Image.new('RGBA', (410, 280), bg)
            panel.alpha_composite(frame, (10, 30))
            panel.alpha_composite(tab, (270, 110))
            draw = ImageDraw.Draw(panel)
            font = ImageFont.truetype(b.FONT, 13, index=0)
            ink = 'black' if bg == 'white' else 'white'
            draw.text((10, 7), 'main 240×240 APNG', font=font, fill=ink)
            draw.text((265, 85), 'tab 96×74 PNG', font=font, fill=ink)
            previews.append(panel.convert('RGB'))
        b.gif(previews, DURATIONS, ROOT / f'main-tab-{bg}-preview.gif')
        previews[0].save(ROOT / f'main-tab-{bg}-preview.png')
    (ROOT / 'reports/listing-source.json').write_text(json.dumps({
        'source': str(SOURCE.relative_to(ROOT)), 'poseOrder': ORDER,
        'durationsMs': DURATIONS, 'mainCommonCrop': box, 'tabCrop': tab_box,
        'method': 'Approved original drawings; fixed crop, outline and resize only',
        'design': 'Text-free mask and beer mug; no manually added play symbol',
        'guidelinesChecked': '2026-10-15',
        'officialSources': [
            'https://creator.line.me/ja/guideline/animationsticker/',
            'https://creator.line.me/ja/guideline/animationsticker/detail/']
    }, ensure_ascii=False, indent=2) + '\n')
    print('Created main.png (240x240 APNG) and tab.png (96x74 PNG)')


if __name__ == '__main__':
    main()
