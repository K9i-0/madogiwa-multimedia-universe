import { fallbackYouTubeThumbnail } from "@/lib/youtube-thumbnail";
import { useEffect, useId, useState } from "react";
import { Play } from "lucide-react";
import "./youtube-player.css";

export function YouTubePlayer({ id, title, poster, autoPlay = false, start, end }: {
  id: string; title: string; poster?: string; autoPlay?: boolean; start?: number; end?: number;
}) {
  const [started, setStarted] = useState(autoPlay);
  const playerId = useId();
  useEffect(() => {
    const stopOther = (event: Event) => {
      if ((event as CustomEvent<string>).detail !== playerId) setStarted(false);
    };
    window.addEventListener("madogiwa-youtube-play", stopOther);
    if (started) {
      window.dispatchEvent(new CustomEvent("madogiwa-youtube-play", { detail: playerId }));
      document.querySelectorAll<HTMLMediaElement>("video, audio").forEach((media) => media.pause());
    }
    return () => window.removeEventListener("madogiwa-youtube-play", stopOther);
  }, [started, playerId]);
  if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return <p role="alert">YouTube動画IDが正しくありません。</p>;
  const params = new URLSearchParams({ autoplay: "1", playsinline: "1", rel: "0" });
  if (start !== undefined) params.set("start", String(Math.max(0, Math.floor(start))));
  if (end !== undefined) params.set("end", String(Math.ceil(end)));
  return <div className="youtube-video">
    {started ? <iframe title={title} src={`https://www.youtube-nocookie.com/embed/${id}?${params}`}
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      allowFullScreen referrerPolicy="strict-origin-when-cross-origin" /> :
      <button type="button" className="deferred-video" aria-label={`${title}を再生`} onClick={() => setStarted(true)}>
        <img onError={fallbackYouTubeThumbnail} onLoad={fallbackYouTubeThumbnail} src={poster || `https://i.ytimg.com/vi/${id}/maxresdefault.jpg`} alt="" loading="lazy" />
        <span className="play-circle"><Play fill="currentColor" /></span>
      </button>}
    <a href={`https://www.youtube.com/watch?v=${id}${start ? `&t=${Math.floor(start)}s` : ""}`} target="_blank" rel="noreferrer">YouTubeで見る ↗</a>
  </div>;
}
