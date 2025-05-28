
class DBConnector:

    def update_master_table(self,simulation_version,result_text_link_array):

        from notion_client import Client
        import datetime  # 日付の自動入力用
        from SeaweedBedSimulationSystemExecuter.id_generator import IDGenerator

        id_generator= IDGenerator()

        notion_token = "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" # Notion API キー
        master_table_id = "1ffdff0c8e2e805683ebe417bde8611f" # master_table の id
        config_table_id = "200dff0c8e2e807298b3ca8844fbcebd" # config_text_table の id
        result_text_table_id = "200dff0c8e2e80489434dd2351b1515f" # result_text_table の id
        result_graph_table_id = "200dff0c8e2e805196d2f36627066109" # result_graph_table の id
        system_version_table_id = "200dff0c8e2e80378958eaa1396544a6" # system_version_table の id

        # Notionクライアントを初期化
        notion = Client(auth = notion_token)

        try:
            # --- プロパティの準備 ---

            result_id = id_generator.generate_data_set_id()
            config_hush = id_generator.make_hush(id_generator.get_config_file_paths_in_folder("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config"))

            properties_add_to_config_text_table = {
                #config_text_set_id
                "config_text_set_id": {
                    "title": [
                        {
                            "text": {
                                "content": config_hush
                            }
                        }
                    ]
                }
            }

            properties_add_to_result_text_table = {
                #result_text_set_id
                "result_text_set_id": {
                    "title": [
                        {
                            "text": {
                                "content": result_id
                            }
                        }
                    ]
                },
                #result_text_file
                "result_text_file": {
                    "files" :[
                        {
                            "name": "result_text_file",
                            "type": "external",
                            "external": {
                                "url": "https://drive.google.com/file/d/1Royw4FFu-EMpq-uyE1t8SSpNeH8zp9ma/view?usp=drive_link"
                            }
                        }
                    ]
                }
            }

            properties_add_to_graph_table = {
                "result_graph_set_id": {
                    "title": [
                        {
                            "text": {
                                "content": result_id
                            }
                        }
                    ]
                }
            }

            # Notionデータベースに新しいページを作成
            create_page_to_config_table = notion.pages.create(
                parent = {"database_id": config_table_id},
                properties = properties_add_to_config_text_table,
            )
            config_text_page_id = create_page_to_config_table['id']
            print(f"<UNK> ID: {create_page_to_config_table['id']}")
            print(f"URL: {create_page_to_config_table.get('url', 'URL<UNK>')}")

            create_page_to_result_text_table = notion.pages.create(
                parent = {"database_id": result_text_table_id},
                properties = properties_add_to_result_text_table,
            )
            result_text_page_id = create_page_to_result_text_table['id']
            print(f"<UNK> ID: {create_page_to_result_text_table['id']}")
            print(f"URL: {create_page_to_result_text_table.get('url', 'URL<UNK>')}")

            create_page_to_graph_table = notion.pages.create(
                parent = {"database_id": result_graph_table_id},
                properties = properties_add_to_graph_table,
            )
            result_graph_page_id = create_page_to_graph_table['id']
            print(f"<UNK> ID: {create_page_to_graph_table['id']}")
            print(f"URL: {create_page_to_graph_table.get('url', 'URL<UNK>')}")

            properties_add_to_master_table = {
                # simulation_version
                "simulation_version": {
                    "title": [
                        {
                            "text": {
                                "content": simulation_version  # ここに実際のシステムバージョン文字列を入れる
                            }
                        }
                    ]
                },
                # date
                "execution_date": {
                    "date": {
                        "start": datetime.date.today().isoformat()  # 今日の日付をYYYY-MM-DD形式で設定
                    }
                },
                "config_text_set_id": {  # 仮のプロパティ名です。実際のNotionのプロパティ名に置き換えてください。
                    "relation": [
                        {"id": config_text_page_id}
                    ]
                },
                "result_text_set_id": {  # 仮のプロパティ名です。実際のNotionのプロパティ名に置き換えてください。
                    "relation": [
                        {"id": result_text_page_id}
                    ]
                },
                "result_graph_set_id": {  # 仮のプロパティ名です。実際のNotionのプロパティ名に置き換えてください。
                    "relation": [
                        {"id": result_graph_page_id}
                    ]
                }
            }

            created_page_to_master_table = notion.pages.create(
                parent={"database_id": master_table_id},
                properties=properties_add_to_master_table,
            )
            print(f"新しいページが作成されました！ ID: {created_page_to_master_table['id']}")
            print(f"URL: {created_page_to_master_table.get('url', 'URLが取得できませんでした')}")

        except Exception as e:
            print(f"エラーが発生しました: {e}")