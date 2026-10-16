# CSV Data Cleaner

A small Python tool that cleans messy CSV files and tells you exactly what was wrong.
Built with the standard library only, so there is nothing to install.

## What it does

- Trims stray whitespace and collapses repeated spaces
- Title-cases names
- Standardises Kenyan phone numbers to `+254XXXXXXXXX` (handles `07..`, `01..`, `254..`)
- Converts dates in several common formats to `YYYY-MM-DD`
- Lowercases emails and validates their format
- Removes blank rows and exact duplicates
- Writes an **errors report** listing the row, column, value and problem for anything it could not fix

## Usage

```bash
python clean.py sample_data/messy_contacts.csv
```

Output files are created next to the input: `messy_contacts_cleaned.csv` and `messy_contacts_errors.csv`.
Use `-o` and `-e` to choose your own paths.

Columns are detected by header name (anything containing `phone`, `email`, `date`/`dob` or `name`).

## Example run

```
Rows read:            8
Rows written:         6
Duplicates removed    1
Blank rows removed    1
Cells changed         18
Problems flagged:     4  (see sample_data/messy_contacts_errors.csv)
Cleaned file:         sample_data/messy_contacts_cleaned.csv
```

## Notes

Dates are read day-first (`05/01/2000` means 5 January). The sample data is fictional.
