# ✦ Interview Copilot ✦

O **Interview Copilot** é um assistente virtual inteligente e silencioso de código aberto desenvolvido para auxiliar candidatos de qualquer área profissional durante entrevistas de emprego em tempo real. 

Ele roda localmente em uma janela translúcida com estilo *glassmorphism* (sem bordas e sempre no topo), captura o áudio do entrevistador e do candidato, transcreve a conversa em tempo real e fornece sugestões de fala personalizadas baseadas no currículo (CV) do candidato e na descrição da vaga (Job Description).

> [!IMPORTANT]  
> **Quer começar rapidamente e sem custos?** Consulte o nosso **[Guia Detalhado de APIs e Custos (API Guide)](API_GUIDE.md)** para aprender como criar suas contas e chaves de forma gratuita nas plataformas integradas (Deepgram, Groq, Cerebras, Gemini, Cloudflare, OpenRouter), entender o mecanismo de failover dinâmico e conferir um cenário real de uso.

---

## 🎯 Objetivo do Projeto

Durante processos seletivos e entrevistas profissionais, é comum ter que lembrar rapidamente de detalhes de projetos anteriores, conceitos teóricos ou estruturar respostas estruturadas e comportamentais em segundos. 

O objetivo do **Interview Copilot** é atuar como uma "segunda mente" em tempo real:
- **Transcrever o áudio** da conversa instantaneamente (tanto do microfone quanto do áudio do computador vindo do Teams, Zoom, Google Meet, etc.).
- **Gerar roteiros e tópicos de resposta personalizados** baseados em experiências reais do seu currículo.
- **Manter a discrição**, rodando em uma janela com opacidade ajustável e design minimalista sem foco em tarefas do sistema.

---

## 🚀 Principais Funcionalidades

1. **Captura Híbrida de Áudio (WASAPI Loopback)**:
   - **Microfone**: Captura a sua própria voz.
   - **Sistema (Desktop Audio)**: Captura a voz do entrevistador vinda de qualquer plataforma (Teams, Zoom, Meet, Slack, Discord).
   - **Modo Híbrido**: Captura ambos simultaneamente.
2. **Transcrição Instantânea (STT)**: Utiliza a API ultrarrápida do **Deepgram** para transcrever o áudio com latência inferior a 1 segundo.
3. **Mecanismo de Correção Automática (Sanitizer)**: Limpa os erros de transcrição e formata jargões específicos e termos de sua área de atuação usando IA rápida.
4. **Respostas sob Medida com Multi-LLM**:
   - Integração com **Groq**, **Cerebras**, **Gemini**, **OpenRouter** e **Cloudflare Workers AI**.
   - Mecanismo de **Failover Automático**: Se o provedor principal demorar mais de `0.8s`, o sistema consulta outro provedor imediatamente para garantir resposta instantânea.
5. **Contextualização com seu Perfil**: Injeta dinamicamente seu histórico profissional (currículo/CV, realizações importantes, competências essenciais) e a descrição da vaga de interesse nas respostas da IA.
6. **Interface Gráfica Premium**:
   - Janela sem bordas (*frameless*) e translúcida.
   - Sempre visível no topo (*always-on-top*).
   - Controle de opacidade em tempo real.
   - Abas integradas para Copilot, customização de Prompts, Visualização de Perfil e Bloco de Notas (Scratchpad).

---

## 📂 Estrutura do Projeto

```text
├── core/
│   ├── audio_capture.py     # Captura de áudio do microfone e loopback WASAPI
│   ├── config.py            # Validação e carregamento de configurações do .env
│   ├── event_loop.py        # Integração do loop assíncrono do asyncio com o PyQt6
│   ├── profile.py           # Gerenciador de perfil do candidato e vaga
│   └── session_logger.py    # Log de sessões de entrevista executadas
├── pipeline/
│   ├── analyzer.py          # Analisador de fluxo de conversas
│   ├── orchestrator.py      # Orquestrador do fluxo Áudio -> STT -> Sanitizer -> LLM
│   ├── responder.py         # Gerenciador de chamadas de LLM (Groq, Cerebras, etc.) com failover
│   ├── sanitizer.py         # Higienizador de áudio e correção técnica
│   ├── stt.py               # Integração de streaming com o Deepgram
│   └── tts.py               # Text-to-Speech (se aplicável para testes)
├── ui/
│   ├── copilot_tab.py       # Aba de transcrição e respostas do Copiloto
│   ├── dashboard.py         # Tela de status e métricas
│   ├── live_session.py      # Visualização da sessão em execução
│   ├── main_window.py       # Janela principal translúcida e eventos de resize/drag
│   ├── profile_tab.py       # Aba para editar o perfil/currículo do candidato
│   ├── prompt_tab.py        # Aba para customizar o Prompt de Sistema do LLM
│   ├── scratchpad_tab.py    # Aba de bloco de notas rápido
│   └── signals.py           # Sinais Qt para comunicação assíncrona
├── scratch/                 # Scripts úteis para testes individuais de APIs e SDKs
├── .env.example             # Modelo das variáveis de ambiente
├── requirements.txt         # Dependências do projeto
├── main.py                  # Ponto de entrada do aplicativo
├── validate_keys.py         # Script utilitário para validar chaves de API
└── run.bat                  # Inicializador rápido para ambiente Windows
```

---

## 🛠️ Instalação e Configuração

Siga os passos abaixo para configurar o projeto no Windows:

### 1. Pré-requisitos
- **Python 3.10 ou superior** instalado.
- Certifique-se de que o gerenciador de pacotes `pip` está atualizado.

### 2. Clonar o Repositório e Instalar as Dependências
Abra o terminal (PowerShell ou CMD) e execute:

```powershell
# Clone o repositório
git clone https://github.com/humberto-jezus/interview-assistant.git
cd "Interview Assistant"

# Crie um ambiente virtual (recomendado)
python -m venv venv
.\venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

> [!NOTE]  
> O projeto utiliza `pyaudiowpatch` para capturar o áudio interno do Windows. Se a instalação padrão falhar devido a restrições de compilação, instale-o explicitamente com:
> `pip install pyaudiowpatch`

### 3. Configurar as Variáveis de Ambiente
1. Copie o arquivo `.env.example` para `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Abra o arquivo `.env` gerado e preencha as chaves com os seus dados reais:
   - `DEEPGRAM_API_KEY`: Necessária para a transcrição em tempo real.
   - `GROQ_API_KEY` / `CEREBRAS_API_KEY` / `GOOGLE_API_KEY` (Gemini) / `OPENROUTER_API_KEY`: Chaves dos provedores de LLM que fornecem os roteiros de fala.
    - `CLOUDFLARE_ACCOUNT_ID` & `CLOUDFLARE_API_TOKEN`: Utilizados caso queira habilitar o corretor técnico de termos da Cloudflare.

> [!WARNING]  
> Nunca adicione chaves reais ao arquivo `.env.example` e nunca envie o arquivo `.env` para repositórios públicos do GitHub. O arquivo `.env` já está protegido no `.gitignore` deste repositório.

### 4. Guia Detalhado das APIs e Custos
Para instruções passo a passo de como criar suas contas nas plataformas de IA (Deepgram, Groq, Cerebras, Gemini, Cloudflare, OpenRouter), obter chaves gratuitas, entender os limites e ver cenários práticos de uso, consulte o [Guia de APIs](API_GUIDE.md).

### 5. Validar as Chaves de API
Antes de rodar a aplicação completa, você pode verificar se as chaves configuradas estão válidas e prontas usando o script validador:
```powershell
python validate_keys.py
```
O script testará a comunicação e latência com os provedores configurados.

---

## 🎮 Como Usar

Para iniciar a aplicação:

1. Dê dois cliques em `run.bat` ou rode pelo PowerShell:
   ```powershell
   .\run.bat
   ```
2. A janela do **Interview Copilot** aparecerá de forma translúcida na tela.
3. No topo da interface, selecione a fonte de áudio:
   - **🎙️ Microphone**: Se quiser testar apenas a sua voz.
   - **🖥️ System Audio**: Se quiser capturar a voz do entrevistador no Zoom/Teams/Meet.
   - **🎧 Both (Hybrid)**: Para capturar todo o contexto da entrevista (Recomendado).
4. No topo direito, selecione o idioma da transcrição (🇬🇧 **EN** ou 🇧🇷 **PT**).
5. Clique em **▶ Start** para iniciar a escuta em tempo real.
6. A Inteligência Artificial passará a preencher a aba **Copilot** com tópicos de fala recomendados em tempo real de acordo com as perguntas que ela escutar!
7. Use o controle deslizante de **Opacity** para ajustar o nível de transparência da janela conforme a sua preferência na tela.

---

## 🔐 Configuração em Produção vs Desenvolvimento

- **Desenvolvimento local:** O aplicativo busca as variáveis de ambiente a partir do arquivo `.env` localizado na raiz do projeto.
- **Produção:** Em ambientes de produção (ou se preferir no seu próprio computador pessoal sem expor arquivos `.env`), você pode definir as variáveis de ambiente diretamente nas variáveis globais do Sistema Operacional (Windows/Linux). O aplicativo prioriza a leitura de variáveis declaradas no SO.

---

## 📜 Licença e Termos de Uso
Este software destina-se apenas a fins educacionais e auxílio de acessibilidade durante o desenvolvimento profissional. Certifique-se de estar em conformidade com as regras de confidencialidade e diretrizes das empresas parceiras ao utilizá-lo.
