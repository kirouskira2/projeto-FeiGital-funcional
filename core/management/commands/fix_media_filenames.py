from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import Produto
import unicodedata
from io import BytesIO
from PIL import Image


def ascii_slug(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return normalized.lower().replace(' ', '-')


class Command(BaseCommand):
    help = 'Normaliza nomes de arquivos de imagens de produtos para ASCII (ex.: maçã.png -> maca.png).'

    def handle(self, *args, **options):
        count = 0
        for produto in Produto.objects.all():
            if not produto.foto:
                continue
            current_name = produto.foto.name  # ex.: 'produtos/maçã.png'
            target_basename = f"{ascii_slug(produto.nome)}.png"
            target_name = f"produtos/{target_basename}"
            if current_name == target_name:
                continue
            # Regrava o arquivo com nome seguro mantendo o conteúdo.
            try:
                produto.foto.open('rb')
                content = produto.foto.read()
                produto.foto.close()
            except FileNotFoundError:
                # Se o arquivo antigo não puder ser aberto (ex.: caracteres não ASCII no caminho),
                # geramos uma imagem simples de placeholder para assegurar um arquivo válido.
                img = Image.new('RGB', (600, 400), '#cccccc')
                bio = BytesIO()
                img.save(bio, format='PNG')
                content = bio.getvalue()
            old_name = current_name
            produto.foto.save(target_basename, ContentFile(content), save=True)
            # Remove o arquivo antigo para evitar lixo em disco.
            try:
                produto.foto.storage.delete(old_name)
            except Exception:
                pass
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Arquivos normalizados: {count}'))