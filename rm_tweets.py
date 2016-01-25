"""
Your Twitter archiveのcsvファイルから全tweetsを削除します。

CSVファイルはAccount SettingsのYour Twitter archiveから取得する。
他のファイルフォーマットはサポートしていません。
https://twitter.com/settings/account
"""

__author__ = 'PyYoshi'

import argparse
import csv
import os
import pickle
import sys
import time
import webbrowser
from datetime import datetime
from tweepy import OAuthHandler, API, TweepError

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
CREDENTIALS_FILE = './.credentials.pickle'


def get_auth():
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    if not os.path.exists(CREDENTIALS_FILE):
        authorization_url = auth.get_authorization_url()
        webbrowser.open_new(authorization_url)
        pin = input('PIN: ')
        auth.get_access_token(pin)
        cred = {
            'ACCESS_TOKEN': auth.access_token,
            'ACCESS_SECRET': auth.access_token_secret
        }
        fp = open(CREDENTIALS_FILE, 'wb')
        pickle.dump(cred, fp)
        fp.close()
    else:
        fp = open(CREDENTIALS_FILE, 'rb')
        cred = pickle.load(fp)
        fp.close()
        auth.set_access_token(cred['ACCESS_TOKEN'], cred['ACCESS_SECRET'])
    return auth


def read_timestamp(timestamp):
    return datetime.strptime(timestamp[:-6], '%Y-%m-%d %H:%M:%S')


def delete_tweets(tw, reader, timestamp):
    if timestamp is not None: timestamp = datetime.fromtimestamp(timestamp)
    for row in reader:
        if timestamp:
            dt = read_timestamp(row['timestamp'])
            if timestamp < dt: continue
        print('ステータス id: %s, text: %s を削除します。' % (row['tweet_id'], row['text'].replace('\n', '')))
        try:
            status = tw.destroy_status(int(row['tweet_id']))
        except TweepError as e:
            if e.response.msg.get('status') == '404 Not Found':
                print('すでにそのステータスは存在しないためスキップします。')
            else:
                print('APIエラーが発生しました。60秒後にリトライします。')
                time.sleep(60)
                print('ステータス id: %s, text: %s を削除します。' % (
                    row['tweet_id'].decode('utf8'), row['text'].decode('utf8').replace('\n', '')))
                status = tw.destroy_status(int(row['tweet_id']))


def main():
    try:
        # スクリプトの引数処理
        parser = argparse.ArgumentParser(description='Your Twitter archiveのcsvファイルから全tweetsを削除します。')
        parser.add_argument('--timestamp', dest='timestamp', type=int, help='unixtime形式。指定した場合それ以前のtweetsを削除します。', )
        parser.add_argument('--filepath', dest='filepath', type=str, help='Your Twitter archiveのCSVパス。')
        args = parser.parse_args()
        if args.filepath == None:
            parser.print_help()
            sys.exit()
        # Twitter認証等
        auth = get_auth()
        tw = API(auth)
        # tweets削除処理
        with open(args.filepath) as csvfile:
            tweetsReader = csv.DictReader(csvfile, delimiter=',')
            delete_tweets(tw, tweetsReader, args.timestamp)
    except KeyboardInterrupt:
        sys.exit()


if __name__ in '__main__':
    sys.exit(main())
