import { useState } from "react";
import DocumentContent from "./document-content";
import { absoluteUrl } from "@/lib/public-data";

export function ExplainerGuide({ slug, markdown, workflow }: { slug: string; markdown: string; workflow?: string }) {
  const [status, setStatus] = useState("");
  const [fallback, setFallback] = useState("");
  const path = `/episodes/${slug}/guide.md`;
  const url = absoluteUrl(path);
  const request = workflow
    ? `以下の実行指示書に従って、私の指定内容と添付素材から制作を進めてください。まず利用可能な環境と不足を確認し、必須工程を別方式へ独断で置き換えないでください。\n\n${workflow}`
    : `以下は動画の解説資料です。私が作りたいものと利用環境を確認し、この資料から実行手順を整理してください。必須のツールが不足している場合はその旨と再開方法を示し、別方式へ独断で変更しないでください。動画当時の設定・価格を現在の仕様と区別してください。\n資料URL: ${url}\n\n${markdown}`;
  async function copy(value: string, label: string) {
    try {
      await navigator.clipboard.writeText(value);
      setFallback(""); setStatus(`${label}をコピーしました`);
    } catch {
      setFallback(value); setStatus("コピーできませんでした。下のテキストを選択してコピーしてください。");
    }
  }
  return <section className="explainer-guide" id="ai-guide" aria-labelledby="ai-guide-title">
    <p className="explainer-guide-eyebrow">動画の内容を、次の制作へ</p>
    <h2 id="ai-guide-title">{workflow ? "この方法で作る" : "この解説をAIに渡す"}</h2>
    <p>コピーした指示を、作りたいものや参照画像と一緒にAIへ貼り付けてください。</p>
    <div className="explainer-guide-actions">
      <button type="button" onClick={() => void copy(request, "AIへの指示")}>AIへの指示をコピー</button>
    </div>
    <p className="episode-copy-status" role="status" aria-live="polite">{status}</p>
    {fallback && <textarea className="explainer-guide-fallback" aria-label="手動コピー用テキスト" readOnly value={fallback} onFocus={(event) => event.currentTarget.select()} />}
    <p className="production-help">使えるツールを確認してから進めます。必須ツールが使えない場合は、設定方法を案内します。</p>
    {workflow && <details><summary>制作手順を読む</summary><p><a href={`/episodes/${slug}/workflow.md`}>実行用Markdown</a></p><DocumentContent text={workflow} format="markdown" /></details>}
    <details><summary>動画の解説資料を読む</summary><p><a href={path}>動画資料のMarkdown</a></p><DocumentContent text={markdown} format="markdown" /></details>
  </section>;
}
