import json

if __name__ == '__main__':

    with open('wocka.json', 'r') as f:
        wocka = f.read()

    parsed_wocka = json.loads(wocka)
    one_liners = []

    for item in parsed_wocka:
        if item['category'] == 'One Liners':
            liner = item['body'].replace('\n', ' ')
            one_liners.append(liner)

    one_liner_string = '\n'.join(one_liners)

    with open('wocka_raw.txt', 'w') as out:
        out.write(one_liner_string)
