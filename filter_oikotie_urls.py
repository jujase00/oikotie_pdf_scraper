#!/usr/bin/env python3
import os
import re
import sys
import argparse
from datetime import datetime

def filter_urls(input_file, listing_type=None, location=None):
    """
    Filter URLs based on listing type and location.
    
    Args:
        input_file (str): Path to the input file containing URLs
        listing_type (str, optional): Type of listing to filter (e.g., 'vuokra-asunnot', 'myytavat-asunnot')
        location (str, optional): Location/city to filter
        
    Returns:
        list: Filtered URLs
    """
    filtered_urls = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            urls = f.read().splitlines()
        
        # Remove empty lines
        urls = [url.strip() for url in urls if url.strip()]
        
        # Filter URLs
        for url in urls:
            # Skip if not an Oikotie URL
            if not url.startswith('https://asunnot.oikotie.fi/') and not url.startswith('https://toimitilat.oikotie.fi/'):
                continue
                
            # Check listing type if specified
            if listing_type and listing_type not in url:
                continue
                
            # Check location if specified
            if location:
                # Parse the URL to find the location
                # Format is usually: domain/listing-type/location/id
                # Use regex to extract the location part more reliably
                regex_pattern = r'https://(?:asunnot|toimitilat)\.oikotie\.fi/[^/]+/([^/]+)'
                location_match = re.search(regex_pattern, url)
                
                if location_match:
                    url_location = location_match.group(1)
                    
                    # Handle URL encoding
                    url_location = url_location.replace('%C3%A4', 'ä')
                    url_location = url_location.replace('%C3%B6', 'ö')
                    url_location = url_location.replace('%C3%A5', 'å')
                    
                    # Case insensitive comparison
                    if location.lower() != url_location.lower():
                        continue
                else:
                    # If we can't find a location in the URL, skip it
                    continue
            
            # If we get here, the URL passed all filters
            filtered_urls.append(url)
                
        return filtered_urls
        
    except Exception as e:
        print(f"Error reading or filtering URLs: {e}")
        return []

def save_filtered_urls(urls, output_file):
    """
    Save filtered URLs to a file.
    
    Args:
        urls (list): List of URLs to save
        output_file (str): Path to output file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(f"{url}\n")
                
        print(f"Saved {len(urls)} URLs to {output_file}")
        
    except Exception as e:
        print(f"Error saving filtered URLs: {e}")

def main():
    """Main function to parse arguments and filter URLs."""
    parser = argparse.ArgumentParser(description='Filter Oikotie URLs by listing type and location')
    
    parser.add_argument('--input', '-i', required=True, 
                        help='Path to input file containing URLs')
    parser.add_argument('--type', '-t', 
                        help='Listing type (e.g., "vuokra-asunnot", "myytavat-asunnot", "myytavat-tontit")')
    parser.add_argument('--location', '-l', 
                        help='Location/city (e.g., "helsinki", "tampere")')
    
    args = parser.parse_args()
    
    if not (args.type or args.location):
        print("Error: You must specify at least one filter criterion (--type or --location)")
        parser.print_help()
        sys.exit(1)
        
    # Filter URLs
    filtered_urls = filter_urls(args.input, args.type, args.location)
    
    # Print debug information
    print(f"Found {len(filtered_urls)} URLs matching the criteria.")
    
    if not filtered_urls:
        print("No URLs matched the filtering criteria.")
        sys.exit(0)
        
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    type_str = args.type if args.type else "any-type"
    location_str = args.location if args.location else "any-location"
    
    output_file = os.path.join("QUEUE", f"filtered_{type_str}_{location_str}_{timestamp}.txt")
    
    # Save filtered URLs
    save_filtered_urls(filtered_urls, output_file)
    
if __name__ == "__main__":
    main() 