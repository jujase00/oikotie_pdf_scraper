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

The location parameter is case-insensitive, and the script handles special Finnish characters (ä, ö, å) in both the URL and the provided location parameter. "# oikotie-pdf-scaper" 
