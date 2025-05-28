
class DBConnector:

    # ファイルパスを引数として、ファイルのハッシュを作成する関数
    def make_hush(self,file_path):
        import hashlib

        try:
            #ハッシュオブジェクトの作成
            hasher = hashlib.sha256()

            # ファイルをバイナリモードで読み込み
            with open(file_path, 'rb') as f:
                # ファイルをチャンクごとに読み込んでハッシュを更新
                # これにより、大きなファイルでもメモリを効率的に使用できる
                while chunk := f.read(4096):  # 4KBずつ読み込む
                    hasher.update(chunk)

            # 計算されたハッシュ値を16進数文字列として返す
            return hasher.hexdigest()

        except FileNotFoundError:
            print(f"エラー: ファイルが見つかりません - {file_path}")
            return None
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None


    def db_update(self,simulation_version):

        from notion_client import Client
        import datetime  # 日付の自動入力用

        notion_token = "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"  # Notion API キー
        master_table_id = "1ffdff0c8e2e805683ebe417bde8611f"  # master_table の id
        config_table_id = "200dff0c8e2e807298b3ca8844fbcebd" # config_text_table の id
        result_text_table_id = "200dff0c8e2e80489434dd2351b1515f" # result_text_table の id
        result_graph_table_id = "200dff0c8e2e805196d2f36627066109" # result_graph_table の id
        system_version_table_id = "200dff0c8e2e80378958eaa1396544a6" # system_version_table の id

        # Notionクライアントを初期化
        notion = Client(auth = notion_token)

        try:
            # --- プロパティの準備 ---

            properties_to_add = {

                #simulation_version
                "system_version": {
                    "title": [
                        {
                            "text": {
                                "content": simulation_version  # ここに実際のシステムバージョン文字列を入れる
                            }
                        }
                    ]
                },
                #config_text (外部URLを指定)
                "config_text": {
                    "files": [
                        {
                            "name": "configuration_used.txt",  # Notion上での表示名
                            "type": "external",
                            "external": {
                                "url": "/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config/fish_config.yml"
                            }
                        }
                    ]
                },
                #result_text (外部URLを指定)
                "result_text": {
                    "files": [
                        {
                            "name": "simulation_result.log",  # Notion上での表示名
                            "type": "external",
                            "external": {
                                "url": "/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/result/result_text/normal_data_feed_amount_change_0.txt"
                            }
                        }
                    ]
                },
                "result_graph": {
                    "files": [
                        {
                            "name": "simulation_result.log",
                            "type": "external",
                            "external":{
                                "url": "https://drive.google.com/file/d/1zUmzE1Sypf-oDaXdMeok_0k1v2xGpdBS/view?usp=drive_link"
                            }
                        }
                    ]
                },

                # date
                "date": {
                    "date": {
                        "start": datetime.date.today().isoformat()  # 今日の日付をYYYY-MM-DD形式で設定
                    }
                }
            }

            # --- デバッグ用に送信するデータを出力 (任意) ---
            # import json
            # print("送信するデータ:")
            # print(json.dumps(properties_to_add, indent=2, ensure_ascii=False))

            # Notionデータベースに新しいページを作成
            created_page = notion.pages.create(
                parent={"database_id": master_table_id},
                properties=properties_to_add
            )

            print(f"新しいページが作成されました！ ID: {created_page['id']}")
            print(f"URL: {created_page.get('url', 'URLが取得できませんでした')}")

        except Exception as e:
            print(f"エラーが発生しました: {e}")