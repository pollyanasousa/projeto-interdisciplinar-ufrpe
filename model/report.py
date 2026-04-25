import os
import webbrowser

from utils.menu import *

class Report:
    def __init__(self, farmer, area, planting, harvest, expense):
        """
        This class defines the report.
        """

        self.farmer = farmer
        self.area = area
        self.planting = planting
        self.harvest = harvest
        self.expense = expense

    def gen_report(self):
        """
        It generates a report in PDF format.
        """

        area_html = ""
        for area in self.area.list_of_area:
            area_html += f"""
            <tr>
                <td>{area["name"]}</td>
            </tr>
            """

        planting_html = ""
        for planting in self.planting.list_of_planting:
            planting_html += f"""
            <tr>
                <td>{planting["culture"]}</td>
                <td>{planting["area"]}</td>
                <td>{planting["amount"]}</td>
                <td>{planting["date"]}</td>
            </tr>
            """

        harvest_html = ""
        for harvest in self.harvest.list_of_harvest:
            harvest_html += f"""
            <tr>
                <td>{harvest["culture"]}</td>
                <td>{harvest["amount"]}</td>
                <td>{harvest["date"]}</td>
            </tr>
            """

        expense_html = ""
        for expense in self.expense.list_of_expenses:
            expense_html += f"""
            <tr>
                <td>{expense["type"]}</td>
                <td>{expense["value"]}</td>
                <td>{expense["date"]}</td>
            </tr>
            """


        report_html = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="utf-8">
            <title>Relatório de safra</title>
            <style>
                * {{
                    font-family: Arial, sans;
                    text-align: center;
                }}

                div {{
                    margin: 0 auto;
                    background-color: #393;
                    color: #FFF;
                    -webkit-text-stroke-width: 1px;
                    -webkit-text-stroke-color: #000;
                    width: 90%;
                    height: 100%;
                }}

                table {{
                    margin: 0 auto;
                    margin-bottom: 20px;
                }}

                hr {{
                    width: 80%;
                }}
            </style>
        </head>
        <body>
            <div>
                <h1>Relatório de safra</h1>
            </div>
            <hr />
            <h2>Dados do agricultor:</h2>
            <p><b>Nome:</b> {self.farmer.name}</p>
            <p><b>CPF:</b> {self.farmer.cpf}</p>
            <p><b>Telefone:</b> {self.farmer.phone_number}</p>
            <p><b>Cidade:</b> {self.farmer.town}</p>
            <p><b>Estado:</b> {self.farmer.state}</p>

            <hr />

            <h2>Lista de áreas:</h2>
            <table border="1">
                <tr>
                    <th>Nome</th>
                </tr>

                {area_html}
            </table>

            <hr />

            <h2>Lista de plantios:</h2>
            <table border="1">
                <tr>
                    <th>Cultura</th>
                    <th>Área</th>
                    <th>Quantidade</th>
                    <th>Data do plantio</th>
                </tr>

                {planting_html}
            </table>

            <hr />

            <h2>Colheita e gastos:</h2>
            <h3>Lista de colheita:</h3>
            <table border="1">
                <tr>
                    <th>Cultura</th>
                    <th>Quantidade</th>
                    <th>Data da colheita</th>
                </tr>

                {harvest_html}
            </table>

            <h3>Lista de gastos:</h3>
            <table border="1">
                <tr>
                    <th>Tipo de gasto</th>
                    <th>Valor</th>
                    <th>Data</th>
                </tr>

                {expense_html}
            </table>
        </body>
        </html>
        """

        try:
            REPORT_NAME = "RelatorioDeSafra.html"

            with open(REPORT_NAME, "w", encoding="utf-8") as result_file:
                result_file.write(report_html)

            print("Relatório gerado com sucesso!")
            print("Deseja abri-lo no navegador?")

            option = show_menu(["Sim", "Não"])
            if option == 0:
                report_path = os.path.realpath(REPORT_NAME)
                webbrowser.open('file://' + report_path)

        except Except as e:
            print("Falha ao gerar o relatório de safra!")
            print(e)
