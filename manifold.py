from datetime import datetime
import requests

markets = []

def fetch_manifold_markets():
    last_id = None
    fetched_count = 0
    for i in range(40):
        resp = requests.get(f"https://api.manifold.markets/v0/markets?limit=1000{f'&before={last_id}' if last_id else ''}")
        events = resp.json()

        if resp.status_code == 200:

            print('Fetched events: ', len(events))
            for event in events:
                if not event.get('closeTime'):
                    # print(event.get('outcomeType'),',', event.get('question'))
                    continue
                try:
                    if datetime.fromtimestamp(event['closeTime']//1000) < datetime.now():
                        # print('Last oudated event: ', datetime.fromtimestamp(events[-1]['closeTime']//1000))
                        continue
                except Exception as e:
                    print(e)
                    continue
                # print(event['closeTime'])
                print(event.get('outcomeType'),',', event.get('question'), ',', event['closeTime'])
                # return
                markets.append(event)
    
            # pprint(events)
            last_id = events[-1]['id']


fetch_manifold_markets()

print('Total: ', len(markets))