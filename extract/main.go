package main

import (
	"fmt"
	"log"
	"path/filepath"

	"etl/config"
	"etl/extract"
)

func main() {
	// Add "Quý" as the first field in each sheet's headers
	balanceSheetHeaders := append([]string{"Quý"}, config.BalanceSheetFields...)
	incomeStatementHeaders := append([]string{"Quý"}, config.IncomeStatementFields...)
	cashFlowHeaders := append([]string{"Quý"}, config.CashFlowFields...)

	// Initialize data with modified headers
	allData := map[string][][]string{
		config.ReportTypeToSheet["bsheet"]:   {balanceSheetHeaders},
		config.ReportTypeToSheet["incsta"]:   {incomeStatementHeaders},
		config.ReportTypeToSheet["cashflow"]: {cashFlowHeaders},
	}

	for year := config.StartYear; year <= config.EndYear; year++ {
		for _, report := range config.ReportTypes {
			fmt.Printf("Fetching %s for year %d\n", report, year)
			rows, err := extract.CrawlReport(config.StockCode, report, year)
			if err != nil {
				log.Printf("Error fetching %s %d: %v\n", report, year, err)
				continue
			}

			// Each row is a slice: [description, Q1, Q2, Q3, Q4]
			// We want to build 4 rows per year, one for each quarter
			for q := 0; q < config.QuarterCount; q++ {
				quarter := fmt.Sprintf("%d/%d", q+1, year)
				dataRow := []string{quarter}

				// Add each field's value for this quarter
				for _, row := range rows {
					if len(row) > q+1 {
						dataRow = append(dataRow, row[q+1])
					} else {
						dataRow = append(dataRow, "")
					}
				}

				allData[config.ReportTypeToSheet[report]] = append(allData[config.ReportTypeToSheet[report]], dataRow)
			}
		}
	}

	// outputPath := filepath.Join("../csv/data_crawl", "financial_reports.xlsx")
	outputPath := filepath.Join("../csv/data_crawl", fmt.Sprintf("financial_report_%s.xlsx", config.StockCode))

	if err := extract.WriteToExcel(outputPath, allData); err != nil {
		log.Fatalf("Failed to write Excel: %v", err)
	}

	fmt.Println("Data exported to:", outputPath)
}
