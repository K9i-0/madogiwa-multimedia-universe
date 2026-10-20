import { ArrowUpRight, GitFork, Smartphone } from "lucide-react";
import "./character-links.css";

const profiles = {
  takosan: {
    handle: "k9i_apps",
    network: "X",
    repository: "K9i-0/madogiwa-multimedia-universe",
    app: { name: "CCPocket", url: "https://k9i-0.github.io/ccpocket/install/" },
  },
  sobaya: {
    handle: "sobaya15",
    network: "Twitter",
    repository: "sobaya-0141/Seedance_Madogiwa",
    app: null,
  },
} as const;

function SocialIcon({ twitter }: { twitter: boolean }) {
  return <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d={twitter
      ? "M23.954 4.57a10 10 0 0 1-2.825.775 4.958 4.958 0 0 0 2.163-2.723 9.99 9.99 0 0 1-3.127 1.195 4.916 4.916 0 0 0-8.384 4.482A13.946 13.946 0 0 1 1.64 3.162a4.916 4.916 0 0 0 1.523 6.558 4.9 4.9 0 0 1-2.229-.616v.061a4.917 4.917 0 0 0 3.946 4.818 4.93 4.93 0 0 1-2.224.084 4.918 4.918 0 0 0 4.588 3.416A9.87 9.87 0 0 1 0 19.518a13.94 13.94 0 0 0 7.548 2.212c9.057 0 14.01-7.503 14.01-14.01 0-.213-.005-.425-.014-.636a10.013 10.013 0 0 0 2.46-2.548z"
      : "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.64 7.584H.47l8.6-9.835L0 1.154h7.594l5.243 6.932 6.064-6.933zm-1.29 19.493h2.039L6.487 3.24H4.3l13.31 17.406z"} />
  </svg>;
}

export function CharacterLinks({ character }: { character: string }) {
  if (character !== "sobaya" && character !== "takosan") return null;
  const profile = profiles[character];
  return <nav className="j-character-links" aria-label="SNS・関連リンク">
    <a className="j-character-social" href={`https://x.com/${profile.handle}`} target="_blank" rel="noopener noreferrer" aria-label={`${profile.network} @${profile.handle}（新しいタブで開く）`}>
      <SocialIcon twitter={character === "sobaya"} />
      <span>@{profile.handle}</span><ArrowUpRight aria-hidden="true" />
    </a>
    <div className="j-character-link-sheet">
      <h2>関連リンク</h2>
      {profile.app && <a href={profile.app.url} target="_blank" rel="noopener noreferrer">
        <Smartphone aria-hidden="true" /><span><strong>{profile.app.name}</strong><small>個人開発アプリ</small></span><ArrowUpRight aria-hidden="true" />
      </a>}
      <a href={`https://github.com/${profile.repository}`} target="_blank" rel="noopener noreferrer">
        <GitFork aria-hidden="true" /><span><strong>窓際族物語の制作リポジトリ</strong><small>GitHub · {profile.repository}</small></span><ArrowUpRight aria-hidden="true" />
      </a>
    </div>
  </nav>;
}
