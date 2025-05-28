
class DBConnector:
    def db_update(self,simulation_version):

        from notion_client import Client
        import datetime  # 日付の自動入力用

        NOTION_TOKEN = "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"  # ご自身のAPIキーに置き換え
        DATABASE_ID = "1ffdff0c8e2e805683ebe417bde8611f"  # ご自身のデータベースIDに置き換え

        # Notionクライアントを初期化
        notion = Client(auth=NOTION_TOKEN)

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
                                # TODO: 実際のconfigファイルのURLに置き換えてください
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
                                # TODO: 実際のresultファイルのURLに置き換えてください
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
                parent={"database_id": DATABASE_ID},
                properties=properties_to_add
            )

            print(f"新しいページが作成されました！ ID: {created_page['id']}")
            print(f"URL: {created_page.get('url', 'URLが取得できませんでした')}")

        except Exception as e:
            print(f"エラーが発生しました: {e}")