import json

if __name__ == '__main__':

    with open('wocka.json', 'r') as f:
        wocka = f.read()

    parsed_wocka = json.loads(wocka)
    samples = []

    for item in parsed_wocka:
        liner = item['body']
        samples.append(liner)

    sample_string = ' '.join(samples).strip('\r\n\t')

    with open('wocka_raw.txt', 'w') as out:
        out.write(sample_string)
