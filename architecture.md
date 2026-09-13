# Multi-Dimensional Logger Analyzer - アーキテクチャ設計案

## 設計方針
- **MVC寄りの責務分離**：データ層（core/models）とUI層（gui）を明確に分離。将来のGUIフレームワーク変更や単体テストのしやすさを重視。
- **Facadeパターン**：`DataManager` が CSV読み込み・キャッシュ・列マッピングを裏で束ね、GUI側は `DataManager` の薄いAPIのみを呼ぶ。
- **Mediator/Signal連携**：グラフ↔地図の双方向同期は、個々のWidgetが直接参照し合うのではなく、`SyncController`（またはMainWindowが仲介）がPyQt6シグナルで仲介する設計にし、結合度を下げる。
- **PyInstaller onefile対応**：`QtWebEngineWidgets` はhidden importでハマりやすいため、後述の注意点を反映した構成にする。

## ディレクトリ構成

```
project_root/
├── main.py                        # エントリーポイント（QApplication起動のみ）
├── requirements.txt
├── LICENSE                        # GPL v3
├── app/
│   ├── __init__.py
│   ├── core/                      # データ処理・解析ロジック（GUI非依存）
│   │   ├── __init__.py
│   │   ├── csv_loader.py          # CSVLoader: 単一/複数CSVの解析、日時結合、ヘッダー自動判定
│   │   ├── data_manager.py        # DataManager: 読込〜結合〜キャッシュ全体のFacade
│   │   ├── cache_manager.py       # CacheManager: npy/pickle + gzip での独自バイナリ保存/復元
│   │   ├── column_mapper.py       # ColumnMapping: 列名・単位の手動マッピング定義
│   │   ├── downsampler.py         # Downsampler: min/max/mean間引きロジック
│   │   └── stats_engine.py        # StatsEngine: 最大/最小/平均、ピアソン相関
│   │
│   ├── models/                    # データモデル（値オブジェクト）
│   │   ├── __init__.py
│   │   ├── dataset.py             # Dataset: 時系列データ本体（numpy構造化配列 or DataFrame）
│   │   └── gps_track.py           # GPSTrack: 緯度経度＋時刻の専用モデル
│   │
│   ├── gui/                       # PyQt6 UI層
│   │   ├── __init__.py
│   │   ├── main_window.py         # MainWindow: 全体レイアウト統括、SyncController保持
│   │   ├── sync_controller.py     # SyncController: グラフ⇔地図の時刻同期を仲介
│   │   ├── left_panel/
│   │   │   ├── __init__.py
│   │   │   ├── file_panel.py          # 読込/追加読込/キャッシュ保存・復元ボタン
│   │   │   ├── mapping_panel.py       # 列名・単位マッピングUI
│   │   │   ├── appearance_panel.py    # カラー選択、軸名称、目盛り間隔
│   │   │   ├── mode_panel.py          # 通常/日変化/頻度分析モード切替
│   │   │   └── stats_panel.py         # 統計値・相関係数の表示
│   │   └── right_panel/
│   │       ├── __init__.py
│   │       ├── graph_widget.py         # GraphWidget: pyqtgraphラッパー、3モード描画切替
│   │       ├── map_widget.py           # MapWidget: QWebEngineView + Leaflet/folium連携
│   │       └── splitter_container.py   # QSplitterによる上下可変・地図非表示制御
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── datetime_utils.py      # 日時パース、ファイル名からの日付抽出
│   │   ├── export_utils.py        # クリップボードコピー(EMF/SVG/PNG)、印刷
│   │   └── signals.py             # カスタムシグナル定義（TimeSelected等）
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py            # QSettingsラッパー（ウィンドウ状態、直近フォルダ等）
│
└── build/
    └── app.spec                   # PyInstaller onefile用specファイル
```

## 主要クラスの責務（要点のみ）

| クラス | 責務 |
|---|---|
| `DataManager` | 外部公開Facade。`load_folder()`, `append_folder()`, `save_cache()`, `load_cache()` を提供し、内部でCSVLoader/CacheManagerを呼び分ける |
| `CSVLoader` | 1ファイル単位のパース。ヘッダー有無判定、日時列の自動結合、GPS形式(時刻・緯度・経度)の判定 |
| `CacheManager` | Datasetをnpy+gzip（または pickle+zlib）でシリアライズ/デシリアライズ |
| `Dataset` | 列名・単位・実データ（numpy構造化配列推奨、大容量向け）を保持する値オブジェクト |
| `SyncController` | GraphWidgetのクリック/範囲選択 ⇔ MapWidgetのピン移動 を仲介。両Widgetは互いを知らない |
| `GraphWidget` | pyqtgraphでの3モード描画（通常/日変化/頻度分析）、ダウンサンプリング適用、ズーム |
| `MapWidget` | OSM軌跡描画、ピン移動、QSplitterでの表示/非表示に対応 |

## PyInstaller onefile化に関する注意点
- `QtWebEngineWidgets` は依存リソース（`.pak`ファイル等）が多く、`--onefile`で失敗しやすいため、`app.spec` で `datas` に明示的に含める必要あり（後工程で対応）。
- `folium`を使う場合、内部でHTMLをレンダリングしQWebEngineViewに渡す方式にすると、folium本体はexeに同梱不要（生成したHTML文字列だけ渡せばよい）。
- ライセンス面：PyQt6はGPL v3、pyqtgraph/numpy/scipyはMIT/BSDでGPL v3と両立可能。folium(MIT)も問題なし。

---
この構成で進めてよければ、次は `CSVLoader` + `DataManager`（CSV読み込み〜結合ロジック）から実装を始めます。
