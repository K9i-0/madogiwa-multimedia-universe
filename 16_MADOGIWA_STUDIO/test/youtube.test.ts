import {env} from 'cloudflare:workers';
import {describe,expect,it} from 'vitest';
import {createEpisode,createGeneration} from '../worker/repository';
import {applyYouTubeStatus,registerYouTube,youtubeRegistrationSchema,listYouTubePublications,publicationState} from '../worker/youtube';
import {queryPublicEpisodes} from '../worker/public-repository';
import {loadPublicEpisode} from '../src/server/public-data.server';
import {readyVideo,publish} from './youtube-fixture';
import {SELF} from 'cloudflare:test';

describe('YouTube publication lifecycle',()=>{
 it('waits for public, processed, embeddable videos from the official channel',()=>{
  const video=readyVideo('abc12345678');
  expect(publicationState(video)).toBe('ready');
  expect(publicationState(undefined)).toBe('unavailable');
  expect(publicationState({...video,snippet:{...video.snippet,channelId:'foreign'}})).toBe('unavailable');
  expect(publicationState({...video,status:{...video.status,privacyStatus:'unlisted'}})).toBe('waiting_public');
  expect(publicationState({...video,status:{...video.status,embeddable:false}})).toBe('unavailable');
  expect(publicationState({...video,status:{...video.status,uploadStatus:'uploaded'}})).toBe('processing');
  expect(publicationState({...video,processingDetails:{processingStatus:'failed'}})).toBe('failed');
 });
 it('keeps the live version during processing and promotes only the newest candidate, hiding private releases',async()=>{
  const episode=await createEpisode(env.DB,{slug:crypto.randomUUID(),title:'Release'},'test');
  const old=await publish(episode.id);
  await env.DB.prepare("UPDATE youtube_publications SET created_at='2000-01-01' WHERE id=?").bind(old.id).run();
  const input=youtubeRegistrationSchema.parse({episodeId:episode.id,youtubeId:'new12345678'});
  const next=await registerYouTube(env.DB,input,'test');
  expect((await registerYouTube(env.DB,input,'test')).id).toBe(next.id);
  expect((await listYouTubePublications(env.DB,episode.id)).length).toBe(2);
  const check=async()=> (await queryPublicEpisodes(env.DB)).find(e=>e.id===episode.id)?.primary_youtube_id;
  await applyYouTubeStatus(env.DB,next,{...readyVideo(next.youtube_id),status:{privacyStatus:'private',uploadStatus:'processed',embeddable:true}});
  expect(await check()).toBe(old.youtube_id);
  await applyYouTubeStatus(env.DB,next,readyVideo(next.youtube_id));
  await applyYouTubeStatus(env.DB,old,readyVideo(old.youtube_id));
  expect(await check()).toBe(next.youtube_id);
  await applyYouTubeStatus(env.DB,next,undefined);
  expect(await check()).toBeUndefined();
  expect(await loadPublicEpisode(episode.slug)).toBeNull();
 });
 it('supports notes-free explainers and rejects duplicate channel IDs or foreign production records',async()=>{
  const episode=await createEpisode(env.DB,{slug:crypto.randomUUID(),title:'Explainer'},'test');
  const foreign=await createEpisode(env.DB,{slug:crypto.randomUUID(),title:'Foreign'},'test');
  const gen=await createGeneration(env.DB,foreign.id,'v2',null,'','test');
  await expect(registerYouTube(env.DB,youtubeRegistrationSchema.parse({episodeId:episode.id,youtubeId:'zzz12345678',generationId:gen.id}),'test')).rejects.toMatchObject({status:400});
  const row=await registerYouTube(env.DB,youtubeRegistrationSchema.parse({episodeId:episode.id,youtubeId:'zzz12345678',contentKind:'explainer'}),'test');
  await expect(registerYouTube(env.DB,youtubeRegistrationSchema.parse({episodeId:foreign.id,youtubeId:row.youtube_id}),'test')).rejects.toMatchObject({status:409});
  await applyYouTubeStatus(env.DB,row,readyVideo(row.youtube_id));
  const detail=await loadPublicEpisode(episode.slug);
  expect(detail?.productions).toEqual([]);
  expect(detail?.episode.content_kind).toBe('explainer');
  const response=await SELF.fetch(`http://localhost/episodes/${episode.slug}`);
  expect(response.status).toBe(200);
  const html=await response.text();
  expect(html).not.toContain('production-prompt');
  expect(html).not.toContain('まだ公開されていません');
  expect(html).not.toMatch(/<video\b/);
 },15000);
});
