#!/usr/bin/env python3

"""
A simple Python script to download a URL with browser cookies,
mimicking `wget --load-cookies`.

"""

import os
import argparse
from urllib.parse import urlparse
import requests
import browsercookie

def download_with_cookies(url, output_file):
    """
    Downloads a given URL to an output file, automatically sending
    any relevant cookies from installed web browsers.
    """
    
    print(f"Attempting to load cookies from browsers (Chrome, Firefox, etc.)...")
    
    try:
        # 1. Load cookies from all supported browsers into a CookieJar object
        # browsercookie.load() finds all profiles for Firefox, Chrome, etc.
        cookie_jar = browsercookie.load()
        
        if not cookie_jar:
            print("Warning: No cookies were found or loaded.")
        else:
            print(f"Successfully loaded {len(cookie_jar)} cookies.")
            
    except Exception as e:
        print(f"Error loading cookies: {e}")
        print("This can happen if browsers are not found or if decryption fails.")
        print("Proceeding without cookies...")
        cookie_jar = None

    # 2. Create a 'requests.Session'
    # A Session object persists cookies, just like a browser or wget.
    with requests.Session() as session:
        
        # 3. "Load" the cookies into the session.
        if cookie_jar:
            session.cookies = cookie_jar
        
        # 4. Set a common User-Agent
        # Many sites block default Python user-agents.
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        }
        
        print(f"\nDownloading: {url}")
        
        try:
            # 5. Make the request
            # The session automatically selects and sends the correct cookies
            # from the 'cookie_jar' based on the URL's domain.
            response = session.get(url, allow_redirects=True)
            
            # Check for HTTP errors (like 404, 403, 500)
            response.raise_for_status()
            
            # 6. Save the content to the output file
            # We use 'wb' (write binary) to correctly handle all file types
            # (images, zips, text, etc.)
            with open(output_file, 'wb') as f:
                f.write(response.content)
                
            print(f"\nSuccess! Content saved to: {output_file}")
            
        except requests.exceptions.HTTPError as e:
            print(f"\nHTTP Error: {e.response.status_code} {e.response.reason}")
            print("This could be due to missing/invalid cookies or a bad URL.")
        except requests.exceptions.RequestException as e:
            print(f"\nAn error occurred: {e}")
        except IOError as e:
            print(f"\nError writing to file {output_file}: {e}")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

def get_output_filename(url, provided_filename=None):
    """
    Determines the output filename.
    If a filename is provided, it's used.
    Otherwise, it's inferred from the URL.
    """
    if provided_filename:
        return provided_filename
    
    # No filename provided, so guess from the URL
    try:
        path = urlparse(url).path
        filename = os.path.basename(path)
        
        # If URL is like "http://example.com/"
        if not filename:
            print("No filename in URL. Defaulting to 'index.html'")
            return 'index.html'
            
        return filename
    except Exception as e:
        print(f"Could not parse URL to get filename: {e}. Defaulting to 'index.html'")
        return 'index.html'

if __name__ == "__main__":
    
    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Download a file using browser cookies (like wget --load-cookies)",
        epilog="Example: ./py_wget_v2.py https://example.com/data.zip -o my_file.zip"
    )
    
    # 2. Add arguments
    parser.add_argument(
        "url",
        help="The URL of the file to download."
    )
    parser.add_argument(
        "-o", "--output",
        help="Optional: The name of the output file. (Default: inferred from URL)",
        default=None
    )
    
    # 3. Parse arguments
    args = parser.parse_args()
    
    # 4. Determine filenames
    target_url = args.url
    output_filename = get_output_filename(target_url, args.output)
    
    # 5. Run the download function
    download_with_cookies(target_url, output_filename)
