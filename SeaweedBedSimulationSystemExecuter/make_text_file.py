import os
import io  # メモリ上でファイルを扱うためにインポート
from mimetypes import guess_type  # ファイル拡張子からMIMEタイプを推測するためにインポート

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

# Google Drive APIのスコープ (ファイルの作成と管理を許可)
SCOPES = ['']


class MakeTextFile:
    """
    Google Driveへのファイル処理関連の機能を提供するクラス。
    テキストファイルだけでなく、ローカルファイルのアップロードもサポートします。
    """

    def __init__(self, default_target_folder_id="1LpzDz6CnRDpyMy3-ewyw2wJDrIaLmjpr"):
        """
        コンストラクタ。

        Args:
            default_target_folder_id (str, optional):
                デフォルトのGoogle Drive上の出力先フォルダID。
        """
        self.default_target_folder_id = default_target_folder_id
        self.creds = self._get_credentials()  # 認証情報を取得・保持
        if self.creds:
            print("Google Drive APIの認証情報を正常に取得または確認しました。")
        else:
            print("警告: Google Drive APIの認証情報の取得に失敗しました。")

    def _get_credentials(self):
        """
        Google Drive APIの認証情報を取得または更新します。
        'credentials.json' (OAuth 2.0 クライアントID情報) が必要です。
        初回実行時はブラウザでの認証が求められ、'token.json' が生成・保存されます。
        """
        creds = None
        token_path = 'token.json'
        credentials_path = 'credentials.json'

        # token.json が存在すれば、そこから認証情報を読み込む
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                print(f"token.json の読み込みに失敗しました: {e}。再認証を試みます。")
                creds = None  # 読み込み失敗時はcredsをNoneに

        # 認証情報が存在しない、または無効な場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # 認証情報が期限切れで、リフレッシュトークンが存在する場合
                try:
                    print("認証情報が期限切れです。トークンを更新しています...")
                    creds.refresh(Request())
                    print("トークンの更新に成功しました。")
                except Exception as e:
                    print(f"トークンの更新に失敗しました: {e}。再認証が必要です。")
                    creds = None  # 更新失敗

            if not creds:  # credsがNone（初回または更新失敗）の場合、新規認証フローを実行
                if not os.path.exists(credentials_path):
                    print(f"エラー: {credentials_path} が見つかりません。")
                    print("Google Cloud Platform からダウンロードし、スクリプトと同じディレクトリに配置してください。")
                    return None
                try:
                    print(f"{credentials_path} を使用して新規認証フローを開始します。")
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    # port=0 を指定すると、利用可能なポートを自動的に使用します
                    creds = flow.run_local_server(port=0)
                    print("新規認証に成功しました。")
                except Exception as e:
                    print(f"認証フローの実行中にエラーが発生しました: {e}")
                    return None

            # 新しい認証情報を token.json に保存
            try:
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                print(f"新しい認証情報を {token_path} に保存しました。")
            except Exception as e:
                print(f"{token_path} への認証情報の保存に失敗しました: {e}")
        return creds

    def is_authenticated(self):
        """
        Google Drive APIへの認証が成功しているかを確認します。

        Returns:
            bool: 認証されていればTrue、そうでなければFalse。
        """
        return self.creds is not None and self.creds.valid

    def _convert_data_array_to_text_content(self, data_array):
        """
        数値データの配列を改行区切りのテキスト文字列に変換します。

        Args:
            data_array (list): 文字列に変換する数値のリスト。

        Returns:
            str: 各要素が改行で区切られたテキストデータ。
        """
        # ファイルの内容を文字列として準備
        file_content = ""
        for item in data_array:
            file_content += str(item) + "\n"
        return file_content

    def upload_text_to_drive(self, text_content, file_name, target_folder_id=None, share_publicly=False):
        """
        指定されたテキストコンテンツをGoogle Driveの指定フォルダにファイルとしてアップロードします。

        Args:
            text_content (str): アップロードするテキストデータ。
            file_name (str): 出力するファイル名 (例: "data_set_1.txt")。
            target_folder_id (str, optional): 保存先フォルダID。Noneの場合デフォルトを使用。
            share_publicly (bool, optional): Trueの場合、リンクを知る全員が閲覧可能に設定。デフォルトはFalse。

        Returns:
            str or None: アップロード成功時はファイルのウェブビューリンク、失敗時はNone。
        """
        if not self.is_authenticated():
            print("認証情報が無効です。アップロード処理を中止します。")
            return None

        resolved_target_folder_id = target_folder_id if target_folder_id else self.default_target_folder_id
        if not resolved_target_folder_id:
            print("エラー: 保存先のGoogle Drive フォルダIDが指定されていません。")
            return None

        try:
            service = build('drive', 'v3', credentials=self.creds)
            file_content_bytes = text_content.encode('utf-8')
            fh = io.BytesIO(file_content_bytes)

            file_metadata = {
                'name': file_name,
                'parents': [resolved_target_folder_id]
            }
            media = MediaIoBaseUpload(fh, mimetype='text/plane', resumable=True)

            print(f"ファイル '{file_name}' をGoogle Driveにアップロードしています...")
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'  # 必要なフィールドを指定
            ).execute()
            file_id = file.get('id')
            print(f"ファイル '{file.get('name')}' (ID: {file_id}) を作成しました。")

            if share_publicly and file_id:
                print(f"ファイル (ID: {file_id}) の共有設定を「リンクを知っている全員が閲覧可能」に変更しています...")
                permission = {'type': 'anyone', 'role': 'reader'}
                service.permissions().create(fileId=file_id, body=permission).execute()
                print("共有設定を変更しました。")

            print(f"アップロード完了。リンク: {file.get('webViewLink')}")
            return file.get('webViewLink')

        except HttpError as error:
            print(f"Google Drive APIエラー (テキストアップロード時): {error}")
            return None
        except Exception as e:
            print(f"予期せぬエラー (テキストアップロード時): {e}")
            return None

    def upload_local_file_to_drive(self, local_file_path, target_folder_id=None, remote_file_name=None, mimetype=None,
                                   share_publicly=False):
        """
        ローカルファイルをGoogle Driveの指定フォルダにアップロードします。

        Args:
            local_file_path (str): アップロードするローカルファイルのパス。
            target_folder_id (str, optional): 保存先フォルダID。Noneの場合デフォルトを使用。
            remote_file_name (str, optional): Drive上でのファイル名。Noneの場合ローカル名を使用。
            mimetype (str, optional): ファイルのMIMEタイプ。Noneの場合、ファイル拡張子から推測。
            share_publicly (bool, optional): Trueの場合、リンクを知る全員が閲覧可能に設定。デフォルトはFalse。

        Returns:
            str or None: アップロード成功時はファイルのウェブビューリンク、失敗時はNone。
        """
        if not self.is_authenticated():
            print("認証情報が無効です。アップロード処理を中止します。")
            return None

        if not os.path.exists(local_file_path):
            print(f"エラー: ローカルファイル '{local_file_path}' が見つかりません。")
            return None

        resolved_target_folder_id = target_folder_id if target_folder_id else self.default_target_folder_id
        if not resolved_target_folder_id:
            print("エラー: 保存先のGoogle Drive フォルダIDが指定されていません。")
            return None

        try:
            service = build('drive', 'v3', credentials=self.creds)
            file_name_on_drive = remote_file_name if remote_file_name else os.path.basename(local_file_path)

            # MIMEタイプの決定
            if mimetype is None:
                mimetype = 'text/yaml' # ファイル拡張子から推測

            file_metadata = {
                'name': file_name_on_drive,
                'parents': [resolved_target_folder_id]
            }
            media = MediaFileUpload(local_file_path, mimetype=mimetype, resumable=True)

            print(
                f"ローカルファイル '{local_file_path}' を '{file_name_on_drive}'としてGoogle Driveにアップロードしています...")
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            file_id = file.get('id')
            print(
                f"ローカルファイル '{local_file_path}' を '{file.get('name')}' (ID: {file_id}) としてアップロードしました。")

            if share_publicly and file_id:
                print(f"ファイル (ID: {file_id}) の共有設定を「リンクを知っている全員が閲覧可能」に変更しています...")
                permission = {'type': 'anyone', 'role': 'reader'}
                service.permissions().create(fileId=file_id, body=permission).execute()
                print("共有設定を変更しました。")

            print(f"アップロード完了。リンク: {file.get('webViewLink')}")
            return file.get('webViewLink')

        except HttpError as error:
            print(f"Google Drive APIエラー (ローカルファイルアップロード時): {error}")
            return None
        except Exception as e:
            print(f"予期せぬエラー (ローカルファイルアップロード時): {e}")
            return None

    def save_data_to_file_on_drive(self, data_array, file_name, target_folder_id=None, share_publicly=False):
        """
        数値データの配列をテキストファイルとしてGoogle Driveの指定フォルダに出力します。

        Args:
            data_array (list): ファイルに出力する数値のリスト。
            file_name (str): 出力ファイル名 (例: "data_set_1.txt")。
            target_folder_id (str, optional): 保存先フォルダID。Noneの場合デフォルトを使用。
            share_publicly (bool, optional): Trueの場合、リンクを知る全員が閲覧可能に設定。デフォルトはFalse。

        Returns:
            str or None: アップロード成功時はファイルのウェブビューリンク、失敗時はNone。
        """
        # ステップ1: データ配列をテキストコンテンツに変換
        text_content = self._convert_data_array_to_text_content(data_array)

        # ステップ2: テキストコンテンツをGoogle Driveにアップロード
        # 以前のメソッド名 `upload_text_to_drive` をそのまま使用
        return self.upload_text_to_drive(text_content, file_name, target_folder_id, share_publicly)
