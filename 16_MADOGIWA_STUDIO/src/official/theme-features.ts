import type { AvailableTheme } from "./site-theme";
import type { Episode } from "./journal-data";

export const themeFeatures: Record<AvailableTheme, { slug: string; character: string; coverAspectRatio: number; note?: string }> = {
  sakaba: { slug: "tako-game-dormitory", character: "yametaro", coverAspectRatio: 854 / 480, note: "やめさん、寝床は選んだほうがいい。" },
  excel: { slug: "professional-window-side-sobaya", character: "sobaya", coverAspectRatio: 832 / 480 },
  underground: { slug: "madogiwa-super-try-underground", character: "yametaro", coverAspectRatio: 854 / 480 },
};

/** Only select playable public entries; unpublished recommendations never leak from a snapshot. */
export function chooseThemeFeature(episodes: Episode[], theme: AvailableTheme): Episode | undefined {
  const available = episodes.filter((episode) => episode.status === "published" && episode.primary_video_id);
  return available.find((episode) => episode.slug === themeFeatures[theme].slug)
    ?? available.find((episode) => episode.has_featured_video === 1)
    ?? available[0];
}
