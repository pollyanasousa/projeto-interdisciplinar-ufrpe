class Report:
    def __init__(self, farmer, planting):
        """
        This class defines the report.
        """

        self.farmer = farmer
        self.planting = planting
        self.harvest = ""
        self.expenses = ""

    def gen_report(self):
        """
        It generates a report in PDF format.
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


        report_html = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="utf-8">
            <title>Relatório de safra</title>
        </head>
        <body>
            <h1>Relatório de safra</h1>
            <hr />
            <h2>Dados do agricultor:</h2>
            <p><b>Nome:</b> {self.farmer.name}</p>
            <p><b>Telefone:</b> {self.farmer.phone_number}</p>
            <p><b>Cidade:</b> {self.farmer.town}</p>
            <p><b>Estado:</b> {self.farmer.state}</p>
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
        </body>
        </html>
        """

        try:
            with open("RelatorioDeSafra.html", "w", encoding="utf-8") as result_file:
                result_file.write(report_html)

            print("Relatório gerado com sucesso!")

        except Except as e:
            print("Falha ao gerar o relatório de safra!")
            print(e)
