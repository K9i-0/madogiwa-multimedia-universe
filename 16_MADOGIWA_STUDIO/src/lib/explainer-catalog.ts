// Public identifiers only; full documents stay in the server module.
export const explainerVideos: Record<string, string> = {
  "flutter-scene-3d-game": "81XlfHfG8N4",
  "codex-tripo-3d-character-workflow": "hCWMw1nB43A",
  "coding-ai-wan-video-workflow": "RMWefLVS9vQ",
  "codex-animated-line-stickers": "PJ3ak1m-Itg",
};
export function hasExplainerGuide(slug: string, youtubeId?: string | null) {
  return Object.hasOwn(explainerVideos, slug) && explainerVideos[slug] === youtubeId;
}
