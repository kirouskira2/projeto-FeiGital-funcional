# FeiGital

Esse é o nosso projeto de feira virtual. O objetivo é deixar os feirantes cadastrarem as bancas e produtos deles, e os clientes conseguirem comprar de várias bancas ao mesmo tempo. No final o sistema gera um QR Code para retirar o pedido.

Coisas principais do sistema:
- Venda de produtos por banca
- Carrinho de compras único (junta tudo num lugar só)
- Gera QR Code pra retirada
- O feirante consegue ver o total de vendas dele

Como rodar o projeto:
Tem que criar o ambiente virtual, instalar os requisitos e rodar as migrações.

Comandos pro Windows:
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Depois é só abrir http://127.0.0.1:8000

Observações:
- Tem login de Feirante e Cliente.
- O banco de dados é o SQLite padrão.
- As imagens ficam salvas na pasta media/.
