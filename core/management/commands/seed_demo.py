from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from PIL import Image
import unicodedata
from django.core.files.base import ContentFile

from core.models import Profile, Banca, Produto, Pedido, ItensPedido


class Command(BaseCommand):
    help = 'Cria dados de demonstração: feirante/cliente, banca, 3 produtos com foto e 1 pedido.'

    def handle(self, *args, **options):
        # Usuário feirante com perfil
        feirante, created = User.objects.get_or_create(
            username='feirante', defaults={'email': 'feirante@example.com'}
        )
        if created:
            feirante.set_password('feirante123')
            feirante.save()
        Profile.objects.get_or_create(user=feirante, defaults={'tipo_usuario': 'feirante'})

        # Usuário cliente com perfil
        cliente, created = User.objects.get_or_create(
            username='cliente', defaults={'email': 'cliente@example.com'}
        )
        if created:
            cliente.set_password('cliente123')
            cliente.save()
        Profile.objects.get_or_create(user=cliente, defaults={'tipo_usuario': 'cliente'})

        # Banca do feirante
        banca, _ = Banca.objects.get_or_create(
            dono=feirante,
            nome_banca='Banca do João',
            defaults={'descricao': 'Produtos frescos e selecionados'}
        )

        # Função auxiliar: gera uma imagem simples com Pillow
        # Porquê: evitamos dependência de rede e garantimos um arquivo válido para ImageField.
        def gerar_imagem_rgb(cor_hex: str) -> ContentFile:
            img = Image.new('RGB', (600, 400), cor_hex)
            bio = BytesIO()
            img.save(bio, format='PNG')
            return ContentFile(bio.getvalue())

        validade = timezone.now().date() + timedelta(days=7)

        # Porquê: nomes de arquivos ASCII evitam problemas de encoding em URLs/SO.
        def ascii_slug(text: str) -> str:
            normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
            return normalized.lower().replace(' ', '-')
        produtos_info = [
            {'nome': 'Maçã', 'preco': 4.50, 'cor': '#d9534f'},
            {'nome': 'Banana', 'preco': 3.20, 'cor': '#f0ad4e'},
            {'nome': 'Alface', 'preco': 2.80, 'cor': '#5cb85c'},
        ]

        produtos = []
        for info in produtos_info:
            produto, created = Produto.objects.get_or_create(
                banca=banca,
                nome=info['nome'],
                defaults={
                    'preco': info['preco'],
                    'validade': validade,
                    'disponibilidade': True,
                },
            )
            # Porquê: garantimos que cada produto tenha uma imagem mesmo em ambientes de teste.
            if created or not produto.foto:
                conteudo = gerar_imagem_rgb(info['cor'])
                safe_name = f"{ascii_slug(info['nome'])}.png"
                produto.foto.save(safe_name, conteudo, save=True)
            produtos.append(produto)

        # Pedido de demonstração para o cliente (mostra QR Code e facilita avaliação)
        pedido = Pedido.objects.create(cliente=cliente, status='novo')
        for idx, p in enumerate(produtos, start=1):
            ItensPedido.objects.create(
                pedido=pedido,
                produto=p,
                quantidade=idx,  # quantidades 1,2,3 para variar subtotais
                preco_unitario=p.preco,  # porquê: preço "congelado" conforme regra de negócio
            )

        self.stdout.write(self.style.SUCCESS('Seed concluído: usuários feirante/cliente, banca, 3 produtos e 1 pedido criados.'))
