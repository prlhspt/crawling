import requests
import json
from bs4 import BeautifulSoup as bs

def get_follow_ids(user_id, username, cursor=-1):
    headers = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'Referer': 'https://twitter.com/TheMFDS',
        'x-twitter-client-language': 'en',
        'x-csrf-token': 'ca76299ced1162cbf3c1a1d8942268cd',
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-active-user': 'yes',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    }

    params = (
        ('include_profile_interstitial_type', '1'),
        ('include_blocking', '1'),
        ('include_blocked_by', '1'),
        ('include_followed_by', '1'),
        ('include_want_retweets', '1'),
        ('include_mute_edge', '1'),
        ('include_can_dm', '1'),
        ('include_can_media_tag', '1'),
        ('skip_status', '1'),
        ('cursor', '-1'),
        ('user_id', '138347667'),
        ('count', '5000'),
        ('with_total_count', 'true'),
    )

    response = requests.get('https://api.twitter.com/1.1/friends/following/list.json', headers=headers, params=params)
    return response.json()


def get_follow_all(user_id, username, user_follow_count=None):
    cursor = -1
    dataset = []

    while cursor != 0:  # 커서가 0이면 다음페이지가 없다.
        data = get_follow_ids(user_id, username, cursor)
        try:
            cursor = data['next_cursor']
        except KeyError as e:
            print(data)
            if data.get('error') and data['error'] == 'Not authorized.':
                open(f"protected/{user_id}", 'w').close()
                print(username, "Protected")
                return
            if data.get('errors') and data['errors'][0]['code'] == 34:
                open(f"deleted/{user_id}", 'w').close()
                print(username, "Does Not exist")
                return
            print('=' * 50)
            print('Username:', username, 'User_id', user_id)
            print(data)
            print('=' * 50)
            raise e
        dataset += data['ids']
        print(f'{username}({user_id}): {len(set(dataset))} / {user_follow_count}', end='\r')
    dataset = list(set(dataset))
    json.dump(dataset, open(f'success/{user_id}.json', 'w+'))
    print(f'# Final for USER [{username}({user_id})]: {len(dataset)} / {user_follow_count}')