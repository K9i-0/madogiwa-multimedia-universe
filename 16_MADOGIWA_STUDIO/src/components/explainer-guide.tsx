import { useState } from "react";
import DocumentContent from "./document-content";
import { absoluteUrl } from "@/lib/public-data";

export function ExplainerGuide({ slug, markdown }: { slug: string; markdown: string }) {
  const [status, setStatus] = useState("");
  const [fallback, setFallback] = useState("");
  const path = `/episodes/${slug}/guide.md`;
  const url = absoluteUrl(path);
  const request = `次の解説資料を読んで、動画で紹介した制作手順・注意点・プロンプト例を理解してください。\n${url}\n\nその内容を参考に、［ここに作りたいもの・相談したいことを書く］。\nURLを取得できない場合は、その旨を教えてください。Markdown全文を貼り付けます。`;
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
    <h2 id="ai-guide-title">この解説をAIに渡す</h2>
    <p>解説の要点・手順・プロンプト例・台本をまとめました。Markdownを貼り付けるか、URLを読めるAIに渡して相談できます。</p>
    <div className="explainer-guide-actions">
      <button type="button" onClick={() => void copy(markdown, "Markdown")}>Markdownをコピー</button>
      <button type="button" onClick={() => void copy(url, "AI用URL")}>AI用URLをコピー</button>
      <button type="button" onClick={() => void copy(request, "依頼文")}>依頼文をコピー</button>
      <a href={path}>Markdownを開く</a>
    </div>
    <p className="episode-copy-status" role="status" aria-live="polite">{status}</p>
    {fallback && <textarea className="explainer-guide-fallback" aria-label="手動コピー用テキスト" readOnly value={fallback} onFocus={(event) => event.currentTarget.select()} />}
    <p className="production-help">動画制作時点の情報を含みます。実行に必要な画像やAPI設定は、ご自身の環境で用意してください。</p>
    <details><summary>解説資料を読む</summary><DocumentContent text={markdown} format="markdown" /></details>
  </section>;
}
