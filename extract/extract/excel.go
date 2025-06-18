package extract

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/xuri/excelize/v2"
)

// WriteToExcel writes the financial data to an Excel file
func WriteToExcel(outputPath string, data map[string][][]string) error {
	// Create directory if it doesn't exist
	dir := filepath.Dir(outputPath)
	if err := os.MkdirAll(dir, os.ModePerm); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	// Create a new Excel file
	f := excelize.NewFile()

	// Add sheets and data
	for sheetName, sheetData := range data {
		// Create a new sheet
		index, err := f.NewSheet(sheetName)
		if err != nil {
			return fmt.Errorf("failed to create sheet '%s': %w", sheetName, err)
		}

		// Write data to the sheet
		for rowIndex, rowData := range sheetData {
			for colIndex, cellValue := range rowData {
				cell, err := excelize.CoordinatesToCellName(colIndex+1, rowIndex+1)
				if err != nil {
					return fmt.Errorf("failed to convert coordinates: %w", err)
				}
				if err := f.SetCellValue(sheetName, cell, cellValue); err != nil {
					return fmt.Errorf("failed to set cell value: %w", err)
				}
			}
		}

		// Set as the default sheet
		if sheetName == "Balance Sheet" {
			f.SetActiveSheet(index)
		}
	}

	// Remove the default Sheet1
	f.DeleteSheet("Sheet1")

	// Save the Excel file
	if err := f.SaveAs(outputPath); err != nil {
		return fmt.Errorf("failed to save Excel file: %w", err)
	}

	return nil
}
