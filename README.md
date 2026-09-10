# Chat Interno Operacional

Chat em rede local para comunicação entre setores de uma operação de restaurante/delivery.

O projeto foi criado para reduzir deslocamentos entre andares e agilizar comunicações entre caixa/salão, delivery e cozinha, em um ambiente onde o uso de celulares não era permitido durante a operação.

## Problema

Na operação, algumas confirmações simples dependiam de deslocamento físico entre setores, como:

- avisar a cozinha/delivery sobre um pedido feito no caixa;
- confirmar retirada de pedidos;
- solicitar sobremesas, sucos ou itens que ficam em outro setor;
- consultar rapidamente se um pedido já estava pronto.

Isso gerava interrupções, idas e vindas entre andares e perda de tempo em horários de movimento.

## Solução

A aplicação cria um chat interno simples, com servidor central e clientes por setor. Cada estação pode enviar mensagens para outro setor ou para todos os usuários conectados.

Na versão atual, o projeto foi reorganizado em:

- `chat_server.py`: servidor TCP responsável por receber conexões, registrar usuários online e encaminhar mensagens.
- `chat_client.py`: interface Tkinter compartilhada pelos terminais.
- `salao.py`, `delivery.py` e `escritorio.py`: atalhos para iniciar cada cliente com o usuário correto.
- `chat_common.py`: funções comuns de configuração, envio e recebimento de pacotes.
- `chat_config.example.json`: exemplo de configuração pública, sem IPs reais da operação.

## Casos de uso

- Confirmar preparo ou retirada de pedidos.
- Solicitar produtos que ficam em outro setor, como sobremesas e sucos.
- Avisar status de pedidos do delivery.
- Reduzir idas e vindas entre salão, caixa e cozinha.
- Acompanhar quais setores estão online.
- Manter histórico local das mensagens em cada terminal.

## Stack

- Python
- Tkinter
- Socket TCP
- Threading
- JSON para configuração

## Como executar

1. Copie o arquivo de exemplo:

```bash
copy chat_config.example.json chat_config.json
```

2. Ajuste `server_host` no `chat_config.json` para o IP do computador que será o servidor.

3. Inicie o servidor no computador principal:

```bash
python servidor.py
```

4. Em cada terminal, rode o cliente correspondente:

```bash
python salao.py
python delivery.py
python escritorio.py
```

Também é possível iniciar o cliente informando o usuário por argumento:

```bash
python chat_client.py --user SALAO
python chat_client.py --user DELIVERY
python chat_client.py --user ESCRITORIO
```

## Funcionalidades

- Envio de mensagens entre setores específicos.
- Envio para todos os usuários conectados.
- Reconexão automática quando o servidor fica indisponível.
- Lista de usuários online.
- Janela volta para frente ao receber mensagem.
- Histórico local por terminal.
- Configuração externa por JSON.

## Privacidade

O IP real da rede interna, arquivos de configuração locais, históricos de conversa e arquivos gerados para distribuição não ficam no repositório.

Este projeto usa dados e nomes genéricos para demonstrar a solução sem expor informações internas da empresa.
