package extract

import (
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"etl/config"

	"github.com/PuerkitoBio/goquery"
)

// CrawlReport fetches financial report data from CafeF
func CrawlReport(stockCode string, reportType string, year int) ([][]string, error) {
	url := config.BuildURL(stockCode, reportType, year)

	// Add sleep to avoid overloading the server
	time.Sleep(2 * time.Second)

	// Make the HTTP request
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch URL: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("received non-200 status: %d", resp.StatusCode)
	}

	// Parse the HTML
	return parseReportHTML(resp.Body)
}

// parseReportHTML extracts financial data from the HTML
func parseReportHTML(body io.Reader) ([][]string, error) {
	doc, err := goquery.NewDocumentFromReader(body)
	if err != nil {
		return nil, fmt.Errorf("failed to parse HTML: %w", err)
	}

	var rows [][]string

	// Find the table with financial data
	table := doc.Find("table#tableContent")
	if table.Length() == 0 {
		return nil, fmt.Errorf("table with ID 'tableContent' not found")
	}

	// Process each row
	table.Find("tbody tr.r_item, tbody tr.r_item_a").Each(func(i int, tr *goquery.Selection) {
		var row []string

		// Get the description (first column)
		description := strings.TrimSpace(tr.Find("td.b_r_c").First().Text())
		row = append(row, description)

		// Get the quarterly data (next 4 columns)
		tr.Find("td.b_r_c").Not(":first-child").Each(func(j int, td *goquery.Selection) {
			value := strings.TrimSpace(td.Text())
			row = append(row, value)
		})

		// Add the row if it has data
		if len(row) > 0 {
			rows = append(rows, row)
		}
	})

	return rows, nil
}
