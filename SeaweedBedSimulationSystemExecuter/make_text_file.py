import os
import io # メモリ上でファイルを扱うためにインポート
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

# Google Drive APIのスコープ (ファイルの作成と管理を許可)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class MakeTextFile:
    """
    Google Driveへのファイル処理関連の機能を提供するクラス。
    """

    def __init__(self, default_target_folder_id="1LpzDz6CnRDpyMy3-ewyw2wJDrIaLmjpr"):
        """
        コンストラクタ。

        Args:
            default_target_folder_id (str, optional):
                デフォルトのGoogle Drive上の出力先フォルダID。
                指定しない場合は、save_data_to_fileメソッドで都度指定が必要。
        """
        self.default_target_folder_id = default_target_folder_id
        self.creds = self._get_credentials() # 認証情報を取得・保持

    def _get_credentials(self):
        """
        Google Drive APIの認証情報を取得または更新します。
        credentials.json が必要です。
        初回実行時はブラウザでの認証が求められ、token.json が生成されます。
        """
        creds = None
        # token.json はアクセストークンとリフレッシュトークンを保存し、
        # 認証フローが初めて完了したときに自動的に作成されます。
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # 有効な認証情報がない場合は、ユーザーにログインを促します。
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"認証情報の更新に失敗しました: {e}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
            else:
                # credentials.json が存在しない場合のエラーハンドリング
                if not os.path.exists('credentials.json'):
                    print("エラー: credentials.json が見つかりません。")
                    print("Google Cloud Platform からダウンロードし、スクリプトと同じディレクトリに配置してください。")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # 次回のために認証情報を保存します
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def save_data_to_file(self, data_array, file_name, target_folder_id=None):
        """
        数値データの配列を1つのテキストファイルとしてGoogle Driveの指定されたフォルダに出力します。
        ファイル内では、各データは改行されて保存されます。

        Args:
            data_array (list): ファイルに出力する数値のリスト。
            file_name (str): 出力するファイル名 (拡張子を含む, 例: "data_set_1.txt")。
            target_folder_id (str, optional):
                ファイルを保存するGoogle DriveのフォルダID。
                指定しない場合はインスタンスのデフォルトフォルダIDを使用。
                どちらも指定されていない場合はエラーとなります。
        """
        if not self.creds:
            print("認証情報がありません。処理を中止します。")
            return

        # 保存先フォルダIDを決定
        resolved_target_folder_id = target_folder_id if target_folder_id else self.default_target_folder_id

        if not resolved_target_folder_id:
            print("エラー: 保存先のGoogle Drive フォルダIDが指定されていません。")
            return

        try:
            # Google Drive APIサービスを構築
            service = build('drive', 'v3', credentials=self.creds)

            # ファイルの内容を文字列として準備
            file_content = ""
            for item in data_array:
                file_content += str(item) + "\n"

            # 文字列データをバイト列に変換
            file_content_bytes = file_content.encode('utf-8')

            # メモリ上でファイルのように扱うためのオブジェクトを作成
            fh = io.BytesIO(file_content_bytes)

            # アップロードするファイルのメタデータ
            # parents にフォルダIDを指定することで、そのフォルダ配下にファイルが作成されます
            file_metadata = {
                'name': file_name,
                'parents': [resolved_target_folder_id]
            }

            # MediaIoBaseUpload を使用してファイルをアップロード
            media = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id, name, webViewLink').execute()

            print(f"ファイル '{file.get('name')}' (ID: {file.get('id')}) をGoogle Driveに作成しました。")
            print(f"リンク: {file.get('webViewLink')}")

            return file.get('webViewLink')

        except HttpError as error:
            print(f"Google Drive APIでエラーが発生しました: {error}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")