Discordのボイスチャット上で稼働するYoutubeライブ配信コメント読み上げボット

必須項目
1. VOICEVOXのインストール
   こちらからインストール
   　[https://voicevox.hiroshiba.jp/]
3. ffmpegのインストール
   windowsの場合はこちらを参照
   　[https://roboin.io/article/2024/02/25/install-ffmpeg-to-windows/]
4. Discord 開発ツールでのBot作成 & BotのTOKEN
5. Google Youtube API v3 の API key

4.と5.に関しては調べれば出てきます。

起動方法
こちらではDiscord Botについての説明は省きます。参考資料に詳細あります。
1. VOICEVOXの起動　こちらはアプリを立ち上げるだけでローカルサーバーが建つのでこれだけで大丈夫です。
2. このコードの実行

以降DiscordにてBotが立ち上がっているのを確認し、読み上げて欲しいボイスチャンネルに自分が入ります。
いづれのテキストチャットで問題ないので、
/join <youtube id>
を送信することで自分がいるボイスチャットに入ってきてくれます。
Youtube id は 配信URLの "="以降の文字列です。
https://www.youtube.com/watch?v=Hogehoge の場合、Hogehoge がIDです。

参加と同時に読み上げが始まります。
また、全てのコメントを取得し読み上げるため、すでにコメントが存在する場合はそのすべてのコメントの読み上げから始まります。

読み上げを終える場合は /leave で終了することができます。

注意

今回、コードの修正やチェックにGPT4oを利用しています。
また、セキュリティ等については深く考慮していないため、私用は自己責任でお願いします。

参考資料

・Python Discord Botのつくりかた [https://qiita.com/shown_it/items/6e7fb7777f45008e0496]
・Pythonで実用Discord Bot(discordpy解説) [https://qiita.com/1ntegrale9/items/9d570ef8175cf178468f]
・Discord.pyとGoogle Cloud Text-to-Speech APIで読み上げbotを作る [https://my-pon.hatenablog.com/entry/2020/12/23/000000]
・discordでつくよみちゃんの読み上げbotを作ってみる Python [https://zenn.dev/hotcocoa/articles/cdca580787c83f]
・Pycord 読み上げBot開発 [https://qiita.com/KamakiriS/items/97b36b8fbc98fe695d3f]
・Discord.py 公式リファレンス [https://discordpy.readthedocs.io/ja/latest/#getting-started]
