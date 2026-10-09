import { useEffect, useState, type FormEvent } from 'react';
import type { EpisodeDetail } from '@/lib/api';
import { YouTubePlayer } from '@/components/youtube-player';

type Publication = { id:string;youtube_id:string;state:string;is_active:number;checked_at:string|null;generation_id:string|null;is_featured:number };
const states:Record<string,string> = {pending:'確認待ち',processing:'YouTube処理中',waiting_public:'YouTube公開待ち',ready:'公開可能',unavailable:'利用不可',failed:'処理失敗'};
async function request(path:string, body?:unknown) {
  const response = await fetch(`/admin-api/${path}`, body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : undefined);
  if(!response.ok) throw new Error(`操作に失敗しました (${response.status})`);
  return response.json() as Promise<{publications:Publication[]}>;
}
export function YouTubeRegistration({detail,onChanged}:{detail:EpisodeDetail;onChanged:()=>Promise<void>}) {
  const [rows,setRows] = useState<Publication[]>([]), [message,setMessage] = useState(''), [busy,setBusy] = useState(false);
  const episodeId = detail.episode.id;
  useEffect(() => {
    let active=true;
    const refresh=()=>request(`youtube-publications?episodeId=${episodeId}`).then(data=>{if(active)setRows(data.publications);}).catch(()=>{if(active)setMessage('YouTube情報を取得できませんでした');});
    void refresh(); const timer=setInterval(()=>void refresh(),30000);
    return ()=>{active=false;clearInterval(timer);};
  },[episodeId]);
  async function submit(event:FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form=new FormData(event.currentTarget); setBusy(true);setMessage('');
    try {
      await request('youtube-publications',{episodeId,youtubeId:String(form.get('youtubeId')).trim(),generationId:form.get('generationId')||null,contentKind:form.get('contentKind'),productionNotes:form.has('notes'),featured:form.has('featured')});
      setRows((await request(`youtube-publications?episodeId=${episodeId}`)).publications);
      await onChanged();
      setMessage('登録しました。公開・処理完了後、約5分で公式サイトに掲載されます。');
    } catch(error){setMessage(error instanceof Error?error.message:'登録に失敗しました');}finally{setBusy(false);}
  }
  const latest=rows[0];
  return <section className="desk-videos"><h3>YouTube動画</h3><p>公開・処理完了・埋め込み可を確認して掲載します。差し替え待ちの間は現在の動画を表示します。</p>
    <form key={`${episodeId}:${latest?.id}`} onSubmit={submit} className="desk-fields">
      <label>動画ID<input name="youtubeId" pattern="[A-Za-z0-9_-]{11}" required defaultValue={latest?.youtube_id} placeholder="oA2NKFvHfGE" /></label>
      <label>種類<select name="contentKind" defaultValue={detail.episode.content_kind||'story'}><option value="story">物語</option><option value="explainer">解説</option><option value="music">音楽</option><option value="other">その他</option></select></label>
      <label>制作記録<select name="generationId" defaultValue={latest?.generation_id||''}><option value="">紐付けなし</option>{detail.generations.map(g=><option key={g.id} value={g.id}>v{g.version} · {g.label}</option>)}</select></label>
      <label><input name="notes" type="checkbox" defaultChecked={detail.episode.production_notes_enabled===1}/>制作ノートを公開</label>
      <label><input name="featured" type="checkbox" defaultChecked={!!latest?.is_featured}/>イチオシ</label>
      <button disabled={busy}>動画IDと掲載設定を登録</button>
    </form>
    <button disabled={busy} onClick={async()=>{setBusy(true);try{await request('youtube-sync',{});setRows((await request(`youtube-publications?episodeId=${episodeId}`)).publications);setMessage('同期しました');}catch{setMessage('同期できませんでした。次の自動確認で再試行します。');}finally{setBusy(false);}}}>今すぐ公開状態を確認</button>
    <p role="status">{message}</p>
    {rows.map(row=><div key={row.id}><p>{row.is_active?'掲載中':states[row.state]||row.state} · <a href={`https://www.youtube.com/watch?v=${row.youtube_id}`} target="_blank" rel="noreferrer">{row.youtube_id}</a> · 最終確認 {row.checked_at?new Date(row.checked_at).toLocaleString():'未確認'}</p>{row.is_active===1&&<YouTubePlayer id={row.youtube_id} title={detail.episode.title}/>}</div>)}
  </section>;
}
