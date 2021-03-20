# 対Twitter・Mastodonユーザコンタクト用非公式ボットインターフェース

![Deploy main branch](https://github.com/twitter-com-nagato/twitter-com-nagato/workflows/Deploy%20main%20branch/badge.svg)
[![Python application](https://github.com/twitter-com-nagato/twitter-com-nagato/actions/workflows/python-app.yml/badge.svg)](https://github.com/twitter-com-nagato/twitter-com-nagato/actions/workflows/python-app.yml)
[![CodeQL](https://github.com/twitter-com-nagato/twitter-com-nagato/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/twitter-com-nagato/twitter-com-nagato/actions/workflows/codeql-analysis.yml)

## 長門有希って誰？

長門有希は、ライトノベル「涼宮ハルヒの憂鬱」シリーズに登場するキャラクターで、情報統合思念体によって作られた対有機生命体コンタクト用ヒューマノイド・インターフェースです。

## @nagato (Twitter)・@yukinagato (Mastodon)について

@[nagato](https://twitter.com/nagato) (Twitter)と@[yukinagato](https://pawoo.net/@yukinagato) (Mastodon)は、平均24時間毎に長門有希の台詞を呟く**非公式**ボットです。リプライ~~かダイレクトメッセージ~~で話し掛けてやると適当な事を喋りますが、彼女は日本語が苦手なのかあまり会話になりません。

自動的にフォローを返します。有機情報連結の解除（リムーブ）をしてほしい場合にはリムーブしてください。自動的にリムーブされます。

~~スパムアカウント対策として、URLを含むダイレクトメッセージが送られてきた場合、その送信者との有機情報連結を解除（ブロック＋アンブロック）します。そのようなダイレクトメッセージを送信してしまいリムーブされた場合には、再度フォローし直してください。~~

2018年9月22日より、Twitter APIの仕様変更に伴いダイレクトメッセージへの応答を一時的に無効化しています。

## 書籍推薦

お勧めの本を教えてくれます。「お勧めの本は？」とリプライで聞いてみましょう。あなたが今何に興味を持っているかを解析して、絶妙なチョイスでお勧めしてくれます。呟きの解析と書籍の検索にはYahoo! APIを利用しています。

## 挨拶

「おはよう」や「こんにちは」といった挨拶をリプライで送ってみましょう。時刻付きで挨拶を返してくれます。

## 流速

長門有希から見たタイムラインの流速を教えてくれます。「流速は？」とリプライで聞いてみましょう。

## ソースコード

Python 3.8で動作確認しています。ライセンスは[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)です。

ソースコードから動作させたい場合には、別途phrases.txtを用意する必要が有ります。phrases.txtはランダムな呟きに用いられるテキストファイルです。UTF-8で一行ずつ呟きを記入します。

    春は、あけぼの。
    夏は、夜。
    秋は、夕暮。
    冬は、つとめて。

また、次のように各種APIキーを環境変数で指定しておく必要が有ります。`...`となっている箇所は実際にそれぞれのAPI提供者から発行された値に置き換えてください。

```sh
#!/usr/bin/env sh
export NAGATO_LOG_STREAM=1 # Set this if you need console log outputs.
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export TWITTER_CONSUMER_KEY="..."
export TWITTER_CONSUMER_SECRET="..."
export TWITTER_ACCESS_TOKEN="..."
export TWITTER_ACCESS_SECRET="..."
export YAHOO_APPLICATION_ID="..."
python3 /path/to/handler.py
```

## 問い合わせ

割と不調な事が多いので、反応が無いときや止まっているとき、誤字脱字などを発見されたときには、@[nagato](https://twitter.com/nagato)または@[yukinagato](https://pawoo.net/@yukinagato)へのダイレクトメッセージにてご一報ください。

## 改変記録

### 2020年12月30日

- 新規フォロワーのリフォローと非相互フォローアカウントのリムーブが正しく動作していなかった問題を修正

### 2018年10月15日

- Mastodon対応
- 挨拶に返答しない問題を修正

### 2018年9月22日

- ダイレクトメッセージAPIの仕様変更に伴いダイレクトメッセージへの応答を一時的に無効化

### 2018年8月20日

- 返答に含まれる時間がずれている問題を修正

### 2018年8月14日

- AWS Lambdaでの実行に対応

### 2018年7月14日

- ストレージの逼迫を解消するため流速のログ出力を廃止
- URLを含むダイレクトメッセージの送信者をブロック＋アンブロックするように変更

### 2015年1月6日

- [Requests](http://docs.python-requests.org/en/latest/)を利用するように改変
- ソースコードのライセンスを[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)に変更

### 2013年3月26日

- Twitter API 1.1へ対応（したはず）
- GitHubにてリポジトリ公開

### 2013年1月13日

- ダイレクトメッセージへの対応
- 書籍推薦で「おもしろい本」などの表現に対応
- URLを含むダイレクトメッセージの送信者をリムーブする機能を追加

### 2011年11月28日

- 「涼宮ハルヒの驚愕」の台詞を追加
- 書籍推薦がAmazon APIの仕様変更により動作していなかったためYahoo! APIを利用するよう変更

## 関連するTwitterアカウント

### 公式

- @[nagato\_chan](https://twitter.com/nagato_chan)

### 非公式

- @[NagatoBot](https://twitter.com/NagatoBot)
- @[yNagato](https://twitter.com/yNagato)
- @[nyagato\_bot](https://twitter.com/nyagato_bot)

## よくある質問

<dl>
<dt>よく@nagatoなんてID取れたね</dt>
<dd>@<a href="https://twitter.com/masiko">masiko</a>に感謝。</dd>
<dt>アカウント名を譲ってください</dt>
<dd>公式及び権利者の方には喜んでお譲りしますので、お問い合わせください。</dd>
<dt>何でよく止まっているの？</dt>
<dd>そういう時はちょっと疲れているようです。</dd>
<dt>長門は俺の嫁</dt>
<dd>いや、長門は俺の嫁。</dd></dl>

[![Webサービス by Yahoo! JAPAN](https://i.yimg.jp/images/yjdn/yjdn_attbtn1_88_35.gif)](https://developer.yahoo.co.jp/about)
