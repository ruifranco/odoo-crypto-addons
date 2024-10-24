import json

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def recompute_balance(self):
        super().recompute_balance()

        for statement in self:
            bank_id = statement.journal_id.bank_account_id.bank_id
            if bank_id.crypto_provider != "kraken":
                continue

            min_ts = float("inf")
            max_ts = 0
            for line in statement.line_ids:
                input_ids = line.crypto_transaction_id.transaction_id.input_ids
                if not input_ids:
                    continue
                data = json.loads(input_ids[0].raw)[1]
                ts = float(data.get("time", 0))
                if ts < min_ts:
                    min_ts = ts
                    balance_start = (
                        float(data.get("balance", 0)) - float(data.get("amount", 0)) + float(data.get("fee", 0))
                    )
                if ts > max_ts:
                    max_ts = ts
                    balance_end_real = float(data.get("balance", 0))

            statement.write({"balance_start": balance_start, "balance_end_real": balance_end_real})
