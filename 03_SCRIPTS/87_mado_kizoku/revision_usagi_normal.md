# 窓際お嬢様部：中国うさぎ・ノーマル版

出力：`final_remotion_subtitles_v12_usagi_normal.mp4`（38.733秒、1162フレーム、1280×720、30fps）。旧採用v11は保持。

たこさんの「本番もお燃えになってますわ」をVOICEVOX中国うさぎ（ノーマル61）、速度1.1、音高0へ変更。発話枠に収めるため前後無音は0.09/0.12秒、発話速度の後加工なし。音声2.1547秒、配置1007フレーム。通知音6回と他の話者の採用音声・BGM・元映像・字幕時刻を維持。末尾2秒のクレジットだけ中国うさぎへ更新。

再現：ルートでIrodori環境のPythonから `remotion/prepare_usagi_normal.py` を実行。採用v11完成MP4と既存public音源が必要。新音声WAVがなければ保存queryをローカルVOICEVOXへ送り再生成。remotion内で `npx tsc -p tsconfig.usagi.json`、`npx remotion render src/usagi-normal.tsx MadoOjousamaUsagi ../final_remotion_subtitles_v12_usagi_normal.mp4 --codec=h264 --crf=18 --concurrency=2`。

確認：限定型検査・720p/30fps/1162実フレーム・全編デコード合格。完成MP4の福ギュン、たこさん3時点、クレジットを目視確認。後半の差し替え範囲外PCM一致。ASRはsmallで「思い」、large-v3-turboで「思え」と変換したが、生成queryは「オモエニ」。音素の取り違えとは区別して記録。

制約：主観的な試聴は未実施。口の動きは元Wan映像のままで新音声との精密な音素同期はしていない。プロジェクト全体の型検査には既存のShorts用3ファイルのエラーがあるため、本編集の独立エントリーを型検査した。外部公開はしていない。
