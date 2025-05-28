class GraphPlotter:
    """
    データセットからグラフを描画するクラス。
    """
    def graph_plottor(self, normal_data_blocks, test_data_blocks):
        """
        通常データとテストデータのブロックからグラフを描画します。

        Args:
            normal_data_blocks (list): 通常データのブロックのリスト。
            test_data_blocks (list): テストデータのブロックのリスト。
        """
        import matplotlib.pyplot as plt

        # グラフ描画（通常データ）
        for i, block in enumerate(normal_data_blocks):
            plt.figure() # 新しい図を作成
            plt.plot(block["data"]) # データをプロット
            plt.title(f"{block['title']}") # グラフタイトルを設定
            plt.xlabel(block["xlabel"]) # X軸ラベルを設定
            plt.ylabel(block["ylabel"]) # Y軸ラベルを設定
            plt.grid(True) # グリッドを表示

        # グラフ描画（テストデータ）
        for i, block in enumerate(test_data_blocks):
            plt.figure() # 新しい図を作成
            plt.plot(block["data"]) # データをプロット
            plt.title(f"[Test] {block['title']}") # グラフタイトルを設定（テストデータであることを明示）
            plt.xlabel(block["xlabel"]) # X軸ラベルを設定
            plt.ylabel(block["ylabel"]) # Y軸ラベルを設定
            plt.grid(True) # グリッドを表示

        plt.show() # 全てのグラフを表示