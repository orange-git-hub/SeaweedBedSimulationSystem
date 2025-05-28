class IDGenerator:

    # データセットを一意に識別するためのidを生成する関数
    def generate_data_set_id(self):
        import secrets

        # 8バイトのランダムなバイト列を16進数文字列に変換 (8バイト * 2文字/バイト = 16文字)
        random_hex_string = secrets.token_hex(8)

        print(f"生成された16進数 (secrets): {random_hex_string}")
        print(f"文字列長: {len(random_hex_string)}")

        return random_hex_string

    def get_config_file_paths_in_folder(self, folder_path):
        """
        指定されたフォルダ内にあるテキストファイル（.txt）のフルパスのリストを取得します。

        Args:
            folder_path (str): 検索対象のフォルダのパス。

        Returns:
            list: テキストファイルのフルパスのリスト。
                  フォルダが存在しない場合や、テキストファイルが見つからない場合は空のリストを返します。
        """
        import os

        text_files = []
        # 指定されたパスが存在し、それがフォルダであるかを確認
        if not os.path.isdir(folder_path):
            print(f"エラー: 指定されたパス '{folder_path}' はフォルダではありません、または存在しません。")
            return text_files  # 空のリストを返す

        # フォルダ内のすべてのファイルとディレクトリ名を取得
        try:
            for item_name in os.listdir(folder_path):
                # アイテムのフルパスを作成
                item_path = os.path.join(folder_path, item_name)
                # アイテムがファイルであり、かつ拡張子が '.yml' であるかを確認
                if os.path.isfile(item_path) and item_name.lower().endswith('.yml'):
                    text_files.append(item_path)
        except OSError as e:
            print(f"エラー: フォルダ '{folder_path}' の読み取り中にエラーが発生しました: {e}")
            return []  # エラー発生時も空のリストを返す

        if not text_files:
            print(f"情報: フォルダ '{folder_path}' 内にテキストファイル（.yml）は見つかりませんでした。")

        return text_files

    # ファイルパスを引数として、ファイルのハッシュを作成する関数
    def make_hush(self, file_paths):
        import hashlib

        # ハッシュオブジェクトの作成
        hasher = hashlib.sha256()

        try:
            for file_path in file_paths:
                with open(file_path, 'rb') as f:  # ファイルをバイナリモードで開く
                    while True:
                        chunk = f.read(4096)  # 4KBずつのチャンクで読み込む
                        if not chunk:
                            break
                        hasher.update(chunk)  # ハッシュオブジェクトを更新
            return hasher.hexdigest()  # 最終的なハッシュ値を16進数文字列で取得

        except FileNotFoundError:
            print(f"エラー: ファイルが見つかりません。 ({file_path})")
            return None

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None