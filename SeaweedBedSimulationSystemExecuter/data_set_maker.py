class DataSetMaker:
    """
    C++プログラムの実行結果からデータセットを作成するクラス。
    """
    def result_data_set_maker(self, executable_path):
        """
        C++プログラムを実行し、その出力から通常データとテストデータのブロックを生成します。

        Args:
            executable_path (str): C++実行ファイルのパス。

        Returns:
            tuple: normal_data_blocks (list), test_data_blocks (list)
                   それぞれのデータブロックは辞書のリストで、各辞書は
                   "data", "title", "xlabel", "ylabel" のキーを持つ。
        """

        import subprocess

        # C++プログラムを実行し、標準出力を取得
        result = subprocess.run([executable_path], capture_output=True, text=True)
        output = result.stdout.splitlines() # 出力を改行で分割してリスト化

        # データ構造の初期化
        normal_data_blocks = []
        test_data_blocks = []
        current_data = []
        current_mode = "normal"  # "normal" または "test"
        current_title = "Data Set" # デフォルトタイトル
        current_xlabel = "Index"   # デフォルトX軸ラベル
        current_ylabel = "Value"   # デフォルトY軸ラベル

        # 出力を行ごとに処理
        for line in output:
            line = line.strip() # 前後の空白を除去

            # "[next data]"マーカーが見つかった場合
            if "[next data]" in line:
                if current_data: # 現在のデータが空でなければ保存
                    block_to_add = {
                        "data": current_data,
                        "title": current_title,
                        "xlabel": current_xlabel,
                        "ylabel": current_ylabel
                    }
                    if current_mode == "normal":
                        normal_data_blocks.append(block_to_add)
                    elif current_mode == "test":
                        test_data_blocks.append(block_to_add)
                # 次のデータブロックのために変数を初期化
                current_data = []
                current_mode = "normal"
                current_title = "Data Set" # デフォルトにリセット
                current_xlabel = "Index"   # デフォルトにリセット
                current_ylabel = "Value"   # デフォルトにリセット
                continue # 次の行の処理へ

            # タイトル情報が含まれる行の場合
            if "[title]" in line:
                current_title = line.replace("[title]", "").strip()
                continue

            # X軸ラベル情報が含まれる行の場合
            if "[x_label]" in line:
                current_xlabel = line.replace("[x_label]", "").strip()
                continue

            # Y軸ラベル情報が含まれる行の場合
            if "[y_label]" in line:
                current_ylabel = line.replace("[y_label]", "").strip()
                continue

            # テストデータが含まれる行の場合
            if "[test data]" in line:
                current_mode = "test"
                try:
                    # "[test data]"タグを除去し、浮動小数点数に変換してデータリストに追加
                    value = float(line.replace("[test data]", "").strip())
                    current_data.append(value)
                except ValueError:
                    print(f"数値変換失敗: {line}") # 変換に失敗した場合はエラーメッセージを表示
                continue

            # 通常データが含まれる行の場合
            if "[data]" in line:
                current_mode = "normal"
                try:
                    # "[data]"タグを除去し、浮動小数点数に変換してデータリストに追加
                    value = float(line.replace("[data]", "").strip())
                    current_data.append(value)
                except ValueError:
                    print(f"数値変換失敗: {line}") # 変換に失敗した場合はエラーメッセージを表示
                continue

        # ループ終了後、最後のデータブロックが残っていれば保存
        if current_data:
            block_to_add = {
                "data": current_data,
                "title": current_title,
                "xlabel": current_xlabel,
                "ylabel": current_ylabel
            }
            if current_mode == "normal":
                normal_data_blocks.append(block_to_add)
            elif current_mode == "test":
                test_data_blocks.append(block_to_add)

        return normal_data_blocks, test_data_blocks