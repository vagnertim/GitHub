#!/usr/bin/env python3
"""Gera a proposta comercial ClipCar (PDF) de um prestador a partir de um arquivo de valores.

Uso:  python3 propostas/gerar.py propostas/exemplos/atelie-do-automovel.json
Sai:  propostas/saida/Proposta-ClipCar-<nome>.pdf  (+ páginas em PNG para conferir)

A apresentação (capa, identidade, cardápio, agenda...) vem do template da categoria
(templates/template-<categoria>.html, o mesmo modelo da cartilha da Lava Lento). As páginas
comerciais (resumo, Módulo Plus, preço, taxas da Asaas, exemplos, próximos passos) são montadas aqui.
As taxas da Asaas ficam em asaas.json (um lugar só para atualizar).
"""
import base64, html, json, os, re, subprocess, sys, unicodedata
from datetime import date
from decimal import Decimal as Dc, ROUND_HALF_UP

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(f'{AQUI}/fontes/icones.json'))
CATEGORIAS = ('estetica', 'mecanica', 'funilaria')
MESES = 'janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro'.split()
# variáveis que vão direto para o template da apresentação
TPL_VARS = ('nome nome_completo artigo logo_fundo cor_principal cor_escura cor_frase frase titulo_capa codigo_qr nota_servicos '
            'servico_1 servico_2 servico_3 servico_4 servico_5 servico_destaque inclui_1 inclui_2 inclui_3 inclui_4 inclui_5 inclui_6 '
            'inclui_7 inclui_mais preco_pequeno preco_medio preco_grande foto_1 foto_2 foto_3').split()


def erro(m):
    sys.exit(f'ERRO: {m}')


def I(n, c=''):
    if n not in G:
        erro(f'ícone inexistente: {n}')
    return f'<i class="{c}">&#{G[n]};</i>'


def dec(v, campo):
    try:
        return Dc(str(v).replace('%', '').replace('R$', '').strip().replace('.', '').replace(',', '.') if isinstance(v, str) and ',' in v else str(v))
    except Exception:
        erro(f'"{campo}" precisa ser um número (veio: {v!r})')


q = lambda v: v.quantize(Dc('0.01'), rounding=ROUND_HALF_UP)
brl = lambda v: 'R$ ' + f'{q(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
pct = lambda v: (f'{int(v)}' if v == v.to_integral_value() else f'{v:.2f}'.replace('.', ',')) + '%'
esc = lambda t: html.escape(str(t), quote=True)


def data_uri(caminho, base):
    p = caminho if os.path.isabs(caminho) else os.path.join(base, caminho)
    if not os.path.isfile(p):
        erro(f'arquivo não encontrado: {caminho}')
    ext = p.rsplit('.', 1)[-1].lower()
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'svg': 'image/svg+xml', 'webp': 'image/webp'}.get(ext)
    if not mime:
        erro(f'imagem precisa ser PNG, JPG, SVG ou WEBP: {caminho}')
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def main():
    if len(sys.argv) < 2:
        erro('informe o arquivo de valores. Ex.: python3 propostas/gerar.py propostas/exemplos/atelie-do-automovel.json')
    arq = os.path.abspath(sys.argv[1])
    v = json.load(open(arq, encoding='utf-8'))
    base = os.path.dirname(arq)
    A = json.load(open(f'{AQUI}/asaas.json', encoding='utf-8'))
    A.update(v.get('asaas') or {})

    # ---------------- valores obrigatórios e padrões
    for k in ('nome', 'artigo', 'categoria', 'validade'):
        if not str(v.get(k, '')).strip():
            erro(f'falta o valor obrigatório "{k}"')
    cat = v['categoria']
    if cat not in CATEGORIAS:
        erro(f'"categoria" precisa ser uma destas: {", ".join(CATEGORIAS)}')
    art = v['artigo'].lower()
    if art not in ('o', 'a'):
        erro('"artigo" precisa ser "o" ou "a"')
    nome = v['nome'].strip()
    v.setdefault('nome_completo', nome)
    ape = (v.get('apelido') or nome).strip()            # como chamar no meio do texto ("o Ateliê")
    Art, de = art.upper(), 'd' + art
    valid = v['validade'].strip()
    if not re.fullmatch(r'\d{2}/\d{2}/\d{4}', valid):
        erro('"validade" no formato DD/MM/AAAA')
    hoje = v.get('data') or (lambda d: f'{d.day} de {MESES[d.month - 1]} de {d.year}')(date.today())
    cidade = v.get('cidade', 'Ubatuba')
    taxa = dec(v.get('taxa_clipcar_pct', 2), 'taxa_clipcar_pct')
    mens = v.get('mensalidade', 'a combinar')
    mens_num = None if str(mens).strip().lower() in ('', 'a combinar', 'a negociar') else dec(mens, 'mensalidade')
    plus = v.get('modulo_plus', 'incluso_ate_validade')
    if plus not in ('incluso_ate_validade', 'incluso', 'nao'):
        erro('"modulo_plus": incluso_ate_validade, incluso ou nao')
    V = dec(v.get('exemplo_valor', 200), 'exemplo_valor')
    PIX, FIX = dec(A['pix'], 'asaas.pix'), dec(A['cartao_fixo'], 'asaas.cartao_fixo')
    C = {k: dec(A[k], f'asaas.{k}') for k in ('credito_avista_pct', 'credito_2a6_pct', 'credito_7a12_pct')}
    foot = lambda dk=False: f'<div class="foot{" fd" if dk else ""}"><span>x</span><span>0</span></div>'

    # ---------------- páginas comerciais
    P = []
    mens_res = f'a mensalidade fixa de {brl(mens_num)}' if mens_num else 'a opção de mensalidade fixa, com valor a combinar'
    rs = [(f'<span class="pi">{I("cellphone-check")}</span>', 'nt', 'O que entra',
           'App, painel e Módulo Plus' if plus != 'nao' else 'App e painel',
           f'O app para os seus clientes agendarem e pagarem e o painel {de} {esc(ape)}'
           + (', com o Módulo Plus (clientes de balcão, ordem de serviço e caixa).' if plus != 'nao' else '.')),
          (f'<span class="big">{pct(taxa)}</span>', 'cc', 'Taxa do ClipCar', 'Sobre o serviço pago pelo app',
           f'Sem taxa de adesão e sem mensalidade. Se preferir, há {mens_res}.'),
          (f'<span class="pi as">{I("bank-outline")}</span>', 'as', 'Taxas da Asaas · à parte', 'Quem processa o Pix e o cartão',
           f'Cobradas pela Asaas em cada pagamento: Pix {brl(PIX)}; cartão de crédito à vista {pct(C["credito_avista_pct"])} + {brl(FIX)}. Não são taxas do ClipCar.')]
    cond = v.get('condicao_especial')
    if cond or plus == 'incluso_ate_validade':
        rs.append((f'<span class="pi">{I("calendar-star")}</span>', 'go', f'Condição especial · até {valid}',
                   esc(v.get('condicao_titulo') or ('Módulo Plus incluso' if not cond else 'Para quem fechar agora')),
                   esc(cond) if cond else 'Aderindo até essa data, o Módulo Plus entra sem custo adicional. Depois dela, o Módulo Plus é cobrado à parte.'))
    P.append(f'''<section class="pg"><div class="eyebrow c-p">Proposta</div><h2 class="m2">A proposta,<br>em uma página.</h2>
<div class="rs">{"".join(f'<div class="r"><div class="rb">{a}</div><div><span class="tg {b}">{c}</span><b>{d}</b><p>{e}</p></div></div>' for a, b, c, d, e in rs)}</div>{foot()}</section>''')

    if plus != 'nao':
        itens = [('account-multiple-outline', 'Clientes de balcão', 'Cadastro do cliente e dos carros (marca, modelo, placa e km), com busca e botão de WhatsApp.'),
                 ('clipboard-text-outline', 'Ordem de serviço', 'Itens do seu cardápio, peças e mão de obra, termo de entrada com as avarias, assinatura do cliente na tela e impressão em PDF.'),
                 ('cash-register', 'Caixa', 'Recebimentos em dinheiro, Pix, débito e crédito. Caixa do dia, fechamento, contas a receber e o resultado do mês.'),
                 ('qrcode-scan', 'Pix e link de pagamento', 'QR Code no balcão ou link de cartão pelo WhatsApp. Pagou, a ordem de serviço fica quitada sozinha.*')]
        ban = (f'<b>Incluso para adesão até {valid}.</b><p>Sem custo adicional. Depois dessa data, o Módulo Plus é cobrado à parte.</p>' if plus == 'incluso_ate_validade'
               else '<b>Incluso nesta proposta.</b><p>Sem custo adicional.</p>')
        P.append(f'''<section class="pg gray"><div class="eyebrow c-p" style="display:flex;align-items:center;gap:14px">Módulo Plus <span class="plusb">{I("star-four-points")} PLUS</span></div>
<h2 class="m2">O balcão também<br>fica organizado.</h2><p class="lede m2">Para o cliente que chega direto, sem passar pelo app.</p>
<div class="fts">{"".join(f'<div class="ft lg"><span class="pi">{I(a)}</span><b>{b}</b><p>{c}</p></div>' for a, b, c in itens)}</div>
<div class="ban"><span class="bi">{I("calendar-star")}</span><div>{ban}</div></div>
<p class="fine l">* QR Code e link do ClipCar seguem as mesmas taxas do app (Asaas + ClipCar). O que você recebe direto, em dinheiro, Pix na sua conta ou maquininha, não paga taxa ao ClipCar.</p>{foot()}</section>''')

    li = lambda xs: ''.join(f'<li>{I("check-circle")}<span>{t}</span></li>' for t in xs)
    op2 = (f'<div class="on tx" style="font-size:92px;margin:34px 0 26px">{brl(mens_num)}</div><div class="os">por mês, valor fixo</div>' if mens_num
           else '<div class="on tx">Valor a<br>combinar</div><div class="os">um valor fixo por mês, definido com você</div>')
    P.append(f'''<section class="pg"><div class="eyebrow c-p">Quanto custa o ClipCar</div><h2 class="m2">Você só paga<br>quando recebe.</h2>
<p class="lede m2">Duas formas de pagar pelo ClipCar. Você escolhe a que combina com o seu movimento.</p>
<div class="opts"><div class="opt hi"><span class="ol">Opção 1 · por uso</span><div class="on">{pct(taxa)}</div><div class="os">sobre o valor de cada serviço pago pelo app</div>
<ul>{li(["Sem taxa de adesão", "Sem mensalidade", "Não recebeu pelo app, não paga nada"])}</ul></div>
<div class="opt"><span class="ol">Opção 2 · mensalidade fixa</span>{op2}
<ul>{li([f"Sem os {pct(taxa)} por serviço", "Receber pelo app passa a ser opcional", "Para quem recebe bastante pelo app"])}</ul></div></div>
<div class="know"><div class="kn">{I("cellphone-check")}<span><b>Na opção por uso</b>, o serviço agendado pelo app é pago pelo app, por Pix ou cartão. É sobre esse valor que os {pct(taxa)} são calculados.</span></div>
<div class="kn">{I("storefront-outline")}<span><b>O que você recebe direto</b> (dinheiro, Pix na sua conta, maquininha) não paga taxa ao ClipCar.</span></div>
<div class="kn">{I("swap-horizontal")}<span><b>Dá para mudar de opção depois</b>, uma vez a cada 30 dias.</span></div></div>
<div class="nextp">{I("bank-outline")}<span>As taxas da Asaas, que processa os pagamentos, são à parte: estão na próxima página.</span></div>{foot()}</section>''')

    rows = [('qrcode', 'Pix', brl(PIX), 'por pagamento recebido', 'Na hora, em poucos segundos'),
            ('credit-card-outline', 'Crédito à vista', f'{pct(C["credito_avista_pct"])} + {brl(FIX)}', 'por venda', f'Em {A["credito_dias"]} dias'),
            ('credit-card-multiple-outline', 'Crédito em 2 a 6 vezes', f'{pct(C["credito_2a6_pct"])} + {brl(FIX)}', 'sobre o valor total', f'Uma parcela a cada {A["credito_dias"]} dias'),
            ('credit-card-multiple-outline', 'Crédito em 7 a 12 vezes', f'{pct(C["credito_7a12_pct"])} + {brl(FIX)}', 'sobre o valor total', f'Uma parcela a cada {A["credito_dias"]} dias')]
    abertura = ('O ClipCar abre a sua conta na Asaas e paga a abertura. Sem mensalidade da Asaas.' if v.get('clipcar_paga_abertura', True)
                else f'A conta é aberta na Asaas em seu nome. Abertura: {brl(dec(A["abertura_subconta"], "asaas.abertura_subconta"))}. Sem mensalidade da Asaas.')
    notes = [('percent-outline', 'Parcelado sem juros para o cliente', f'O percentual é sobre o valor total e os {brl(FIX)} saem uma vez por venda. O máximo de parcelas é combinado com você.'),
             ('fast-forward-outline', 'Quer receber o cartão antes?', f'A Asaas antecipa em 2 dias úteis: {pct(dec(A["antecipacao_avista_pct"], "a"))} ao mês no à vista e {pct(dec(A["antecipacao_parcelado_pct"], "a"))} ao mês no parcelado.'),
             ('bank-transfer-out', 'Para levar o dinheiro ao seu banco', esc(A['transferencia_texto'])),
             ('account-check-outline', 'Conta de recebimento', abertura)]
    promo = f' {esc(A["promocao_texto"])}' if A.get('promocao_texto') else ''
    P.append(f'''<section class="pg gray"><div class="eyebrow c-a" style="display:flex;align-items:center;gap:16px">Meio de pagamento · Asaas <span class="notcc">{I("information-outline")} Estas taxas não são do ClipCar</span></div>
<h2 class="m2">As taxas da Asaas,<br>à parte.</h2>
<p class="lede m2" style="margin-bottom:30px">O Pix e o cartão são processados pela Asaas, instituição de pagamento autorizada pelo Banco Central. A taxa dela sai de cada pagamento recebido e fica com ela.</p>
<div class="atb"><div class="arow hd"><span>Forma de pagamento</span><span>Taxa da Asaas</span><span>Quando fica disponível</span></div>
{"".join(f'<div class="arow"><div class="fm">{I(a)}<span>{b}</span></div><div class="tx">{c}<small>{d}</small></div><div class="qd">{e}</div></div>' for a, b, c, d, e in rows)}</div>
<div class="anotes">{"".join(f'<div class="an">{I(a)}<div><b>{b}</b><p>{c}</p></div></div>' for a, b, c in notes)}</div>
<p class="src">Taxas padrão da Asaas conferidas em {esc(A["conferido_em"])}.{promo} Quem define e pode alterar essas taxas é a Asaas: valem as que aparecem no painel da sua conta.</p>{foot()}</section>''')

    def rc(ic, n, asaas, qd):
        c = q(V * taxa / 100)
        liq = V - asaas - c
        return f'''<div class="rc"><div class="rh">{I(ic)}<span>{n}</span></div><div class="rl"><span>Valor do serviço</span><b>{brl(V)}</b></div>
<div class="rl"><span><em style="background:#8e8e93"></em>Taxa da Asaas</span><b>− {brl(asaas)}</b></div>
<div class="rl"><span><em style="background:#1E88F5"></em>Taxa do ClipCar ({pct(taxa)})</span><b>− {brl(c)}</b></div>
<div class="rt"><span>Você recebe</span><b>{brl(liq)}</b><small>{f"{liq / V * 100:.1f}".replace(".", ",")}% do valor<br>{qd}</small></div></div>'''
    exs = [rc('qrcode', 'Pix', PIX, 'na hora'),
           rc('credit-card-outline', 'Cartão à vista', q(V * C['credito_avista_pct'] / 100) + FIX, f'em {A["credito_dias"]} dias'),
           rc('credit-card-multiple-outline', 'Cartão em 3 vezes', q(V * C['credito_2a6_pct'] / 100) + FIX, f'uma parcela a cada {A["credito_dias"]} dias')]
    P.append(f'''<section class="pg dark"><div class="eyebrow c-pl">Na prática</div><h2 class="m2">Quanto você<br>recebe.</h2>
<p class="lede m2" style="color:#a1a1a6;margin-bottom:30px">Exemplo com um serviço de {brl(V)} pago pelo app, na opção por uso ({pct(taxa)}), com as taxas padrão da Asaas.</p>
<div class="leg"><span><em style="background:#8e8e93"></em>Asaas: processa o pagamento</span><span><em style="background:#1E88F5"></em>ClipCar: app e painel</span></div>
<div class="rcs">{"".join(exs)}</div>
<div class="tips"><div class="tip"><b>No Pix, a taxa da Asaas é fixa</b><p>São {brl(PIX)} por pagamento, seja qual for o valor. Quanto maior o serviço, menor o peso dela.</p></div>
<div class="tip"><b>Cliente de balcão</b><p>Pagou direto, em dinheiro, Pix na sua conta ou maquininha? Não há taxa do ClipCar.</p></div></div>{foot(True)}</section>''')

    tl = [('Você dá o ok', f'Basta responder a esta proposta até {valid}.'),
          ('Abrimos a conta de recebimento', 'Na Asaas, em seu nome. É preciso CNPJ (MEI serve) e os documentos do responsável. Quem aprova a conta é a Asaas.'),
          ('Montamos o cardápio juntos', 'Seus serviços e preços. Modo exclusivo, com o seu logo e as suas cores.'),
          ('QR no balcão', 'E o convite pronto para os seus clientes no WhatsApp.')]
    conds = ['A taxa do ClipCar e as taxas da Asaas são cobranças separadas, de empresas diferentes.',
             'As taxas da Asaas são definidas por ela e podem mudar. Valem as que aparecem no painel da sua conta.']
    chips = [f'{pct(taxa)} por serviço pago pelo app', 'Sem adesão']
    if plus == 'incluso_ate_validade':
        conds.append(f'O Módulo Plus está incluso para adesão até {valid}. Depois dessa data, é cobrado à parte.')
    if plus != 'nao':
        chips.append('Módulo Plus incluso')
    NEXT = f'''<section class="pg"><div class="eyebrow c-p">Próximos passos</div><h2 class="m2">Começar<br>é simples.</h2>
<div class="tl sm">{"".join(f'<div class="t"><span class="td"></span><div><b>{a}</b><p>{b}</p></div></div>' for a, b in tl)}</div>
<div class="cond"><b>Condições desta proposta</b>{"".join(f"<p>{c}</p>" for c in conds)}<p>{esc(cidade)}, {esc(hoje)}.</p></div>
<div class="final pp"><div><b>Proposta válida até {valid}.</b><p>Respondam esta mensagem para combinarmos o início.</p></div>
<div class="chips">{"".join(f"<span>{c}</span>" for c in chips)}</div></div>{foot()}</section>'''

    # ---------------- template da apresentação, preenchido
    s = open(f'{AQUI}/templates/template-{cat}.html', encoding='utf-8').read()
    vals = {k: str(v[k]) for k in TPL_VARS if k in v}
    vals['logo'] = data_uri(v['logo'], base) if v.get('logo') else ''
    for k in ('foto_1', 'foto_2', 'foto_3'):
        if vals.get(k):
            vals[k] = data_uri(vals[k], base)
    s = re.sub(r'\{\{([a-z0-9_]+)\}\}', lambda m: esc(vals[m.group(1)]) if m.group(1) in vals else m.group(0), s)
    secs = list(re.finditer(r'<section class="pg[^"]*">.*?</section>', s, flags=re.S))
    txt = [m.group(0) for m in secs]
    olho = lambda x: re.sub(r'<[^>]+>', '', (re.search(r'<div class="eyebrow[^>]*>(.*?)</div>', x, flags=re.S) or [None, ''])[1]).strip()
    ip = next((i for i, x in enumerate(txt) if olho(x) == 'Pagamentos'), None)
    ix = next((i for i, x in enumerate(txt) if olho(x) == 'Próximos passos'), None)
    if ip is None or ix is None or ix < ip:
        erro(f'o template de {cat} mudou: não achei as páginas "Pagamentos" e "Próximos passos"')
    txt[0] = txt[0].replace('Uma apresentação para', 'Proposta comercial para', 1).replace(
        '<div class="glowp">', f'<div style="text-align:center"><div class="vpill">{I("calendar-star")} Proposta válida até {valid}</div></div><div class="glowp">', 1)
    nova = txt[:ip] + P + txt[ip + 1:ix] + [NEXT, txt[-1]]
    rod = f'Proposta ClipCar para {art} {esc(nome)} · válida até {valid}'
    out = [re.sub(r'(<div class="foot[^"]*"><span>).*?</span><span>\d+</span></div>',
                  lambda m, n=n: f'{m.group(1)}{rod}</span><span>{n}</span></div>', sec, count=1, flags=re.S) for n, sec in enumerate(nova, 1)]
    doc = s[:secs[0].start()] + ''.join(out) + s[secs[-1].end():]
    css = open(f'{AQUI}/proposta.css', encoding='utf-8').read().replace('__FONTE__', f'{AQUI}/fontes/MaterialCommunityIcons.ttf')
    doc = doc.replace('</style>', css + '</style>', 1)
    doc = re.sub(r'<title>.*?</title>', f'<title>Proposta ClipCar para {art} {esc(nome)}</title>', doc, count=1)

    slug = re.sub(r'[^A-Za-z0-9]+', '-', unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode()).strip('-')
    pasta = f'{AQUI}/saida/{slug}'
    os.makedirs(pasta, exist_ok=True)
    open(f'{pasta}/proposta.html', 'w', encoding='utf-8').write(doc)
    pdf = f'{pasta}/Proposta-ClipCar-{slug}.pdf'
    r = subprocess.run(['node', f'{AQUI}/render.cjs', f'{pasta}/proposta.html', pasta, pdf], capture_output=True, text=True)
    if r.returncode:
        erro('não consegui gerar o PDF:\n' + r.stderr[-800:])
    print(f'{len(out)} páginas · {pdf}')
    print(f'conferir as páginas: {pasta}/q-01.png ... q-{len(out):02d}.png')


if __name__ == '__main__':
    main()
