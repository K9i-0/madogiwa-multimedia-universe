const SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.force-ssl'];
const enc = new TextEncoder();
const b64 = b => btoa(String.fromCharCode(...b)).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
const unb64 = s => Uint8Array.from(atob(s.replaceAll('-', '+').replaceAll('_', '/')), c => c.charCodeAt(0));
const random = () => b64(crypto.getRandomValues(new Uint8Array(32)));
const hash = async s => b64(new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(s))));
const now = () => Math.floor(Date.now() / 1000);
const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const headers = {'Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY'};
const json = (data, status=200) => new Response(JSON.stringify(data), {status, headers:{...headers,'Content-Type':'application/json'}});
function page(text, status=200, extra='', nonce='', formPage=false) {
  return new Response(`<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>窓際族物語 YouTube連携</title><body><main><h1>窓際族物語 YouTube連携</h1><p>${escape(text)}</p>${extra}</main></body></html>`, {status, headers:{...headers,'Referrer-Policy':formPage?'same-origin':'no-referrer','Content-Type':'text/html; charset=utf-8','Content-Security-Policy':`default-src 'none'; script-src ${nonce ? `'nonce-${nonce}'` : "'none'"}; form-action 'self' ${formPage?'https://accounts.google.com':''}; base-uri 'none'; frame-ancestors 'none'`}});
}
async function seal(value, secret) {
  const key = await crypto.subtle.importKey('raw', unb64(secret), 'AES-GCM', false, ['encrypt']);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const cipher = await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:enc.encode('mmu-youtube-refresh-v1')},key,enc.encode(value));
  return `${b64(iv)}.${b64(new Uint8Array(cipher))}`;
}
async function unseal(value, secret) {
  const [iv,cipher] = value.split('.');
  const key = await crypto.subtle.importKey('raw',unb64(secret),'AES-GCM',false,['decrypt']);
  return new TextDecoder().decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:unb64(iv),additionalData:enc.encode('mmu-youtube-refresh-v1')},key,unb64(cipher)));
}
async function admin(request, env) {
  if (!env.ADMIN_TOKEN) return false;
  return (await hash(request.headers.get('Authorization') || '')) === (await hash(`Bearer ${env.ADMIN_TOKEN}`));
}
async function boundedText(response, limit=131072) {
  const reader = response.body?.getReader();
  if (!reader) throw new Error('empty_upstream');
  let size=0; const chunks=[];
  while (true) {
    const {done,value}=await reader.read(); if (done) break;
    size+=value.length; if(size>limit){await reader.cancel();throw new Error('large_upstream');} chunks.push(value);
  }
  const data = new Uint8Array(size);let at=0;for(const chunk of chunks){data.set(chunk,at);at+=chunk.length;}
  return new TextDecoder().decode(data);
}
async function boundedJson(response) { return JSON.parse(await boundedText(response)); }
async function tokenRequest(fields, upstream) {
  const response = await upstream('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(fields),signal:AbortSignal.timeout(15000)});
  const data=await boundedJson(response);
  if(!response.ok || typeof data.access_token!=='string') throw new Error(data.error==='invalid_grant'?'reauthorization_required':'token_exchange_failed');
  return data;
}
/** @param {Request} request @param {Env} env */
export async function handle(request,env,upstream=fetch) {
  const url=new URL(request.url);
  if(url.origin!==env.PUBLIC_ORIGIN) return page('正規の認証URLを使用してください。',400);
  if(request.method==='GET' && url.pathname==='/health') return json({ok:true,configured:!!(env.GOOGLE_CLIENT_ID && env.GOOGLE_CLIENT_SECRET && env.TOKEN_KEY && env.ADMIN_TOKEN)});
  if(request.method==='GET' && url.pathname==='/privacy') return page('プライバシーポリシー（2026年10月9日）',200,`<h2>用途と取得情報</h2><p>窓際族物語の公式チャンネル運営者向け連携です。チャンネルID・名称・許可された権限・認証トークンを取得し、動画投稿、投稿後の編集、チャンネル確認に使います。Googleのパスワードは取得しません。</p><h2>保存と共有</h2><p>継続利用用トークンは暗号化してCloudflare D1に保存します。運用担当者は認証付き管理機能で短期トークンを取得しGoogle/YouTube APIへアクセスします。GoogleとCloudflareを処理・保存に利用します。連携データの広告利用・販売は行いません。投稿動画と説明文はYouTubeへ送信され、公開範囲は動画ごとの設定に従います。</p><h2>解除と削除</h2><p>Googleアカウントのサードパーティ接続設定から許可を取り消せます。保存した連携情報の削除は youtube@madogiwa.work へご連絡ください。情報は連携運用に必要な期間保持し、削除依頼に応じ運用担当者が削除します。連携解除だけでは投稿済み動画は削除されません。</p><h2>Google APIデータ</h2><p>Google APIから取得した情報の利用・他アプリへの転送は、Limited Use要件を含むGoogle API Services User Data Policyに従います。</p><p><a href="https://developers.google.com/terms/api-services-user-data-policy">Google API Services User Data Policy</a> / <a href="https://myaccount.google.com/connections">Googleアカウントの接続設定</a></p><p>連絡先：youtube@madogiwa.work</p>`);
  if(request.method==='GET' && url.pathname==='/') return page('公式チャンネル所有者向けの連携受付です。担当者から受け取った招待URLを開いてください。');
  if(url.pathname.startsWith('/admin/')) {
    if(!await admin(request,env)) return json({error:'unauthorized'},401);
    if(request.method==='POST' && url.pathname==='/admin/invitations') {
      if(!env.GOOGLE_CLIENT_ID || !env.GOOGLE_CLIENT_SECRET || !env.TOKEN_KEY) return json({error:'oauth_not_configured'},503);
      const token=random(),expires=now()+86400;
      await env.DB.batch([env.DB.prepare('DELETE FROM invitations WHERE expires < ?').bind(now()),env.DB.prepare('DELETE FROM sessions WHERE expires < ?').bind(now()),env.DB.prepare('INSERT INTO invitations(hash,expires) VALUES(?,?)').bind(await hash(token),expires)]);
      return json({url:`${env.PUBLIC_ORIGIN}/connect#${token}`,expires},201);
    }
    if(request.method==='GET' && url.pathname==='/admin/status') {
      const record=await env.DB.prepare('SELECT channel_id,title,scopes,updated FROM connections WHERE channel_id=?').bind(env.EXPECTED_CHANNEL_ID).first();
      return json({connected:!!record,connection:record});
    }
    if(request.method==='POST' && url.pathname==='/admin/access-token') {
      const row=await env.DB.prepare('SELECT encrypted_refresh FROM connections WHERE channel_id=?').bind(env.EXPECTED_CHANNEL_ID).first();
      if(!row) return json({error:'not_connected'},409);
      const tokens=await tokenRequest({client_id:env.GOOGLE_CLIENT_ID,client_secret:env.GOOGLE_CLIENT_SECRET,refresh_token:await unseal(row.encrypted_refresh,env.TOKEN_KEY),grant_type:'refresh_token'},upstream);
      return json({access_token:tokens.access_token,expires_in:tokens.expires_in,channel_id:env.EXPECTED_CHANNEL_ID});
    }
    return json({error:'not_found'},404);
  }
  if(request.method==='GET' && url.pathname==='/connect') {
    const nonce=random();
    return page('公式チャンネルの所有者アカウントでGoogleへログインしてください。閲覧・動画アップロード・投稿後の編集権限を確認して許可すると連携が完了します。編集権限には動画・コメント・字幕などの削除も含まれます。この操作で動画を投稿することはありません。',200,`<form method="post" action="/start"><input type="hidden" name="invitation" id="invitation"><button id="submit" disabled>Googleで連携する</button></form><p>取得した認証情報は暗号化して運用環境に保存します。Googleアカウントの接続設定から連携を解除できます。</p><script nonce="${nonce}">const t=location.hash.slice(1);history.replaceState(null,'','/connect');if(/^[A-Za-z0-9_-]{43}$/.test(t)){document.getElementById('invitation').value=t;document.getElementById('submit').disabled=false;}</script>`,nonce,true);
  }
  if(request.method==='POST' && url.pathname==='/start') {
    if(request.headers.get('Origin')!==env.PUBLIC_ORIGIN) return page('開始元が一致しません。',403);
    if(!env.GOOGLE_CLIENT_ID || !env.GOOGLE_CLIENT_SECRET || !env.TOKEN_KEY) return page('連携の準備中です。',503);
    if(Number(request.headers.get('Content-Length')||0)>4096) return page('入力が大きすぎます。',413);
    let body;try{body=await boundedText(request,4096);}catch{return page('入力が大きすぎます。',413);}
    const token=new URLSearchParams(body).get('invitation')||'';
    if(!/^[A-Za-z0-9_-]{43}$/.test(token))return page('招待URLが無効です。',400);
    const invite=await env.DB.prepare('DELETE FROM invitations WHERE hash=? AND expires>=? RETURNING hash').bind(await hash(token),now()).first();
    if(!invite)return page('招待URLが期限切れ、または使用済みです。新しいURLを依頼してください。',410);
    const state=random(),browser=random(),verifier=random();
    await env.DB.prepare('INSERT INTO sessions(state_hash,browser_hash,verifier,expires) VALUES(?,?,?,?)').bind(await hash(state),await hash(browser),verifier,now()+900).run();
    const target=new URL('https://accounts.google.com/o/oauth2/v2/auth');
    target.search=new URLSearchParams({client_id:env.GOOGLE_CLIENT_ID,redirect_uri:`${env.PUBLIC_ORIGIN}/callback`,response_type:'code',scope:SCOPES.join(' '),access_type:'offline',prompt:'consent',state,code_challenge:await hash(verifier),code_challenge_method:'S256'}).toString();
    return new Response(null,{status:303,headers:{...headers,Location:target.href,'Set-Cookie':`__Host-mmu-youtube=${browser}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900`}});
  }
  if(request.method==='GET' && url.pathname==='/callback') {
    const state=url.searchParams.get('state')||'';
    const browser=(request.headers.get('Cookie')||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-mmu-youtube='))?.split('=')[1]||'';
    if(!state || !browser)return page('認証セッションを確認できません。招待URLからやり直してください。',400);
    const session=await env.DB.prepare('DELETE FROM sessions WHERE state_hash=? AND browser_hash=? AND expires>=? RETURNING verifier').bind(await hash(state),await hash(browser),now()).first();
    if(!session)return page('認証セッションが期限切れ、または使用済みです。',400);
    if(url.searchParams.has('error'))return page('Googleで連携が許可されませんでした。必要なら新しい招待URLを依頼してください。',400);
    const code=url.searchParams.get('code');if(!code)return page('認可コードがありません。',400);
    const tokens=await tokenRequest({client_id:env.GOOGLE_CLIENT_ID,client_secret:env.GOOGLE_CLIENT_SECRET,code,code_verifier:session.verifier,redirect_uri:`${env.PUBLIC_ORIGIN}/callback`,grant_type:'authorization_code'},upstream);
    const granted=new Set((tokens.scope||'').split(' '));
    if(!SCOPES.every(s=>granted.has(s)))return page('閲覧・アップロード・編集の権限が必要です。',403);
    const response=await upstream('https://www.googleapis.com/youtube/v3/channels?part=id%2Csnippet&mine=true',{headers:{Authorization:`Bearer ${tokens.access_token}`},signal:AbortSignal.timeout(15000)});
    const channels=await boundedJson(response);
    if(!response.ok)return page('YouTube APIでチャンネルを確認できませんでした。担当者へ連絡してください。',502);
    const channel=channels.items?.find(x=>x.id===env.EXPECTED_CHANNEL_ID);
    if(!channel)return page('公式チャンネルと一致しないため連携を保存しませんでした。公式チャンネルの所有者で認可してください。',403);
    if(!tokens.refresh_token)return page('継続利用の認証情報を取得できませんでした。再連携を依頼してください。',409);
    await env.DB.prepare('INSERT INTO connections(channel_id,title,encrypted_refresh,scopes,updated) VALUES(?,?,?,?,?) ON CONFLICT(channel_id) DO UPDATE SET title=excluded.title,encrypted_refresh=excluded.encrypted_refresh,scopes=excluded.scopes,updated=excluded.updated').bind(channel.id,channel.snippet?.title||'',await seal(tokens.refresh_token,env.TOKEN_KEY),tokens.scope,now()).run();
    return new Response(null,{status:303,headers:{...headers,Location:`${env.PUBLIC_ORIGIN}/complete`,'Set-Cookie':'__Host-mmu-youtube=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0'}});
  }
  if(request.method==='GET' && url.pathname==='/complete')return page('認証手続きが完了しました。担当者へ完了をお知らせください。動画投稿はまだ行っていません。');
  return page('ページが見つかりません。',404);
}
export default {async fetch(request,env){try{return await handle(request,env);}catch{return page('連携処理に失敗しました。担当者へ再接続を依頼してください。',502);}}};
