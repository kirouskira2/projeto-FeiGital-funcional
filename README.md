# FeiGital

Aplicação de feira virtual para que feirantes cadastrem suas bancas e produtos. Clientes podem montar um carrinho com itens de diferentes bancas, finalizar um pedido único e retirar usando QR Code.

## Objetivo
- Permitir a venda organizada por banca.
- Oferecer carrinho unificado para o cliente.
- Gerar QR Code para retirada do pedido.
- Mostrar resumo de vendas para o feirante.

## Instalação
1. Criar e ativar o ambiente virtual.
2. Instalar as dependências.
3. Aplicar migrações.
4. Popular o banco de dados (cria usuários, produtos e imagens).
5. Rodar o servidor.

Comandos (Windows):
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Acesse: `http://127.0.0.1:8000`

## Credenciais de Acesso (Demo)
Após rodar o `seed_demo`, utilize estas contas para testar:
- **Admin**: `admin` / `admin123` (Acesso total ao Django Admin)
- **Feirante**: `feirante` / `feirante123` (Gestão de banca e produtos)
- **Cliente**: `cliente` / `cliente123` (Compra e carrinho)

## Principais Funcionalidades
- Autenticação com tipos de usuário: Feirante e Cliente.
- Feirante: CRUD de produtos, gestão de pedidos e resumo de vendas.
- Cliente: carrinho na sessão, checkout e histórico de pedidos.
- QR Code: página do pedido exibe o QR para retirada.

## Observações
- Banco de dados em SQLite para desenvolvimento.
- Imagens de produtos são salvas em `media/`.
- Para produção, configurar `DEBUG=False`, `ALLOWED_HOSTS` e armazenamento de mídia/estáticos.
