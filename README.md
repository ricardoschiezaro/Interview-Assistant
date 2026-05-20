# ✦ Interview Copilot ✦

O **Interview Copilot** é um assistente virtual inteligente e silencioso de código aberto desenvolvido para auxiliar candidatos de qualquer área profissional durante entrevistas de emprego em tempo real. 

Ele roda localmente em uma janela translúcida com estilo *glassmorphism* (sem bordas e sempre no topo), captura o áudio do entrevistador e do candidato, transcreve a conversa em tempo real e fornece sugestões de fala personalizadas baseadas no currículo (CV) do candidato e na descrição da vaga (Job Description).

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
2. Abra o arquivo `.env` gerado e preencha as chaves com os seus dados reais. Veja abaixo como criar cada uma delas gratuitamente.

> [!WARNING]  
> Nunca adicione chaves reais ao arquivo `.env.example` e nunca envie o arquivo `.env` para repositórios públicos do GitHub. O arquivo `.env` já está protegido no `.gitignore` deste repositório.

### 4. Validar as Chaves de API
Antes de rodar a aplicação completa, você pode verificar se as chaves configuradas estão válidas e prontas usando o script validador:
```powershell
python validate_keys.py
```
O script testará a comunicação e latência com os provedores configurados.

---

## 🔑 Guia de APIs: Como Criar, Benefícios e Custos

A maioria dos serviços integrados no **Interview Copilot** oferece camadas gratuitas extremamente generosas. Você pode usar o aplicativo para testes e dezenas de entrevistas reais **sem gastar absolutamente nada**.

### 🎙️ Deepgram — Transcrição de Áudio em Tempo Real (STT)

*   **O que faz:** Transcreve a fala do microfone ou do áudio do computador em tempo real com baixíssima latência.
*   **Camada Gratuita:** **$20 de créditos gratuitos** ao cadastrar (~**33 horas** de streaming em tempo real com o modelo Nova-2).
*   **Custo pós-gratuito:** ~$0.0043/minuto (~$0.26/hora). 10 horas de entrevista no mês = **~$2.60 USD**.
*   **Como criar a chave:**
    1. Acesse [console.deepgram.com](https://console.deepgram.com/) e crie uma conta gratuita.
    2. No menu esquerdo, vá em **API Keys** → **Create a New API Key**.
    3. Dê um nome (ex: `InterviewCopilot`) e selecione permissão `Member`.
    4. Copie a chave e cole em `DEEPGRAM_API_KEY` no seu `.env`.

---

### ⚡ Groq — LLM Ultrarrápido (Provedor Principal)

*   **O que faz:** Gera as respostas do copiloto com latência de ~150–300ms usando hardware LPU dedicado.
*   **Camada Gratuita:** **100% gratuita** no plano básico (com Rate Limits por minuto — suficiente para todas as entrevistas).
*   **Custo pós-gratuito:** ~$0.59 por 1 milhão de tokens de entrada / ~$0.79 por 1 milhão de tokens de saída (centavos de dólar por entrevista).
*   **Como criar a chave:**
    1. Acesse [console.groq.com](https://console.groq.com/) e crie uma conta.
    2. Vá para a aba **API Keys** → **Create API Key**.
    3. Copie a chave (começa com `gsk_`) e cole em `GROQ_API_KEY` no seu `.env`.

---

### 🧠 Cerebras — LLM de Altíssima Velocidade (Failover)

*   **O que faz:** Inferência baseada em hardware CS-3 com a maior taxa de geração de tokens/segundo do mercado. Serve de fallback automático quando a Groq está lenta.
*   **Camada Gratuita:** **100% gratuita** na fase atual de Developer Beta (30 requisições/minuto).
*   **Custo pós-Beta:** Estimado entre $0.10–$0.60 por 1 milhão de tokens.
*   **Como criar a chave:**
    1. Acesse [cloud.cerebras.ai](https://cloud.cerebras.ai/) e cadastre-se.
    2. Vá em **API Keys** no menu de desenvolvimento → crie a chave (começa com `csk-`).
    3. Cole em `CEREBRAS_API_KEY` no seu `.env`.

---

### ♊ Google Gemini — Raciocínio e Contexto Longo (Failover)

*   **O que faz:** Excelente compreensão semântica e suporte a janelas de contexto gigantescas para cruzar seu currículo com perguntas difíceis.
*   **Camada Gratuita:** **15 RPM e 1.500 requisições/dia** com o modelo `Gemini-2.5-Flash` — mais do que suficiente para qualquer entrevista.
*   **Custo pós-gratuito:** $0.075 por 1 milhão de tokens de entrada / $0.30 de saída — um dos modelos mais baratos do mundo.
*   **Como criar a chave:**
    1. Acesse [aistudio.google.com](https://aistudio.google.com/) e faça login com sua conta Google.
    2. Clique em **Get API Key** → **Create API Key** (escolha um projeto ou crie um novo).
    3. Cole a chave gerada em `GOOGLE_API_KEY` no seu `.env`.

---

### ☁️ Cloudflare Workers AI — Sanitizer / Corretor de Texto (Edge)

*   **O que faz:** Roda modelos leves na borda da rede Cloudflare para corrigir erros de transcrição e formatar jargões de sua área de atuação antes de enviar à LLM principal.
*   **Camada Gratuita:** **10.000 "Neurons" por dia** (~10.000–20.000 tokens gerados/dia, o suficiente para 1–2 horas diárias de entrevista).
*   **Custo pós-gratuito:** ~$0.011 USD por 1.000 Neurons adicionais.
*   **Como criar a chave:**
    1. Faça login em [dash.cloudflare.com](https://dash.cloudflare.com/).
    2. Seu **Account ID** está no painel lateral direito na tela inicial.
    3. Vá em **My Profile** (canto superior direito) → **API Tokens** → **Create Token** usando o template **Workers AI (Beta)**.
    4. Salve o Account ID em `CLOUDFLARE_ACCOUNT_ID` e o token em `CLOUDFLARE_API_TOKEN`.

---

### 🌐 OpenRouter — Hub Multimodelo (Failover Opcional)

*   **O que faz:** Dá acesso a centenas de modelos (Llama, Claude, Mistral) com uma única chave e faturamento unificado.
*   **Camada Gratuita:** Acesso a modelos open-source **totalmente grátis** (ex: `Llama 3 8B Instruct free`, `Mistral 7B Instruct free`).
*   **Custo pós-gratuito:** Pré-pago a partir de $5 USD, cobrado pelo token do modelo escolhido ($0.07–$0.80 por milhão de tokens).
*   **Como criar a chave:**
    1. Acesse [openrouter.ai](https://openrouter.ai/) e crie uma conta.
    2. Vá nas configurações de perfil → **Keys** → **Create Key**.
    3. Cole em `OPENROUTER_API_KEY` no seu `.env`.

---

## 📊 Resumo de Benefícios e Latências

| Plataforma | Papel no Sistema | Latência Média | Camada Gratuita |
| :--- | :--- | :--- | :--- |
| **Deepgram** | Transcrição (STT) | < 300ms | $20 créditos (~33h de stream) |
| **Groq** | LLM Principal | ~150–300ms | Gratuita (Rate Limits) |
| **Cerebras** | LLM Failover | ~100–250ms | Gratuita (Beta) |
| **Google Gemini** | LLM Failover | ~600ms–1s | 1.500 req/dia grátis |
| **Cloudflare** | Sanitizer/Corretor | ~200–400ms | 10.000 Neurons/dia grátis |
| **OpenRouter** | Hub Multimodelo | Variável | Modelos grátis disponíveis |

---

## 🔄 Como Funciona o Failover Automático de APIs

O **Interview Copilot** garante que você **nunca** fique sem resposta durante uma entrevista, mesmo que uma API falhe ou fique lenta:

1. **Tentativa Principal:** O sistema dispara a pergunta para o provedor principal (ex: Groq).
2. **Timeout de 800ms:** Um cronômetro interno aguarda a resposta por no máximo **800 milissegundos**.
3. **Failover Instantâneo:** Se a API principal ultrapassar o limite (instabilidade, lentidão ou Rate Limit), a requisição é cancelada e o sistema consulta imediatamente o provedor secundário (ex: Cerebras ou Gemini).
4. **Transparência Total:** Você não percebe nenhuma queda — a resposta aparece na tela em menos de **1.5 segundos** no total.

> [!TIP]  
> Quanto mais chaves de API você configurar no `.env`, mais robusto e resiliente será o sistema de failover!

---

## 🎬 Cenário de Uso Prático

Veja como o fluxo funciona em uma entrevista real:

1. **A Pergunta:** O entrevistador pergunta via Zoom:
   > *"Como você lida com projetos atrasados e com orçamento estourado?"*
2. **Captura:** O áudio sai nas caixas de som e é capturado pelo driver WASAPI (modo `System Audio`).
3. **Transcrição (Deepgram):** Em **~250ms**, a fala vira texto na sua tela.
4. **Sanitização (Cloudflare):** Em **~200ms**, o corretor formata o texto e ajusta jargões da sua área.
5. **Consulta à LLM (Groq):** O texto + seu currículo são enviados ao Groq. A rede oscila e atinge o limite de 800ms sem resposta.
6. **Failover (Cerebras):** O sistema rotaciona automaticamente para o Cerebras. Em **~350ms** a resposta é gerada.
7. **Exibição:** Na aba **Copilot**, você vê os tópicos de resposta baseados no seu histórico real.
8. **Resultado:** Menos de **1.5 segundos** após o entrevistador parar de falar, você já tem o roteiro na tela e pode responder com naturalidade e autoridade.

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
