from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Banca, Produto, Pedido, ItensPedido
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Cast


def home(request):
    # Lista bancas e produtos disponíveis
    bancas = Banca.objects.all()
    produtos = Produto.objects.filter(disponibilidade=True)
    return render(request, 'home.html', {'bancas': bancas, 'produtos': produtos})


def banca_detalhe(request, id_banca):
    banca = get_object_or_404(Banca, id=id_banca)
    produtos = banca.produtos.filter(disponibilidade=True)
    return render(request, 'banca_detalhe.html', {'banca': banca, 'produtos': produtos})


def produto_detalhe(request, id_produto):
    produto = get_object_or_404(Produto, id=id_produto)
    return render(request, 'produto_detalhe.html', {'produto': produto})


def _get_carrinho(session):
    # Carrinho na sessão
    carrinho = session.get('carrinho')
    if carrinho is None:
        carrinho = {}
        session['carrinho'] = carrinho
    return carrinho


@require_POST
def carrinho_add(request, id_produto):
    produto = get_object_or_404(Produto, id=id_produto, disponibilidade=True)
    carrinho = _get_carrinho(request.session)
    item = carrinho.get(str(produto.id))
    if item:
        item['quantidade'] += 1  # incrementa quantidade
    else:
        carrinho[str(produto.id)] = {
            'nome': produto.nome,
            'preco': float(produto.preco),
            'quantidade': 1,
            'banca_id': produto.banca_id,
        }
    request.session.modified = True  # salva a sessão
    return redirect('carrinho')


def carrinho_view(request):
    carrinho = request.session.get('carrinho', {})
    # Calcula subtotais
    carrinho_list = []
    total_carrinho = 0.0
    for pid, item in carrinho.items():
        subtotal = item['preco'] * item['quantidade']
        total_carrinho += subtotal
        carrinho_list.append({
            'pid': pid,
            'nome': item['nome'],
            'preco': item['preco'],
            'quantidade': item['quantidade'],
            'subtotal': subtotal,
        })
    return render(request, 'carrinho.html', {'carrinho_list': carrinho_list, 'total_carrinho': total_carrinho})


@require_POST
def carrinho_update(request, id_produto):
    quantidade = int(request.POST.get('quantidade', 1))  # mínimo 1
    carrinho = _get_carrinho(request.session)
    item = carrinho.get(str(id_produto))
    if item:
        item['quantidade'] = max(1, quantidade)
        request.session.modified = True
    return redirect('carrinho')


@require_POST
def carrinho_remove(request, id_produto):
    carrinho = _get_carrinho(request.session)
    if str(id_produto) in carrinho:
        del carrinho[str(id_produto)]
        request.session.modified = True
    return redirect('carrinho')


@login_required
def checkout(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, 'Adicione pelo menos um item ao carrinho para prosseguir para o checkout.')
        return redirect('carrinho')
    total_carrinho = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    return render(request, 'checkout.html', {'carrinho': carrinho, 'total_carrinho': total_carrinho})


@login_required
@require_POST
def finalizar_pedido(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        return redirect('carrinho')

    # Cria o pedido com itens do carrinho
    pedido = Pedido.objects.create(cliente=request.user, status='novo')
    for pid, item in carrinho.items():
        produto = get_object_or_404(Produto, id=pid)
        ItensPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=item['quantidade'],
            preco_unitario=item['preco'],
        )

    # Limpa o carrinho
    request.session['carrinho'] = {}
    request.session.modified = True
    messages.success(request, 'Pedido criado com sucesso! Aqui está seu QR para retirada.')
    return redirect('pedido_detalhe_qr', pedido.qr_code_id)


@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-data_pedido')
    return render(request, 'meus_pedidos.html', {'pedidos': pedidos})


@login_required
@require_POST
def meus_pedidos_delete(request, id_pedido):
    pedido = get_object_or_404(Pedido, id=id_pedido, cliente=request.user)
    pedido.delete()
    messages.success(request, 'Pedido apagado com sucesso.')
    return redirect('meus_pedidos')


def pedido_detalhe_qr(request, qr_code_id):
    pedido = get_object_or_404(Pedido, qr_code_id=qr_code_id)
    qr_payload = request.build_absolute_uri(reverse('pedido_detalhe_qr', args=[pedido.qr_code_id]))
    return render(request, 'pedido_detalhe_qr.html', {'pedido': pedido, 'qr_payload': qr_payload})


@login_required
def dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    return render(request, 'dashboard.html')


@login_required
def dashboard_pedidos(request):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    # Pedidos com itens das bancas do feirante
    minhas_bancas = request.user.bancas.all()
    # Busca pedidos via itens ligados aos produtos
    pedidos_ids = ItensPedido.objects.filter(produto__banca__in=minhas_bancas).values_list('pedido_id', flat=True).distinct()
    pedidos = Pedido.objects.filter(id__in=pedidos_ids).order_by('-data_pedido')
    return render(request, 'dashboard_pedidos_list.html', {'pedidos': pedidos})


@login_required
@require_POST
def dashboard_pedidos_update_status(request, id_pedido):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    pedido = get_object_or_404(Pedido, id=id_pedido)
    novo_status = request.POST.get('status')
    if novo_status in dict((s, d) for s, d in (('novo','Novo'),('em_separacao','Em Separação'),('pronto','Pronto'),('entregue','Entregue'))):
        pedido.status = novo_status  # atualiza status
        pedido.save()
    return redirect('dashboard_pedidos')


@login_required
def dashboard_produtos_list(request):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    produtos = Produto.objects.filter(banca__dono=request.user)
    return render(request, 'dashboard_produtos_list.html', {'produtos': produtos})


@login_required
def dashboard_produtos_novo(request):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    if request.method == 'POST':
        nome = request.POST.get('nome')
        preco = request.POST.get('preco')
        banca_id = request.POST.get('banca_id')
        foto = request.FILES.get('foto')
        disponibilidade = request.POST.get('disponibilidade') == 'on'
        validade = request.POST.get('validade') or None
        banca = get_object_or_404(Banca, id=banca_id, dono=request.user)
        novo_produto = Produto.objects.create(
            banca=banca,
            nome=nome,
            preco=preco,
            foto=foto,
            validade=validade,
            disponibilidade=disponibilidade,
        )
        if novo_produto.disponibilidade:
            messages.success(request, 'Produto criado e já aparece na lista pública de Produtos.')
        else:
            messages.info(request, 'Produto criado. Marque como disponível para aparecer na lista pública.')
        return redirect('dashboard_produtos_list')
    bancas = Banca.objects.filter(dono=request.user)
    return render(request, 'dashboard_produtos_form.html', {'bancas': bancas})


@login_required
def dashboard_produtos_editar(request, id_produto):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    produto = get_object_or_404(Produto, id=id_produto, banca__dono=request.user)
    if request.method == 'POST':
        produto.nome = request.POST.get('nome')
        produto.preco = request.POST.get('preco')
        if request.FILES.get('foto'):
            produto.foto = request.FILES['foto']
        produto.validade = request.POST.get('validade') or None
        produto.disponibilidade = request.POST.get('disponibilidade') == 'on'
        produto.save()
        return redirect('dashboard_produtos_list')
    return render(request, 'dashboard_produtos_form.html', {'produto': produto})


@login_required
def dashboard_produtos_deletar(request, id_produto):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    produto = get_object_or_404(Produto, id=id_produto, banca__dono=request.user)
    if request.method == 'POST':
        produto.delete()
        return redirect('dashboard_produtos_list')
    return render(request, 'dashboard_produtos_deletar.html', {'produto': produto})


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo_usuario = request.POST.get('tipo_usuario')
        if username and password and tipo_usuario in ('feirante', 'cliente'):
            user = User.objects.create_user(username=username, email=email, password=password)
            from .models import Profile
            Profile.objects.create(user=user, tipo_usuario=tipo_usuario)
            login(request, user)
            return redirect('home')
    return render(request, 'registration/signup.html')


@login_required
def dashboard_resumo(request):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'feirante':
        messages.info(request, 'Acesso restrito ao perfil Feirante.')
        return redirect('home')
    # Resumo de vendas (total geral e por produto)

    # Minhas bancas
    minhas_bancas = request.user.bancas.all()

    # Itens vendidos das bancas do feirante
    itens_vendidos = ItensPedido.objects.filter(produto__banca__in=minhas_bancas)

    # Subtotal = quantidade * preço
    calculo_subtotal = F('quantidade') * Cast(
        F('preco_unitario'), output_field=DecimalField(max_digits=10, decimal_places=2)
    )

    # Total geral
    total_geral_feirante = itens_vendidos.aggregate(total=Sum(calculo_subtotal))['total'] or 0.00

    # Total por produto
    totais_por_produto = itens_vendidos.values('produto__nome').annotate(
        total_vendido=Sum(calculo_subtotal)
    ).order_by('-total_vendido')

    return render(
        request,
        'core/dashboard_resumo.html',
        {
            'total_geral_feirante': total_geral_feirante,
            'totais_por_produto': totais_por_produto,
        },
    )
