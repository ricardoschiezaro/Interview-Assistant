# Guia de APIs: Criação, Benefícios, Failover e Cenário de Uso

Este documento detalha o ecossistema de APIs integrado no **Interview Copilot**, ensinando como obter as chaves de API, os benefícios de cada plataforma, como funciona a rotatividade (failover) automática de modelos e um cenário prático de uso.

---

## 🔑 1. Como Criar as Chaves de API nas Plataformas

### 🎙️ Deepgram (Transcrição de Áudio - STT)
*   **O que faz:** Transcreve a fala do microfone ou do áudio do computador em tempo real com baixa latência.
*   **Como criar a chave:**
    1. Acesse o console oficial: [console.deepgram.com](https://console.deepgram.com/).
    2. Crie uma conta gratuita (você ganha $20 em créditos iniciais, o suficiente para dezenas de horas de transcrição).
    3. No menu esquerdo, vá em **API Keys**.
    4. Clique em **Create a New API Key**.
    5. Dê um nome (ex: `InterviewCopilot`) e selecione a permissão `Administrator` ou `Member`.
    6. Copie a chave gerada e cole em `DEEPGRAM_API_KEY` no seu arquivo `.env`.

### ⚡ Groq (LLM Ultrarrápido)
*   **O que faz:** Processa o contexto e gera as respostas do copiloto instantaneamente.
*   **Como criar a chave:**
    1. Acesse o console da Groq: [console.groq.com](https://console.groq.com/).
    2. Crie sua conta ou faça login.
    3. Vá para a aba **API Keys**.
    4. Clique em **Create API Key**.
    5. Copie a chave gerada (ela começa com `gsk_`) e configure-a em `GROQ_API_KEY`.

### 🧠 Cerebras (LLM de Altíssima Velocidade)
*   **O que faz:** Oferece inferência recorde baseada em hardware CS-3, servindo como uma alternativa extremamente rápida à Groq.
*   **Como criar a chave:**
    1. Acesse: [cloud.cerebras.ai](https://cloud.cerebras.ai/).
    2. Cadastre-se na plataforma.
    3. Acesse a seção **API Keys** no menu de desenvolvimento.
    4. Crie uma nova chave de API (começa com `csk-`) e salve em `CEREBRAS_API_KEY`.

### ♊ Google AI Studio (Gemini - Contexto Longo e Raciocínio)
*   **O que faz:** Provedor alternativo excelente para processamento de múltiplos idiomas e compreensão profunda.
*   **Como criar a chave:**
    1. Acesse o Google AI Studio: [aistudio.google.com](https://aistudio.google.com/).
    2. Faça login com sua conta do Google.
    3. Clique no botão azul **Get API Key** (Obter chave de API) no canto superior esquerdo.
    4. Clique em **Create API Key** e selecione se deseja associá-la a um projeto existente do Google Cloud ou criar um novo projeto.
    5. Copie a chave gerada e cole em `GOOGLE_API_KEY`.

### 🌐 OpenRouter (Hub Multimodelo)
*   **O que faz:** Dá acesso a centenas de modelos de código aberto (Llama, Claude, Mistral) através de uma única interface de pagamento e chave.
*   **Como criar a chave:**
    1. Acesse: [openrouter.ai](https://openrouter.ai/).
    2. Cadastre-se e crie sua conta.
    3. Vá em **Keys** nas configurações de perfil.
    4. Clique em **Create Key**, copie o valor gerado e configure em `OPENROUTER_API_KEY`.

### ☁️ Cloudflare Workers AI (Inferência na Borda/Edge)
*   **O que faz:** Rodar modelos leves na rede de borda da Cloudflare, usado no projeto principalmente para o higienizador/corretor de texto (`Sanitizer`).
*   **Como criar a chave:**
    1. Faça login no painel: [dash.cloudflare.com](https://dash.cloudflare.com/).
    2. No menu esquerdo, navegue até **AI** > **Workers AI**.
    3. Para obter seu **Account ID**, basta copiar o ID numérico exibido no painel lateral direito na página principal do seu painel Cloudflare.
    4. Para o **API Token**, acesse **My Profile** (canto superior direito) > **API Tokens**.
    5. Clique em **Create Token**, use o template **Workers AI (Beta)**, dê a permissão necessária e gere o token. Salve-os em `CLOUDFLARE_ACCOUNT_ID` e `CLOUDFLARE_API_TOKEN`.

---

## 📈 2. Benefícios de Cada Plataforma

| Plataforma | Especialidade | Latência Média | Benefício Principal |
| :--- | :--- | :--- | :--- |
| **Deepgram** | Speech-to-Text | < 300ms | Transcrições contínuas em tempo real com excelente precisão em português e inglês. |
| **Groq** | LPU Inference | ~150ms-300ms | Processamento instantâneo de modelos complexos como o `Llama-3.3-70b`, gerando respostas sem atraso na fala. |
| **Cerebras** | CS-3 Silicon | ~100ms-250ms | A maior velocidade de geração de tokens por segundo do mercado atual. |
| **Google Gemini** | LLM Raciocínio | ~600ms-1s | Compreensão semântica superior para conectar pontos do seu currículo com perguntas difíceis. |
| **Cloudflare** | Edge Computing | ~200ms-400ms | Custos insignificantes e estabilidade para rodar o higienizador/corretor ortográfico de termos. |
| **OpenRouter** | Diversidade | Variável | Flexibilidade para alternar de modelo ou usar APIs redundantes sem código extra. |

---

## 🔄 3. Rotatividade de APIs (Failover Automático)

### Como funciona no código?
No arquivo `pipeline/responder.py` do projeto, o Copilot implementa um mecanismo de **Orquestração com Failover**:

1. **Tentativa Principal:** O aplicativo dispara a pergunta para o provedor definido como principal (ex: Groq).
2. **Timeout Estrito:** Um temporizador interno aguarda a resposta por no máximo **800 milissegundos**.
3. **Failover Dinâmico:** Se a API principal demorar para responder (devido a lentidão na rede, instabilidade do servidor ou limite de requisições excedido), a requisição é cancelada e o Copilot envia a mesma pergunta imediatamente para o **provedor secundário** (ex: Cerebras ou Gemini).
4. **Resiliência:** O usuário final na tela do aplicativo não percebe a queda de um serviço, pois a resposta ainda aparece em menos de 1.5 segundos.

### Rotacionamento e Segurança de Chaves
- **Chaves no ambiente local (`.env`):** Suas chaves ficam salvas na sua máquina local, protegidas e ignoradas pelo Git (`.gitignore`).
- **Produção:** Em servidores ou plataformas na nuvem, as chaves não são armazenadas em arquivos. Elas são injetadas em memória como Variáveis de Ambiente do Sistema. Isso garante que nenhum atacante com acesso ao repositório do Git consiga ler suas chaves.

---

## 🎬 4. Cenário de Uso Prático

Imagine o seguinte fluxo durante uma entrevista de emprego de qualquer área (ex: Gerente de Projetos):

1. **A Pergunta:** O entrevistador pergunta por chamada de vídeo no Zoom: 
   > *"Como você lida com projetos que estão atrasados e com o orçamento estourado?"*
   
2. **A Captura:** O áudio do entrevistador sai no seu computador e é capturado imediatamente pelo driver de loopback WASAPI do Windows (`System Audio` no Interview Copilot).
3. **STT (Deepgram):** Em **250ms**, a fala do entrevistador é transcrita em texto e exibida na sua tela.
4. **Sanitização (Cloudflare):** O higienizador corrige gramática e jargões específicos de gestão em **200ms**.
5. **A Consulta à LLM:** O texto sanitizado é disparado para o Groq junto com o seu currículo (onde consta que você tem certificação PMP e experiência real salvando cronogramas).
6. **O Failover em Ação:** 
   - A rede da Groq sofre uma oscilação momentânea e a resposta atinge o limite de 800ms sem retornar nada.
   - O aplicativo cancela a requisição da Groq e dispara imediatamente para o Cerebras/Gemini.
   - Em mais **350ms**, o Cerebras retorna a resposta estruturada.
7. **A Exibição na Tela:** Na aba **Copilot**, você vê tópicos de resposta como:
   *   *«Bem, em situações de estouro, eu primeiro aplico uma análise de valor agregado (EVM) para mapear o desvio real de custo e prazo.»*
   *   *«Na minha experiência anterior, quando lidamos com um desvio no projeto X, reuni os stakeholders, apresentei um plano de compressão (crashing) e renegociamos o escopo de menor valor.»*
8. **O Resultado:** Menos de **1.5 segundos** se passaram desde que o entrevistador terminou de falar. Você lê os tópicos na tela e responde com naturalidade, segurança e autoridade profissional técnica.
