package config

import "fmt"

const (
	StockCode    = "VGI"
	StartYear    = 2008
	EndYear      = 2024
	QuarterCount = 4
)

// Report types
const (
	BalanceSheet    = "bsheet"
	IncomeStatement = "incsta"
	CashFlow        = "cashflow"
	CashFlowDirect  = "cashflowdirect"
)

var ReportTypes = []string{
	BalanceSheet,
	IncomeStatement,
	CashFlow,
}

var ReportTypeToSheet = map[string]string{
	BalanceSheet:    "Balance Sheet",
	IncomeStatement: "Income Statement",
	CashFlow:        "Cash Flow",
	CashFlowDirect:  "Cash Flow Direct",
}

// BuildURL creates the URL for fetching financial statements
func BuildURL(stockCode string, reportType string, year int) string {
	return fmt.Sprintf(
		"https://cafef.vn/du-lieu/bao-cao-tai-chinh/%s/%s/%d/4/0/0/bao-cao-tai-chinh-.chn",
		stockCode, reportType, year,
	)
}
