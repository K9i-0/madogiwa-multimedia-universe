import type { SyntheticEvent } from "react";

// YouTube may return an error or a tiny placeholder when maxres is unavailable.
export function fallbackYouTubeThumbnail(event: SyntheticEvent<HTMLImageElement>) {
  const image = event.currentTarget;
  if (/^https:\/\/i\.ytimg\.com\/vi\/[\w-]{11}\/maxresdefault\.jpg$/.test(image.src)
      && (event.type === "error" || image.naturalWidth < 480)) {
    image.src = image.src.replace("maxresdefault.jpg", "hqdefault.jpg");
  }
}
