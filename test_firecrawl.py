#!/usr/bin/env python3
import os
import sys
import re

# Add parent to path
sys.path.insert(0, '/home/diego/Documentos/picklepicker')

os.environ['FIRECRAWL_API_KEY'] = 'fc-f204c48a130b443aa773fee19680934b'

from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.environ['FIRECRAWL_API_KEY'])

# Test search endpoint
print('Testing Firecrawl search endpoint...')
query = 'site:brazilpickleballstore.com.br raquete pickleball'

result = app.search(query)

print('Result type:', type(result))
print('Result:', result)

# Check for web results
if hasattr(result, 'web'):
    web_results = result.web
    print(f'\nFound {len(web_results)} web results')

    # Filter for product URLs
    product_urls = [r for r in web_results if '/produtos/' in r.url.lower()]
    print(f'\nProduct URLs: {len(product_urls)}')

    for item in product_urls[:3]:
        print(f'\nTitle: {item.title}')
        print(f'URL: {item.url}')

        # Try to scrape this product page
        print('  Scraping product page for image...')
        try:
            product_result = app.scrape(item.url)
            if hasattr(product_result, 'markdown'):
                md = product_result.markdown
                # Look for image URLs
                img_pattern = r'(https?://[^\s\)]+\.mitiendanube\.com[^\s\)]*\.(?:jpg|jpeg|png|webp))'
                matches = re.findall(img_pattern, md, re.IGNORECASE)
                if matches:
                    print(f'  Found {len(matches)} images:')
                    for img in matches[:2]:
                        print(f'    - {img[:80]}...')
                else:
                    print('  No images found in markdown')
            else:
                print('  No markdown found')
        except Exception as e:
            print(f'  Error scraping: {e}')
