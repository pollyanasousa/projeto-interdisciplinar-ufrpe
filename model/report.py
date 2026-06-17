import os
import re
import webbrowser
from datetime import datetime


def _fmt_name(name: str) -> str:
    """Iniciais maiúsculas, ignora preposições."""
    preps = {"de", "da", "do", "das", "dos", "e"}
    return " ".join(
        w.capitalize() if w.lower() not in preps else w.lower()
        for w in name.strip().split()
    )

def _fmt_cpf(cpf: str) -> str:
    """Formata CPF: 05072207498 → 050.722.074-98"""
    digits = re.sub(r"\D", "", str(cpf))
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return cpf  # devolve original se não tiver 11 dígitos


class Report:
    def __init__(self, farmer, area, planting, harvest, expense):
        self.farmer = farmer
        self.area = area
        self.planting = planting
        self.harvest = harvest
        self.expense = expense
        self.REPORT_NAME = "RelatorioDeSafra.html"

    def gen_report(self):
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        # ── Áreas ─────────────────────────────────────────────────────────────
        area_html = ""
        for area in self.area.list_of_area:
            area_html += f"<tr><td>{area['name']}</td></tr>\n"

        # ── Multiproprietários (RF009) ─────────────────────────────────────────
        coowners_section = ""
        try:
            coowners = self.farmer.coowners.list_of_coowners
        except AttributeError:
            coowners = []

        if coowners:
            rows = ""
            for c in coowners:
                share = c.get("share_pct", "")
                share_display = f"{share}%" if share else "—"
                rows += f"""<tr>
                    <td>{_fmt_name(c['name'])}</td>
                    <td>{_fmt_cpf(c['cpf'])}</td>
                    <td>{c['role']}</td>
                    <td>{share_display}</td>
                </tr>\n"""
            coowners_section = f"""
            <hr />
            <h2>Multiproprietários e Herdeiros:</h2>
            <table border="1">
                <tr>
                    <th>Nome</th><th>CPF</th><th>Vínculo</th><th>% Participação</th>
                </tr>
                {rows}
            </table>"""
        else:
            coowners_section = """
            <hr />
            <h2>Multiproprietários e Herdeiros:</h2>
            <p><i>Nenhum coproprietário ou herdeiro cadastrado.</i></p>"""

        # ── Plantios (com valor canônico para banco) ───────────────────────────
        planting_html = ""
        for p in self.planting.list_of_planting:
            canonical = p.get("amount_canonical", p["amount"])
            display = p["amount"] if p["amount"] == canonical else f"{p['amount']} <small>({canonical})</small>"
            planting_html += f"""<tr>
                <td>{_fmt_name(p['culture'])}</td>
                <td>{_fmt_name(p['area'])}</td>
                <td>{display}</td>
                <td>{p['date']}</td>
            </tr>\n"""

        # ── Colheita (com valor canônico para banco) ───────────────────────────
        harvest_html = ""
        for h in self.harvest.list_of_harvest:
            canonical = h.get("amount_canonical", h["amount"])
            display = h["amount"] if h["amount"] == canonical else f"{h['amount']} <small>({canonical})</small>"
            harvest_html += f"""<tr>
                <td>{_fmt_name(h['culture'])}</td>
                <td>{display}</td>
                <td>{h['date']}</td>
            </tr>\n"""

        # ── Gastos ────────────────────────────────────────────────────────────
        expense_html = ""
        for e in self.expense.list_of_expenses:
            expense_html += f"""<tr>
                <td>{e['type']}</td>
                <td>{e.get('culture', 'Geral')}</td>
                <td>{e['value']}</td>
                <td>{e['date']}</td>
            </tr>\n"""

        report_html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Relatório de Safra — AgroBook</title>
    <style>
        * {{ font-family: Arial, sans-serif; }}
        body {{ background: #f4f8f4; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #fff; border-radius: 10px;
                      padding: 30px; box-shadow: 0 2px 12px #0002; }}
        .header {{ background: #124831; color: #fff; border-radius: 8px; padding: 18px 24px;
                   margin-bottom: 24px; }}
        .header h1 {{ margin: 0 0 4px 0; font-size: 28px; }}
        .header p {{ margin: 0; font-size: 13px; opacity: .8; }}
        h2 {{ color: #124831; border-left: 5px solid #6DAD65; padding-left: 10px; margin-top: 28px; }}
        h3 {{ color: #3a6e3a; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
        th {{ background: #124831; color: #fff; padding: 8px 12px; text-align: left; }}
        td {{ padding: 7px 12px; border-bottom: 1px solid #ddd; }}
        tr:nth-child(even) td {{ background: #f0f7f0; }}
        .farmer-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px 24px; }}
        .farmer-grid p {{ margin: 4px 0; }}
        .label {{ font-weight: bold; color: #124831; }}
        .badge {{ background: #6DAD65; color: #fff; border-radius: 12px; padding: 2px 10px;
                  font-size: 12px; font-weight: bold; }}
        .note {{ font-size: 11px; color: #888; font-style: italic; }}
        hr {{ border: none; border-top: 1px solid #ccc; margin: 20px 0; }}
        small {{ color: #7C5A3C; font-size: 11px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📋 Relatório de Safra — AgroBook</h1>
        <p>Gerado em: {now}</p>
    </div>

    <h2>Dados do Agricultor</h2>
    <div class="farmer-grid">
        <p><span class="label">Nome:</span> {_fmt_name(self.farmer.name)}</p>
        <p><span class="label">CPF:</span> {_fmt_cpf(self.farmer.cpf)}</p>
        <p><span class="label">Telefone:</span> {self.farmer.phone_number}</p>
        <p><span class="label">Cidade:</span> {self.farmer.town}</p>
        <p><span class="label">Estado:</span> {self.farmer.state}</p>
    </div>

    {coowners_section}

    <hr />
    <h2>Áreas de Plantio</h2>
    <table>
        <tr><th>Nome da Área</th></tr>
        {area_html if area_html else '<tr><td><i>Nenhuma área cadastrada.</i></td></tr>'}
    </table>

    <hr />
    <h2>Plantios</h2>
    <p class="note">Quantidades entre parênteses estão em unidade padrão para uso bancário.</p>
    <table>
        <tr><th>Cultura</th><th>Área</th><th>Quantidade</th><th>Data do Plantio</th></tr>
        {planting_html if planting_html else '<tr><td colspan="4"><i>Nenhum plantio registrado.</i></td></tr>'}
    </table>

    <hr />
    <h2>Colheita</h2>
    <p class="note">Quantidades entre parênteses estão em unidade padrão para uso bancário.</p>
    <table>
        <tr><th>Cultura</th><th>Quantidade</th><th>Data da Colheita</th></tr>
        {harvest_html if harvest_html else '<tr><td colspan="3"><i>Nenhuma colheita registrada.</i></td></tr>'}
    </table>

    <hr />
    <h2>Gastos</h2>
    <table>
        <tr><th>Tipo de Gasto</th><th>Cultura</th><th>Valor</th><th>Data</th></tr>
        {expense_html if expense_html else '<tr><td colspan="4"><i>Nenhum gasto registrado.</i></td></tr>'}
    </table>

    <hr />
    <p class="note" style="text-align:center">
        Relatório gerado pelo AgroBook — Sistema de Gestão para Agricultores (UFRPE)<br>
        Dados de quantidade convertidos automaticamente para padrão bancário.
    </p>
</div>
</body>
</html>"""

        try:
            with open(self.REPORT_NAME, "w", encoding="utf-8") as f:
                f.write(report_html)
            return 0
        except Exception as e:
            print("Falha ao gerar o relatório:", e)
            return 1

    def open_report(self):
        report_path = os.path.realpath(self.REPORT_NAME)
        webbrowser.open('file://' + report_path)
