import { createRoot } from 'react-dom/client';
import { createRootRoute, createRoute, createRouter, RouterProvider } from '@tanstack/react-router';
import { ImageLightboxProvider } from '../src/components/image-lightbox';
import { EpisodePage } from '../src/pages/episode-page';
import Journal from '../src/official/journal';
import { ClipsPage, ClipPage, type Clip } from '../src/features/clips/clips';
import { WorkEditor } from '../src/pages/admin-page';
import type { EpisodeDetail } from '../src/lib/api';
import { HomePage } from '../src/pages/home-page';
import type { PublicEpisodeDetail } from '../src/lib/public-data';
import type { EpisodeSummary } from '../src/lib/api';
import fixture from './fixture.json';
import themeCovers from './theme-covers.json';
import './style.css';
const detail = structuredClone(fixture) as PublicEpisodeDetail;
detail.videos[0].poster_url = 'https://i.ytimg.com/vi/oA2NKFvHfGE/maxresdefault.jpg';
detail.productions.push({...detail.productions[0],generation_id:'record-only',version:0,label:'過去版の制作記録（検証用）',inputs:[],prompt:{label:'制作履歴',body:'動画本体がなくてもプロンプトと使用モデルを保存・表示する検証です。',version:1}});
const episodes: EpisodeSummary[] = [
  {...detail.episode, generation_count:1,video_count:1,input_count:32,prompt_label:null,primary_video_id:detail.videos[0].id,primary_youtube_id:'oA2NKFvHfGE',primary_video_poster_url:detail.videos[0].poster_url,has_featured_video:1,featured_video_created_at:null,members:[{id:'yotan',slug:'yotan',name:'よーたん',sort_order:1}]},
  {...detail.episode,id:'aeron',slug:'aeron-chua-explainer',title:'アーロンチュア解説',summary:'ずんだもん・四国めたんの解説',generation_count:0,video_count:1,input_count:0,prompt_label:null,primary_video_id:'aeron-video',primary_youtube_id:'C_j0IvGPYjM',primary_video_poster_url:'https://i.ytimg.com/vi/C_j0IvGPYjM/maxresdefault.jpg',has_featured_video:0,featured_video_created_at:null,members:[]},
];
// A test excerpt from an uploaded video, not a false mapping of old clips.
const sample: Clip = {id:'youtube-excerpt',episode:88,character:'よーたん',title:'YouTube区間再生の検証（冒頭10秒）',tag:'埋め込み検証',kind:'検証用',seconds:10,startSeconds:0,filename:'',bytes:0,episodeSlug:detail.episode.slug,video:'',source:'',poster:'https://i.ytimg.com/vi/oA2NKFvHfGE/maxresdefault.jpg',youtube_id:'oA2NKFvHfGE',source_youtube_id:'oA2NKFvHfGE',youtube_start:0,youtube_end:10};
const adminDetail: EpisodeDetail = {episode:detail.episode,members:episodes[0].members,generations:[{id:detail.videos[0].generation_id,episode_id:detail.episode.id,version:1,label:'完成版',model_name:'Wan 3.0',notes:'',created_by:null,created_at:detail.episode.created_at,updated_at:detail.episode.updated_at,prompt:null,promptHistory:[],inputAssets:[],videos:[{...detail.videos[0],youtube_id:'oA2NKFvHfGE',episode_id:detail.episode.id,poster_r2_key:null,filename:'',content_type:'',size_bytes:null,status:'published',is_primary:1,display_order:0,uploaded_by:null,updated_at:detail.episode.updated_at}]}]};
function App() {
  const path=location.pathname;
  const content=path==='/admin-preview' ? <WorkEditor detail={adminDetail} members={adminDetail.members} onDirty={()=>{}} onSaved={async()=>{}} onRefresh={async()=>adminDetail}/> : path.startsWith('/episodes/') ? <EpisodePage detail={detail}/> : path==='/clips' ? <ClipsPage page={1} items={[sample]}/> : path.startsWith('/clips/') ? <ClipPage clip={sample}/> : path==='/legacy-home' ? <HomePage episodes={episodes} galleryItems={[]} articles={[]}/> : <Journal episodes={new URLSearchParams(location.search).has("covers") ? themeCovers as EpisodeSummary[] : episodes} galleryItems={[]} initialHref={location.href} catalog={{episodes}}/>;
  return <ImageLightboxProvider><aside className="preview-nav"><strong>{new URLSearchParams(location.search).has("covers") ? "固定エピソードの画像配置検証（再生対象外）" : "YouTubeのみ・動画バイナリ遮断"}</strong><a href="/">トップ</a><a href="/?page=movies">動画一覧</a><a href="/?page=characters&character=yotan">よーたん</a><a href={`/episodes/${detail.episode.slug}`}>制作ノート</a><a href="/clips">切り抜き一覧</a><a href="/clips/youtube-excerpt">切り抜き詳細</a><a href="/legacy-home">旧トップ</a><a href="/admin-preview">管理プレビュー</a></aside>{content}</ImageLightboxProvider>;
}
const root=createRootRoute({component:App});
const catchAll=createRoute({getParentRoute:()=>root,path:'$'});
const router=createRouter({routeTree:root.addChildren([catchAll])});
createRoot(document.getElementById('root')!).render(<RouterProvider router={router}/>);
