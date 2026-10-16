import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const out = path.resolve(here, '../remotion/out/thumbnails_v1');
fs.mkdirSync(out, {recursive: true});
const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const relative = file => path.relative(root, file);
const magick = args => {
  const result = spawnSync('magick', args, {encoding: 'utf8'});
  if (result.status !== 0) throw new Error(result.stderr || 'ImageMagick failed');
  return result.stdout.trim();
};
const sources = Object.fromEntries(['sobaya', 'yametaro', 'yotan'].map(name => [
  name, path.join(root, '27_LINE_STICKERS/sets/01/stickers', name, 'still.png'),
]));
const layouts = {
  a: {name: '制作テーマを大きく', layers: [
    {character: 'yametaro', x: 700, y: 35, size: 270},
    {character: 'yotan', x: 990, y: 40, size: 260},
    {character: 'sobaya', x: 820, y: 325, size: 380},
  ]},
  b: {name: '失敗から学ぶコツ', layers: [
    {character: 'yotan', x: 5, y: 45, size: 240},
    {character: 'sobaya', x: 250, y: 35, size: 280},
    {character: 'yametaro', x: 80, y: 320, size: 380},
  ]},
  c: {name: '完成スタンプを紹介', layers: [
    {character: 'sobaya', x: 70, y: 350, size: 350},
    {character: 'yametaro', x: 465, y: 350, size: 350},
    {character: 'yotan', x: 860, y: 350, size: 350},
  ]},
};
const manifest = {
  title: 'Codexで動くLINEスタンプを作ってみた！失敗から学んだ制作のコツ',
  status: 'candidates-awaiting-user-selection',
  generation: {tool: 'built-in image_gen', mode: 'new typography/background plates', prompts: 'thumbnails/prompts/{a,b,c}_v1.txt'},
  composition: 'ImageMagick: layout and Lanczos resizing of existing transparent PNGs; no character redraw or deformation',
  canvas: {width: 1280, height: 720},
  sources: Object.fromEntries(Object.entries(sources).map(([id, file]) => [id, {path: relative(file), sha256: sha256(file)}])),
  variants: {},
};
for (const [id, layout] of Object.entries(layouts)) {
  const plate = path.join(out, `plate_${id}.png`);
  const dimensions = magick(['identify', '-format', '%w %h', plate]).split(' ').map(Number);
  if (Math.abs(dimensions[0] / dimensions[1] - 16 / 9) > 0.025) {
    throw new Error(`Plate ${id} must be composed as 16:9; received ${dimensions.join('x')}`);
  }
  const png = path.join(out, `thumbnail_${id}.png`);
  const jpg = path.join(out, `thumbnail_${id}.jpg`);
  const args = [plate, '-filter', 'Lanczos', '-resize', '1280x720!', '-colorspace', 'sRGB'];
  for (const {character, x, y, size} of layout.layers) {
    args.push('(', sources[character], '-filter', 'Lanczos', '-resize', `${size}x${size}`, ')', '-geometry', `+${x}+${y}`, '-compose', 'Over', '-composite');
  }
  args.push('-alpha', 'off', '-strip', png);
  magick(args);
  magick([png, '-sampling-factor', '4:4:4', '-quality', '94', '-strip', jpg]);
  const preview = path.join(out, `preview_${id}.jpg`);
  magick([png, '-resize', '960x540', '-background', '#20242a', '-gravity', 'center', '-extent', '992x604', '-font', 'Helvetica-Bold', '-fill', 'white', '-pointsize', '25', '-gravity', 'northwest', '-annotate', '+16+4', id.toUpperCase(), '-quality', '94', preview]);
  manifest.variants[id] = {
    ...layout,
    plate: {path: relative(plate), dimensions, sha256: sha256(plate)},
    png: {path: relative(png), sha256: sha256(png)},
    jpg: {path: relative(jpg), sha256: sha256(jpg), bytes: fs.statSync(jpg).size},
  };
}
magick([...Object.keys(layouts).map(id => path.join(out, `preview_${id}.jpg`)), '-append', '-quality', '93', path.join(out, 'comparison.jpg')]);
fs.writeFileSync(path.join(here, 'candidates_v1.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify({out: relative(out), variants: Object.keys(layouts), comparison: relative(path.join(out, 'comparison.jpg'))}, null, 2));
