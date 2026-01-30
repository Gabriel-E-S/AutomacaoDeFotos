# Automatição e separação de fotos

Nesse repositório a ideia principal é criar um script python que ao interagir com o Telegram filtra, classifica 
e organiza as fotos tiradas do quadro durante as aulas da semana. Assim esses registros irão ficar mais organizados,
facilitando os estudos.

# Como utilizar o script?

## 🤖 Passo 1: Criando o Bot no Telegram (Obrigatório)
Para que o sistema funcione, você precisa criar um bot no Telegram:

Abra o Telegram e pesquise por @BotFather.

Envie o comando /newbot.

Dê um nome para o bot (Exemplo: OrganizadorFaculdade).

Escolha um username (deve terminar em bot, exemplo: MeuOrganizadorBot).

O BotFather vai te enviar um TOKEN (algo como 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11).

Guarde esse Token, você vai precisar dele agora.

## Configuração
Crie um arquivo chamado .env na raiz do projeto (onde está o script.py). A configuração muda dependendo de como você quer usar:

### Modo 1: Apenas Local (Sem Google Drive)
Se você quer salvar as fotos apenas no seu computador.

No arquivo .env, adicione:

```env
APIKEY_TELEGRAM="Cole_Seu_Token_Aqui"
CAMINHOLOCAL="C:\Users\SeuUsuario\Documents\Faculdade"
```

Pronto, é só utilizar o organizador.

### Modo 2: Completo (Com Google Drive)
Para salvar localmente E fazer backup na nuvem.

Configuração no Google Cloud:

Acesse o Google Cloud Console.

Crie um novo projeto.

Ative a Google Drive API.

Em "Tela de Permissão OAuth", configure como Externo e adicione seu e-mail em Usuários de Teste (Test Users).

Em "Credenciais", crie um ID do Cliente OAuth (Desktop App).

Baixe o arquivo JSON, renomeie para credentials.json e coloque na pasta do projeto.

Pegar o ID da Pasta (Opcional):

Abra a pasta no Google Drive onde quer salvar tudo.

Olhe a URL: drive.google.com/drive/u/0/folders/1abcDEfg...

O código final (1abcDEfg...) é o ID.

Configurar o .env:

```env
APIKEY_TELEGRAM="Cole_Seu_Token_Aqui"
CAMINHOLOCAL="C:\Users\SeuUsuario\Documents\Faculdade"
IDPASTADRIVE="Cole_o_ID_da_Pasta_Drive_Aqui"
```

## Como Usar

Edite a Grade Horária: Abra o arquivo script.py e procure por GRADE_HORARIA. Ajuste os horários e matérias conforme sua necessidade (0 = Segunda, 1 = Terça, etc).

Execute o Bot:

```bash
python3 script.py
```

ou

```bash
python3 scriptDrive.py
```

Nota: Na primeira vez (modo Drive), uma janela do navegador abrirá pedindo permissão.

No Telegram: Envie fotos para o seu bot. O terminal mostrará o progresso e os arquivos aparecerão magicamente nas pastas!

***OBS***: Para instalar todas as bibliotecas necessárias para o projeto rode

```bash
pip install -r requirements.txt
```