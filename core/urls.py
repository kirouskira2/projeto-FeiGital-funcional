from django.urls import path
from . import views

urlpatterns = [
    # Público
    path('', views.home, name='home'),
    path('banca/<int:id_banca>/', views.banca_detalhe, name='banca_detalhe'),
    path('produto/<int:id_produto>/', views.produto_detalhe, name='produto_detalhe'),

    # Carrinho
    path('carrinho/', views.carrinho_view, name='carrinho'),
    path('carrinho/add/<int:id_produto>/', views.carrinho_add, name='carrinho_add'),
    path('carrinho/update/<int:id_produto>/', views.carrinho_update, name='carrinho_update'),
    path('carrinho/remove/<int:id_produto>/', views.carrinho_remove, name='carrinho_remove'),

    # Checkout e pedidos
    path('checkout/', views.checkout, name='checkout'),
    path('finalizar-pedido/', views.finalizar_pedido, name='finalizar_pedido'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('meus-pedidos/<uuid:qr_code_id>/', views.pedido_detalhe_qr, name='pedido_detalhe_qr'),
    path('meus-pedidos/deletar/<int:id_pedido>/', views.meus_pedidos_delete, name='meus_pedidos_delete'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/pedidos/', views.dashboard_pedidos, name='dashboard_pedidos'),
    path('dashboard/pedidos/update-status/<int:id_pedido>/', views.dashboard_pedidos_update_status, name='dashboard_pedidos_update_status'),
    path('dashboard/produtos/', views.dashboard_produtos_list, name='dashboard_produtos_list'),
    path('dashboard/produtos/novo/', views.dashboard_produtos_novo, name='dashboard_produtos_novo'),
    path('dashboard/produtos/editar/<int:id_produto>/', views.dashboard_produtos_editar, name='dashboard_produtos_editar'),
    path('dashboard/produtos/deletar/<int:id_produto>/', views.dashboard_produtos_deletar, name='dashboard_produtos_deletar'),

    # Cadastro
    path('accounts/signup/', views.signup, name='signup'),

    # Resumo de vendas
    path('dashboard/resumo/', views.dashboard_resumo, name='dashboard_resumo'),
]
