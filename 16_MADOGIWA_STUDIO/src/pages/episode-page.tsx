import { useEffect, useState } from "react";
import { ArrowLeft, ImageIcon, Music2, Paperclip } from "lucide-react";
import { DeferredVideo } from "@/components/deferred-video";
import { DocumentPreview } from "@/components/document-preview";
import { ZoomableImage } from "@/components/image-lightbox";
import { absoluteUrl, episodePoster, type PublicEpisodeDetail, type PublicInputAsset } from "@/lib/public-data";
import "./production-note.css";

export function EpisodePage({ detail }: { detail: PublicEpisodeDetail }) {
  const { episode, videos, productions } = detail;
  const [selected, setSelected] = useState(episode.representative_video_id ?? videos[0]?.id ?? "");
  const [recordOnly, setRecordOnly] = useState<string | null>(null);
  const [returnTo, setReturnTo] = useState("/?page=movies");
  useEffect(() => {
    const requested = location.hash.replace("#making-", "");
    if (videos.some((video) => video.id === requested)) setSelected(requested);
    try {
      const saved = JSON.parse(sessionStorage.getItem("madogiwa-production-return") ?? "null");
      if (saved?.slug === episode.slug && typeof saved.href === "string" && saved.href.startsWith("/") && !saved.href.startsWith("//")) setReturnTo(saved.href);
    } catch { /* Direct visits return to the video list. */ }
  }, [episode.slug, videos]);
  const video = recordOnly ? undefined : videos.find((item) => item.id === selected) ?? videos[0];
  const production = productions.find((item) => item.generation_id === (recordOnly ?? video?.generation_id)) ?? (!video ? productions[0] : undefined);
  const jsonLd = { "@context": "https://schema.org", "@type": "VideoObject", name: episode.title, description: episode.summary || episode.title, thumbnailUrl: [absoluteUrl(episodePoster(detail))], uploadDate: episode.published_at ?? episode.updated_at, contentUrl: video && !video.youtube_id ? absoluteUrl(`/media/${video.id}`) : undefined, embedUrl: video?.youtube_id ? `https://www.youtube-nocookie.com/embed/${video.youtube_id}` : undefined, url: absoluteUrl(`/episodes/${episode.slug}`) };
  return <article className="production-note">
    {video && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />}
    <a className="production-back" href={returnTo}><ArrowLeft size={17} />動画に戻る</a>
    <header className="production-heading"><p>窓際族物語 / {productions.length ? "制作ノート" : "動画"}</p><h1>{episode.title}</h1><p>{episode.summary}</p></header>
    {videos.length > 1 && <label className="production-select">制作バージョン<select value={video?.id} onChange={(event) => { setRecordOnly(null); setSelected(event.target.value); history.replaceState(null, "", `#making-${event.target.value}`); }}>{videos.map((item) => <option key={item.id} value={item.id}>{item.label || "動画"} · v{productions.find((p) => p.generation_id === item.generation_id)?.version ?? "—"}</option>)}</select></label>}
    {productions.some((p) => !videos.some((v) => v.generation_id === p.generation_id)) && <label className="production-select">制作記録<select value={recordOnly ?? ""} onChange={(event) => setRecordOnly(event.target.value || null)}><option value="">公開動画の制作記録</option>{productions.filter((p) => !videos.some((v) => v.generation_id === p.generation_id)).map((p) => <option key={p.generation_id} value={p.generation_id}>v{p.version} · {p.label}（動画なし）</option>)}</select></label>}
    {!video && <p className="production-help">このバージョンは制作記録のみ保存しています。</p>}
    {video && <section className="production-video"><DeferredVideo key={video.id} src={`/media/${video.id}`} youtubeId={video.youtube_id} poster={video.poster_url ?? episodePoster(detail)} label={video.label || episode.title} /></section>}
    {production ? <div id={`making-${video?.id ?? production.generation_id}`} className="production-content">
      {production.model_name && <section className="production-model"><h2>使用モデル</h2><p>{production.model_name || "未登録"}<small>生成 v{production.version} · {production.label}</small></p></section>}
      {production.notes && <section><h2>制作メモ</h2><p style={{whiteSpace:"pre-wrap"}}>{production.notes}</p></section>}
      {production.inputs.length > 0 && <section className="production-inputs"><h2>制作素材 <small>{production.inputs.length}件</small></h2><div className="production-input-grid">{production.inputs.map((asset) => <InputAssetPreview key={asset.id} asset={asset} />)}</div></section>}
      {production.prompt && <section className="production-prompt"><h2>プロンプト</h2><p className="production-help">{production.prompt.label} · revision {production.prompt.version}</p><PromptBody key={production.generation_id} body={production.prompt.body} /></section>}
    </div> : null}
    <a className="production-back production-back-bottom" href={returnTo}><ArrowLeft size={17} />動画に戻る</a>
  </article>;
}

function InputAssetPreview({ asset }: { asset: PublicInputAsset }) {
  const metadata = [asset.group_label, asset.reference_label, asset.filename].filter(Boolean).join(" · ");
  return <article className="episode-input-asset">
    {asset.kind === "image" ? <ZoomableImage src={asset.url} alt={asset.label} caption={asset.label} loading="lazy" buttonClassName="episode-input-preview episode-input-image-trigger" /> : null}
    {asset.kind === "audio" ? <div className="episode-input-audio"><Music2 /><audio src={asset.url} controls preload="none" /></div> : null}
    {asset.kind === "document" || asset.kind === "other" ? <DocumentPreview asset={asset} /> : null}
    <div className="episode-input-copy">
      <span>{asset.kind === "image" ? <ImageIcon /> : asset.kind === "audio" ? <Music2 /> : <Paperclip />}{asset.kind.toUpperCase()}</span>
      <h3>{asset.label}</h3>
      {metadata ? <small>{metadata}</small> : null}
      {asset.notes ? <p>{asset.notes}</p> : null}
    </div>
  </article>;
}

function PromptBody({ body }: { body: string }) {
  const [message, setMessage] = useState("");
  async function copy() {
    try { await navigator.clipboard.writeText(body); setMessage("コピーしました"); }
    catch { setMessage("コピーできませんでした。本文を選択してコピーしてください。"); }
  }
  return <><button className="episode-prompt-copy" onClick={() => void copy()}>プロンプトをコピー</button><span className="episode-copy-status" role="status">{message}</span><pre>{body}</pre></>;
}
