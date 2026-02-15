# 応用情報技術者試験 学習アプリ 機能アイデア

## 座学機能

- 教材を閲覧して学習できる
- 各単元の最後に確認問題を出題

## 過去問練習機能

- 過去問からランダムに出題
- 自分の苦手カテゴリの分析・可視化

## 音声学習機能

- NotebookLM で生成した音声を再生できる
- API でバッチ生成できないか検討 → `notebooklm_podcast_generation_plan.md` に実装計画あり
  - 参考: [NotebookLM Enterprise API - Audio Overview](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-audio-overview?hl=ja)
- 配信方法: Spotify にアップして API 経由で再生する案もあり

### 音声コンテンツの方針

- 1エピソード1テーマで深掘りする形式がベスト
- カテゴリを網羅的に1本でやると浅くなってしまう
- わかりやすい解説をゆっくり、深い理解を得られる構成にする
- Podcast も1テーマ深掘り回の方が面白い
