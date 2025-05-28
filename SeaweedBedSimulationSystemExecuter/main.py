import sys

simulation_version = "0.0.2"
"""
    同じversionでシステムを動作させてもdbに結果は保存されないため注意
    *.*.n:nは初期値の変更時などに1ずつ増加させる
    *.n.*:nは既存の種に関するアルゴリズムの変更や、追加の際に1ずつ増加させる
    n.*.*:nは根本的なアルゴリズムの変更や、新たな種の追加の際に1ずつ増加させる
    上位のバージョンNo.の変更の際、下位のバージョンNo.は0にリセットされる
"""

def main():
    # region::import/インスタンス化
    from SeaweedBedSimulationSystemExecuter.make_text_file import MakeTextFile
    from SeaweedBedSimulationSystemExecuter.db_connector import DBConnector
    from SeaweedBedSimulationSystemExecuter.data_set_maker import DataSetMaker
    from SeaweedBedSimulationSystemExecuter.graph_plotter import GraphPlotter
    from SeaweedBedSimulationSystemExecuter.id_generator import IDGenerator
    text_file_maker = MakeTextFile()
    db_connector = DBConnector()
    data_set_maker = DataSetMaker()
    graph_plotter = GraphPlotter()
    id_generator = IDGenerator()
    # endregion

    # region::実行環境確認
    print("Python executable in use:")
    print(sys.executable)
    print("[SYSTEM VERSION] " + simulation_version)
    # endregion

    # C++ 実行ファイルのパス（適宜修正）
    executable_path = "/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/src/cmake-build-debug/SeaweedBedSimulationSystem"

    # DataSetMakerを使用して実行結果のデータセット配列brockを作成
    normal_data_blocks, test_data_blocks = data_set_maker.result_data_set_maker(executable_path)

    # region::dataをtextファイルとしてGDriveに保存,リンクを取得
    result_text_link_array = []
    for i, block in enumerate(normal_data_blocks):
        # ファイル名をタイトルとインデックスから生成（重複を避けるため）
        safe_title = "".join(c if c.isalnum() else "_" for c in block['title'])
        file_name = f"normal_data_{safe_title}_{i}.txt"
        result_text_link_array.append(text_file_maker.save_data_to_file_on_drive(block["data"], file_name, share_publicly=True))

    for i, block in enumerate(test_data_blocks):
        # ファイル名をタイトルとインデックスから生成
        safe_title = "".join(c if c.isalnum() else "_" for c in block['title'])
        file_name = f"test_data_{safe_title}_{i}.txt"
        result_text_link_array.append(text_file_maker.save_data_to_file_on_drive(block["data"], file_name, share_publicly=True))
    # endregion

    # configファイルをGDriveに保存,リンクを取得
    config_file_paths = id_generator.get_config_file_paths_in_folder("/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/config")
    config_link_array = []  # Google Drive のリンクを格納するための新しい空のリストを初期化

    # region::各ローカルファイルパスに対して処理を実行
    for i, local_path in enumerate(config_file_paths):
        # configファイルをGoogle Driveにアップロードし、共有リンクを取得
        # share_publicly=True を指定して、共有可能なリンクを取得するようにする
        gdrive_link = text_file_maker.upload_local_file_to_drive(
            local_path,
            "14dh2tWvT0L7-NzRdACq0NvuXF8B59DdB",  # target_folder_id
            f"config_file_{i + 1}.yml",  # remote_file_name
            share_publicly=True  # 共有設定をTrueにする
        )
        # リンクが正常に取得できた場合のみリストに追加
        if gdrive_link:
            config_link_array.append(gdrive_link)
        else:
            # アップロードまたはリンク取得に失敗した場合の警告（必要に応じてエラー処理を強化）
            print(f"警告: {local_path} のGoogle Driveへのアップロードまたはリンク取得に失敗したためスキップします。")
    # endregion

    # GraphPlotterを使用してグラフを描画、GDriveに保存、リンクを取得
    result_graph_link_array = graph_plotter.plot_and_save_to_gdrive(normal_data_blocks, test_data_blocks, db_connector, "1aJcsbPARZ9IiAhsx7vrgGe_8z8vVCQmx")

    # tableを更新
    db_connector.update_master_table(simulation_version, result_text_link_array, config_link_array, result_graph_link_array)

if __name__ == "__main__":
    main()
