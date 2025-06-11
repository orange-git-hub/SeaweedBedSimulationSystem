# 藻場生態系シミュレーションシステム (SeaweedBedSimulationSystem)

## 概要

本プロジェクトは、特定の環境条件下における藻場（海藻の群生地）の生態系をシミュレートするC++製アプリケーションと、その実行・データ管理・可視化を自動で行うPython製パイプラインを組み合わせたシステムです。

C++で記述されたシミュレーションコアは、水温や日照量といった環境パラメータに基づき、藻類の成長や、それを捕食する動物の動態を計算します。Pythonスクリプトは、このシミュレーションを実行し、得られた結果（時系列データ）をテキストファイルやグラフ画像として整形します。さらに、これらの生成物と使用した設定ファイルをGoogle Driveに自動でアップロードし、すべての実行記録をNotionデータベースに集約・保存します。

これにより、パラメータを変更しながら繰り返しシミュレーションを実行し、その結果を一元的に管理・比較・分析することが容易になります。

## 主な機能

* **C++による生態系シミュレーション:**
   * 藻類（`algae`）の成長モデル：光合成量や水温、日齢が葉状部の数や長さに与える影響を計算。
   * 動物（`animal`）の摂餌・成長モデルの基盤を実装。
   * 環境データ生成：月次の水温・日照量データから、日々の値を線形補間で生成。
* **YAMLによる柔軟な設定管理:**
   * シミュレーションの初期値や各種パラメータを外部のYAMLファイルで管理。
* **Pythonによる実行パイプライン:**
   * C++プログラムの実行と、標準出力からのデータ取得を自動化。
   * シミュレーション結果をテキストファイルとグラフ（PNG画像）に自動で整形・保存。
* **クラウド連携によるデータ管理:**
   * **Google Drive:** 生成したテキストファイル、グラフ画像、およびシミュレーションに使用した設定ファイル（YAML）を自動でアップロードし、共有可能なリンクを生成。
   * **Notion:** Google Driveの共有リンク、シミュレーションバージョン、実行日などをNotionの複数の連携データベースに自動で記録し、実験結果を一元管理。

## アーキテクチャ

本システムは、責務の異なる2つの主要コンポーネントで構成されています。

### 1. C++ シミュレーションコア
シミュレーションの計算処理を担当する心臓部です。

* `main.cpp`: シミュレーション全体の時間進行を管理するエントリーポイント。
* `algae.h/.cpp`: 藻類の成長（葉状部の数・長さ・面積）をモデル化。
* `animal.h/.cpp`: 動物の基底クラス。摂餌や体重増加に関する基本ロジックと仮想関数を定義。
* `daily_temperature_generator.h/.cpp`: 月次データから日々の水温を生成。
* `daily_photosynthesis_rate_generator.h/.cpp`: 月次データから日々の光量子束密度を生成。
* `config_loader.h/.cpp`: `yaml-cpp`ライブラリを利用して、設定ファイル（`.yml`）を読み込む。
* `CMakeLists.txt`: プロジェクトのビルド構成を定義。

### 2. Python 実行・連携パイプライン
C++コアの実行、結果の処理、外部サービスとの連携を担当します。

* `main.py`: パイプライン全体を制御するメインスクリプト。
* `data_set_maker.py`: C++実行ファイルの標準出力を解析し、グラフ描画用のデータセットを構築。
* `graph_plotter.py`: `matplotlib` を用いてデータセットからグラフを生成し、Google Driveにアップロード。
* `make_text_file.py`: シミュレーション結果の数値データをテキストファイルとしてGoogle Driveにアップロード。
* `db_connector.py`: Google Drive APIとNotion APIを操作し、ファイルのアップロードやデータベースへの記録を行う。
* `id_generator.py`: 設定ファイルのハッシュ値や乱数から、実行ごとのユニークIDを生成。

## 動作環境・前提条件

### C++ 環境
* C++20 に対応したコンパイラ (GCC, Clangなど)
* `CMake` (バージョン 3.21 以上)
* `yaml-cpp` ライブラリ
   * macOS (Homebrew) の場合: `brew install yaml-cpp`

### Python 環境
* Python 3.x
* 必要なライブラリ:
   * `google-api-python-client`
   * `google-auth-httplib2`
   * `google-auth-oauthlib`
   * `notion-client`
   * `matplotlib`

### API認証情報
* **Google Cloud:**
   * Google Drive APIを有効にしたプロジェクトで、OAuth 2.0 クライアントIDを作成し、認証情報ファイル `credentials.json` をPythonスクリプトと同じディレクトリに配置する必要があります。
* **Notion:**
   * インテグレーションを作成し、発行されたトークンを `db_connector.py` 内の `notion_token` 変数に設定する必要があります。また、連携先のデータベースをインテグレーションに共有設定する必要があります。

## セットアップと実行方法

1.  **リポジトリのクローン:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **C++ シミュレーションコアのビルド:**
    ```bash
    # 外部ライブラリのインストール (macOSの例)
    brew install yaml-cpp

    # ビルド
    mkdir build
    cd build
    cmake ..
    make
    ```
    これにより、ビルドディレクトリ（`build/`）内に実行ファイル `SeaweedBedSimulationSystem` が生成されます。

3.  **Python パイプラインのセットアップ:**
    ```bash
    # (推奨) 仮想環境の作成と有効化
    python3 -m venv venv
    source venv/bin/activate

    # 必要なライブラリのインストール
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib notion-client matplotlib
    ```

4.  **認証情報と設定ファイルの準備:**
   * **Google Drive API:** Google Cloud Consoleからダウンロードした `credentials.json` をリポジトリのルートディレクトリに配置します。
   * **Notion API:** `db_connector.py` を開き、以下の変数を自分の環境に合わせて設定します。
      * `notion_token`
      * `master_table_id`, `config_table_id`, `result_text_table_id`, `result_graph_table_id`
   * **ファイルパス:** `main.py` および各ソースコード内にハードコードされているファイルパスを、ご自身の環境に合わせて修正してください。特に以下の設定は重要です。
      * `main.py` 内の `executable_path`(SeaweedBedSimulationSystem/cmake-build-debug/内の実行ファイルパス),
      * `main.py` 内の `config_folder_path`(SeaweedBedSimulationSystem/configのパス)
      * C++ソースコード内のコンフィグファイルへのパス
      * `algae.cpp`,`daily_photosynthesis_rate_generator.cpp`,`daily_temperature_generator.cpp`,`fish.cpp`,`main.cpp`内のパスをご自身の環境に合わせて修正してください。
5.  **実行:**
   * すべての設定が完了したら、Pythonのメインスクリプトを実行します。
    ```bash
    python main.py
    ```
   * 初回実行時には、ブラウザが起動しGoogleアカウントでの認証が求められます。承認すると `token.json` が生成され、次回以降は自動で認証が行われます。

## バージョン管理

本プロジェクトのバージョンは `main.py` の `simulation_version` 変数で管理されます。バージョニングルールは以下の通りです。

* `n.*.*` (メジャー): 根本的なアルゴリズムの変更や、新たな種の追加。
* `*.n.*` (マイナー): 既存の種に関するアルゴリズムの変更や、追加。
* `*.*.n` (パッチ): 結果の変化を伴わないリファクタリングやバグ修正。

**注意:** 同じバージョン番号で複数回実行しても、結果は上書きされず別々に記録されます（IDで一意に識別されるため）。しかし、変更内容を追跡するため、コードを修正した際は適切にバージョンを更新することが推奨されます。
