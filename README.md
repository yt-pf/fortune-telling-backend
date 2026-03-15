# Fortune Telling Demonstration API

このリポジトリは、私が個人で開発・使用している占いパッケージ群の一部をオープンソース化（OSS）したものです。

FastAPI ベースの API として再構成しております。

## 目次

- 機能
- 技術スタック
- サブモジュール
- インストール
- 使用方法
- API エンドポイント
- 環境変数
- 既知の制限事項
- ライセンス

## 機能

- 四柱推命 (Four Pillars of Destiny): 生年月日・時刻から干支、通変星、十二運星を算出
- 数秘術 (Numerology): 生年月日から運命数、過去数、未来数を算出
- 自動 API ドキュメント: Swagger UI による対話型テスト環境

## 技術スタック

| カテゴリ       | 技術                     |
| -------------- | ------------------------ |
| Python         | 3.11+                    |
| フレームワーク | FastAPI 0.135+           |
| バリデーション | Pydantic 2.0+            |
| ASGI サーバー  | Uvicorn 0.41+            |
| テスト         | pytest 9.0+, httpx 0.28+ |

## サブモジュール

このプロジェクトは以下の外部リポジトリをサブモジュールとして使用しています：

| サブモジュール | パス       | URL                                                                                                  |
| -------------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| numerology     | numerology | [https://github.com/yt-pf/numerology](https://github.com/yt-pf/numerology)                           |
| meishiki       | meishiki   | [https://github.com/hajime-f/meishiki](https://github.com/hajime-f/meishiki) (Apache 2.0 ライセンス) |

### サブモジュールの更新

```
# 全サブモジュールを更新
git submodule update --remote

# 特定のサブモジュールのみ更新
git submodule update --remote numerology
```

## インストール

### 前提条件

- Python 3.11 以上
- Git

### クローンとセットアップ

```
# リポジトリのクローン（サブモジュール含む）
git clone --recurse-submodules https://github.com/yt-pf/fortune-telling-backend.git
cd fortune-telling-backend

# または既存のクローン後にサブモジュールを取得
git submodule update --init --recursive

# 仮想環境の作成
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -e .

# uvを使用する場合（推奨）
uv sync
```

### 依存パッケージ

```
pydantic>=2.0.0
python-dateutil>=2.8.0
lunarcalendar>=0.0.9
lunar_python>=1.4.0
jinja2>=3.1.6
fastapi>=0.135.1
uvicorn>=0.41.0
```

## 使用方法

### 開発サーバーの起動

```
# 直接実行
python api.py

# または uvicorn を直接使用
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### API ドキュメントへのアクセス

サーバー起動後、以下の URL から対話型ドキュメントにアクセスできます：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

または、curl コマンドで直接試せます：

```
# 四柱推命
curl "http://localhost:8000/pillars?y=1990&m=5&d=15"

# 数秘術
curl "http://localhost:8000/numerology?y=1990&m=5&d=15"
```

### テストの実行

```
# pytest の実行
pytest -v

# カバレッジ付き
pytest --cov=. --cov-report=html
```

## API エンドポイント

### 1. 四柱推命データ取得

```
GET /pillars
```

**パラメータ:**

| パラメータ | 型  | 必須   | 説明                 |
| ---------- | --- | ------ | -------------------- |
| `y`        | int | はい   | 生年                 |
| `m`        | int | はい   | 生月                 |
| `d`        | int | はい   | 生日                 |
| `h`        | int | いいえ | 生時 (0-23)          |
| `g`        | int | いいえ | 性別 (デフォルト: 0) |

**レスポンス例:**

```
{
  "year_stem": "庚",
  "year_branch": "午",
  "year_hidden_stems": "丙",
  "year_twelve_fortune": "沐",
  "year_stem_transformation_star": "比肩",
  "year_branch_transformation_star": "偏官",
  "month_stem": "辛",
  "month_branch": "巳",
  "month_hidden_stems": "丙",
  "month_twelve_fortune": "長",
  "month_stem_transformation_star": "劫財",
  "month_branch_transformation_star": "偏官",
  "day_stem": "庚",
  "day_branch": "辰",
  "day_hidden_stems": "乙",
  "day_twelve_fortune": "養",
  "day_stem_transformation_star": "－",
  "day_branch_transformation_star": "正財",
  "hour_stem": "－",
  "hour_branch": "－",
  "hour_hidden_stems": "－",
  "hour_twelve_fortune": "－",
  "hour_stem_transformation_star": "－",
  "hour_branch_transformation_star": "－"
}
```

### 2. 数秘術データ取得

```
GET /numerology
```

**パラメータ:**

| パラメータ | 型  | 必須 | 説明 |
| ---------- | --- | ---- | ---- |
| `y`        | int | はい | 生年 |
| `m`        | int | はい | 生月 |
| `d`        | int | はい | 生日 |

**レスポンス例:**

```
{
  "life_path_number": 7,
  "past_number": 5,
  "future_number": 3
}
```

## 環境変数

- ALLOWED_ORIGINS: CORS の許可元

## 既知の制限事項

- 四柱推命の時間(`h`)を指定しない場合、 hour 関連の値は `"-"` で返されます
- 性別(`g`)のパラメータは現在実装されていますが、命式の計算には不要です

## ライセンス

このプロジェクトは Apache 2.0 ライセンスのライブラリを使用しています。

**注意**: この API はデモンストレーション目的で作成されています。実際の占いや人生の決断に使用する場合は自己責任でお願いいたします。

This code is provided for demonstration and learning purposes only.

This project includes the following third-party components:

- meishiki - Licensed under Apache License 2.0

These components are subject to their respective license terms.
