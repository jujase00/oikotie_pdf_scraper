# Oikotie URL Filter

This script allows you to filter Oikotie property listing URLs from a source file based on two criteria:
1. Listing type (e.g., rental apartments, properties for sale, lots for sale)
2. Location (city where the property is located)

## Usage

```bash
python filter_oikotie_urls.py -i INPUT_FILE [--type TYPE] [--location LOCATION]
```

### Parameters

- `-i, --input`: Path to the input file containing URLs (required)
- `-t, --type`: Listing type (e.g., "vuokra-asunnot", "myytavat-asunnot", "myytavat-tontit")
- `-l, --location`: Location/city (e.g., "helsinki", "tampere")

You must specify at least one of either `--type` or `--location` parameters.

### Examples

Filter all rental apartments:
```bash
python filter_oikotie_urls.py -i URL_LIST/oikotie_listing_urls_example.txt -t vuokra-asunnot
```

Filter all properties in Helsinki:
```bash
python filter_oikotie_urls.py -i URL_LIST/oikotie_listing_urls_example.txt -l helsinki
```

Filter rental apartments in Tampere:
```bash
python filter_oikotie_urls.py -i URL_LIST/oikotie_listing_urls_example.txt -t vuokra-asunnot -l tampere
```

## Output

The script creates a text file in the `QUEUE` directory with a filename that includes the filtering criteria and a timestamp:

```
QUEUE/filtered_TYPE_LOCATION_TIMESTAMP.txt
```

For example:
```
QUEUE/filtered_vuokra-asunnot_helsinki_20250430_200912.txt
```

## All Supported Listing Types

Here are all the listing types you can use with the `--type` parameter:

- `vuokra-asunnot`: Rental apartments
- `myytavat-asunnot`: Properties for sale
- `myytavat-tontit`: Lots for sale
- `myytavat-loma-asunnot`: Vacation properties for sale
- `vuokrattavat-loma-asunnot`: Vacation properties for rent
- `myytavat-autotallit`: Garages for sale
- `vuokrattavat-autotallit`: Garages for rent
- `vuokrattavat-toimitilat`: Commercial spaces for rent
- `myytavat-toimitilat`: Commercial spaces for sale

## Note

The location parameter is case-insensitive, and the script handles special Finnish characters (ä, ö, å) in both the URL and the provided location parameter.

# Oikotie PDF Downloader

This script (`oikotie_downloader_viaURL.py`) allows you to download PDF brochures from Oikotie property listings and optionally extract text from them.

## Usage

You can use the script in two ways: via command line or by importing it in Python.

### Command Line

#### Process a single URL:
```bash
python oikotie_downloader_viaURL.py --url "https://asunnot.oikotie.fi/..." [--output output.txt] [--keep-pdfs]
```

#### Process a list of URLs from a file:
```bash
python oikotie_downloader_viaURL.py --file URL_LIST/oikotie_listing_urls.txt [--keep-pdfs]
```

### Parameters

- `--url` or `-u`: Single Oikotie URL to process
- `--file` or `-f`: File containing Oikotie URLs to process (one URL per line)
- `--output` or `-o`: Output path for extracted text content (only for single URL)
- `--keep-pdfs` or `-k`: Keep the downloaded PDFs (by default they are deleted after text extraction)

### Python Import

You can also use the script by importing it in your Python code:

```python
import oikotie_downloader_viaURL

# Process a single URL
text_content, pdf_path = oikotie_downloader_viaURL.get_property_info(
    url="https://asunnot.oikotie.fi/...", 
    keep_pdf=True,  # Keep the PDF (default: False)
    verbose=True    # Show progress messages (default: True)
)

# Process a list of URLs from a file
successful_urls = oikotie_downloader_viaURL.process_url_list(
    url_list_file="URL_LIST/oikotie_listing_urls.txt",
    keep_pdfs=True  # Keep the downloaded PDFs (default: True)
)
```

## Output

- PDFs are saved to the `PDFs` directory with filenames based on the listing ID
  - When processing a URL list, PDFs are saved to a subfolder within `PDFs` directory named `{input_filename}_{timestamp}`
- When processing a URL list, reports of successful and failed URLs are saved to the `DONE_URLs` directory
- Text content is either displayed on the console, saved to a specified file, or returned as a string when imported as a module

### Additional Command Line Options

When processing a single URL, you can specify a custom subfolder name:
```bash
python oikotie_downloader_viaURL.py --url "https://asunnot.oikotie.fi/..." --subfolder my_custom_folder
```

## Workflow Example

1. Filter URLs with `filter_oikotie_urls.py`
2. Process the filtered URLs with `oikotie_downloader_viaURL.py`
3. Analyze the extracted text or work with the downloaded PDFs 
