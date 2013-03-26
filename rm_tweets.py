# -*- coding:utf8 -*-
"""
Your Twitter archiveのcsvファイルから全tweetsを削除します。

CSVファイルはAccount SettingsのYour Twitter archiveから取得する。
他のファイルフォーマットはサポートしていません。
https://twitter.com/settings/account
"""

__author__ = 'PyYoshi'

import csv
import argparse
from datetime import datetime
import sys
import os
import pickle
import webbrowser
import time

# pip install -U tweepy
from tweepy import OAuthHandler, API, TweepError

#
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
        CRED_OBJ = {
            'ACCESS_TOKEN': auth.access_token.key,
            'ACCESS_SECRET': auth.access_token.secret
        }
        fp = open(CREDENTIALS_FILE,'wb')
        pickle.dump(CRED_OBJ, fp)
        fp.close()
    else:
        fp = open(CREDENTIALS_FILE,'rb')
        CRED_OBJ = pickle.load(fp)
        fp.close()
        auth.set_access_token(CRED_OBJ['ACCESS_TOKEN'], CRED_OBJ['ACCESS_SECRET'])
    return auth

def read_timestamp(timestamp):
    return datetime.strptime(timestamp[:-6], '%Y-%m-%d %H:%M:%S')

def delete_tweets(tw, reader, timestamp):
    if timestamp != None: timestamp = datetime.fromtimestamp(timestamp)
    for row in reader:
        if timestamp:
            dt = read_timestamp(row['timestamp'])
            if timestamp < dt: continue
        print(u'ステータス id: %s, text: %s を削除します。' %(row['tweet_id'].decode('utf8'), row['text'].decode('utf8').replace('\n', '')))
        try:
            status = tw.destroy_status(int(row['tweet_id']))
        except TweepError as e:
            if e.response.msg.get('status') == '404 Not Found':
                print(u'すでにそのステータスは存在しないためスキップします。')
            else:
                print(u'APIエラーが発生しました。60秒後にリトライします。')
                time.sleep(60)
                print(u'ステータス id: %s, text: %s を削除します。' %(row['tweet_id'].decode('utf8'), row['text'].decode('utf8').replace('\n', '')))
                status = tw.destroy_status(int(row['tweet_id']))

def main():
    try:
        # スクリプトの引数処理
        parser = argparse.ArgumentParser(description=u'Your Twitter archiveのcsvファイルから全tweetsを削除します。')
        parser.add_argument('--timestamp',dest='timestamp',type=int, help=u'unixtime形式。指定した場合それ以前のtweetsを削除します。',)
        parser.add_argument('--filepath',dest='filepath', type=str, help=u'Your Twitter archiveのCSVパス。')
        args = parser.parse_args()
        if args.filepath == None:
            parser.print_help()
            sys.exit()
        # Twitter認証等
        auth = get_auth()
        tw = API(auth)
        # tweets削除処理
        tweetsReader = csv.DictReader(open(args.filepath,'rb'), delimiter=',')
        delete_tweets(tw, tweetsReader, args.timestamp)
    except KeyboardInterrupt:
        sys.exit()

if __name__ in '__main__':
    sys.exit(main())

