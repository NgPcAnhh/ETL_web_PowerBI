from excel2csv import excel2csv_from_config
from balancesheet_process import process_balancesheet_from_config
from income_statement import process_income_statement_from_config
from cash_flow import process_cash_flow_from_config
from time import sleep


if __name__ == "__main__":
    excel2csv_from_config("config.txt")
    sleep(0.5)
    process_balancesheet_from_config("config.txt")
    sleep(0.5)
    process_income_statement_from_config("config.txt")
    sleep(0.5)
    process_cash_flow_from_config("config.txt")