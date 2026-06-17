"""
events.py — VA3: Eventos que conectam a interface à lógica de voz.

═══════════════════════════════════════════════════════════════════════════════
VA3 — CAMADA DE CONEXÃO ENTRE INTERFACE E VOZ
═══════════════════════════════════════════════════════════════════════════════

FUNÇÃO:
  Esta classe conecta os cliques em botões e eventos da interface gráfica
  às funções de negócio. Na VA3, ela ganhou os eventos de navegação entre
  telas e a integração com os diálogos de voz (plantio, colheita, gasto).

FLUXO DE VOZ (como os eventos se encadeiam):
  Botão "Novo plantio" → events.new_planting()
    → dialog.planting_dialog() → PlantioDialog (voz)
    → LLM interpreta → resultado volta para events
    → model.planting.save() → salva no JSON

ARQUIVOS RELACIONADOS:
  - gui/dialog.py → diálogos com microfone (PlantioDialog, ColheitaDialog, etc.)
  - utils/voice_input.py → captura e transcrição de áudio
  - utils/llm_parser.py → interpretação semântica da fala
  - utils/llm_normalizer.py → normalização de datas/medidas
"""

from gui.dialog import Dialog, CANCELLED
from utils.validators import *
from model.coowners import CoOwners


class Events:
    def __init__(self, window):
        self.window = window
        self.dialog = Dialog(parent=window)

    # ── Cadastro — dados pessoais ──────────────────────────────────────────────

    def sign_up(self):
        self.window.stacked_widget.setCurrentIndex(1)

    def sign_up_receive_code(self):
        if is_valid_phone(self.window.phone_screen.phone_lineedit.text()):
            phone = self.window.phone_screen.phone_lineedit.text()
            self.window.sms.send(phone)
            self.window.farmer.phone_number = phone
            self.window.stacked_widget.setCurrentIndex(2)
        else:
            self.dialog.error_dialog("Telefone inválido!")

    def sign_up_code_next_lineedit(self, lineedit):
        lineedit.setFocus()

    def sign_up_check_code(self):
        user_entry = (
            self.window.sms_screen.code_lineedit1.text()
            + self.window.sms_screen.code_lineedit2.text()
            + self.window.sms_screen.code_lineedit3.text()
            + self.window.sms_screen.code_lineedit4.text()
        )
        if user_entry == self.window.sms.code:
            self.window.farmer.save(mute=True)  # salva phone_number imediatamente
            self.window.stacked_widget.setCurrentIndex(3)
        else:
            self.dialog.error_dialog("Código inválido!")

    def sign_up_get_name(self):
        if is_valid_name(self.window.farmer_name_screen.name_lineedit.text()):
            self.window.farmer.name = self.window.farmer_name_screen.name_lineedit.text()
            self.window.stacked_widget.setCurrentIndex(4)
        else:
            self.dialog.error_dialog("Nome inválido!")

    def sign_up_get_cpf(self):
        if is_valid_cpf(self.window.farmer_cpf_screen.cpf_lineedit.text()):
            self.window.farmer.cpf = self.window.farmer_cpf_screen.cpf_lineedit.text()
            self.window.stacked_widget.setCurrentIndex(5)
        else:
            self.dialog.error_dialog("CPF inválido!")

    def sign_up_get_location(self):
        if is_valid_town(self.window.farmer_location_screen.town_lineedit.text()):
            self.window.farmer.town = self.window.farmer_location_screen.town_lineedit.text()
            self.window.farmer.state = self.window.farmer_location_screen.state_combobox.currentText()
            self.window.farmer.save()
            self._signup_refresh_areas()
            self.window.stacked_widget.setCurrentIndex(13)
        else:
            self.dialog.error_dialog("Cidade inválida!")

    # ── Cadastro — Áreas obrigatórias (idx 14) ────────────────────────────────

    def _signup_refresh_areas(self):
        lw = self.window.signup_areas_screen.area_listwidget
        lw.clear()
        for area in self.window.farmer.area.list_of_area:
            lw.addItem(area["name"])

    def signup_new_area(self):
        areas_existentes = [a["name"] for a in self.window.farmer.area.list_of_area]
        nome = self.dialog.area_dialog(areas_existentes)
        if nome is CANCELLED:
            return
        if nome is None:
            self.dialog.error_dialog("Nome inválido! Use apenas letras e espaços.")
        else:
            self.window.farmer.area.new_area(nome)
            self.window.farmer.save()
            self._signup_refresh_areas()

    def signup_update_area(self):
        line = self.window.signup_areas_screen.area_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione uma área para editar.")
            return
        areas_existentes = [a["name"] for a in self.window.farmer.area.list_of_area]
        nome = self.dialog.area_dialog(areas_existentes)
        if nome is CANCELLED:
            return
        if nome is None:
            self.dialog.error_dialog("Nome inválido! Use apenas letras e espaços.")
        else:
            self.window.farmer.area.update_area(line, nome)
            self.window.farmer.save()
            self._signup_refresh_areas()

    def signup_delete_area(self):
        line = self.window.signup_areas_screen.area_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione uma área para remover.")
            return
        if self.dialog.yes_or_no_dialog("Deseja remover a área selecionada?"):
            error = self.window.farmer.area.delete_area(line)
            if error:
                self.dialog.error_dialog(error)
            else:
                self.window.farmer.save()
                self._signup_refresh_areas()

    def signup_areas_done(self):
        if len(self.window.farmer.area.list_of_area) == 0:
            self.dialog.error_dialog("Cadastre pelo menos uma área para continuar!")
            return
        self._signup_refresh_coowners()
        self.window.stacked_widget.setCurrentIndex(14)

    # ── Cadastro — Coproprietários (idx 15) ───────────────────────────────────

    def _signup_refresh_coowners(self):
        lw = self.window.signup_coowners_screen.coowner_listwidget
        lw.clear()
        for c in self.window.farmer.coowners.list_of_coowners:
            share = f" | {c['share_pct']}%" if c.get("share_pct") else ""
            lw.addItem(f"{c['name']} | CPF: {c['cpf']} | {c['role']}{share}")

    def _coowner_form(self, prefill=None):
        return self.dialog.coowner_dialog(prefill=prefill)

    def signup_new_coowner(self):
        data = self._coowner_form()
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Dados inválidos! Verifique CPF, nome e vínculo.")
        else:
            role = data[2].strip()
            if role.isdigit():
                role = CoOwners.ROLES[int(role) - 1]
            self.window.farmer.coowners.new_coowner(data[0], data[1], role, data[3])
            self._signup_refresh_coowners()
            self.window.signup_coowners_screen.no_coowners_checkbox.setChecked(False)

    def signup_update_coowner(self):
        line = self.window.signup_coowners_screen.coowner_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um coproprietário para editar.")
            return
        c = self.window.farmer.coowners.list_of_coowners[line]
        data = self._coowner_form(prefill=[c["name"], c["cpf"], c["role"], c.get("share_pct", "")])
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Dados inválidos!")
        else:
            role = data[2].strip()
            if role.isdigit():
                role = CoOwners.ROLES[int(role) - 1]
            self.window.farmer.coowners.update_coowner(line, data[0], data[1], role, data[3])
            self._signup_refresh_coowners()

    def signup_delete_coowner(self):
        line = self.window.signup_coowners_screen.coowner_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um coproprietário para remover.")
            return
        if self.dialog.yes_or_no_dialog("Deseja remover o coproprietário selecionado?"):
            self.window.farmer.coowners.delete_coowner(line)
            self._signup_refresh_coowners()

    def signup_coowners_done(self):
        checkbox = self.window.signup_coowners_screen.no_coowners_checkbox
        tem_coowners = len(self.window.farmer.coowners.list_of_coowners) > 0
        if not tem_coowners and not checkbox.isChecked():
            self.dialog.error_dialog(
                "Adicione um coproprietário ou marque\n\"Não tenho coproprietários ou herdeiros\" para continuar."
            )
            return
        self.window.farmer.save()
        self.window.stacked_widget.setCurrentIndex(6)

    # ── Login ─────────────────────────────────────────────────────────────────

    def login(self):
        # Só permite login se o agricultor já tiver cadastro
        if self.window.farmer.phone_number:
            self.window.stacked_widget.setCurrentIndex(6)
        else:
            self.dialog.error_dialog("Nenhum cadastro encontrado. Por favor, faça o cadastro primeiro.")

    # ── Meus dados ────────────────────────────────────────────────────────────

    def my_data(self):
        self.window.my_data_screen.name_lineedit.setText(self.window.farmer.name)
        self.window.my_data_screen.cpf_lineedit.setText(self.window.farmer.cpf)
        self.window.my_data_screen.phone_lineedit.setText(self.window.farmer.phone_number)
        self.window.my_data_screen.town_lineedit.setText(self.window.farmer.town)
        combo = self.window.my_data_screen.state_combobox
        if combo.count() == 0:
            combo.addItems(list_of_states)
        combo.setCurrentText(self.window.farmer.state)
        self.window.stacked_widget.setCurrentIndex(7)

    def process_my_data(self):
        self.window.farmer.name = self.window.my_data_screen.name_lineedit.text()
        self.window.farmer.cpf = self.window.my_data_screen.cpf_lineedit.text()
        self.window.farmer.phone_number = self.window.my_data_screen.phone_lineedit.text()
        self.window.farmer.town = self.window.my_data_screen.town_lineedit.text()
        self.window.farmer.state = self.window.my_data_screen.state_combobox.currentText()
        self.window.farmer.save()
        self.window.stacked_widget.setCurrentIndex(6)

    # ── Gastos ────────────────────────────────────────────────────────────────

    def expenses(self):
        self.window.expenses_screen.expense_listwidget.clear()
        for expense in self.window.farmer.expense.list_of_expenses:
            culture = expense.get("culture", "Geral")
            text = f"Tipo: {expense['type']} | Cultura: {culture} | Valor: {expense['value']} | Data: {expense['date']}"
            self.window.expenses_screen.expense_listwidget.addItem(text)
        self.window.stacked_widget.setCurrentIndex(8)

    def process_expenses(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def new_expense(self):
        plantios = self.window.farmer.planting.list_of_planting
        if not plantios:
            self.dialog.error_dialog("Cadastre pelo menos um plantio antes de registrar um gasto.")
            return
        cultures = list({p["culture"] for p in plantios})
        data = self.dialog.expense_dialog(cultures)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao adicionar gasto! Verifique os dados digitados.")
        else:
            self.window.farmer.expense.new_expense(data["type"], data["value"], data["date"], data["culture"])
            self.window.farmer.save()
            self.expenses()

    def delete_expense(self):
        line = self.window.expenses_screen.expense_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um gasto para remover.")
            return
        if self.dialog.yes_or_no_dialog("Deseja remover o gasto selecionado?"):
            self.window.farmer.expense.delete_expense(line)
            self.window.farmer.save()
            self.expenses()

    def update_expense(self):
        line = self.window.expenses_screen.expense_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um gasto para editar.")
            return
        e = self.window.farmer.expense.list_of_expenses[line]
        cultures = list({p["culture"] for p in self.window.farmer.planting.list_of_planting})
        data = self.dialog.expense_dialog(cultures, prefill=e)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao editar gasto! Verifique os dados digitados.")
        else:
            self.window.farmer.expense.update_expense(line, data["type"], data["value"], data["date"], data["culture"])
            self.window.farmer.save()
            self.expenses()

    # ── Áreas ─────────────────────────────────────────────────────────────────

    def areas(self):
        self.window.areas_screen.area_listwidget.clear()
        for area in self.window.farmer.area.list_of_area:
            self.window.areas_screen.area_listwidget.addItem(area["name"])
        self.window.stacked_widget.setCurrentIndex(9)

    def process_areas(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def new_area(self):
        areas_existentes = [a["name"] for a in self.window.farmer.area.list_of_area]
        nome = self.dialog.area_dialog(areas_existentes)
        if nome is CANCELLED:
            return
        if nome is None:
            self.dialog.error_dialog("Erro ao adicionar área! Verifique os dados digitados.")
        else:
            self.window.farmer.area.new_area(nome)
            self.window.farmer.save()
            self.areas()

    def delete_area(self):
        line = self.window.areas_screen.area_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione uma área para remover.")
            return
        if self.dialog.yes_or_no_dialog("Deseja remover a área selecionada?"):
            error = self.window.farmer.area.delete_area(line)
            if error:
                self.dialog.error_dialog(error)
            else:
                self.window.farmer.save()
                self.areas()

    def update_area(self):
        line = self.window.areas_screen.area_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione uma área para editar.")
            return
        areas_existentes = [a["name"] for a in self.window.farmer.area.list_of_area]
        nome = self.dialog.area_dialog(areas_existentes)
        if nome is CANCELLED:
            return
        if nome is None:
            self.dialog.error_dialog("Erro ao editar área! Verifique os dados digitados.")
        else:
            self.window.farmer.area.update_area(line, nome)
            self.window.farmer.save()
            self.areas()

    # ── Plantio ───────────────────────────────────────────────────────────────

    def planting(self):
        self.window.planting_screen.planting_listwidget.clear()
        for p in self.window.farmer.planting.list_of_planting:
            canonical = p.get("amount_canonical", p["amount"])
            qty_display = p["amount"] if p["amount"] == canonical else f"{p['amount']} ({canonical})"
            text = f"Cultura: {p['culture']} | Área: {p['area']} | Qtd: {qty_display} | Data: {p['date']}"
            self.window.planting_screen.planting_listwidget.addItem(text)
        self.window.stacked_widget.setCurrentIndex(10)

    def process_planting(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def new_planting(self):
        areas = [a["name"] for a in self.window.farmer.area.list_of_area]
        if not areas:
            self.dialog.error_dialog("Cadastre pelo menos uma área antes de registrar um plantio.")
            return
        data = self.dialog.planting_dialog(areas)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao adicionar plantio! Verifique os dados digitados.")
        else:
            self.window.farmer.planting.new_planting(data["culture"], data["area"], data["amount"], data["date"])
            self.window.farmer.save()
            self.planting()

    def delete_planting(self):
        line = self.window.planting_screen.planting_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um plantio para remover.")
            return
        if self.dialog.yes_or_no_dialog("Deseja remover o plantio selecionado?"):
            self.window.farmer.planting.delete_planting(line)
            self.window.farmer.save()
            self.planting()

    def update_planting(self):
        line = self.window.planting_screen.planting_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um plantio para editar.")
            return
        p = self.window.farmer.planting.list_of_planting[line]
        areas = [a["name"] for a in self.window.farmer.area.list_of_area]
        data = self.dialog.planting_dialog(areas, prefill=p)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao editar plantio! Verifique os dados digitados.")
        else:
            self.window.farmer.planting.update_planting(line, data["culture"], data["area"], data["amount"], data["date"])
            self.window.farmer.save()
            self.planting()

    # ── Colheita ──────────────────────────────────────────────────────────────

    def harvest(self):
        self.window.harvests_screen.harvest_listwidget.clear()
        for h in self.window.farmer.harvest.list_of_harvest:
            canonical = h.get("amount_canonical", h["amount"])
            qty_display = h["amount"] if h["amount"] == canonical else f"{h['amount']} ({canonical})"
            text = f"Cultura: {h['culture']} | Qtd: {qty_display} | Data: {h['date']}"
            self.window.harvests_screen.harvest_listwidget.addItem(text)
        self.window.stacked_widget.setCurrentIndex(11)

    def process_harvests(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def new_harvest(self):
        plantios = self.window.farmer.planting.list_of_planting
        if not plantios:
            self.dialog.error_dialog("Cadastre pelo menos um plantio antes de registrar uma colheita.")
            return
        data = self.dialog.harvest_dialog(plantios)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao adicionar colheita! Verifique os dados digitados.")
        else:
            self.window.farmer.harvest.new_harvest(data["culture"], data["amount"], data["date"])
            self.window.farmer.save()
            self.harvest()

    def delete_harvest(self):
        line = self.window.harvests_screen.harvest_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione uma colheita para remover.")
            return
        if self.dialog.yes_or_no_dialog("Deseja remover a colheita selecionada?"):
            self.window.farmer.harvest.delete_harvest(line)
            self.window.farmer.save()
            self.harvest()

    def update_harvest(self):
        line = self.window.harvests_screen.harvest_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione uma colheita para editar.")
            return
        h = self.window.farmer.harvest.list_of_harvest[line]
        plantios = self.window.farmer.planting.list_of_planting
        if not plantios:
            self.dialog.error_dialog("Nenhum plantio cadastrado para selecionar a cultura.")
            return
        data = self.dialog.harvest_dialog(plantios, prefill=h)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao editar colheita! Verifique os dados digitados.")
        else:
            self.window.farmer.harvest.update_harvest(line, data["culture"], data["amount"], data["date"])
            self.window.farmer.save()
            self.harvest()

    # ── Relatório ─────────────────────────────────────────────────────────────

    def report(self):
        if self.window.farmer.report.gen_report() != 0:
            self.dialog.error_dialog("Erro: não foi possível gerar o relatório!")
        if self.dialog.yes_or_no_dialog("Relatório gerado com sucesso! Deseja abri-lo no navegador?"):
            self.window.farmer.report.open_report()

    # ── RF009 — Multiproprietários e herdeiros ────────────────────────────────

    def coowners(self):
        self._refresh_coowners()
        self.window.stacked_widget.setCurrentIndex(12)

    def _refresh_coowners(self):
        lw = self.window.coowners_screen.coowner_listwidget
        lw.clear()
        for c in self.window.farmer.coowners.list_of_coowners:
            share = f" | {c['share_pct']}%" if c.get("share_pct") else ""
            lw.addItem(f"{c['name']} | CPF: {c['cpf']} | {c['role']}{share}")

    def new_coowner(self):
        data = self._coowner_form()
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Dados inválidos! Verifique CPF, nome e vínculo.")
        else:
            role = data[2].strip()
            if role.isdigit():
                role = CoOwners.ROLES[int(role) - 1]
            self.window.farmer.coowners.new_coowner(data[0], data[1], role, data[3])
            self._refresh_coowners()

    def delete_coowner(self):
        line = self.window.coowners_screen.coowner_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um coproprietário para remover.")
            return
        if self.dialog.yes_or_no_dialog("Deseja remover o coproprietário selecionado?"):
            self.window.farmer.coowners.delete_coowner(line)
            self._refresh_coowners()

    def update_coowner(self):
        line = self.window.coowners_screen.coowner_listwidget.currentRow()
        if line < 0:
            self.dialog.error_dialog("Selecione um coproprietário para editar.")
            return
        c = self.window.farmer.coowners.list_of_coowners[line]
        data = self._coowner_form(prefill=[c["name"], c["cpf"], c["role"], c.get("share_pct", "")])
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Dados inválidos! Verifique CPF, nome e vínculo.")
        else:
            role = data[2].strip()
            if role.isdigit():
                role = CoOwners.ROLES[int(role) - 1]
            self.window.farmer.coowners.update_coowner(line, data[0], data[1], role, data[3])
            self._refresh_coowners()

    def process_coowners(self):
        self.window.stacked_widget.setCurrentIndex(6)
    # ═══════════════════════════════════════════════════════════════════════════
    # VA3 — RF011: REGISTRO POR VOZ (plantio, colheita, gasto)
    # ═══════════════════════════════════════════════════════════════════════════
    #
    # FLUXO COMPLETO:
    #   1. Agricultor clica em "Novo plantio/colheita/gasto"
    #   2. → events.py chama dialog.planting_dialog() / harvest_dialog() / expense_dialog()
    #   3. → dialog.py abre um QDialog com microfone (PlantioDialog/ColheitaDialog/GastoDialog)
    #   4. → Agricultor FALA uma frase (ex: "plantei três sacos de milho no roçado ontem")
    #   5. → VoiceThread (dialog.py) grava → VoiceInput (voice_input.py) transcreve com Whisper
    #   6. → LLMParser (llm_parser.py) interpreta a fala → devolve JSON estruturado
    #   7. → Campos do diálogo são preenchidos automaticamente
    #   8. → Agricultor confirma ou corrige manualmente
    #   9. → events.py salva no model → model salva no JSON
    #
    # DIFERENÇA DA VA2:
    #   VA2: agricultor DIGITAVA em formulários com campos separados
    #   VA3: agricultor FALA UMA FRASE e o LLM preenche TUDO automaticamente
    #
    # PRÓXIMO PASSO (futuro):
    #   - Transformar todos os formulários em entrada por voz como método principal
    #   - Digitação manual como fallback apenas

    def new_planting_voice(self):
        """
        RF011 — Novo plantio por voz.
        O agricultor fala: "plantei três sacos de milho no roçado ontem"
        O LLM extrai cultura, quantidade, área e data automaticamente.
        """
        areas = [a["name"] for a in self.window.farmer.area.list_of_area]
        if not areas:
            self.dialog.error_dialog("Cadastre pelo menos uma área antes de registrar um plantio.")
            return
        data = self.dialog.voice_planting_dialog(areas)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao adicionar plantio! Verifique os dados.")
        else:
            self.window.farmer.planting.new_planting(
                data["culture"], data["area"], data["amount"], data["date"]
            )
            self.window.farmer.save()
            self.planting()

    def new_harvest_voice(self):
        """
        RF011 — Nova colheita por voz.
        O agricultor fala: "colhi dez arrobas de feijão hoje"
        """
        cultures = list({p["culture"] for p in self.window.farmer.planting.list_of_planting})
        if not cultures:
            self.dialog.error_dialog("Cadastre pelo menos um plantio antes de registrar uma colheita.")
            return
        data = self.dialog.voice_harvest_dialog(cultures)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao adicionar colheita! Verifique os dados.")
        else:
            self.window.farmer.harvest.new_harvest(
                data["culture"], data["amount"], data["date"]
            )
            self.window.farmer.save()
            self.harvest()

    def new_expense_voice(self):
        """
        RF011 — Novo gasto por voz.
        O agricultor fala: "gastei duzentos reais com adubo pro milho ontem"
        """
        cultures = list({p["culture"] for p in self.window.farmer.planting.list_of_planting})
        data = self.dialog.voice_expense_dialog(cultures)
        if data is CANCELLED:
            return
        if data is None:
            self.dialog.error_dialog("Erro ao adicionar gasto! Verifique os dados.")
        else:
            self.window.farmer.expense.new_expense(
                data["type"], data["value"], data["date"], data["culture"]
            )
            self.window.farmer.save()
            self.expenses()
