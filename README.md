# YT Downloader

Aplicativo de desktop para macOS que baixa vídeos do YouTube em alta qualidade e os salva na pasta `~/Downloads`.

## Como Usar

O aplicativo é **autocontido** — não requer nenhuma instalação manual de dependências (Python, yt-dlp ou ffmpeg).

### 1. Baixe o Aplicativo
Vá para a [página de Releases](https://github.com/vagnersantosaraujo/yt-downloader-app/releases) e baixe o arquivo `YT-Downloader.app.zip` da versão mais recente.

### 2. Descompacte e Mova
- Dê duplo clique no `.zip` para descompactar.
- Arraste o `YT Downloader.app` para a sua pasta de **Aplicativos**.

### 3. Autorize a Execução (Apenas na Primeira Vez)
O macOS bloqueia apps de desenvolvedores não identificados (Gatekeeper). Para liberar:

1. Tente abrir o app — o macOS exibirá um alerta. Clique em **OK**.
2. Abra **Ajustes do Sistema → Privacidade e Segurança**.
3. Role até a seção "Segurança" e clique em **"Abrir Mesmo Assim"**.
4. Confirme com sua senha ou Touch ID.

O macOS não perguntará novamente.

### 4. Baixe Vídeos
- Cole a URL de um vídeo do YouTube no campo de texto.
- Clique em **"Baixar Vídeo"**.
- O arquivo será salvo em `~/Downloads`.

---

## Desenvolvimento

### Pré-requisitos

```bash
brew install python-tk yt-dlp ffmpeg
pip install pyinstaller
```

### Rodar localmente (sem build)

```bash
python3 yt_downloader_gui.py
```

### Gerar o `.app` com PyInstaller

```bash
pyinstaller YT_Downloader.spec --noconfirm
# O app gerado estará em: dist/YT Downloader.app
```

O spec (`YT_Downloader.spec`) lê os caminhos dos binários de variáveis de ambiente, com fallback para o Homebrew:

| Variável | Padrão |
|---|---|
| `YT_DLP_PATH` | `/opt/homebrew/bin/yt-dlp` |
| `FFMPEG_PATH` | `/opt/homebrew/bin/ffmpeg` |

### Estrutura do projeto

```
yt-downloader-app/
├── yt_downloader_gui.py   # Código principal (GUI + lógica de download)
├── YT_Downloader.spec     # Configuração do PyInstaller
├── requirements-dev.txt   # Dependências de desenvolvimento
└── .github/
    └── workflows/
        └── build.yml      # CI/CD — build e release automático no GitHub Actions
```

### CI/CD (GitHub Actions)

O workflow `.github/workflows/build.yml` é disparado automaticamente ao criar uma tag de versão (`v*.*.*`). Ele:

1. Baixa o binário standalone do **yt-dlp** diretamente do repositório oficial.
2. Instala o **ffmpeg** via Homebrew.
3. Compila o `.app` com PyInstaller.
4. Empacota em `.zip` e publica como Release no GitHub.

Para criar um release:

```bash
git tag v1.2.0
git push origin v1.2.0
```

---

## Histórico de Mudanças

### v1.2.0
- **Migração de `py2app` para PyInstaller** — empacotamento mais confiável e portável; resolve erros de dependência (`jaraco.text`, Tcl/Tk) que impediam a execução em outras máquinas.
- **Correção do erro HTTP 403** — o YouTube passou a bloquear streams mp4 separados via protocolo SABR. Corrigido usando `--extractor-args youtube:player_client=android,web` e seleção de formato sem restrição de extensão.
- **Barra de progresso corrigida** — o código anterior tentava parsear stdout como JSON (nunca funcionou). Substituído por leitura linha a linha com `--newline` e regex em cima das linhas `[download] XX.X%`.
- **CI/CD com GitHub Actions** — build e publicação de releases automáticos ao criar uma tag `v*.*.*`.

### v1.1.0
- Empacotamento inicial com `py2app`.
- Interface gráfica com Tkinter.
- Integração com yt-dlp e ffmpeg.
