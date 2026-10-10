import { z } from 'zod';
import { HttpError } from './http';

export const youtubeRegistrationSchema = z.object({
 episodeId:z.string().uuid(), generationId:z.string().uuid().nullable().optional(),
 youtubeId:z.string().regex(/^[A-Za-z0-9_-]{11}$/), featured:z.boolean().default(false),
 contentKind:z.enum(['story','explainer','music','other']).default('story'),
 productionNotes:z.boolean().default(false),
});
export type Publication = {id:string;episode_id:string;generation_id:string|null;legacy_video_id:string|null;youtube_id:string;state:string;is_active:number;is_featured:number;thumbnail_url:string|null;created_at:string;checked_at:string|null};
export async function listYouTubePublications(db:D1Database, episodeId?:string) {
 const rows=(await db.prepare(`SELECT p.*, s.checked_at AS sync_checked_at FROM youtube_publications p
 LEFT JOIN youtube_sync_status s ON s.id=1 AND p.created_at<=s.checked_at
 ${episodeId ? 'WHERE episode_id=?' : ''} ORDER BY created_at DESC`).bind(...(episodeId?[episodeId]:[])).all<Publication & {sync_checked_at:string|null}>()).results;
 return rows.map(({sync_checked_at,...row})=>({...row,checked_at:row.checked_at && sync_checked_at && sync_checked_at>row.checked_at ? sync_checked_at : row.checked_at}));
}
// One heartbeat per successful full scan, never a write per unchanged video.
export async function recordYouTubeSync(db:D1Database,startedAt:string) {
 return db.prepare(`INSERT INTO youtube_sync_status(id,checked_at) VALUES(1,?)
 ON CONFLICT(id) DO UPDATE SET checked_at=excluded.checked_at
 WHERE excluded.checked_at>youtube_sync_status.checked_at`).bind(startedAt).run();
}
export async function registerYouTube(db:D1Database,input:z.infer<typeof youtubeRegistrationSchema>,actor:string) {
 const episode=await db.prepare('SELECT id FROM episodes WHERE id=?').bind(input.episodeId).first();
 if(!episode)throw new HttpError(404,'作品が見つかりません');
 if(input.productionNotes && !input.generationId)throw new HttpError(400,'制作ノートには生成バージョンを指定してください');
 if(input.generationId && !await db.prepare('SELECT id FROM generations WHERE id=? AND episode_id=?').bind(input.generationId,input.episodeId).first())throw new HttpError(400,'生成バージョンが作品と一致しません');
 const existing=await db.prepare('SELECT * FROM youtube_publications WHERE youtube_id=?').bind(input.youtubeId).first<Publication>();
 if(existing && existing.episode_id!==input.episodeId)throw new HttpError(409,'このYouTube動画は別の作品に登録済みです');
 const id=existing?.id ?? crypto.randomUUID();
 await db.batch([
  db.prepare(`INSERT INTO youtube_publications(id,episode_id,generation_id,youtube_id,is_featured,created_at,created_by) VALUES(?,?,?,?,?,?,?) ON CONFLICT(youtube_id) DO UPDATE SET generation_id=excluded.generation_id,is_featured=excluded.is_featured`).bind(id,input.episodeId,input.generationId??null,input.youtubeId,Number(input.featured),new Date().toISOString(),actor),
  db.prepare('UPDATE episodes SET content_kind=?,production_notes_enabled=?,updated_at=? WHERE id=?').bind(input.contentKind,Number(input.productionNotes),new Date().toISOString(),input.episodeId),
 ]);
 return (await listYouTubePublications(db,input.episodeId)).find(p=>p.id===id)!;
}
type YouTubeVideo = {id:string;snippet:{channelId:string;title:string;thumbnails?:Record<string,{url:string}>};status:{privacyStatus:string;uploadStatus:string;embeddable:boolean};processingDetails?:{processingStatus?:string}};
async function boundedJson(response:Response):Promise<unknown>{
 if(!response.ok)throw new Error(`YouTube upstream HTTP ${response.status}`);
 const reader=response.body?.getReader();if(!reader)throw new Error('Empty upstream response');
 const chunks:Uint8Array[]=[];let size=0;
 while(true){const {value,done}=await reader.read();if(done)break;size+=value.byteLength;if(size>2_000_000){await reader.cancel();throw new Error('Oversized upstream response');}chunks.push(value);}
 const bytes=new Uint8Array(size);let at=0;for(const chunk of chunks){bytes.set(chunk,at);at+=chunk.length;}return JSON.parse(new TextDecoder().decode(bytes));
}
export function publicationState(video:YouTubeVideo|undefined):string{
 if(!video || video.snippet.channelId!=='UCyQtPu94OaiGxFdd2A6bXdw')return 'unavailable';
 if(['failed','rejected','deleted'].includes(video.status.uploadStatus) || ['failed','terminated'].includes(video.processingDetails?.processingStatus??''))return 'failed';
 if(video.status.uploadStatus!=='processed' || (video.processingDetails?.processingStatus && video.processingDetails.processingStatus!=='succeeded'))return 'processing';
 if(video.status.privacyStatus!=='public')return 'waiting_public';
 return video.status.embeddable ? 'ready' : 'unavailable';
}
export async function applyYouTubeStatus(db:D1Database,row:Publication,video:YouTubeVideo|undefined){
 const state=publicationState(video), now=new Date().toISOString();
 const thumbs=video?.snippet.thumbnails;const thumbnail=thumbs?.maxres?.url??thumbs?.standard?.url??thumbs?.high?.url??null;
 const title=video?.snippet.title??null, privacy=video?.status.privacyStatus??null;
 const processing=video?.processingDetails?.processingStatus??null, embeddable=Number(video?.status.embeddable??false);
 // Compare against the database (not a possibly stale scan) and handle nullable fields.
 const statements=[db.prepare(`UPDATE youtube_publications SET state=?,thumbnail_url=?,youtube_title=?,privacy_status=?,processing_status=?,embeddable=?,checked_at=?,is_active=CASE WHEN ?='ready' THEN is_active ELSE 0 END
 WHERE id=? AND (state IS NOT ? OR thumbnail_url IS NOT ? OR youtube_title IS NOT ?
 OR privacy_status IS NOT ? OR processing_status IS NOT ? OR embeddable IS NOT ?
 OR checked_at IS NULL OR (?!='ready' AND is_active!=0))`)
 .bind(state,thumbnail,title,privacy,processing,embeddable,now,state,row.id,state,thumbnail,title,privacy,processing,embeddable,state)];
 if(state==='ready'){
  // Only the most recently registered candidate may replace the current release.
  const latest=`(SELECT id FROM youtube_publications WHERE episode_id=? ORDER BY created_at DESC,id DESC LIMIT 1)`;
  statements.push(db.prepare(`UPDATE youtube_publications SET is_active=0 WHERE episode_id=? AND is_active=1 AND id!=? AND ?=${latest}`).bind(row.episode_id,row.id,row.id,row.episode_id));
  statements.push(db.prepare(`UPDATE youtube_publications SET is_active=1 WHERE id=? AND is_active=0 AND id=${latest}`).bind(row.id,row.episode_id));
 }
 const results=await db.batch(statements);
 return results.reduce((total,result)=>total+result.meta.rows_written,0);
}
export async function syncYouTube(env:Env){
 const startedAt=new Date().toISOString();
 let rowsWritten=0;
 const rows=await listYouTubePublications(env.DB);if(!rows.length)return {checked:0};
 const auth=await boundedJson(await env.YOUTUBE_AUTH.fetch('https://youtube-auth.madogiwa.work/admin/access-token',{method:'POST',headers:{Authorization:`Bearer ${env.YOUTUBE_AUTH_ADMIN_TOKEN}`},signal:AbortSignal.timeout(20000)})) as {access_token:string;channel_id:string};
 if(auth.channel_id!=='UCyQtPu94OaiGxFdd2A6bXdw'||!auth.access_token)throw new Error('Unexpected YouTube authorization');
 for(let i=0;i<rows.length;i+=50){
  const batch=rows.slice(i,i+50),params=new URLSearchParams({part:'snippet,status,processingDetails',id:batch.map(r=>r.youtube_id).join(','),fields:'items(id,snippet(channelId,title,thumbnails),status(privacyStatus,uploadStatus,embeddable),processingDetails(processingStatus))'});
  const data=await boundedJson(await fetch(`https://www.googleapis.com/youtube/v3/videos?${params}`,{headers:{Authorization:`Bearer ${auth.access_token}`},signal:AbortSignal.timeout(20000)})) as {items:YouTubeVideo[]};
  if(!Array.isArray(data.items))throw new Error('Invalid YouTube response');
  for(const row of batch)rowsWritten+=await applyYouTubeStatus(env.DB,row,data.items.find(v=>v.id===row.youtube_id));
 }
 rowsWritten+=(await recordYouTubeSync(env.DB,startedAt)).meta.rows_written;
 return {checked:rows.length,rowsWritten};
}
