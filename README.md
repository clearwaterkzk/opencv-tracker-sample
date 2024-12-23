# OpenCVによる追跡サンプル

## デモ
```bash
# サンプル動画で結果を画面表示
python DaSiamRPN_sample.py --device sample_movie/bird_short.mp4

# サンプル動画で結果を描画し動画ファイルに保存, トラッキング点をCSVに保存
python DaSiamRPN_sample.py \
    --device sample_movie/bird_short.mp4 \
    --outpath sample_movie/bird_short_result.mp4 \
```
![demo](demo.gif)

## 出力するCSVのフォーマット

| frame | x | y |
| ----- | - | - | 
| 1     | aaa | bbb 
| 2     | ccc | ddd |
| 3     | eee | fff |
| ...   | ... | ... |

## Reference
- https://github.com/Kazuhito00/OpenCV-Object-Tracker-Python-Sample

## License
OpenCV-Object-Tracker-Sample is under Apache-2.0 License.

## License(Image)
サンプル動画はNHKクリエイティブ・ライブラリーのハクセキレイ　エサをついばみながら歩くを使用しています.
