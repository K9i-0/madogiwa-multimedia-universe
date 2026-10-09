import {env} from 'cloudflare:workers';
import {applyYouTubeStatus,registerYouTube,youtubeRegistrationSchema} from '../worker/youtube';
export const readyVideo=(id:string)=>({id,snippet:{channelId:'UCyQtPu94OaiGxFdd2A6bXdw',title:'YouTube release',thumbnails:{maxres:{url:`https://i.ytimg.com/vi/${id}/maxresdefault.jpg`}}},status:{privacyStatus:'public',uploadStatus:'processed',embeddable:true},processingDetails:{processingStatus:'succeeded'}});
export async function publish(episodeId:string,generationId?:string,featured=false) {
 const row=await registerYouTube(env.DB,youtubeRegistrationSchema.parse({episodeId,generationId,youtubeId:crypto.randomUUID().replaceAll('-','').slice(0,11),productionNotes:!!generationId,featured}), 'test');
 await applyYouTubeStatus(env.DB,row,readyVideo(row.youtube_id));return row;
}
