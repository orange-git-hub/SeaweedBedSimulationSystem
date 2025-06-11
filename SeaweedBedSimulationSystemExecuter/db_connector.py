import datetime
import os.path
from google.auth.transport.requests import Request  # Google認証用
from google.oauth2.credentials import Credentials  # Google認証用
from google_auth_oauthlib.flow import InstalledAppFlow  # Google認証用
from googleapiclient.discovery import build  # Google APIクライアントビルド用
from googleapiclient.http import MediaFileUpload  # Google Driveファイルアップロード用
from googleapiclient.errors import HttpError  # Google APIエラーハンドリング用

from notion_client import Client
from SeaweedBedSimulationSystemExecuter.id_generator import IDGenerator


class DBConnector:
    # Google Drive API のスコープ。ファイルをアップロードし、権限を変更するために 'drive' を使用します。
    # より限定的なスコープ 'drive.file' でも良い場合がありますが、権限設定には 'drive' が確実です。
    DRIVE_SCOPES = ['']
    # 認証情報を保存するファイルのパス (credentials.json はGoogle Cloud Consoleからダウンロード)
    DRIVE_CREDENTIALS_FILE = 'credentials.json'
    # アクセストークンとリフレッシュトークンを保存するファイルのパス (初回認証後に自動生成)
    DRIVE_TOKEN_FILE = 'token.json'

    def __init__(self):
        """
        DBConnectorの初期化。
        Notionクライアントと、Google Drive APIサービスを初期化（または初期化準備）します。
        """
        # Notion関連の初期化
        self.notion_token = ""
        self.master_table_id = ""
        self.config_table_id = ""
        self.result_text_table_id = ""
        self.result_graph_table_id = ""
        self.notion = Client(auth=self.notion_token)
        self.id_generator = IDGenerator()

        # Google Drive APIサービスクライアント (初回利用時に初期化)
        self._drive_service = None  # アンダースコアで内部利用を示唆

    def _get_drive_service(self):
        """
        Google Drive APIサービスへの認証を行い、サービスオブジェクトを返します。
        初回認証時にはユーザーの承認が必要です。
        """
        # 既にサービスオブジェクトが初期化されていればそれを返す
        if self._drive_service:
            return self._drive_service

        creds = None
        # token.json ファイルが存在すれば、保存された認証情報を読み込む
        if os.path.exists(self.DRIVE_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.DRIVE_TOKEN_FILE, self.DRIVE_SCOPES)

        # 認証情報が存在しないか、有効でない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # 認証情報が期限切れで、リフレッシュトークンがあれば更新
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Google Drive APIトークンのリフレッシュに失敗: {e}")
                    # リフレッシュ失敗時は再認証フローへ
                    creds = None  # credsをNoneに戻して再認証を促す

            if not creds:  # credsがNone（新規またはリフレッシュ失敗）の場合、新規認証フローを実行
                # credentials.json が存在するか確認
                if not os.path.exists(self.DRIVE_CREDENTIALS_FILE):
                    print(
                        f"エラー: Google Drive APIの認証情報ファイル '{self.DRIVE_CREDENTIALS_FILE}' が見つかりません。")
                    print("Google Cloud Consoleからダウンロードし、正しいパスに配置してください。")
                    return None
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.DRIVE_CREDENTIALS_FILE, self.DRIVE_SCOPES)
                    # ユーザーにブラウザでの認証を促す
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Google Drive APIの認証フロー中にエラー: {e}")
                    return None

            # 新しい認証情報を token.json に保存
            if creds:
                try:
                    with open(self.DRIVE_TOKEN_FILE, 'w') as token_file:
                        token_file.write(creds.to_json())
                    print(f"Google Drive APIの認証情報を '{self.DRIVE_TOKEN_FILE}' に保存しました。")
                except IOError as e:
                    print(f"警告: Google Drive APIの認証情報をファイルに保存できませんでした: {e}")

        if creds:
            try:
                # 認証されたサービスオブジェクトをビルド
                self._drive_service = build('drive', 'v3', credentials=creds)
                print("Google Drive APIサービスへの接続を確立しました。")
                return self._drive_service
            except HttpError as error:
                print(f"Google Drive APIサービスオブジェクトのビルド中にエラーが発生しました: {error}")
                self._drive_service = None  # エラー時はNoneに戻す
                return None
        else:
            print("Google Drive APIの認証情報を取得できませんでした。")
            return None

    def upload_png_and_get_sharable_link(self, local_file_path, gdrive_filename, gdrive_folder_id=None):
        """
        ローカルのPNGファイルをGoogle Driveにアップロードし、共有可能なリンクを返します。

        Args:
            local_file_path (str): アップロードするローカルPNGファイルのパス。
            gdrive_filename (str): Google Drive上でのファイル名。
            gdrive_folder_id (str, optional): 保存先のGoogle DriveフォルダID。
                                            Noneの場合、マイドライブのルートに保存されます。

        Returns:
            str or None: アップロードされたファイルの共有可能なウェブリンク。失敗した場合はNone。
        """
        # Google Drive APIサービスを取得 (認証含む)
        drive_service = self._get_drive_service()
        if not drive_service:
            print("Google Driveサービスに接続できなかったため、アップロードを中止します。")
            return None

        try:
            # ファイルメタデータの設定
            file_metadata = {
                'name': gdrive_filename
            }
            if gdrive_folder_id:
                file_metadata['parents'] = [gdrive_folder_id]  # 親フォルダを指定

            # アップロードするメディアの設定
            media = MediaFileUpload(local_file_path, mimetype='image/png', resumable=True)

            # ファイルのアップロード実行
            print(f"'{local_file_path}' をGoogle Driveに '{gdrive_filename}'としてアップロード開始...")
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'  # アップロード後にファイルのIDとwebViewLinkを取得
            ).execute()

            print(f"ファイル '{gdrive_filename}' (ID: {file.get('id')}) のアップロードが完了しました。")

            # --- ファイルの権限を「リンクを知っている全員が閲覧可能」に変更 ---
            file_id = file.get('id')
            permission_body = {
                'type': 'anyone',  # 誰でも
                'role': 'reader'  # 閲覧者
            }
            drive_service.permissions().create(
                fileId=file_id,
                body=permission_body,
            ).execute()
            print(f"ファイル (ID: {file_id}) の権限を「リンクを知っている全員が閲覧可能」に変更しました。")

            # 共有可能なリンクを返す
            sharable_link = file.get('webViewLink')
            if sharable_link:
                print(f"共有可能リンク: {sharable_link}")
                return sharable_link
            else:
                file_details = drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
                sharable_link = file_details.get('webViewLink')
                if sharable_link:
                    print(f"共有可能リンク (再取得): {sharable_link}")
                    return sharable_link
                else:
                    print("エラー: アップロードされたファイルの共有可能リンクを取得できませんでした。")
                    return None

        except HttpError as error:
            print(f"Google Driveへのファイルアップロードまたは権限設定中にエラーが発生しました: {error}")
            if error.resp and hasattr(error.resp, 'status') and error.resp.status == 403:
                print("エラー詳細: 403 Forbidden. APIの権限、スコープ、または共有設定を確認してください。")
                print(f"エラーコンテンツ: {error.content}")
            elif error.resp and hasattr(error.resp, 'status') and error.resp.status == 404:
                print(
                    f"エラー詳細: 404 Not Found. 指定されたフォルダID '{gdrive_folder_id}' が存在しない可能性があります。")
            return None
        except Exception as e:
            print(f"Google Driveへのファイルアップロード中に予期せぬエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_master_table(self, simulation_version, result_text_link_array, config_link_array, result_graph_link_array, config_folder_path):
        # Notionクライアントは __init__ で初期化済み (self.notion を使用)
        try:
            # --- プロパティの準備 ---
            result_id = self.id_generator.generate_data_set_id()  # self.id_generator を使用
            config_hush = self.id_generator.make_hush(self.id_generator.get_config_file_paths_in_folder(config_folder_path))

            # (config_files_for_notion の準備処理は変更なし)
            config_files_for_notion = []
            if config_link_array:
                for i, link_url in enumerate(config_link_array):
                    if link_url and isinstance(link_url, str):
                        file_name_from_url = link_url.split('/')[-1].split('?')[0]
                        if not file_name_from_url: # URLからファイル名が取れない場合のフォールバック
                            file_name_from_url = f"uploaded_config_{i + 1}.yml"
                        config_files_for_notion.append({
                            "name": file_name_from_url,
                            "type": "external",
                            "external": {"url": link_url}
                        })
                    else:
                        print(f"警告: config_link_array の {i + 1} 番目のリンク '{link_url}' が無効なためスキップ。")
            if not config_files_for_notion:
                print("情報: config_text_table に追加する有効な設定ファイルリンクがありませんでした。")

            properties_add_to_config_text_table = {
                "config_text_set_id": {"title": [{"text": {"content": config_hush}}]},
                "config_text_file": {"files": config_files_for_notion}
            }

            config_text_page_id = None # 初期化

            # --- ▼▼▼ config_text_tableへの保存前に重複チェック ▼▼▼ ---
            print(f"\n--- config_text_table ({self.config_table_id}) で config_text_set_id = '{config_hush}' の重複チェック開始 ---")
            try:
                query_filter_for_config = {
                    "property": "config_text_set_id",
                    "title": {
                        "equals": config_hush
                    }
                }
                response = self.notion.databases.query(
                    database_id=self.config_table_id,
                    filter=query_filter_for_config
                )

                if response and response.get("results"):
                    # 重複が見つかった場合の処理
                    existing_page = response["results"][0]
                    existing_page_id = existing_page["id"] # 既存ページのIDを取得
                    existing_page_url = existing_page.get("url", "N/A")
                    print(f"  警告: config_text_set_id '{config_hush}' は既に存在します（既存ページID: {existing_page_id}, URL: {existing_page_url}）。")
                    print(f"  config_text_table への新規ページ作成はスキップし、既存のページID ({existing_page_id}) を使用します。")
                    config_text_page_id = existing_page_id # ★★★ 既存のページIDを代入 ★★★
                else:
                    # 重複が見つからなかった場合、新しいページを作成
                    print(f"  '{config_hush}' は重複していません。config_text_table へのページ作成試行 ---")
                    create_page_to_config_table = self.notion.pages.create(
                        parent={"database_id": self.config_table_id},
                        properties=properties_add_to_config_text_table,
                    )
                    config_text_page_id = create_page_to_config_table['id']
                    print(
                        f"  設定テーブルにページ作成 ID: {config_text_page_id}, URL: {create_page_to_config_table.get('url', 'N/A')}")

            except Exception as e:
                print(f"  config_text_tableの重複チェックまたはページ作成中にエラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                # エラー発生時は config_text_page_id は None のまま
            # --- ▲▲▲ 重複チェック処理完了 ▲▲▲ ---

            # config_text_page_id が None (重複チェックやページ作成でエラーが発生した場合のみ)
            # の場合、以降の処理に影響が出る可能性があるため、ログで通知
            if config_text_page_id is None:
                print(f"警告: config_text_table に対応するページIDが取得できませんでした（エラー発生の可能性）。マスターテーブルとの関連付けは行われません。")
                # 必要であればここで処理を中断するロジックを追加 (例: return)


            # --- result_text_table へのページ作成 ---
            # (この部分のロジックは変更なし)
            result_files_for_notion = []
            if result_text_link_array:
                for i, link_url in enumerate(result_text_link_array):
                    if link_url and isinstance(link_url, str):
                        file_name_from_url = link_url.split('/')[-1].split('?')[0]
                        if not file_name_from_url:
                             file_name_from_url = f"uploaded_result_text_{i + 1}.txt"
                        result_files_for_notion.append({
                            "name": file_name_from_url,
                            "type": "external",
                            "external": {"url": link_url}
                        })
                    else:
                        print(
                            f"警告: result_text_link_array の {i + 1} 番目のリンク '{link_url}' が無効なためスキップ。")
            if not result_files_for_notion:
                print("情報: 有効な結果テキストファイルリンクなし。")

            properties_add_to_result_text_table = {
                "result_text_set_id": {"title": [{"text": {"content": result_id}}]},
                "result_text_file": {"files": result_files_for_notion}
            }
            print("\n--- result_text_table へのページ作成試行 ---")
            create_page_to_result_text_table = self.notion.pages.create(
                parent={"database_id": self.result_text_table_id},
                properties=properties_add_to_result_text_table,
            )
            result_text_page_id = create_page_to_result_text_table['id']
            print(
                f"  結果テキストテーブルにページ作成 ID: {result_text_page_id}, URL: {create_page_to_result_text_table.get('url', 'N/A')}")

            # --- result_graph_table へのページ作成 ---
            # (この部分のロジックは変更なし)
            result_graph_for_notion = []
            if result_graph_link_array:
                for i, link_url in enumerate(result_graph_link_array):
                    if link_url and isinstance(link_url, str):
                        file_name_from_url = link_url.split('/')[-1].split('?')[0]
                        if not file_name_from_url:
                            file_name_from_url = f"uploaded_result_graph_{i + 1}.png"
                        result_graph_for_notion.append({
                            "name": file_name_from_url,
                            "type": "external",
                            "external": {"url": link_url}
                        })
                    else:
                        print(
                            f"警告: result_graph_link_array の {i + 1} 番目のリンク '{link_url}' が無効なためスキップ。")
            if not result_graph_for_notion:
                print("情報: 有効な結果グラフファイルリンクなし。")


            properties_add_to_graph_table = {
                "result_graph_set_id": {"title": [{"text": {"content": result_id}}]},
                "result_graph_file": {"files": result_graph_for_notion}
            }

            print("\n--- result_graph_table へのページ作成試行 ---")
            create_page_to_graph_table = self.notion.pages.create(
                parent={"database_id": self.result_graph_table_id},
                properties=properties_add_to_graph_table,
            )
            result_graph_page_id = create_page_to_graph_table['id']
            print(
                f"  結果グラフテーブルにページ作成 ID: {result_graph_page_id}, URL: {create_page_to_graph_table.get('url', 'N/A')}")


            # --- master_table へのページ作成 ---
            properties_add_to_master_table = {
                "simulation_version": {"title": [{"text": {"content": simulation_version}}]},
                "execution_date": {"date": {"start": datetime.date.today().isoformat()}},
                "result_text_set_id": {"relation": [{"id": result_text_page_id}]},
                "result_graph_set_id": {"relation": [{"id": result_graph_page_id}]}
            }

            # config_text_page_id が取得できた場合 (新規作成 or 既存ID取得) のみ、リレーションを設定
            if config_text_page_id:
                properties_add_to_master_table["config_text_set_id"] = {"relation": [{"id": config_text_page_id}]}
            else:
                # このブロックは、重複チェックやページ作成の try-except 内でエラーが発生し、
                # config_text_page_id が None のままになった場合にのみ実行される
                print(f"情報: マスターテーブルの 'config_text_set_id' リレーションは設定されません（config_text_page_idが不明なため）。")

            print("\n--- master_table へのページ作成試行 ---")
            # (master_tableへの作成処理は変更なし)
            created_page_to_master_table = self.notion.pages.create(
                parent={"database_id": self.master_table_id},
                properties=properties_add_to_master_table,
            )
            print(
                f"  マスターテーブルにページ作成 ID: {created_page_to_master_table['id']}, URL: {created_page_to_master_table.get('url', 'N/A')}")

        except Exception as e:
            print(f"Notionテーブル更新全体でエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()