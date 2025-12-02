from django.db import models
from django.contrib.auth.models import User
import uuid

# Tipos de usuário
TIPO_USUARIO_CHOICES = (
    ('feirante', 'Feirante'),
    ('cliente', 'Cliente'),
)


class Profile(models.Model):
    # Perfil com tipo de usuário
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_tipo_usuario_display()})"


class Banca(models.Model):
    # Banca do feirante
    dono = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__tipo_usuario': 'feirante'},
        related_name='bancas'
    )
    nome_banca = models.CharField(max_length=120)
    descricao = models.TextField()
    logo = models.ImageField(upload_to='bancas/', blank=True, null=True)

    def __str__(self):
        return self.nome_banca


class Produto(models.Model):
    # Produto da banca com preço, foto e validade
    banca = models.ForeignKey(Banca, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=120)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    foto = models.ImageField(upload_to='produtos/')
    validade = models.DateField(blank=True, null=True)
    disponibilidade = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.banca.nome_banca})"


# Status do pedido
STATUS_CHOICES = (
    ('novo', 'Novo'),
    ('em_separacao', 'Em Separação'),
    ('pronto', 'Pronto'),
    ('entregue', 'Entregue'),
)


class Pedido(models.Model):
    # Pedido do cliente com QR para retirada
    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__tipo_usuario': 'cliente'},
        related_name='pedidos'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    data_pedido = models.DateTimeField(auto_now_add=True)
    qr_code_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Pedido #{self.id} de {self.cliente.username} - {self.get_status_display()}"


class ItensPedido(models.Model):
    # Item do pedido com preço unitário e quantidade
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido {self.pedido.id})"
