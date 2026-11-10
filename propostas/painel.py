#!/usr/bin/env python3
"""Gera o PDF "Recursos do painel" de um prestador, com a mesma identidade da proposta.
Uso: python3 propostas/painel.py propostas/exemplos/atelie-do-automovel.json"""
import json, os, re, subprocess, sys, unicodedata
from gerar import AQUI, I, esc, data_uri, erro, TPL_VARS

arq = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else erro('informe o arquivo de valores')
v = json.load(open(arq, encoding='utf-8'))
nome, art = v['nome'].strip(), v['artigo'].lower()
de = 'd' + art
ape = (v.get('apelido') or nome).strip()
plus = v.get('modulo_plus', 'incluso_ate_validade') != 'nao'
PB = f' <span class="plusb" style="font-size:19px;padding:6px 14px;vertical-align:middle;margin-left:6px">{I("star-four-points")} PLUS</span>'

CSS_PN = '''.pn .fts{gap:26px}.pn .ft.lg{min-height:400px;padding:46px 46px;border-radius:44px}
.pn .ft.lg .pi{width:112px;height:112px;font-size:60px;border-radius:32px;margin-bottom:32px}
.pn .ft.lg b{font-size:44px;line-height:1.12}.pn .ft.lg p{font-size:30px;line-height:1.42;margin-top:16px}
.pn h2.m2{font-size:104px;margin-bottom:28px}.pn .lede.m2{font-size:32px;margin-bottom:40px}'''

def pagina(olho, titulo, lede, itens, gray=False):
    itens = [x for x in itens if plus or not x[3]]
    t = ''.join(f'<div class="ft lg"><span class="pi">{I(a)}</span><b>{b}{PB if p else ""}</b><p>{c}</p></div>' for a, b, c, p in itens)
    return f'''<section class="pg pn{" gray" if gray else ""}"><div class="eyebrow c-p">{olho}</div><h2 class="m2">{titulo}</h2>
<p class="lede m2">{lede}</p><div class="fts">{t}</div><div class="foot"><span>x</span><span>0</span></div></section>'''

P = [pagina('Atendimento', 'Do pedido<br>à entrega.', 'Tudo o que chega pelo app e o que está acontecendo agora, numa tela só.', [
        ('clipboard-text-outline', 'Pedidos', 'Orçamentos e agendamentos que chegam pelo app: você responde com preço e data, e o cliente confirma.', 0),
        ('car-wrench', 'Na oficina hoje', 'Os carros do dia, etapa por etapa. Você marca o andamento, manda fotos e pede aprovação de serviço extra.', 0),
        ('calendar-month-outline', 'Agenda', 'Os horários marcados no calendário, com o que está esperando a sua resposta.', 0),
        ('file-document-edit-outline', 'Ordens de serviço', 'OS de balcão com itens, termo de entrada, assinatura do cliente na tela e impressão em PDF.', 1)]),
     pagina('Clientes', 'Quem é cliente,<br>sempre por perto.', 'Do cadastro ao retorno: o painel ajuda a trazer o cliente de volta.', [
        ('account-group-outline', 'Clientes', 'Quem já foi atendido, com os carros e o histórico de serviços.', 0),
        ('account-multiple-outline', 'Clientes de balcão', 'Cadastro de quem chega direto, com os carros, busca por nome ou placa e botão de WhatsApp.', 1),
        ('qrcode', 'Clientes no app', 'QR Code para o balcão e mensagem pronta para convidar os seus clientes a usar o app.', 0),
        ('bell-ring-outline', 'Alertas dos clientes', 'Avisos dos carros que você já atendeu, como manutenção vencida e o diagnóstico do app.', 0)], True),
     pagina('Financeiro', 'O dinheiro<br>sob controle.', 'O que entrou, o que falta receber e como o mês está indo.', [
        ('cash-check', 'Recebimentos', 'Pagamentos por Pix e cartão feitos pelo app, com o valor líquido de cada um e o estorno quando precisar.', 0),
        ('cash-register', 'Caixa', 'Entradas e saídas do dia, dinheiro na gaveta, fechamento, contas a receber e o resultado do mês.', 1),
        ('file-chart-outline', 'Relatório de atendimentos', 'Tudo o que foi entregue, com valores, garantia e anexos, para consultar e exportar em planilha.', 0),
        ('chart-line', 'Desempenho', 'Os números do mês: velocidade de resposta, conversão dos pedidos e faturamento.', 0)]),
     pagina(f'A sua vitrine', 'Do seu jeito,<br>com o seu time.', 'Você define o que o cliente vê e quem da equipe acessa o quê.', [
        ('tag-multiple-outline', 'Serviços e preços', 'Seu cardápio com fotos, o que cada serviço inclui e o preço por porte do carro. Mudou aqui, mudou no app.', 0),
        ('star-outline', 'Perfil e avaliações', 'A vitrine no app e as avaliações dos clientes, com a sua resposta pública.', 0),
        ('account-key-outline', 'Equipe', 'Um login para cada pessoa. Quem é da equipe atualiza os carros do dia e não vê o financeiro.', 0),
        ('handshake-outline', 'Parcerias com lojas', 'Revendas de veículos que indicam você para quem comprou carro com elas.', 0)], True),
     pagina('Acesso e segurança', 'No computador<br>e no celular.', 'O painel abre no navegador, sem instalar nada.', [
        ('monitor-cellphone', 'Em qualquer tela', 'No computador, os menus ficam em grupos. No celular, os atalhos principais ficam na barra de baixo.', 0),
        ('history', 'Histórico que ninguém apaga', 'As ações importantes ficam registradas, com data e hora.', 0),
        ('shield-lock-outline', 'Proteção contra senha errada', 'Tentativas seguidas travam a entrada por alguns minutos.', 0),
        ('account-cancel-outline', 'Saiu da equipe, saiu na hora', 'Desativou o acesso, a entrada para no mesmo instante.', 0)])]

s = open(f'{AQUI}/templates/template-{v["categoria"]}.html', encoding='utf-8').read()
vals = {k: str(v[k]) for k in TPL_VARS if k in v}
vals.setdefault('nome_completo', nome)
vals['logo'] = data_uri(v['logo'], os.path.dirname(arq)) if v.get('logo') else ''
s = re.sub(r'\{\{([a-z0-9_]+)\}\}', lambda m: esc(vals[m.group(1)]) if m.group(1) in vals else m.group(0), s)
secs = list(re.finditer(r'<section class="pg[^"]*">.*?</section>', s, flags=re.S))
capa = secs[0].group(0)
capa = capa.replace('Uma apresentação para', 'Recursos do painel para', 1)
capa = re.sub(r'<h1 class="xl">.*?</h1>', '<h1 class="xl">O seu painel.</h1>', capa, count=1, flags=re.S)
capa = capa.replace('No bolso de cada', 'Tudo num lugar', 1).replace('>cliente.<', '>só.<', 1)
capa = re.sub(r'<div class="coverphone">.*</div></section>$', '</section>', capa, flags=re.S)
capa = capa.replace('<div class="glowp">', f'''<p style="font-size:34px;line-height:1.4;color:#a1a1a6;max-width:820px;margin:60px auto 0;font-weight:500">Pedidos, agenda, clientes e financeiro {de} {esc(ape)}, no computador ou no celular.</p>
<div style="display:flex;justify-content:center;gap:18px;margin-top:70px;flex-wrap:wrap">{"".join(f'<span class="vpill" style="margin:0">{I(a)} {b}</span>' for a,b in [("clipboard-text-outline","Atendimento"),("account-group-outline","Clientes"),("cash-check","Financeiro"),("storefront-outline","Vitrine e equipe")])}</div><div class="glowp">''', 1)
nova = [capa] + P + [secs[-1].group(0)]
rod = f'Painel ClipCar para {art} {esc(nome)}'
out = [re.sub(r'(<div class="foot[^"]*"><span>).*?</span><span>\d+</span></div>', lambda m, n=n: f'{m.group(1)}{rod}</span><span>{n}</span></div>', x, count=1, flags=re.S) for n, x in enumerate(nova, 1)]
doc = s[:secs[0].start()] + ''.join(out) + s[secs[-1].end():]
doc = doc.replace('</style>', open(f'{AQUI}/proposta.css').read().replace('__FONTE__', f'{AQUI}/fontes/MaterialCommunityIcons.ttf') + CSS_PN + '</style>', 1)
slug = re.sub(r'[^A-Za-z0-9]+', '-', unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode()).strip('-')
pasta = f'{AQUI}/saida/{slug}/painel'; os.makedirs(pasta, exist_ok=True)
open(f'{pasta}/painel.html', 'w', encoding='utf-8').write(doc)
pdf = f'{pasta}/Painel-ClipCar-{slug}.pdf'
r = subprocess.run(['node', f'{AQUI}/render.cjs', f'{pasta}/painel.html', pasta, pdf], capture_output=True, text=True)
if r.returncode: erro(r.stderr[-600:])
print(len(out), 'páginas ·', pdf)
