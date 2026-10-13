import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame, interpolate} from 'remotion';
import rawManifest from './edit-manifest.json';
import {DuoSprite} from './DuoSprite';
import {memberColors} from '../../../00_TEMPLATES/subtitles/member-colors';

type Dialogue = {id?: string; who: string; text: string; caption: string; captionFontSize?: number; mood?: string; view: string; chapter?: string; startFrame: number; durationInFrames: number; envelope: number[]};
type Clip = {src: string; startFrame: number; durationInFrames: number; sourceStartFrame: number; label: string; layout?: 'full' | 'comparison'; tag?: string};
type Manifest = {dialogue: Dialogue[]; clips: Clip[]; creditsStartFrame: number; composition: {durationInFrames: number}};
const ink = '#263e44', green = '#438255', purple = '#95527e', muted = '#61716d', paper = '#f6f3eb';
const Title: React.FC<{children: React.ReactNode}> = ({children}) => <div style={{fontSize: 33, fontWeight: 700, lineHeight: 1.4, marginBottom: 24}}>{children}</div>;
const Note: React.FC<{children: React.ReactNode}> = ({children}) => <div style={{fontSize: 23, lineHeight: 1.6, marginTop: 21, color: '#52666a'}}>{children}</div>;
const Source: React.FC<{children: React.ReactNode}> = ({children}) => <div style={{fontSize: 16, lineHeight: 1.5, marginTop: 12, color: muted}}>{children}</div>;
const Eyebrow: React.FC<{children: React.ReactNode}> = ({children}) => <div style={{fontSize: 19, lineHeight: 1.5, color: green, marginBottom: 12}}>{children}</div>;
const Pic: React.FC<{name: string; w?: number; h?: number; style?: React.CSSProperties}> = ({name, w = 700, h = 350, style}) => <Img src={staticFile(name)} style={{width: w, height: h, objectFit: 'contain', ...style}}/>;
const Label: React.FC<{children: React.ReactNode; color?: string}> = ({children, color = green}) => <div style={{color, fontSize: 23, lineHeight: 1.5, marginTop: 12, fontWeight: 600}}>{children}</div>;
const Arrow: React.FC = () => <span style={{fontSize: 31, color: '#8b9f92', padding: '0 10px'}}>→</span>;
const Row: React.FC<{children: React.ReactNode; gap?: number}> = ({children, gap = 20}) => <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap, width: '100%'}}>{children}</div>;
const Box: React.FC<{children: React.ReactNode; color?: string; width?: number; small?: boolean}> = ({children, color = green, width, small}) => <div style={{padding: small ? '18px 15px' : '24px 20px', background: color === green ? '#e2ebdf' : '#eddfE8', color: ink, borderRadius: 12, fontSize: small ? 24 : 27, fontWeight: 600, lineHeight: 1.65, whiteSpace: 'pre-line', width, flex: width ? undefined : 1}}>{children}</div>;
const Lines: React.FC<{items: string[]}> = ({items}) => <div style={{display: 'flex', flexDirection: 'column', gap: 23, width: 660, textAlign: 'left'}}>{items.map((text, i) => <div key={text} style={{display: 'flex', alignItems: 'center', gap: 20, fontSize: 27, lineHeight: 1.55}}><span style={{fontSize: 19, color: green, fontWeight: 700}}>0{i + 1}</span>{text}</div>)}</div>;
const Pair: React.FC<{a: string; b: string; al: string; bl: string; h?: number}> = ({a,b,al,bl,h=225}) => <Row gap={22}><div><Pic name={a} w={347} h={h}/><Label>{al}</Label></div><div><Pic name={b} w={347} h={h}/><Label color={purple}>{bl}</Label></div></Row>;

/** The source sheet gives the clothing panel and facial portrait distinct jobs. */
const Crop: React.FC<{part: 'face' | 'body'}> = ({part}) => <div style={{width: part === 'face' ? 305 : 176, height: part === 'face' ? 282 : 370, overflow: 'hidden', position: 'relative', background: 'white', borderRadius: 8}}><Img src={staticFile('fuku_sheet.png')} style={part === 'face' ? {position: 'absolute', width: 850, maxWidth: 'none', left: -545, top: 0} : {position: 'absolute', height: 370, maxWidth: 'none', left: 0, top: 0}}/></div>;

/** One shared overview, with a focused stage only when the story returns to it. */
const Workflow: React.FC<{focus?: 'agent' | 'generation' | 'edit' | 'all'}> = ({focus = 'all'}) => {
  const dim = (stage: string) => focus === 'all' || focus === stage ? 1 : .47;
  return <div style={{width: 720}}>
    <div style={{fontSize: 23, marginBottom: 14}}>人間が、作りたいことを伝える</div>
    <div style={{fontSize: 25, color: '#8b9f92', marginBottom: 10}}>↓</div>
    <div style={{background: '#e2ebdf', padding: '14px 18px', borderRadius: 12, opacity: dim('agent')}}><div style={{fontSize: 30, fontWeight: 700, color: green}}>Codex / Claude Code</div><div style={{fontSize: 21, marginTop: 6}}>依頼を整理し、制作の道具を操作する</div></div>
    <div style={{fontSize: 26, color: '#8b9f92', margin: '6px 0'}}>↓</div>
    <div style={{display: 'flex', alignItems: 'center'}}><div style={{flex: 1, opacity: dim('generation')}}><Box small><span style={{fontSize: 28, color: green}}>Wan 3.0</span><br/>映像・生成音声</Box></div><Arrow/><div style={{flex: 1, opacity: dim('edit')}}><Box small color={purple}><span style={{fontSize: 28, color: purple}}>Remotion</span><br/>字幕・編集・書き出し</Box></div></div>
    <div style={{display: 'flex', marginTop: 10, alignItems: 'center', justifyContent: 'center', gap: 15, fontSize: 21, opacity: dim('generation')}}><span style={{color: purple}}>必要な声の修正</span><span>↳ Irodori-TTS</span><span style={{color: '#8b9f92'}}>↗</span></div>
  </div>;
};

const PromptEvidence: React.FC<{model?: boolean}> = ({model = false}) => <>
  <Eyebrow>第53話「替え玉出社」／実際の生成指示</Eyebrow>
  <Title>{model ? '意図を、生成モデルまで届ける' : '「誰の何か」まで、指示にする'}</Title>
  <div style={{width: 704, display: 'flex', gap: 25, alignItems: 'center'}}>
    <div style={{width: 300}}><Pic name="news_mask.jpg" w={300} h={205}/><Label>仮面を着けても、福ギュン</Label></div>
    <div style={{flex: 1, textAlign: 'left', fontSize: 24, lineHeight: 1.8}}><div><span style={{color: green, fontWeight: 700}}>人物・体格</span>：福ギュン</div><div><span style={{color: purple, fontWeight: 700}}>仮面の意匠</span>：そば屋</div><div>筋肉質な本人に変身させない</div></div>
  </div>
  <div style={{fontFamily: 'monospace', fontSize: 18, lineHeight: 1.55, width: 700, marginTop: 24, textAlign: 'left', background: '#e8ebe3', padding: '17px 22px', borderRadius: 8}}>“He remains slim and recognizably Fukuchan;<br/>he never turns into the muscular real Sobaya.”</div>
  <Source>prompt_wan3_v6.txt より抜粋／説明ラベルは編集で追加</Source>
</>;

const ResolutionBranches: React.FC = () => <div style={{width: 710}}><Box small>低解像度で、構図・演出を確認</Box><div style={{height: 30, color: '#8b9f92', fontSize: 28}}>↙　　　　　　　　　↘</div><Row gap={26}><div style={{flex: 1}}><Box small>そのまま採用</Box><Label>普段の窓際動画</Label><div style={{fontSize: 21, lineHeight: 1.6, marginTop: 7}}>ネタ・会話を優先<br/>次の一本にも予算を使う</div></div><div style={{flex: 1}}><Box small color={purple}>高解像度で再生成</Box><Label color={purple}>精細さが必要な作品</Label><div style={{fontSize: 21, lineHeight: 1.6, marginTop: 7}}>演技・細部が変わり得る<br/>最終結果を確認する</div></div></Row></div>;

const ApiCheck: React.FC<{mode: 'single' | 'split' | 'validation'}> = ({mode}) => <>
  <Eyebrow>第53話の制作ログから</Eyebrow>
  <Title>{mode === 'validation' ? '分かった制約を、実行前チェックへ' : mode === 'single' ? '参照音声が、長すぎた' : '分割しても、合計は30秒'}</Title>
  {mode === 'validation' ? <><div style={{width: 690, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 22}}>{['各ファイルの長さ', 'すべての合計時間'].map(s => <div key={s} style={{background: '#e2ebdf', borderRadius: 12, padding: '26px 12px', fontSize: 26}}><span style={{color: green}}>✓</span> {s}</div>)}</div><div style={{fontSize: 32, color: '#8b9f92', margin: '18px 0'}}>↓</div><Row gap={24}><Box small>条件内 → API送信</Box><Box small color={purple}>条件外 → 送信前に停止</Box></Row><Source>qwen_wan3_generate.py／参照素材の実測尺と合計を検証</Source></> : <><div style={{width: 690, display: 'flex', gap: 8, height: 94, marginTop: 18}}>{(mode === 'single' ? ['30秒の音声'] : ['8.53秒', '8.46秒', '13.00秒']).map((t, i) => <div key={t} style={{flex: mode === 'single' ? 1 : [8.53, 8.46, 13][i], background: '#dedfda', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 27, color: ink}}>{t}</div>)}</div><div style={{width: 690, display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 17, fontSize: 24}}><span>{mode === 'single' ? '1本で上限を超過' : '各ファイルは15秒以内'}</span><span style={{color: purple, fontWeight: 700}}>合計30秒</span></div><div style={{background: '#ecdfe5', padding: '18px 28px', borderRadius: 10, fontSize: 27, marginTop: 27, width: 640}}>APIで拒否：InvalidParameter</div><Source>当時の参照音声の制限：1本・合計とも15秒まで<br/>wan_generation_log_v4.md／2026年8月27日の記録</Source></>}
</>;

const Center: React.FC<{view: string; localFrame: number; utterance?: Dialogue}> = ({view, localFrame, utterance}) => {
  if (view === 'opening' || view === 'intro_ready') return <>
    <Eyebrow>AIとWebサイト・アプリを作っている人へ</Eyebrow>
    <div style={{fontSize: 43, fontWeight: 700, lineHeight: 1.5, margin: '14px 0 26px'}}>Codexで<br/><span style={{color: green}}>動画まで作る。</span></div>
    <div style={{fontSize: 28, lineHeight: 1.7}}>窓際族物語のAI制作術</div>
    <Note>{view === 'intro_ready' ? 'まず、実際に作った動画を見てみましょう。' : 'いつものAIとのものづくりを、動画へ。'}</Note>
  </>;
  if (view === 'promise' && ['u005','u006','u007'].includes(utterance?.id ?? '')) return <><Title>この動画で分かること</Title><Lines items={['制作の道具は、どう分担する？', '顔・声・編集を、どう仕上げる？', '費用と失敗を、次の制作にどう生かす？']}/><Note>実際の作品と、制作ログで見ていきます。</Note></>;
  if (view === 'intro_reaction') return <><Title>窓際族物語の動画制作</Title><Pair a="news.jpg" b="cm.jpg" al="架空ニュース" bl="架空CM"/><Note>この映像、どうやって作っている？</Note></>;
  if (view === 'promise' && ['u003','u004'].includes(utterance?.id ?? '')) return <><Title>いつものAIから、動画づくりへ</Title><div style={{fontSize:39,color:green,margin:'25px 0'}}>Claude Code / Codex</div><Note>制作手順・素材・実行コードを用意した環境で</Note><Source>このリポジトリの作り方を、実例で紹介します。</Source></>;
  if (view === 'promise') return <><Eyebrow>今回分解するのは、このニュース</Eyebrow><Title>第53話「替え玉出社」</Title><Pic name="news.jpg" w={690} h={360}/><Source>窓際族物語／生成映像に音声修正と編集を加えた完成版</Source></>;
  if (view === 'roadmap') return <><Title>映像は、動画生成モデルが作る</Title><Workflow focus="all"/><Source>Codex・Claude Codeが、Wanへ生成の指示を渡す</Source></>;
  if (view === 'roles') return <><Title>Codexが、動画制作の道具を動かす</Title><Workflow/><Source>この解説：やめ太郎はIrodori、たこさんはVOICEVOX</Source></>;
  if (view === 'automation') return <><Title>操作は、会話からプログラムへ</Title><div style={{fontSize: 33, color: green, fontWeight: 700, marginBottom: 29}}>Codex / Claude Code</div><div style={{width: 710, display: 'grid', gridTemplateColumns: '190px 1fr 205px', alignItems: 'center', gap: 15, fontSize: 25, lineHeight: 1.8}}><div style={{textAlign: 'left'}}>Wan<br/>Irodori<br/>Remotion</div><div style={{color: muted}}>APIで呼び出す →<br/>コードで実行 →<br/>コマンドで実行 →</div><div style={{textAlign: 'left', color: green}}>動画生成<br/>音声の修正<br/>編集・書き出し</div></div><Note>編集ソフトのタイムライン操作なしで制作</Note></>;
  if (view === 'environment') return <><Title>リポジトリに、制作環境を用意する</Title><div style={{width: 650, textAlign: 'left', background: '#e8ebe3', padding: '24px 33px', borderRadius: 12, fontSize: 27, lineHeight: 1.9}}><span style={{color: green}}>制作リポジトリ</span><br/>├ キャラクター・音声の参照資料<br/>├ AIが読む制作手順（スキル）<br/>└ 道具を呼び出すコード</div><Note>Webアプリの開発環境を整える感覚で。</Note></>;
  if (view === 'human_review') return <><Title>人間が、作るものと採用を決める</Title><Row><Box>依頼する</Box><Arrow/><Box>結果を確認</Box><Arrow/><Box color={purple}>修正・採用</Box></Row><Note>映像を見る。声を聴く。意図に合っているか確かめる。</Note></>;
  if (view === 'request') return <><Eyebrow>第53話の企画を、説明用に要約</Eyebrow><Title>「こんなニュースを作りたい」</Title><div style={{width: 680, background: '#fffef9', borderRadius: 16, padding: '27px 31px', textAlign: 'left', fontSize: 29, lineHeight: 1.8}}>他人を身代わりに出社させ、<br/>自分は家で酒を飲んでいた<br/>会社員のニュース。</div><Note>AIと相談して、台本と映像の指示へ。</Note></>;
  if (view === 'prompt_evidence' || view === 'prompt_model') return <PromptEvidence model={view === 'prompt_model'}/>;
  if (view === 'sheet_identity') return <><Title>別の作品でも、同じ人物へ</Title><Pair a="news_fuku.jpg" b="park_fuku.jpg" al="第53話・ニュース" bl="第72話・パークCM"/><Note>顔・髪型・体格の基準を、画像で渡す</Note><Source>福ギュン／各作品の実際の生成フレーム</Source></>;
  if (view === 'fuku_sheet') return <><Title>基準にするキャラクターシート</Title><Pic name="fuku_sheet.png" w={685} h={380}/><Source>福ギュン／実際の参照素材</Source></>;
  if (view === 'faceless' || view === 'ref_roles') return <><Title>{view === 'faceless' ? '全身側の顔は、あえて消す' : '顔と全身で、参照する役割を分ける'}</Title><Row gap={40}><div><Crop part="body"/><Label>体格・服装</Label></div><div style={{fontSize: 32, color: '#8b9f92'}}>＋</div><div><Crop part="face"/><Label color={purple}>大きく鮮明な顔</Label></div></Row></>;
  if (view === 'generate') return <><Title>資料と台本から、Wanで生成する</Title><Workflow focus="generation"/><Source>第53話の工程：人物資料と声の見本 → Wan 3.0</Source></>;
  if (view === 'voice_sources') return <><Title>声の見本と、読ませる台詞は別</Title><Row gap={24}><div style={{flex: 1}}><Box small>声の見本</Box><Label>声質・話し方</Label><div style={{fontSize: 23, marginTop: 10}}>既存アナウンサーの音声</div></div><div style={{flex: 1}}><Box small color={purple}>新しい台詞</Box><Label color={purple}>今回話す内容</Label><div style={{fontSize: 23, marginTop: 10}}>「速報です。そば屋と…」</div></div></Row><div style={{fontSize: 32, color: '#8b9f92', margin: '17px 0'}}>↓</div><Box small width={625}>Wanが、映像と声を一緒に生成する</Box></>;
  if (view === 'voice_problem') return <><Title>映像は良い。でも、一言だけ違う。</Title><Pic name="news_raw.jpg" w={680} h={320}/><Note>読み間違い・言葉の抜け・余計な発話を確認</Note></>;
  if (view === 'news_patch') return <><Eyebrow>第53話・音声修正の実例</Eyebrow><Title>冒頭の「速報です」を差し替える</Title><Pic name="news_raw.jpg" w={610} h={285}/><Note>Irodoriで用意した声を、同じ映像へ。</Note></>;
  if (view === 'patch_cost') return <><Title>映像を残して、必要な声を直す</Title><div style={{width: 690, display: 'flex', gap: 5, margin: '28px 0 18px'}}><div style={{flex: 1, background: '#e8d5e1', padding: '23px 5px', fontSize: 23}}>速報です</div><div style={{flex: 4, background: '#dce7d9', padding: '23px 5px', fontSize: 23}}>以降の採用した音声</div></div><div style={{display: 'flex', width: 690, fontSize: 23}}><div style={{width: 138, color: purple}}>↑ 差し替え</div><div style={{flex: 1, color: green}}>そのまま生かす</div></div><Note>この音声修正では、Wanの生成APIを再送していない</Note></>;
  if (view === 'park_intro' || view === 'park_method') return <><Eyebrow>別作品の検証例／第72話</Eyebrow><Title>{view === 'park_intro' ? '短い言葉が、元の尺に入らない' : '一文を生成して、必要な部分を切り出す'}</Title><div style={{width: 695, textAlign: 'left', fontSize: 27, lineHeight: 1.8, background: '#e8ebe3', padding: '23px 28px', borderRadius: 10}}>このTシャツ、<span style={{background: '#d8b9cf', padding: '4px 8px'}}>公式サイトでも</span><br/>買えるんですって。</div><div style={{fontSize: 32, color: '#8b9f92', margin: '18px 0'}}>↓</div><Box small color={purple} width={355}>「公式サイトでも」</Box><Note>一文から1.2秒を切り出し／速度変更なし</Note><Source>第72話・部分修復の比較実験（本編とは別の検証）</Source></>;
  if (view === 'sync') return <><Title>声を替えても、口の動きは変わらない</Title><Pic name="news_raw.jpg" w={610} h={285}/><Note>声の調子・長さ・口とのずれを確認する</Note></>;
  if (view === 'offscreen') return <><Title>説明する内容に、見せ方を合わせる</Title><Pair a="news_raw.jpg" b="news_sobaya.jpg" al="画面内で話す" bl="資料映像に声を重ねる" h={215}/><Note>口元を見せる場面と、長い正確な説明を分ける</Note></>;
  if (view === 'news_before' || view === 'news_after') return <><Eyebrow>第53話・完成編集</Eyebrow><Title>{view === 'news_before' ? '生成素材から、完成画面へ' : '正確な文字を、Remotionで重ねる'}</Title><Pic name={view === 'news_before' ? 'news_raw.jpg' : 'news.jpg'} w={695} h={365}/><Source>{view === 'news_before' ? 'Wanが生成した映像' : '字幕・見出し・局のロゴ・放送時刻を編集'}</Source></>;
  if (view === 'edit_demo') {
    const shifted = localFrame >= 95;
    return <><Eyebrow>コード編集の再現デモ</Eyebrow><Title>「字幕を少し下へ」も、会話で頼む</Title><div style={{width: 640, height: 330, position: 'relative', overflow: 'hidden'}}><Pic name="news_raw.jpg" w={640} h={330} style={{objectFit: 'cover'}}/><div style={{position: 'absolute', left: 25, right: 25, bottom: shifted ? 19 : 74, background: '#253d44ee', padding: '10px 14px', color: 'white', fontSize: 24, fontWeight: 600}}>窓際社員「そば屋」に実刑判決</div><div style={{position: 'absolute', top: 12, left: 12, background: paper, padding: '6px 11px', fontSize: 19}}>{shifted ? '修正後' : '修正前'}</div></div><Source>説明用の再現／字幕の位置だけを変更して書き出し</Source></>;
  }
  if (view === 'repair') return <><Title>問題に合った、直し方を選ぶ</Title><Row gap={35}><div style={{width: 330, textAlign: 'left'}}><Label>編集で調整する</Label><div style={{fontSize: 25, lineHeight: 2.05, marginTop: 13}}>字幕・テロップ<br/>音量・声の部分修正<br/>タイミング・間</div></div><div style={{width: 330, textAlign: 'left'}}><Label color={purple}>映像を見直す</Label><div style={{fontSize: 25, lineHeight: 2.05, marginTop: 13}}>顔・人物の同一性<br/>手足や物体の破綻<br/>演技・カメラ</div></div></Row><Note>直す対象を切り分けて、再生成を判断する</Note></>;
  if (view === 'price') return <><Title>30秒を、1回生成する料金</Title><div style={{display: 'flex', alignItems: 'flex-end', gap: 30, height: 287, width: 650}}>{[1.5, 3, 6].map((p, i) => <div key={i} style={{flex: 1}}><div style={{fontSize: 32, fontWeight: 700, marginBottom: 10}}>${p.toFixed(2)}</div><div style={{height: p * 29, background: [green, '#87976c', purple][i], borderRadius: '7px 7px 0 0'}}/><div style={{fontSize: 25, marginTop: 12}}>{['480p', '720p', '1080p'][i]}</div></div>)}</div><Note>通常表示価格／解像度で2倍・4倍に</Note><Source>Qwen Cloud / wan3.0-video｜2026-10-13確認｜動画生成分のみ<br/>確認時点で30%割引表示あり。適用条件・価格は実行時に確認。</Source></>;
  if (view === 'retry') return <><Title>不採用の生成分も、制作費。</Title><div style={{fontSize: 44, fontWeight: 700, margin: '18px 0 30px'}}>$1.50 × 3回 = <span style={{color: purple}}>$4.50</span></div><Row gap={16}>{['候補 1', '候補 2', '採用'].map((t, i) => <div key={t} style={{flex: 1, background: i === 2 ? '#dce8d7' : '#e8e5df', padding: '25px 10px', borderRadius: 10, fontSize: 27}}>{t}<div style={{fontSize: 21, marginTop: 11, color: muted}}>$1.50</div></div>)}</Row><Note>480p・30秒を3回生成／通常表示価格で計算</Note></>;
  if (view === 'resolution' || view === 'highres') return <><Title>{view === 'resolution' ? '低解像度で試して、採用方法を選ぶ' : '高解像度で再生成した結果も、確認する'}</Title><ResolutionBranches/></>;
  if (view === 'choice') return <><Title>窓際動画は、480pを基本に採用</Title><Pair a="news_sobaya.jpg" b="park_sobaya.jpg" al="ニュース" bl="架空CM"/><Note>ネタ・会話が伝わることを優先<br/>予算を、次の一本にも使う</Note></>;
  if (view === 'export') return <><Title>生成解像度と、完成出力を分ける</Title><div style={{width: 710, display: 'flex', flexDirection: 'column', gap: 24}}><div style={{textAlign: 'left', fontSize: 22, color: green}}>普段の投稿用</div><Row><Box small>480pで生成</Box><Arrow/><Box small>720pへ拡大<br/>字幕を追加</Box></Row><div style={{textAlign: 'left', fontSize: 22, color: purple, marginTop: 2}}>精細さが必要な場合</div><Row><Box small color={purple}>高解像度で<br/>再生成</Box><Arrow/><Box small color={purple}>演技・細部を<br/>あらためて確認</Box></Row></div><Source>通常の拡大だけで、元映像の細かい情報は増えない</Source></>;
  if (view === 'total') return <><Title>制作費は、生成料金だけではない</Title><Lines items={['動画生成の料金 × 試行回数', 'Codex・Claude Codeなどの利用料', '処理する環境・待ち時間・人の作業']}/><Note>何を含めた金額か、分けて考える。</Note></>;
  if (view === 'logs') return <><Eyebrow>完成動画の裏側に残るもの</Eyebrow><Title>失敗と修正を、次の制作へ</Title><div style={{width: 675, textAlign: 'left', fontSize: 25, lineHeight: 1.65}}>{[['v3', '音声1本が長すぎて、APIで拒否'], ['v4', '分割したが、合計時間でも拒否'], ['現在', '送信前に、各素材と合計を確認']].map(([v,t], i) => <div key={v} style={{display: 'flex', padding: '18px 0', gap: 22, borderBottom: i < 2 ? '1px solid #dce0d5' : undefined}}><span style={{color: i === 2 ? green : purple, width: 64, flexShrink: 0, fontWeight: 700}}>{v}</span><span>{t}</span></div>)}</div><Source>第53話の制作ログと、現在の実行コード</Source></>;
  if (view === 'skill_intro') return <><Title>AIが次回も読む、制作手順を育てる</Title><div style={{fontSize: 44, fontWeight: 700, color: green, margin: '5px 0 24px'}}>スキル</div><Row gap={16}><Box small>手順</Box><Box small>参照資料</Box><Box small color={purple}>実行コード</Box></Row><Note>作品で得た知見を、次回使う形で残す。</Note></>;
  if (view === 'api_failure' || view === 'api_split' || view === 'validation') return <ApiCheck mode={view === 'api_failure' ? 'single' : view === 'api_split' ? 'split' : 'validation'}/>;
  if (view === 'skill_reuse' && utterance?.id === 'u094') return <><Eyebrow>後日の別比較／2026年9月30日</Eyebrow><Title>比較評価で、修正用の標準を更新</Title><Row gap={24}><Box small>Irodori Small</Box><Box small color={purple}>Irodori Large</Box></Row><Note>おかやまんの台詞を比較し、<br/>今後の修正用途にはLargeを採用</Note><Source>okayaman_large_patch.md／ユーザーの比較評価を手順へ反映<br/>先ほどの福ギュンの切り出し実験とは、別の比較</Source></>;
  if (view === 'skill_reuse') return <><Eyebrow>第72話・音声修復で得た知見</Eyebrow><Title>比較して採用した方法を、手順にする</Title><Row gap={13}><Box small>一文を生成</Box><Arrow/><Box small>必要部分を<br/>切り出す</Box><Arrow/><Box small color={purple}>声・長さ・<br/>同期を確認</Box></Row><Note>修復手順とスクリプトを、スキルから参照</Note><Source>voice_patch_experiment.md → video-voice-patch.md</Source></>;
  if (view === 'skill_scope') return <><Title>設定と一緒に、使える条件を残す</Title><Lines items={['どの話者・参照音声で使ったか', '短文か長文か、何を直したか', '何を比較して、どこまで確認したか']}/><Note>一つの成功を、すべての場面へ広げない。</Note></>;
  if (view === 'skill_loop') return <><Title>一本作るたび、作り方も育つ</Title><div style={{width: 704, display: 'grid', gridTemplateColumns: '1fr 40px 1fr', alignItems: 'center', gap: 14}}><Box small>制作する</Box><Arrow/><Box small>問題を切り分ける</Box><div style={{color: '#8b9f92', fontSize: 29}}>↑</div><div/><div style={{color: '#8b9f92', fontSize: 29}}>↓</div><Box small color={purple}>手順・コードを更新</Box><div style={{fontSize: 31, color: '#8b9f92'}}>←</div><Box small color={purple}>比較して、採用する</Box></div><Note>知見を使い、結果を見て、また見直す。</Note></>;
  if (view === 'summary') return <><Title>会話で作り、判断を次に残す</Title><Workflow/><Source>人物と声の基準／問題に合う修正／費用と制作ログ</Source></>;
  if (view === 'first_step') return <><Title>最初は、一人・一場面から。</Title><div style={{fontSize: 39, color: green, lineHeight: 1.75, margin: '18px 0'}}>短い動画を作る<br/>結果を見て、一つ直す</div><Note>いつものAIとのものづくりを、動画にも。</Note></>;
  if (view === 'h3') return <><Eyebrow>次回予告</Eyebrow><Title>h3さんの制作手法も紹介予定</Title><div style={{fontSize: 35, color: green, fontWeight: 700, margin: '12px 0 16px'}}>Seedance_Madogiwa</div><div style={{fontSize: 20}}>github.com/sobaya-0141/Seedance_Madogiwa</div><Row gap={19}><div style={{fontSize: 27, marginTop: 28, padding: '17px 22px', borderBottom: '3px solid #b5cbb0'}}>料金</div><div style={{fontSize: 27, marginTop: 28, padding: '17px 22px', borderBottom: '3px solid #b5cbb0'}}>待ち時間</div><div style={{fontSize: 27, marginTop: 28, padding: '17px 22px', borderBottom: '3px solid #c8a7be'}}>手作業</div></Row><Note>財布と休日、両方に合う作り方へ。</Note></>;
  if (view === 'ending') return <><Title>Codexで動画まで作る。</Title><div style={{fontSize: 35, color: green, margin: '30px 0'}}>ご視聴ありがとうございました</div><Note>窓際族物語 ／ また次の解説で</Note></>;
  throw Error('Unmapped view ' + view);
};

const ClipPlayer: React.FC<{clip: Clip}> = ({clip}) => {
  const comparison = clip.layout === 'comparison';
  return <AbsoluteFill style={{background: paper}}>
    <div style={{position: 'absolute', top: comparison ? 22 : 16, left: 70, right: 70, height: comparison ? 74 : 42, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 5}}>
      {clip.tag && <div style={{fontSize: 18, color: muted}}>{clip.tag}</div>}
      <div style={{fontSize: comparison ? 27 : 24, fontWeight: 700, color: comparison ? purple : ink}}>{clip.label}</div>
    </div>
    <Sequence from={clip.startFrame} durationInFrames={clip.durationInFrames}>
      <OffthreadVideo muted src={staticFile(clip.src)} startFrom={clip.sourceStartFrame} style={{position: 'absolute', left: comparison ? 136 : 72, top: comparison ? 113 : 69, width: comparison ? 1008 : 1136, height: comparison ? 567 : 639, objectFit: 'contain', background: '#15272a'}}/>
    </Sequence>
  </AbsoluteFill>;
};

export const Explainer: React.FC<{manifest?: Manifest; audioSrc?: string}> = ({manifest, audioSrc='mixed.wav'}) => {
  const m=manifest ?? rawManifest as Manifest;
  const f = useCurrentFrame();
  const active = m.dialogue.find(d => f >= d.startFrame && f < d.startFrame + d.durationInFrames);
  const previousIndex = m.dialogue.reduce((last, d, i) => f >= d.startFrame ? i : last, -1);
  const previous = m.dialogue[previousIndex];
  const clip = m.clips.find(c => f >= c.startFrame && f < c.startFrame + c.durationInFrames);
  const credits = f >= m.creditsStartFrame;
  const view = previous?.view ?? 'opening';
  let sceneIndex = Math.max(0, previousIndex);
  while (sceneIndex > 0 && m.dialogue[sceneIndex - 1].view === view) sceneIndex--;
  const start = m.dialogue[sceneIndex]?.startFrame ?? 0;
  const appear = interpolate(f - start, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: paper, fontFamily: '"Hiragino Sans", sans-serif', color: ink}}>
    <Audio src={staticFile(audioSrc)}/>
    {clip ? <ClipPlayer clip={clip}/> : credits ? <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontSize: 23, lineHeight: 2, textAlign: 'center'}}>
      <div style={{fontSize: 30, marginBottom: 24}}>窓際族物語 ／ 制作の裏側</div>
      <div>出演：やめ太郎 ／ たこさん<br/>やめ太郎音声：Irodori-TTS<br/>たこさん音声：VOICEVOX:中国うさぎ<br/>立ち絵：窓際族物語<br/>導入：昼下がり気分 ／ KK<br/>本編：ほのぼのワルツ【リコーダー】／ エクシエ<br/>エンディング：TheFatRat - Unity<br/>資料映像・キャラクター：窓際族物語</div>
      <div style={{fontSize: 17, marginTop: 25}}>料金確認：2026年10月13日 ／ 出典・音源リンクは概要欄</div>
    </AbsoluteFill> : <>
      <div style={{position: 'absolute', left: 260, top: 24, width: 760, height: 531, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', opacity: appear, transform: `translateY(${(1 - appear) * 5}px)`}}><Center view={view} localFrame={f - start} utterance={previous}/></div>
      {(['yametaro','takosan'] as const).map(who => {
        const speaking=active?.who===who; const local=active?f-active.startFrame:0;
        const peak=Math.max(...(active?.envelope??[0]));
        const open=speaking&&(active?.envelope[Math.floor(local/2)*2]??0)>Math.max(.0025,peak*.15);
        return <DuoSprite key={who} who={who} speaking={speaking} open={open} surprise={speaking&&active?.mood==='surprise'} local={local}/>;
      })}
      {active && <div style={{position: 'absolute', left: 245, right: 245, bottom: 29, minHeight: 110, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><div style={{fontSize: active.captionFontSize ?? 29, fontWeight: 700, lineHeight: 1.65, textAlign: 'center', whiteSpace: 'pre-line', color: active.who === 'yametaro' ? memberColors.yametaro : memberColors.takosan, WebkitTextStroke: '5px #fff', paintOrder: 'stroke fill', textShadow: '0 2px 3px #0002'}}>{active.caption}</div></div>}
    </>}
    <AbsoluteFill style={{background: paper, opacity: interpolate(f, [m.composition.durationInFrames - 30, m.composition.durationInFrames - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}/>
  </AbsoluteFill>;
};
