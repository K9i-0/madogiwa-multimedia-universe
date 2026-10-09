import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {handle} from './worker.mjs';
const origin='https://youtube-auth.madogiwa.work';
function setup(){
 const sqlite=new DatabaseSync(':memory:');sqlite.exec(readFileSync(new URL('./migrations/0001_auth.sql',import.meta.url),'utf8'));
 const DB={prepare(sql){const statement=sqlite.prepare(sql);let args=[];return {bind(...values){args=values;return this;},async first(){return statement.get(...args)||null;},async run(){return statement.run(...args);}};},async batch(statements){return Promise.all(statements.map(s=>s.run()));}};
 const env={DB,PUBLIC_ORIGIN:origin,EXPECTED_CHANNEL_ID:'official',GOOGLE_CLIENT_ID:'client',GOOGLE_CLIENT_SECRET:'secret',ADMIN_TOKEN:'admin',TOKEN_KEY:Buffer.alloc(32,7).toString('base64url')};
 return {env,sqlite};
}
const req=(path,options={})=>new Request(origin+path,options);
const admin={Authorization:'Bearer admin'};
async function begin(env){
 const invite=await (await handle(req('/admin/invitations',{method:'POST',headers:admin}),env)).json();
 const token=new URL(invite.url).hash.slice(1);
 const response=await handle(req('/start',{method:'POST',headers:{Origin:origin},body:new URLSearchParams({invitation:token})}),env);
 const auth=new URL(response.headers.get('Location'));
 return {token,auth,cookie:response.headers.get('Set-Cookie').split(';')[0]};
}
function google(channel='official',scope='https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.force-ssl'){
 return async(url,options)=>{
  if(url.includes('/token')){
   assert.equal(options.body.get('client_secret'),'secret');
   return Response.json({access_token:'access',refresh_token:'refresh-private',scope,expires_in:3600});
  }
  return Response.json({items:[{id:channel,snippet:{title:'公式チャンネル'}}]});
 };
}
test('admin endpoints and noncanonical host deny access',async()=>{const {env}=setup();assert.equal((await handle(req('/admin/status'),env)).status,401);assert.equal((await handle(new Request('https://other/health'),env)).status,400);});
test('unconfigured app does not issue invitations',async()=>{const {env}=setup();delete env.GOOGLE_CLIENT_SECRET;assert.equal((await handle(req('/admin/invitations',{method:'POST',headers:admin}),env)).status,503);});
test('invitation is single use; authorization uses PKCE and restricted scopes',async()=>{const {env}=setup();const {token,auth,cookie}=await begin(env);assert.equal(auth.searchParams.get('code_challenge_method'),'S256');assert.match(cookie,/__Host-mmu-youtube=/);assert.equal(auth.searchParams.get('redirect_uri'),origin+'/callback');assert.equal((await handle(req('/start',{method:'POST',headers:{Origin:origin},body:new URLSearchParams({invitation:token})}),env)).status,410);});
test('cross-origin start is blocked',async()=>{const {env}=setup();assert.equal((await handle(req('/start',{method:'POST',headers:{Origin:'https://evil.example'}}),env)).status,403);});
test('callback requires browser cookie; wrong cookie does not consume valid session',async()=>{const {env,sqlite}=setup();const {auth}=await begin(env);const callback='/callback?code=code&state='+auth.searchParams.get('state');assert.equal((await handle(req(callback),env)).status,400);assert.equal((await handle(req(callback,{headers:{Cookie:'__Host-mmu-youtube=wrong'}}),env)).status,400);assert.equal(sqlite.prepare('SELECT COUNT(*) n FROM sessions').get().n,1);});
test('wrong channel cannot replace a connection',async()=>{const {env,sqlite}=setup();const {auth,cookie}=await begin(env);const response=await handle(req('/callback?code=code&state='+auth.searchParams.get('state'),{headers:{Cookie:cookie}}),env,google('wrong'));assert.equal(response.status,403);assert.equal(sqlite.prepare('SELECT COUNT(*) n FROM connections').get().n,0);});
test('missing upload permission is rejected',async()=>{const {env}=setup();const {auth,cookie}=await begin(env);assert.equal((await handle(req('/callback?code=code&state='+auth.searchParams.get('state'),{headers:{Cookie:cookie}}),env,google('official','https://www.googleapis.com/auth/youtube.readonly'))).status,403);});
test('successful callback encrypts refresh token, prevents replay, and supports authenticated refresh',async()=>{const {env,sqlite}=setup();const {auth,cookie}=await begin(env);const callback='/callback?code=code&state='+auth.searchParams.get('state');assert.equal((await handle(req(callback,{headers:{Cookie:cookie}}),env,google())).status,303);const row=sqlite.prepare('SELECT * FROM connections').get();assert.ok(row.encrypted_refresh);assert.ok(!row.encrypted_refresh.includes('refresh-private'));assert.equal((await handle(req(callback,{headers:{Cookie:cookie}}),env,google())).status,400);const status=await (await handle(req('/admin/status',{headers:admin}),env)).json();assert.equal(status.connected,true);assert.ok(!JSON.stringify(status).includes('encrypted_refresh'));const result=await handle(req('/admin/access-token',{method:'POST',headers:admin}),env,async(url,options)=>{assert.equal(options.body.get('refresh_token'),'refresh-private');return Response.json({access_token:'new-access',expires_in:3600});});assert.equal((await result.json()).access_token,'new-access');assert.equal(result.headers.get('Cache-Control'),'no-store');});
test('expired session cannot be used',async()=>{const {env,sqlite}=setup();const {auth,cookie}=await begin(env);sqlite.exec('UPDATE sessions SET expires=0');assert.equal((await handle(req('/callback?code=code&state='+auth.searchParams.get('state'),{headers:{Cookie:cookie}}),env)).status,400);});

test('connect preserves same-origin form Origin while callback stays no-referrer',async()=>{const {env}=setup();const response=await handle(req('/connect'),env);assert.equal(response.headers.get('Referrer-Policy'),'same-origin');assert.match(response.headers.get('Content-Security-Policy'),/form-action 'self' https:\/\/accounts.google.com/);assert.equal((await handle(req('/callback'),env)).headers.get('Referrer-Policy'),'no-referrer');});
test('null and missing origins remain rejected without consuming invitation',async()=>{for(const value of [null,'null']){const {env,sqlite}=setup();const invite=await (await handle(req('/admin/invitations',{method:'POST',headers:admin}),env)).json();const headers=value?{Origin:value}:{};const response=await handle(req('/start',{method:'POST',headers,body:new URLSearchParams({invitation:new URL(invite.url).hash.slice(1)})}),env);assert.equal(response.status,403);assert.equal(sqlite.prepare('SELECT COUNT(*) n FROM invitations').get().n,1);}});
