import matplotlib.pyplot as plt
import os

# SeaweedBedSimulationSystemExecuter.make_text_file は直接使用されていないため、
# 必要に応じてコメントアウトまたは削除を検討してください。
# from SeaweedBedSimulationSystemExecuter.make_text_file import MakeTextFile

# DBConnectorをインポート
from SeaweedBedSimulationSystemExecuter.db_connector import DBConnector


class GraphPlotter:
    """
    データセットからグラフを描画し、オプションでGoogle Driveに保存するクラス。
    """

    def graph_plottor(self, normal_data_blocks, test_data_blocks):
        """
        通常データとテストデータのブロックからグラフを描画します。(ローカル表示用)

        Args:
            normal_data_blocks (list): 通常データのブロックのリスト。
                                       各ブロックは {"data": list, "title": str, "xlabel": str, "ylabel": str} の形式。
            test_data_blocks (list): テストデータのブロックのリスト。形式はnormal_data_blocksと同じ。
        """
        for i, block in enumerate(normal_data_blocks):
            fig = plt.figure()
            plt.plot(block["data"])
            plt.title(f"{block['title']}")
            plt.xlabel(block["xlabel"])
            plt.ylabel(block["ylabel"])
            plt.grid(True)
            print(f"通常データグラフ '{block['title']}' を準備しました。")

        for i, block in enumerate(test_data_blocks):
            fig = plt.figure()
            plt.plot(block["data"])
            plt.title(f"[Test] {block['title']}")
            plt.xlabel(block["xlabel"])
            plt.ylabel(block["ylabel"])
            plt.grid(True)
            print(f"テストデータグラフ '{block['title']}' を準備しました。")

        plt.show()
        plt.close('all')
        print("全てのグラフを表示し、関連する図を閉じました。")

    def plot_and_save_to_gdrive(self, normal_data_blocks, test_data_blocks,
                                gdrive_connector: DBConnector,
                                gdrive_folder_id=None):
        """
        グラフをPNGファイルとして生成し、Google Driveに保存し、その共有リンクを返します。
        引数で渡されたDBConnectorのインスタンスを介してGoogle Driveと通信します。

        Args:
            normal_data_blocks (list): 通常データのブロックのリスト。
            test_data_blocks (list): テストデータのブロックのリスト。
            gdrive_connector (DBConnector): 初期化済みのDBConnectorインスタンス。 # 説明も修正
            gdrive_folder_id (str, optional): 保存先のGoogle DriveフォルダID。

        Returns:
            list: アップロードされた各グラフのGoogle Drive共有リンクの文字列のリスト。
        """
        gdrive_links = []
        temp_local_files = []  # 作成した一時ファイルのパスを保存するリスト

        # gdrive_connectorがDBConnectorのインスタンスであることを前提とします。
        # is_authenticatedメソッドの有無はDBConnectorの実装によります。
        # もしis_authenticatedがない場合は、このチェックを修正または削除してください。
        if not gdrive_connector: # DBConnectorがNoneでないかチェック
            print("エラー: DBConnectorが提供されていません。")
            return []
        # `is_authenticated` メソッドの存在は DBConnector の仕様に依存します。
        # if not gdrive_connector.is_authenticated(): # 必要であればこのチェックを有効化
        #     print("エラー: DBConnectorが認証されていません。")
        #     return []


        # --- グラフ処理の共通関数 (内部利用) ---
        def _process_blocks_for_gdrive(block_list, data_type_prefix=""):
            for i, block in enumerate(block_list):
                safe_title = "".join(c if c.isalnum() or c in ['_', '-'] else "_" for c in block['title'])
                gdrive_filename = f"{data_type_prefix}{safe_title}_{i}.png"
                temp_local_file_path = os.path.join('.', f"temp_plot_{gdrive_filename}")

                fig = plt.figure()
                try:
                    plt.plot(block["data"])
                    current_title_prefix = "[Test] " if data_type_prefix == "test_" else ""
                    plt.title(f"{current_title_prefix}{block['title']}")
                    plt.xlabel(block["xlabel"])
                    plt.ylabel(block["ylabel"])
                    plt.grid(True)

                    plt.savefig(temp_local_file_path)
                    print(f"グラフ '{gdrive_filename}' をローカルに一時保存: {temp_local_file_path}")
                    temp_local_files.append(temp_local_file_path)

                    # 引数で渡された gdrive_connector を使用してアップロード
                    link = gdrive_connector.upload_png_and_get_sharable_link(temp_local_file_path, gdrive_filename, gdrive_folder_id)
                    if link:
                        gdrive_links.append(link)
                except Exception as e:
                    print(f"グラフ '{gdrive_filename}' の処理 (保存/アップロード) 中にエラー: {e}")
                finally:
                    plt.close(fig)

        print("\n通常データのグラフをGoogle Driveへ保存処理開始...")
        _process_blocks_for_gdrive(normal_data_blocks, data_type_prefix="normal_")

        print("\nテストデータのグラフをGoogle Driveへ保存処理開始...")
        _process_blocks_for_gdrive(test_data_blocks, data_type_prefix="test_")

        print("\n一時ファイルのクリーンアップ開始...")
        for f_path in temp_local_files:
            if os.path.exists(f_path):
                try:
                    os.remove(f_path)
                    print(f"一時ファイル '{f_path}' を削除しました。")
                except Exception as e:
                    print(f"一時ファイル '{f_path}' の削除失敗: {e}")

        if not gdrive_links:
            print("\n処理完了。Google Driveにアップロードされたグラフはありませんでした。")
        else:
            print("\n全処理完了。生成されたGoogle Drive共有リンク:")
            for idx, link_url in enumerate(gdrive_links):
                print(f"  リンク {idx + 1}: {link_url}")

        return gdrive_links