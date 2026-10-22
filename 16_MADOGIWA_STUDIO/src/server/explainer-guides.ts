import { explainerVideos } from "../lib/explainer-catalog";
import tripoWorkflow from "../content/workflows/tripo-character.md?raw";
import tripo from "../content/explainers/codex-tripo-3d-character-workflow.md?raw";
import wan from "../content/explainers/coding-ai-wan-video-workflow.md?raw";
import stickers from "../content/explainers/codex-animated-line-stickers.md?raw";

// Only editorially reviewed viewer-facing documents belong here. Never export
// generation notes or arbitrary input assets as an explainer guide.
const guides = new Map([
  ["codex-tripo-3d-character-workflow", { youtubeId: explainerVideos["codex-tripo-3d-character-workflow"], markdown: tripo, workflow: tripoWorkflow }],
  ["coding-ai-wan-video-workflow", { youtubeId: explainerVideos["coding-ai-wan-video-workflow"], markdown: wan, workflow: undefined }],
  ["codex-animated-line-stickers", { youtubeId: explainerVideos["codex-animated-line-stickers"], markdown: stickers, workflow: undefined }],
]);

export function getExplainerGuide(slug: string, publicYoutubeIds: (string | null | undefined)[]) {
  const guide = guides.get(slug);
  return guide && publicYoutubeIds.includes(guide.youtubeId) ? guide : undefined;
}
