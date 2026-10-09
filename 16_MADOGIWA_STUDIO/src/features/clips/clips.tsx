import { YouTubePlayer } from "@/components/youtube-player";
import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { Link } from "@tanstack/react-router";
import {
  ArrowLeft,
  ArrowUpRight,
  Copy,
  Play,
  Share2,
  X,
} from "lucide-react";
import catalog from "./catalog.json";
import { Route as RootRoute } from "@/routes/__root";
import { useSiteTheme } from "@/official/site-theme";
import {
  ThemeSwitcher,
  DesktopChrome,
  ExcelFormula,
  WorkSheet,
} from "@/official/episode-themes";
import { Noren } from "@/official/sakaba-entrance";
import "@/official/journal.css";
import "@/official/sakaba.css";
import "./clips.css";

export const clips = catalog;
export type Clip = (typeof clips)[number] & { youtube_id?: string; source_youtube_id?: string; youtube_start?: number; youtube_end?: number };
export const CLIPS_PER_PAGE = 18;
const seconds = (clip: Clip) => `${clip.seconds.toFixed(1)}秒`;

function Player({ clip }: { clip: Clip }) {
  const [playing, setPlaying] = useState(false);
  if (clip.youtube_id) return <YouTubePlayer id={clip.youtube_id} title={clip.title} poster={clip.poster} start={clip.youtube_start} end={clip.youtube_end} />;
  return (
    <div className="clips-player">
      {playing ? (
        <video
          src={clip.video}
          poster={clip.poster}
          controls
          autoPlay
          playsInline
          preload="metadata"
          onPlay={(event) => {
            document.querySelectorAll("video").forEach((video) => {
              if (video !== event.currentTarget) video.pause();
            });
          }}
        />
      ) : (
        <button
          className="clips-play"
          onClick={() => setPlaying(true)}
          aria-label={`${clip.title}を再生`}
        >
          <img src={clip.poster} alt="" loading="lazy" />
          <span>
            <Play size={24} fill="currentColor" />
          </span>
          <small>音声つき · {seconds(clip)}</small>
        </button>
      )}
    </div>
  );
}

function MainVideoDialog({ clip }: { clip: Clip }) {
  const [open, setOpen] = useState(false);
  const [failed, setFailed] = useState(false);
  return (
    <Dialog.Root
      open={open}
      onOpenChange={(nextOpen) => {
        if (nextOpen) {
          document
            .querySelectorAll("video, audio")
            .forEach((media) => (media as HTMLMediaElement).pause());
          setFailed(false);
        }
        setOpen(nextOpen);
      }}
    >
      <Dialog.Trigger asChild>
        <button className="clips-source-link">
          <Play size={14} />
          本編を再生
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="clips-dialog-overlay" />
        <Dialog.Content
          className="clips-video-dialog"
          aria-describedby={undefined}
        >
          <div className="clips-dialog-heading">
            <Dialog.Title>第{clip.episode}話 · 本編</Dialog.Title>
            <Dialog.Close asChild>
              <button aria-label="本編を閉じる">
                <X size={22} />
              </button>
            </Dialog.Close>
          </div>
          {open && (clip.source_youtube_id ? <YouTubePlayer id={clip.source_youtube_id} title={`第${clip.episode}話の本編`} autoPlay /> :
            <video
              src={clip.source}
              controls
              autoPlay
              playsInline
              preload="metadata"
              aria-label={`第${clip.episode}話の本編`}
              onError={() => setFailed(true)}
            />
          )}
          {failed && (
            <p role="alert">
              本編を読み込めませんでした。閉じてからもう一度お試しください。
            </p>
          )}
          {clip.episodeSlug && (
            <a
              className="clips-dialog-episode"
              href={`https://madogiwa.work/episodes/${clip.episodeSlug}`}
              target="_blank"
              rel="noreferrer"
            >
              本編の詳細を見る
              <ArrowUpRight size={14} />
            </a>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function Actions({ clip }: { clip: Clip }) {
  const [copied, setCopied] = useState(false);
  const [fallbackUrl, setFallbackUrl] = useState("");
  async function copy() {
    const url = new URL(`/clips/${clip.id}`, window.location.origin).href;
    try { await navigator.clipboard.writeText(url); setCopied(true); setFallbackUrl(""); }
    catch { setFallbackUrl(url); }
  }
  return <div className="clips-actions-wrap"><div className="clips-actions">
    {clip.youtube_id && <a href={`https://www.youtube.com/watch?v=${clip.youtube_id}${clip.youtube_start ? `&t=${Math.floor(clip.youtube_start)}s` : ""}`} target="_blank" rel="noreferrer"><Share2 size={17} />YouTubeで開く・共有</a>}
    <button onClick={() => void copy()}><Copy size={17} />{copied ? "コピーしました" : "ページURLをコピー"}</button>
  </div>{fallbackUrl && <input readOnly value={fallbackUrl} aria-label="共有URL" onFocus={(event) => event.target.select()} />}</div>;
}

function Shell({ children }: { children: React.ReactNode }) {
  const { clipTheme } = RootRoute.useLoaderData();
  const { theme, changeTheme } = useSiteTheme(clipTheme ?? undefined);
  const [working, setWorking] = useState(false);
  return (
    <div className="clips-shell">
      <DesktopChrome
        theme={theme}
        working={working}
        onToggleWork={() => {
          document
            .querySelectorAll("video, audio")
            .forEach((media) => (media as HTMLMediaElement).pause());
          setWorking((value) => !value);
        }}
      />
      <header className="j-header clips-site-header">
        {theme === "sakaba" && <Noren />}
        <div className="j-header-main">
          <a href={`/?theme=${theme}`} className="j-brand">
            <img src="/site/sobaya-icon.jpg" alt="" />
            <span>
              窓際族物語<small>公式サイト</small>
              {theme === "sakaba" && (
                <i className="j-sakaba-seal" aria-hidden="true">
                  窓際
                </i>
              )}
            </span>
          </a>
          <nav aria-label="作品メニュー">
            <a href={`/?theme=${theme}`}>ホーム</a>
            <a href={`/episodes?theme=${theme}`}>本編一覧</a>
          </nav>
          <ThemeSwitcher
            theme={theme}
            onChange={changeTheme}
            onOpen={() => {}}
          />
        </div>
      </header>
      {theme === "excel" && <ExcelFormula title="迷言・迷場面集" />}
      {theme === "excel" && working && (
        <WorkSheet onClose={() => setWorking(false)} />
      )}
      <div hidden={theme === "excel" && working}>{children}</div>
      <footer className="clips-footer">
        <b>窓際族物語</b>
        <span>迷言・迷場面集</span>
        <small>© MADOGIWAZOKU MONOGATARI</small>
      </footer>
      {theme === "excel" && (
        <nav className="e-sheet-tabs" aria-label="ワークシート">
          <a href="/?theme=excel">ホーム</a>
          <a href="/episodes?theme=excel">動画</a>
          <a href="/clips?theme=excel" aria-current="page">
            迷言・迷場面集
          </a>
        </nav>
      )}
    </div>
  );
}

export function ClipsPage({ page, items = clips }: { page: number; items?: Clip[] }) {
  const pageCount = Math.max(1, Math.ceil(items.length / CLIPS_PER_PAGE));
  const currentPage = Math.min(page, pageCount);
  const offset = (currentPage - 1) * CLIPS_PER_PAGE;
  const visibleClips = items.slice(offset, offset + CLIPS_PER_PAGE);
  return (
    <Shell>
      <main className="clips-main">
        <header className="clips-heading">
          <h1>迷言・迷場面集</h1>
          <p>SNS、チャットツールにおすすめ</p>
        </header>
        <div className="clips-results">
          <h2>クリップ一覧</h2>
          <span aria-live="polite">{items.length} 本</span>
        </div>
        <div className="clips-grid">
          {visibleClips.map((clip) => (
            <article className="clips-card" key={clip.id}>
              <Player clip={clip} />
              <div className="clips-card-body">
                <div className="clips-card-meta">
                  <span>{clip.character}</span>
                  <span>
                    第{clip.episode}話 · {clip.kind}
                  </span>
                </div>
                <h3>
                  <Link to="/clips/$slug" params={{ slug: clip.id }}>
                    {clip.title}
                  </Link>
                </h3>
                <div className="clips-card-info">
                  <span>#{clip.tag}</span>
                  <span>
                    {seconds(clip)}
                  </span>
                </div>
                <Actions clip={clip} />
                <MainVideoDialog clip={clip} />
              </div>
            </article>
          ))}
        </div>
        {pageCount > 1 && (
          <nav className="clips-pagination" aria-label="クリップのページ送り">
            {currentPage > 1 ? (
              <Link to="/clips" search={{ page: currentPage - 1 }} resetScroll>
                前へ
              </Link>
            ) : (
              <span aria-disabled="true">前へ</span>
            )}
            <span aria-live="polite">
              {currentPage} / {pageCount}
            </span>
            {currentPage < pageCount ? (
              <Link to="/clips" search={{ page: currentPage + 1 }} resetScroll>
                次へ
              </Link>
            ) : (
              <span aria-disabled="true">次へ</span>
            )}
          </nav>
        )}
      </main>
    </Shell>
  );
}

export function ClipPage({ clip }: { clip: Clip }) {
  return (
    <Shell>
      <main className="clips-main clips-detail">
        <Link className="clips-back" to="/clips">
          <ArrowLeft size={16} />
          迷言・迷場面集へ
        </Link>
        <div className="clips-detail-grid">
          <section>
            <Player clip={clip} />
            <div className="clips-detail-caption">
              <span>
                第{clip.episode}話 ／ {clip.character}
              </span>
              <span>{seconds(clip)} · 音声つき</span>
            </div>
          </section>
          <section className="clips-detail-info">
            <div className="clips-eyebrow">
              {clip.kind} ／ #{clip.tag}
            </div>
            <h1>{clip.title}</h1>
            <p>この一幕を、会話のおともに。</p>
            <Actions clip={clip} />
            <div className="clips-source-box">
              <h2>第{clip.episode}話</h2>
              <MainVideoDialog clip={clip} />
              {clip.episodeSlug && (
                <a
                  href={`https://madogiwa.work/episodes/${clip.episodeSlug}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  公式サイトで第{clip.episode}話を見る
                  <ArrowUpRight size={14} />
                </a>
              )}
            </div>
          </section>
        </div>
        <p className="clips-guide">ページURLをコピーして、この一幕を共有できます。</p>
        <aside className="clips-detail-next">
          <b>ほかの一幕も、のぞいていく？</b>
          <Link to="/clips">
            迷言・迷場面集へ
            <ArrowUpRight size={18} />
          </Link>
        </aside>
      </main>
    </Shell>
  );
}
