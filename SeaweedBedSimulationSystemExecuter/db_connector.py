
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

    # データセットを一意に識別するためのidを生成する関数
    def generate_data_set_id(self):
        import secrets

        # 8バイトのランダムなバイト列を16進数文字列に変換 (8バイト * 2文字/バイト = 16文字)
        random_hex_string = secrets.token_hex(8)

        print(f"生成された16進数 (secrets): {random_hex_string}")
        print(f"文字列長: {len(random_hex_string)}")

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

            result_id = self.generate_data_set_id()

            properties_add_to_master_table = {

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
                #config_text_set_id
                "config_text": {
                    "title": [
                        {
                            "text": {
                                "content": self.generate_data_set_id()
                            }
                        }
                    ]
                },
                #result_text set_id
                "result_text": {
                    "title": [
                        {
                            "text": {
                                "content": result_id
                            }
                        }
                    ]
                },
                "result_graph": {
                    "title": [
                        {
                            "text": {
                                "content": result_id
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