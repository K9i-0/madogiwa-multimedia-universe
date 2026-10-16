import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const record = JSON.parse(fs.readFileSync(path.join(here, 'selected_thumbnail.json')));
const out = path.resolve(process.argv[2] || path.join(here, '../remotion/out/selected_thumbnail_rebuild'));
const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const magick = args => {
  const result = spawnSync('magick', args, {encoding: 'utf8'});
  if (result.status !== 0) throw Error(result.stderr);
};
for (const input of [record.plate, ...Object.values(record.sources)]) {
  if (sha256(path.join(root, input.path)) !== input.sha256) throw Error(`Input changed: ${input.path}`);
}
fs.mkdirSync(out, {recursive: true});
const png = path.join(out, 'thumbnail_youtube.png');
const jpg = path.join(out, 'thumbnail_youtube.jpg');
const args = [path.join(root, record.plate.path), '-filter', 'Lanczos', '-resize', '1280x720!', '-colorspace', 'sRGB'];
for (const {character, x, y, size} of record.layers) {
  args.push('(', path.join(root, record.sources[character].path), '-filter', 'Lanczos', '-resize', `${size}x${size}`, ')', '-geometry', `+${x}+${y}`, '-compose', 'Over', '-composite');
}
magick([...args, '-alpha', 'off', '-strip', png]);
magick([png, '-sampling-factor', '4:4:4', '-quality', '94', '-strip', jpg]);
console.log(JSON.stringify({out, matchesAdopted: {png: sha256(png) === record.outputs.png.sha256, jpg: sha256(jpg) === record.outputs.jpg.sha256}}, null, 2));
