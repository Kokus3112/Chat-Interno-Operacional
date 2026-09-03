# Chat Interno Operacional

Chat simples em rede local para comunicação entre setores de uma operação de restaurante/delivery.

O projeto foi criado para reduzir deslocamentos entre andares e agilizar comunicações entre caixa/salão, delivery e cozinha, em um ambiente onde o uso de celulares não era permitido durante a operação.

## Casos de uso

- Confirmar preparo ou retirada de pedidos.
- Solicitar produtos que ficam em outro setor, como sobremesas e sucos.
- Avisar status de pedidos do delivery.
- Reduzir idas e vindas entre salão, caixa e cozinha.

## Stack

- Python
- Tkinter
- Socket TCP
- Threading

## Como executar

1. Inicie o servidor no computador principal:

```bash
set CHAT_HOST=127.0.0.1
set CHAT_PORT=5000
python salao.py
```

2. Nos outros computadores, informe o IP do servidor:

```bash
set CHAT_HOST=IP_DO_SERVIDOR
set CHAT_PORT=5000
python delivery.py
```

Opcionalmente, rode `python escritorio.py` para o terminal do escritório.

## Privacidade

O IP real da rede interna não fica no código. Históricos locais de conversa também ficam fora do repositório.
