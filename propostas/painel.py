#!/usr/bin/env python3
"""Gera o PDF "Recursos do painel" de um prestador, com a mesma identidade da proposta.
Telas ilustrativas (dados de teste) em propostas/telas/.
Uso: python3 propostas/painel.py propostas/exemplos/atelie-do-automovel.json"""
import json, os, re, subprocess, sys, unicodedata
from gerar import AQUI, I, esc, data_uri, erro, TPL_VARS

arq = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else erro('informe o arquivo de valores')
v = json.load(open(arq, encoding='utf-8'))
nome, art = v['nome'].strip(), v['artigo'].lower()
ape = (v.get('apelido') or nome).strip()
plus = v.get('modulo_plus', 'incluso_ate_validade') != 'nao'
PB = f'<span class="plusb pbs">{I("star-four-points")} PLUS</span>'
T = lambda f: data_uri(f'telas/{f}', AQUI)

CSS_PN = '''
.pn h2.m2{font-size:100px;margin-bottom:22px}.pn .lede.m2{font-size:32px;margin-bottom:46px}
.fig{position:relative;margin:0 0 54px}
.shot{border-radius:24px;overflow:hidden;background:#fff;border:1px solid #dcdce1;box-shadow:0 30px 70px rgba(0,0,0,.14)}
.shot .bar{height:40px;background:#ececf0;display:flex;align-items:center;gap:9px;padding:0 18px}
.shot .bar em{width:13px;height:13px;border-radius:50%;background:#c7c7cc}
.shot img{display:block;width:100%;aspect-ratio:1366/760;object-fit:cover;object-position:top left}
.duo{padding-bottom:120px}.duo .shot{width:880px}
.cel{width:290px;border-radius:46px;border:11px solid #1d1d1f;overflow:hidden;background:#1d1d1f;box-shadow:0 30px 70px rgba(0,0,0,.28)}
.cel img{display:block;width:100%;aspect-ratio:390/790;object-fit:cover;object-position:top;border-radius:34px}
.duo .cel{position:absolute;right:0;top:70px}
.cels{display:flex;justify-content:center;gap:60px}.cels .cel{width:330px}
.lis{display:grid;grid-template-columns:1fr 1fr;gap:30px 40px}
.li{display:flex;gap:20px;align-items:center}
.li .pi{margin:0;width:70px;height:70px;font-size:36px;border-radius:21px;flex-shrink:0}
.li b{display:flex;align-items:center;gap:10px;font-family:IT;font-weight:700;font-size:31px;letter-spacing:-.02em;line-height:1.1}
.li p{margin:5px 0 0;font-size:23px;line-height:1.3;color:#6e6e73}
.pbs{font-size:15px;padding:5px 11px;letter-spacing:.08em}
.capfig{position:relative;margin:80px auto 0;width:1000px}
.capfig .shot{width:860px;border-color:#2c2c2e}
.capfig .cel{position:absolute;right:0;top:60px;width:270px;border-color:#2c2c2e}
'''

def shot(f):
    return f'<div class="shot"><div class="bar"><em></em><em></em><em></em></div><img src="{T(f)}"></div>'

def cel(f):
    return f'<div class="cel"><img src="{T(f)}"></div>'

def pagina(olho, titulo, lede, fig, itens, gray=False):
    itens = [x for x in itens if plus or not x[3]]
    t = ''.join(f'<div class="li"><span class="pi">{I(a)}</span><div><b>{b}{PB if p else ""}</b><p>{c}</p></div></div>' for a, b, c, p in itens)
    return f'''<section class="pg pn{" gray" if gray else ""}"><div class="eyebrow c-p">{olho}</div><h2 class="m2">{titulo}</h2>
<p class="lede m2">{lede}</p>{fig}<div class="lis">{t}</div><div class="foot"><span>x</span><span>0</span></div></section>'''

P = [pagina('Atendimento', 'Do pedido<br>à entrega.', 'O cliente acompanha cada etapa pelo celular.',
        f'<div class="fig">{shot("na-oficina-hoje.png")}</div>', [
        ('clipboard-text-outline', 'Pedidos', 'Responda com preço e data.', 0),
        ('car-wrench', 'Na oficina hoje', 'Cada carro, etapa por etapa.', 0),
        ('calendar-month-outline', 'Agenda', 'Seus horários num calendário.', 0),
        ('file-document-edit-outline', 'Ordens de serviço', 'Com assinatura na tela.', 1)]),
     pagina('Clientes', 'Quem é cliente,<br>sempre por perto.', 'Do cadastro ao retorno.',
        f'<div class="fig">{shot("clientes-balcao.png")}</div>', [
        ('account-group-outline', 'Clientes', 'Histórico de cada carro.', 0),
        ('account-multiple-outline', 'Clientes de balcão', 'Busca por nome ou placa.', 1),
        ('qrcode', 'Clientes no app', 'QR Code e convite pronto.', 0),
        ('bell-ring-outline', 'Alertas', 'Manutenção vencida dos seus clientes.', 0)], True),
     pagina('Financeiro', 'O dinheiro<br>sob controle.', 'O que entrou, o que falta e o resultado do mês.',
        f'<div class="fig duo">{shot("caixa.png")}{cel("celular-caixa.png")}</div>', [
        ('cash-check', 'Recebimentos', 'Pix e cartão, já com o líquido.', 0),
        ('cash-register', 'Caixa', 'Entradas, saídas e fechamento.', 1),
        ('file-chart-outline', 'Relatório', 'Exporta em planilha.', 0),
        ('chart-line', 'Desempenho', 'Os números do mês.', 0)]),
     pagina('A sua vitrine', 'Do seu jeito,<br>com o seu time.', 'Mudou no painel, mudou no app.',
        f'<div class="fig">{shot("servicos.png")}</div>', [
        ('tag-multiple-outline', 'Serviços e preços', 'Com fotos e preço por porte.', 0),
        ('star-outline', 'Perfil e avaliações', 'Sua vitrine no app.', 0),
        ('account-key-outline', 'Equipe', 'Um login por pessoa.', 0),
        ('handshake-outline', 'Parcerias', 'Lojas que indicam você.', 0)], True),
     pagina('Acesso e segurança', 'No computador<br>e no celular.', 'Abre no navegador, sem instalar nada.',
        f'<div class="fig cels">{cel("celular-menu.png")}{cel("celular-os.png")}</div>', [
        ('monitor-cellphone', 'Qualquer tela', 'Computador ou celular.', 0),
        ('history', 'Histórico', 'Tudo registrado, com data e hora.', 0),
        ('shield-lock-outline', 'Senha errada', 'Trava após várias tentativas.', 0),
        ('account-cancel-outline', 'Saiu da equipe', 'Acesso cortado na hora.', 0)])]

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
capa = capa.replace('<div class="glowp">', f'<div class="capfig">{shot("inicio.png")}{cel("celular-menu.png")}</div><div class="glowp">', 1)
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
