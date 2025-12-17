import telebot
import os
from datetime import datetime

CHAVE_API = ""
bot = telebot.TeleBot(CHAVE_API)

PASTA_RAIZ = r"C:\Users\Gabriel\Documents\Faculdade" 


GRADE_HORARIA = {
    0: [{"inicio": "08:00", "fim": "10:00", "materia": "Calculo I"}],
    
}

def descobrir_materia(timestamp_msg):
    # Converte o tempo do Telegram (timestamp) para data legível
    data_envio = datetime.fromtimestamp(timestamp_msg)
    
    dia_semana = data_envio.weekday()
    hora_envio = data_envio.strftime("%H:%M")
    
    if dia_semana in GRADE_HORARIA:
        for aula in GRADE_HORARIA[dia_semana]:
            if aula["inicio"] <= hora_envio <= aula["fim"]:
                return aula["materia"]
    return "Geral"

def processar_pendencias():
    # Pega as mensagens acumuladas no servidor
    updates = bot.get_updates()
    
    if not updates:
        print("Nenhuma foto nova para processar.")
        return

    print(f"Processando {len(updates)} mensagens...")

    ultimo_update_id = 0

    for update in updates:
        # Atualiza o ID para marcar como lido depois
        ultimo_update_id = update.update_id
        
        # Verifica se é uma mensagem e se tem foto
        if update.message and update.message.content_type == 'photo':
            mensagem = update.message
            
            try:
                # 1. Pega a data REAL do envio da mensagem
                timestamp = mensagem.date
                data_obj = datetime.fromtimestamp(timestamp)
                data_pasta = data_obj.strftime("%Y-%m-%d")
                
                # 2. Descobre a matéria baseada na hora do ENVIO
                materia = descobrir_materia(timestamp)
                
                # 3. Estrutura de pastas
                caminho_final = os.path.join(PASTA_RAIZ, materia, data_pasta)
                if not os.path.exists(caminho_final):
                    os.makedirs(caminho_final)
                
                # 4. Baixa a foto
                file_id = mensagem.photo[-1].file_id
                file_info = bot.get_file(file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                
                nome_arquivo = f"foto_{data_obj.strftime('%H-%M-%S')}.jpg"
                caminho_completo = os.path.join(caminho_final, nome_arquivo)
                
                with open(caminho_completo, 'wb') as new_file:
                    new_file.write(downloaded_file)
                
                print(f"[OK] {materia} - {nome_arquivo}")
                
            except Exception as e:
                print(f"[ERRO] Falha ao processar mensagem: {e}")

    # Limpa a fila do Telegram (confirma que recebeu até o último ID)
    if ultimo_update_id > 0:
        bot.get_updates(offset=ultimo_update_id + 1)
        print("Limpeza concluída. Fila do Telegram esvaziada.")

if __name__ == "__main__":
    processar_pendencias()