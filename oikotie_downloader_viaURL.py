#!/usr/bin/env python3
import re
import os
import sys
import requests
import tempfile
import argparse
from datetime import datetime
from PyPDF2 import PdfReader
import unicodedata


def normalize_text(text):
    """Normalize Unicode text by replacing special characters."""
    # Replace common problematic characters
    replacements = {
        "Ã¤": "ä",
        "Ã¶": "ö",
        "Ã…": "Å",
        "Ã¥": "å",
        "â‚¬": "€",
        "mÂ²": "m²"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def convert_to_showcase_url(url):
    """Convert an Oikotie property URL to its showcase PDF URL format.
    
    Args:
        url (str): Original Oikotie property URL
        
    Returns:
        str: URL for the showcase PDF
    """
    # Extract the property ID from the URL
    # The pattern should match /digits at the end of the URL
    match = re.search(r'/(\d+)/?$', url)
    if not match:
        raise ValueError(f"Invalid Oikotie URL format: {url}. Expected URL ending with a property ID.")
    
    property_id = match.group(1)
    print(f"Extracted property ID: {property_id}")
    return f"https://asunnot.oikotie.fi/nayttoesite/{property_id}"


def download_pdf(showcase_url, output_path=None, listing_id=None, pdf_subfolder=None):
    """Download the PDF from the showcase URL.
    
    Args:
        showcase_url (str): The showcase URL to download the PDF from
        output_path (str, optional): Path to save the PDF. If None, uses a temporary file.
        listing_id (str, optional): The listing ID to use in the filename
        pdf_subfolder (str, optional): Subfolder within PDFs directory to save the file
        
    Returns:
        str: Path to the downloaded PDF file
    """
    print(f"Attempting to download PDF from: {showcase_url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(showcase_url, headers=headers)
        
        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to download PDF. Status code: {response.status_code}")
        
        # If no output path is specified, create a proper filename in PDFs directory
        if output_path is None:
            # Create PDFs directory if it doesn't exist
            os.makedirs('PDFs', exist_ok=True)
            
            # If a subfolder is specified, create it and adjust the path
            pdf_dir = 'PDFs'
            if pdf_subfolder:
                pdf_dir = os.path.join('PDFs', pdf_subfolder)
                os.makedirs(pdf_dir, exist_ok=True)
            
            # Use listing ID for filename if provided
            if listing_id:
                filename = f"oikotie_{listing_id}.pdf"
            else:
                # Extract ID from URL
                match = re.search(r'/(\d+)/?$', showcase_url)
                if match:
                    filename = f"oikotie_{match.group(1)}.pdf"
                else:
                    # Use timestamp if ID can't be extracted
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"oikotie_{timestamp}.pdf"
            
            output_path = os.path.join(pdf_dir, filename)
        
        # Write the PDF content to the file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"PDF successfully downloaded to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        raise


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        str: Extracted text content
    """
    print(f"Extracting text from PDF: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        text = ""
        
        # Extract text from each page
        for i, page in enumerate(reader.pages):
            print(f"Processing page {i+1}/{len(reader.pages)}")
            page_text = page.extract_text()
            text += page_text + "\n\n"
        
        # Normalize problematic characters
        normalized_text = normalize_text(text)
        
        return normalized_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise


def process_oikotie_url(url, keep_pdf=False, pdf_subfolder=None):
    """Process an Oikotie URL to download the PDF and convert it to text.
    
    Args:
        url (str): Original Oikotie property URL
        keep_pdf (bool): Whether to keep the PDF file after processing
        pdf_subfolder (str, optional): Subfolder within PDFs directory to save the file
        
    Returns:
        tuple: (text_content, pdf_path) where text_content is the extracted text
               and pdf_path is the path to the PDF file (or None if not kept)
    """
    print(f"Processing Oikotie URL: {url}")
    pdf_path = None
    
    try:
        # Extract the listing ID from the URL
        listing_id = None
        match = re.search(r'/(\d+)/?$', url)
        if match:
            listing_id = match.group(1)
        
        # Convert the URL to showcase format
        showcase_url = convert_to_showcase_url(url)
        
        # Download the PDF
        pdf_path = download_pdf(showcase_url, listing_id=listing_id, pdf_subfolder=pdf_subfolder)
        
        # Extract text from the PDF
        text_content = extract_text_from_pdf(pdf_path)
        
        # If we don't want to keep the PDF, delete it
        if not keep_pdf and pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                print(f"PDF file deleted: {pdf_path}")
                # Return None for pdf_path if we deleted it
                return text_content, None
            except Exception as e:
                print(f"Warning: Failed to delete PDF file: {e}")
        
        # Return both the text content and the PDF path
        return text_content, pdf_path
    except Exception as e:
        print(f"Error processing URL: {e}")
        if pdf_path and os.path.exists(pdf_path) and not keep_pdf:
            try:
                os.remove(pdf_path)
            except:
                pass
        raise


def get_property_info(url, keep_pdf=False, verbose=True, pdf_subfolder=None):
    """Main function to get property information from an Oikotie URL.
    
    This is the recommended function to use when importing this module.
    
    Args:
        url (str): Original Oikotie property URL
        keep_pdf (bool): Whether to keep the PDF file after processing
        verbose (bool): Whether to print progress messages
        pdf_subfolder (str, optional): Subfolder within PDFs directory to save the file
        
    Returns:
        tuple: (text_content, pdf_path) where text_content is the extracted text
               and pdf_path is the path to the PDF file (or None if not kept)
    """
    # Save the current print function
    original_print = print
    
    # If verbose is False, disable printing
    if not verbose:
        # Define a function that does nothing
        def silent_print(*args, **kwargs):
            pass
        # Replace the built-in print function with our silent version
        globals()['print'] = silent_print
    
    try:
        # Process the URL and get the property information
        return process_oikotie_url(url, keep_pdf, pdf_subfolder=pdf_subfolder)
    finally:
        # Restore the original print function
        globals()['print'] = original_print


def process_url_list(url_list_file, keep_pdfs=True):
    """Process a list of URLs from a file.
    
    Args:
        url_list_file (str): Path to the file containing URLs
        keep_pdfs (bool): Whether to keep the downloaded PDFs
        
    Returns:
        list: List of successful URLs
    """
    successful_urls = []
    failed_urls = []
    
    try:
        # Read the URLs from the file
        with open(url_list_file, 'r', encoding='utf-8') as f:
            urls = f.read().splitlines()
        
        # Remove empty lines
        urls = [url.strip() for url in urls if url.strip()]
        
        print(f"Found {len(urls)} URLs in {url_list_file}")
        
        # Create a timestamp for file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get the base name of the input file (without directory and extension)
        base_name = os.path.splitext(os.path.basename(url_list_file))[0]
        
        # Create a unique subfolder for this URL list's PDFs
        pdf_subfolder = f"{base_name}_{timestamp}"
        print(f"Creating PDF subfolder: PDFs/{pdf_subfolder}")
        
        # Process each URL
        for i, url in enumerate(urls):
            print(f"\nProcessing URL {i+1}/{len(urls)}: {url}")
            try:
                # Process the URL with the specific subfolder
                _, pdf_path = process_oikotie_url(url, keep_pdf=keep_pdfs, pdf_subfolder=pdf_subfolder)
                
                # If a PDF was successfully downloaded, add the URL to the successful list
                if pdf_path:
                    successful_urls.append(url)
                    print(f"Successfully processed: {url}")
                else:
                    # This should not happen if keep_pdfs is True, but just in case
                    failed_urls.append(url)
                    print(f"Failed to download PDF: {url}")
            except Exception as e:
                # If an error occurred, add the URL to the failed list
                failed_urls.append(url)
                print(f"Error processing URL: {url}")
                print(f"Error: {e}")
        
        # Create DONE_URLs directory if it doesn't exist
        os.makedirs('DONE_URLs', exist_ok=True)
        
        # Save the successful URLs to a file
        if successful_urls:
            success_file = os.path.join('DONE_URLs', f"{base_name}_successful_{timestamp}.txt")
            with open(success_file, 'w', encoding='utf-8') as f:
                for url in successful_urls:
                    f.write(f"{url}\n")
            print(f"\nSuccessfully processed {len(successful_urls)} URLs")
            print(f"Successful URLs saved to: {success_file}")
            print(f"PDFs saved to: PDFs/{pdf_subfolder}/")
        else:
            print("\nNo URLs were successfully processed")
        
        # Save the failed URLs to a file
        if failed_urls:
            failed_file = os.path.join('DONE_URLs', f"{base_name}_failed_{timestamp}.txt")
            with open(failed_file, 'w', encoding='utf-8') as f:
                for url in failed_urls:
                    f.write(f"{url}\n")
            print(f"Failed to process {len(failed_urls)} URLs")
            print(f"Failed URLs saved to: {failed_file}")
        
        return successful_urls
    except Exception as e:
        print(f"Error processing URL list: {e}")
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download PDFs from Oikotie property listings')
    
    # Create a mutually exclusive group for single URL vs URL list
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', '-u', help='Single Oikotie URL to process')
    group.add_argument('--file', '-f', help='File containing Oikotie URLs to process')
    
    parser.add_argument('--output', '-o', help='Output path for text content (only for single URL)')
    parser.add_argument('--keep-pdfs', '-k', action='store_true', help='Keep the downloaded PDFs')
    parser.add_argument('--subfolder', '-s', help='Specify a custom subfolder name for PDFs (only for single URL)')
    
    args = parser.parse_args()
    
    try:
        print("\n=== Oikotie Property Downloader ===\n")
        
        if args.url:
            # Process a single URL
            text_content, pdf_path = process_oikotie_url(args.url, keep_pdf=args.keep_pdfs, pdf_subfolder=args.subfolder)
            
            # If output path is provided, write to file
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                print(f"\nText content written to: {args.output}")
            else:
                # Otherwise print to console
                print("\n=== Extracted Text Content ===\n")
                print(text_content)
                
            if pdf_path:
                print(f"\nPDF saved to: {pdf_path}")
        else:
            # Process a list of URLs
            process_url_list(args.file, keep_pdfs=args.keep_pdfs or True)  # Always keep PDFs in list mode
        
        print("\nProcess completed successfully.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
