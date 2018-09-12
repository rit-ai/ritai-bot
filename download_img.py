import requests
import sys

headers = {'User-agent': 'Mozilla/5.0'}

def download_img(url, name):
    sess = requests.Session()
    r = sess.get(url, headers=headers)

    if r.status_code == 200:
        with open(name, 'wb') as f:
            for chunk in r:
                f.write(chunk)
    else:
        raise Exception('Exception: %d' % r.status_code)

def main():
    url = sys.argv[1]
    download_img(url, 'test.png')

if __name__ == '__main__':
    main()
