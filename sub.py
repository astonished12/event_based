from settings import channel, r
import sys

if __name__ == '__main__':
    pubsub = r.pubsub()
    pubsub.subscribe(channel)

    print('Listening to {channel}'.format(**locals()))
    while True:
        for item in pubsub.listen():
            print(item['data'])
