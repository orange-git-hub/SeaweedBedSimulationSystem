import sys

simulation_version = "0.0.1"
"""
    同じversionでシステムを動作させてもdbに結果は保存されないため注意
    *.*.n:nは初期値の変更時などに1ずつ増加させる
    *.n.*:nは既存の種に関するアルゴリズムの変更や、追加の際に1ずつ増加させる
    n.*.*:nは根本的なアルゴリズムの変更や、新たな種の追加の際に1ずつ増加させる
    上位のバージョンNo.の変更の際、下位のバージョンNo.は0にリセットされる
"""

def main():
    from SeaweedBedSimulationSystemExecuter.make_text_file import MakeTextFile
    from SeaweedBedSimulationSystemExecuter.db_connector import DBConnector
    from SeaweedBedSimulationSystemExecuter.data_set_maker import DataSetMaker
    from SeaweedBedSimulationSystemExecuter.graph_plotter import GraphPlotter
    text_file_maker = MakeTextFile()
    db_show = DBConnector()
    data_set_maker = DataSetMaker()
    graph_plotter = GraphPlotter()

    #実行環境確認
    print("Python executable in use:")
    print(sys.executable)
    print("[SYSTEM VERSION] " + simulation_version)

    # C++ 実行ファイルのパス（適宜修正）
    executable_path = "/Users/ishikawasora/Library/Mobile Documents/com~apple~CloudDocs/AE1/特別研究/SeaWeedBedSimulationSystemBase/SeaweedBedSimulationSystem/src/cmake-build-debug/SeaweedBedSimulationSystem"

    # DataSetMakerを使用してデータセットを作成
    normal_data_blocks, test_data_blocks = data_set_maker.result_data_set_maker(executable_path)

    # GraphPlotterを使用してグラフを描画
    graph_plotter.graph_plottor(normal_data_blocks, test_data_blocks)

    db_show.update(simulation_version)

    # dataをtextファイルとして保存
    for i, block in enumerate(normal_data_blocks):
        # ファイル名をタイトルとインデックスから生成（重複を避けるため）
        # ファイル名に使えない文字を置換するなどの処理を追加するとより堅牢になります。
        safe_title = "".join(c if c.isalnum() else "_" for c in block['title'])
        file_name = f"normal_data_{safe_title}_{i}.txt"
        text_file_maker.save_data_to_file(block["data"], file_name)

    for i, block in enumerate(test_data_blocks):
        # ファイル名をタイトルとインデックスから生成
        safe_title = "".join(c if c.isalnum() else "_" for c in block['title'])
        file_name = f"test_data_{safe_title}_{i}.txt"
        text_file_maker.save_data_to_file(block["data"], file_name)



if __name__ == "__main__":
    main()
