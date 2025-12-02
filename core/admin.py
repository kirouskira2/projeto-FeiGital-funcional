from django.contrib import admin
from .models import Profile, Banca, Produto, Pedido, ItensPedido


class ItensPedidoInline(admin.TabularInline):
    model = ItensPedido
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario')
    list_filter = ('tipo_usuario',)


@admin.register(Banca)
class BancaAdmin(admin.ModelAdmin):
    list_display = ('nome_banca', 'dono')
    search_fields = ('nome_banca', 'dono__username')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'banca', 'preco', 'disponibilidade')
    list_filter = ('banca', 'disponibilidade')
    search_fields = ('nome',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'data_pedido')
    list_filter = ('status', 'data_pedido')
    inlines = [ItensPedidoInline]

# Register your models here.
