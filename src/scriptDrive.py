# -- CÓDIGO POR: Gabriel do Espírito Santo, 2026 --

import telebot
import os
import os.path
from datetime import datetime
from dotenv import load_dotenv

# --- Importações do Google Drive ---
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

CHAVE_API = os.getenv("APIKEY_TELEGRAM")
SCOPES = ['https://www.googleapis.com/auth/drive.file'] # Permissão apenas para criar/editar arquivos criados pelo bot

if not CHAVE_API:
    raise ValueError("A chave da API não foi encontrada nas variáveis de ambiente")
    
bot = telebot.TeleBot(CHAVE_API)

_caminho_env = os.getenv("CAMINHOLOCAL")

if _caminho_env is None:
    raise ValueError("A variável CAMINHOLOCAL não está definida no arquivo .env")

PASTA_RAIZ = _caminho_env

GRADE_HORARIA = {
    0: [{"inicio": "08:00", "fim": "10:00", "materia": "Calculo I"}],
}

# --- FUNÇÕES DO GOOGLE DRIVE ---

def autenticar_drive():
    """Autentica e retorna o serviço do Google Drive."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Requer o arquivo credentials.json baixado do Google Cloud
            if not os.path.exists('credentials.json'):
                print("ERRO: Arquivo credentials.json não encontrado.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salva o token para a próxima vez não precisar logar
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def encontrar_ou_criar_pasta(service, nome_pasta, id_pai=None):
    """Procura uma pasta no Drive. Se não existir, cria."""
    query = f"name='{nome_pasta}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if id_pai:
        query += f" and '{id_pai}' in parents"
    
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    if files:
        return files[0]['id'] # Retorna o ID da pasta existente
    else:
        # Cria a pasta se não existir
        file_metadata = {
            'name': nome_pasta,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if id_pai:
            file_metadata['parents'] = [id_pai]
        
        folder = service.files().create(body=file_metadata, fields='id').execute()
        print(f"📁 Pasta Drive Criada: {nome_pasta}")
        return folder.get('id')

def upload_para_drive(service, caminho_arquivo_local, nome_arquivo, materia, data_pasta):
    """Gerencia a estrutura de pastas e faz o upload."""
    try:
        id_raiz = os.getenv("IDPASTADRIVE")

        if id_raiz is None:
            raise ValueError("Erro ao carregar id da raiz do drive")

        # Verifica/Cria pasta da Matéria
        id_materia = encontrar_ou_criar_pasta(service, materia, id_raiz)

        # Verifica/Cria pasta da Data dentro da Matéria
        id_data = encontrar_ou_criar_pasta(service, data_pasta, id_materia)

        # Faz o Upload
        file_metadata = {
            'name': nome_arquivo,
            'parents': [id_data]
        }
        media = MediaFileUpload(caminho_arquivo_local, mimetype='image/jpeg')
        
        arquivo = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"☁️ Upload concluído no Drive: {nome_arquivo} (ID: {arquivo.get('id')})")
        
    except Exception as e:
        print(f"❌ Erro no Upload para o Drive: {e}")

# --- FUNÇÕES PARA INTERAGIR COM O TELEGRAM E CRIAR A ORGANIZAÇÃO DE PASTAS ---

def descobrir_materia(timestamp_msg):
    data_envio = datetime.fromtimestamp(timestamp_msg)
    dia_semana = data_envio.weekday()
    hora_envio = data_envio.strftime("%H:%M")
    
    if dia_semana in GRADE_HORARIA:
        for aula in GRADE_HORARIA[dia_semana]:
            if aula["inicio"] <= hora_envio <= aula["fim"]:
                return aula["materia"]
    return "Geral"

def processar_pendencias():

    service_drive = autenticar_drive()
    if not service_drive:
        print("Aviso: Serviço do Google Drive não iniciado. Os arquivos serão apenas salvos localmente.")

    updates = bot.get_updates()
    
    if not updates:
        print("Nenhuma foto nova para processar.")
        return

    print(f"Processando {len(updates)} mensagens...")
    ultimo_update_id = 0

    for update in updates:
        
        ultimo_update_id = update.update_id
        
        if update.message and update.message.content_type == 'photo':
            mensagem = update.message
            
            try:
                timestamp = mensagem.date
                data_obj = datetime.fromtimestamp(timestamp)
                data_pasta = data_obj.strftime("%Y-%m-%d")
                materia = descobrir_materia(timestamp)
        
                if materia is None or data_pasta is None:
                    raise ValueError("Erro")
       
                caminho_final = os.path.join(PASTA_RAIZ, materia, data_pasta)

                if not os.path.exists(caminho_final):
                    os.makedirs(caminho_final) 
                
                if mensagem.photo is None:
                    continue

                file_id = mensagem.photo[-1].file_id

                file_info = bot.get_file(file_id)

                if file_info.file_path is None:
                    raise ValueError("Erro ao pegar arquivo do telegram")

                downloaded_file = bot.download_file(file_info.file_path)
               
                if not downloaded_file:
                   raise ValueError("O arquivo não foi baixado\n")

                nome_arquivo = f"foto_{data_obj.strftime('%H-%M-%S')}.jpg"

                caminho_completo = os.path.join(caminho_final, nome_arquivo)
                
                with open(caminho_completo, 'wb') as new_file:
                    new_file.write(downloaded_file)
                
                print(f"[OK] Salvo Localmente: {materia} - {nome_arquivo}")

                if service_drive:
                    print("Iniciando upload para o Drive...")
                    upload_para_drive(service_drive, caminho_completo, nome_arquivo, materia, data_pasta)
                
            except Exception as e:
                print(f"[ERRO] Falha ao processar mensagem: {e}")

    if ultimo_update_id > 0:
        bot.get_updates(offset=ultimo_update_id + 1)
        print("Limpeza concluída. Fila do Telegram esvaziada.")

if __name__ == "__main__":
    processar_pendencias() 
