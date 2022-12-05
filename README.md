# Mufg Scrape Image
MUFG確定拠出年金サイトをスクレイピングするDockerイメージを  
GoogleContainerRegistryにアップロードします。

## Overview
MUFG確定拠出年金サイトへログインし、  
現在の全体および、投資商品毎の資産評価額、運用利回りを取得する為  
該当ページへ移動しHTMLソースをダウンロードします。  
ダウンロード後はBeautifulSoupで抽出処理を行い、 抽出結果をLINEで通知します。  
日々の運用状況確認をLINEで通知することで確認の手間を自動化します。  

## Architecture
- Production
![mufg_scrape_image_prd drawio](https://user-images.githubusercontent.com/52909397/205480111-873e1be4-ea65-4f84-a0d3-20246174b8bd.png)
- Development
![mufg_scrape_image_dev drawio](https://user-images.githubusercontent.com/52909397/205479746-5547340b-edc0-4a8d-981f-6838ce5595d8.png)

## Infrastructure
mufg_scrape_infraリポジトリを参照して下さい  
https://github.com/py-gori/mufg_scrape_infra
