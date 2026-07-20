import urllib.request, urllib.parse, re
dish = 'Spaghetti Bolognese'
url = f'https://www.google.com/search?tbm=isch&q={urllib.parse.quote(dish)}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    match = re.search(r'<img.*?src=\"(https://encrypted-tbn0\.gstatic\.com/images[^\"]+)\"', html)
    if match:
        print('URL:', match.group(1))
    else:
        print('No image found')
except Exception as e:
    print('Error:', e)
