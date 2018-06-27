from baseaaapi import BaseAAAPI
from twittle import Twittle
from kotorpc import KotoRpc
import re
import random
import string
import sqlite3
from decimal import Decimal
import hashlib
from time import sleep, time

class TipKoto(BaseAAAPI):

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, rpc_user, rpc_password, rpc_port = '8432'):
        self.twitter = Twittle(consumer_key, consumer_secret, access_token, access_token_secret)
        self.koto = KotoRpc(rpc_user, rpc_password, rpc_port)
        self.database_init()

    def database_init(self):
        database = sqlite3.connect('USERS_DATABASE', timeout = 30)
        db = database.cursor()
        db.execute('create table if not exists users (user_id text, address text)')
        database.commit()
        database.close()

        database = sqlite3.connect('TRANSACTIONS_DATABASE', timeout = 30)
        db = database.cursor()
        db.execute('create table if not exists transactions (from_address text, transaction_hash text)')
        database.commit()
        database.close()

    def tweet_create_events(self, data):
        text = data['tweet_create_events'][0]['text']
        user_id = data['tweet_create_events'][0]['user']['id_str']
        name = data['tweet_create_events'][0]['user']['name']
        screen_name = data['tweet_create_events'][0]['user']['screen_name']
        status_id = data['tweet_create_events'][0]['id_str']

        if screen_name != 'tipkotone' and not re.findall('(^RT |^QT | RT | QT )', text):
            reply_message = self.execute(text, user_id, name, screen_name, from_tweet = True)

            if reply_message is not None:
                reply_message = reply_message if len(reply_message) <= 140 else reply_message[: - (len(reply_message) - 140)]   # 140文字以下にする
                self.twitter.tweet(reply_message, status_id)

    def direct_message_events(self, data):
        if data['direct_message_events'][0]['type'] == 'message_create':
            text = '@tipkotone ' + data['direct_message_events'][0]['message_create']['message_data']['text']
            user_id = data['direct_message_events'][0]['message_create']['sender_id']
            name = data['users'][user_id]['name']
            screen_name = data['users'][user_id]['screen_name']

            if screen_name != 'tipkotone':
                reply_message = self.execute(text, user_id, name, screen_name, from_tweet = False)

                if reply_message is not None:
                    self.twitter.dm(reply_message, user_id)

    def execute(self, text, user_id, name, screen_name, from_tweet = None):
        command = self.get_command(text)

        if command[0] in ['tip', '投げ銭', '投銭', 'send', '送金']:
            if len(command) >= 3:
                if command[1].startswith('@'):
                    to_screen_name = command[1][1:]

                    response = self.twitter.user(to_screen_name)
                    if response.status_code == 200:
                        to_user = response.json()
                        to_user_id = to_user['id_str']
                        to_name = to_user['name']

                        if self.is_amount(command[2]):
                            from_address = self.get_address(user_id)
                            to_address = self.get_address(to_user_id)
                            amount = command[2].lower() if command[2].lower() in ['all', '全額'] else Decimal(self.round_down(command[2]))

                            result = self.send_koto(from_address, to_address, amount)

                            if result['status'] == 'success':
                                if to_screen_name != 'tipkotone':
                                    reply_message = '\n'.join(['{name}さんから {to_name}さんへ お心付けです！ {amount}KOTO'.format(name = name, to_name = to_name, amount = result['amount']),
                                                               '',
                                                               self.get_random_string()])

                                else:
                                    reply_message = '\n'.join(['{name}さんから {amount}KOTO いただきました！ ありがとうございます！'.format(name = name, amount = result['amount']),
                                                               '',
                                                               self.get_random_string()])

                            elif result['status'] == 'failed':
                                reply_message = '\n'.join(['失敗しました・・・',
                                                           '',
                                                           self.get_random_string()])

                            elif result['status'] == 'cancelled':
                                reply_message = '\n'.join(['キャンセルされました・・・',
                                                           '',
                                                           self.get_random_string()])

                            elif result['status'] == 'insufficient':
                                reply_message = '\n'.join(['残高不足です・・・ {balance}KOTO (+{confirming_balance} 承認中)'.format(balance = result['balance'], confirming_balance = result['confirming_balance']),
                                                           '',
                                                           self.get_random_string()])

                            elif result['status'] == 'dust':
                                reply_message = '\n'.join(['この金額では投げ銭できません・・・',
                                                           '',
                                                           self.get_random_string()])

                            elif result['status'] == 'timeout':
                                reply_message = '\n'.join(['待ち時間が長すぎたので中断されました・・・',
                                                           '',
                                                           self.get_random_string()])

                        else:
                            reply_message = '\n'.join(['金額が正しくありません・・・',
                                                       '',
                                                       self.get_random_string()])

                    else:
                        reply_message = '\n'.join(['宛先が見つかりませんでした・・・',
                                                   '',
                                                   self.get_random_string()])

                else:
                    reply_message = '\n'.join(['宛先が正しくありません・・・',
                                               '',
                                               self.get_random_string()])

            else:
                reply_message = '\n'.join(['tipkotoneの使い方はこちらです！ https://github.com/akarinS/aaapi-tipkoto/blob/master/doc/HowToUse.md',
                                           '',
                                           self.get_random_string()])

            if from_tweet:
                if result['status'] == 'success' and to_screen_name != 'tipkotone':
                    reply_message = '@{screen_name} @{to_screen_name} {reply_message}'.format(screen_name = screen_name, to_screen_name = to_screen_name, reply_message = reply_message)

                else:
                    reply_message = '@{screen_name} {reply_message}'.format(screen_name = screen_name, reply_message = reply_message)

            return reply_message

        elif command[0] in ['balance', '残高']:
            address = self.get_address(user_id)
            balance, confirming_balance = self.get_balance(address)

            if confirming_balance == 0:
                reply_message = '\n'.join(['{name}さんの残高は {balance}KOTO です！'.format(name = name, balance = balance),
                                           '',
                                           self.get_random_string()])

            else:
                reply_message = '\n'.join(['{name}さんの残高は {balance}KOTO (+{confirming_balance}KOTO 承認中) です！'.format(name = name, balance = balance, confirming_balance = confirming_balance),
                                           '',
                                           self.get_random_string()])

            if from_tweet:
                reply_message = '@{screen_name} {reply_message}'.format(screen_name = screen_name, reply_message = reply_message)

            return reply_message

        elif command[0] in ['deposit', '入金', 'address', 'アドレス']:
            address = self.get_address(user_id)

            reply_message = '\n'.join(['こちらに送金してください！',
                                       '{address}'.format(address = address),
                                       '',
                                       self.get_random_string()])

            if from_tweet:
                reply_message = '@{screen_name} {reply_message}'.format(screen_name = screen_name, reply_message = reply_message)

            return reply_message

        elif command[0] in ['withdraw', '出金']:
            if len(command) >= 3:
                if self.is_address(command[1]):
                    to_address = command[1]

                    if self.is_amount(command[2]):
                        from_address = self.get_address(user_id)
                        amount = command[2].lower() if command[2].lower() in ['all', '全額'] else Decimal(self.round_down(command[2]))

                        result = self.send_koto(from_address, to_address, amount)

                        if result['status'] == 'success':
                            reply_message = '\n'.join(['{amount}KOTO を {to_address} に出金しました！'.format(amount = result['amount'], to_address = to_address),
                                                       '',
                                                       'txid: {txid}'.format(txid = result['txid'])])

                        elif result['status'] == 'failed':
                            reply_message = '\n'.join(['失敗しました・・・',
                                                       '',
                                                       self.get_random_string()])

                        elif result['status'] == 'cancelled':
                            reply_message = '\n'.join(['キャンセルされました・・・',
                                                       '',
                                                       self.get_random_string()])

                        elif result['status'] == 'insufficient':
                            reply_message = '\n'.join(['残高不足です・・・ {balance}KOTO (+{confirming_balance} 承認中)'.format(balance = result['balance'], confirming_balance = result['confirming_balance']),
                                                       '',
                                                       self.get_random_string()])

                        elif result['status'] == 'dust':
                            reply_message = '\n'.join(['この金額では出金できません・・・',
                                                       '',
                                                       self.get_random_string()])

                        elif result['status'] == 'timeout':
                            reply_message = '\n'.join(['待ち時間が長すぎたので中断されました・・・',
                                                       '',
                                                       self.get_random_string()])

                    else:
                        reply_message = '\n'.join(['金額が正しくありません・・・',
                                                   '',
                                                   self.get_random_string()])

                else:
                    reply_message = '\n'.join(['アドレスが正しくありません・・・',
                                               '',
                                               self.get_random_string()])
            else:
                reply_message = '\n'.join(['tipkotoneの使い方はこちらです！ https://github.com/akarinS/aaapi-tipkoto/blob/master/doc/HowToUse.md',
                                           '',
                                           self.get_random_string()])

            if from_tweet:
                reply_message = '@{screen_name} {reply_message}'.format(screen_name = screen_name, reply_message = reply_message)

            return reply_message

        elif command[0] in ['followme', 'フォローミー', 'フォローして']:
            self.twitter.follow(user_id)

            reply_message = '\n'.join(['フォローしました！',
                                       '',
                                       self.get_random_string()])

            if from_tweet:
                reply_message = '@{screen_name} {reply_message}'.format(screen_name = screen_name, reply_message = reply_message)

            return reply_message

        elif command[0] in ['help', 'ヘルプ']:
            reply_message = '\n'.join(['tipkotoneの使い方はこちらです！ https://github.com/akarinS/aaapi-tipkoto/blob/master/doc/HowToUse.md',
                                       '',
                                       self.get_random_string()])

            return reply_message

        return None

    def get_command(self, text):
        text = re.sub(' +', ' ', re.sub('(\n+|　+)', ' ', text))
        words = text.split(' ')

        while '@tipkotone' in words:
            words = words[words.index('@tipkotone') + 1:]
            command = words
            command[0] = command[0].lower()

            if command[0] in ['tip', '投げ銭', '投銭',
                              'send', '送金',
                              'balance', '残高',
                              'deposit', '入金',
                              'address', 'アドレス',
                              'withdraw', '出金',
                              'followme', 'フォローミー', 'フォローして',
                              'help', 'ヘルプ']:
                return command

            elif command[0].startswith('残高'):     # '残高教えて'のような文に対応
                return ['残高']

            elif command[0].startswith('入金'):     # '入金したい'のような文に対応
                return ['入金']

        return [None]

    def get_address(self, user_id):
        user_id = 'twitter-tipkotone-' + user_id

        database = sqlite3.connect('USERS_DATABASE', timeout = 30)
        db = database.cursor()
        result = db.execute('select address from users where user_id = ?', (user_id,)).fetchone()
        database.close()

        if result is not None:
            address = result[0]

        else:
            address = self.create_address(user_id)

        return address

    def create_address(self, user_id):
        address = self.koto.call('getnewaddress')

        database = sqlite3.connect('USERS_DATABASE', timeout = 30)
        db = database.cursor()
        db.execute('insert into users (user_id, address) values (?, ?)', (user_id, address))
        database.commit()

        # 同時にこの関数が呼ばれても同じアドレスを使うために、最初に登録されたアドレスを取り出す。
        address = db.execute('select address from users where user_id = ?', (user_id,)).fetchone()[0]
        database.close()

        return address

    def get_balance(self, address):
        balance = Decimal(str(self.koto.call('z_getbalance', address)))
        confirming_balance = Decimal(str(self.koto.call('z_getbalance', address, 0))) - balance

        return (balance, confirming_balance)

    def is_address(self, arg):
        if arg.startswith('k1') or arg.startswith('k3') or arg.startswith('jz'):
            if len(arg) == 35:
                return True

        return False

    def is_amount(self, arg):
        if arg.lower() in ['all', '全額']:
            return True

        try:
            float(arg)

        except ValueError:
            return False

        if 'e' in arg.lower():
            return False

        return True

    def round_down(self, amount_str):
        if '.' in amount_str:
            return amount_str[:(amount_str.index('.') + 1) + 8]

        return amount_str

    def send_koto(self, from_address, to_address, amount):
        transaction_hash = hashlib.sha256(self.get_random_string(64).encode()).hexdigest()

        database = sqlite3.connect('TRANSACTIONS_DATABASE', timeout = 30)
        db = database.cursor()
        db.execute('insert into transactions (from_address, transaction_hash) values (?, ?)', (from_address, transaction_hash))
        database.commit()

        time_limit = time() + 3600  # 1時間
        try:
            while True:
                if time() > time_limit:
                    raise Exception

                head_transaction_hash = db.execute('select transaction_hash from transactions where from_address = ?', (from_address,)).fetchone()[0]

                if transaction_hash == head_transaction_hash:
                    break

                sleep(10)

            fee = Decimal('0.0001')
            while True:
                if time() > time_limit:
                    raise Exception

                balance, confirming_balance = self.get_balance(from_address)

                if amount not in ['all', '全額'] and balance + confirming_balance < amount + fee:
                    result = {'status': 'insufficient',
                              'balance': balance,
                              'confirming_balance': confirming_balance}

                else:
                    if amount in ['all', '全額']:
                        amount = balance - fee
                        change = 0

                    elif balance >= amount + fee:
                        change = balance - amount - fee

                    else:
                        sleep(10)
                        continue

                    amount_limit = Decimal('5.4e-7')
                    if amount < amount_limit or 0 < change < amount_limit:
                        result = {'status': 'dust'}
                        break

                    params = self.get_params(from_address, to_address, amount, balance, change)
                    opid = self.koto.call('z_sendmany', *params)

                    while True:
                        if time() > time_limit:
                            raise Exception

                        op_status = self.koto.call('z_getoperationstatus', [opid])

                        if len(op_status) != 0 and op_status[0]['status'] in ['success', 'failed', 'cancelled']:
                            if op_status[0]['status'] == 'success':
                                result = {'status': 'success',
                                          'amount': amount,
                                          'txid': op_status[0]['result']['txid']}

                            elif op_status[0]['status'] == 'failed':
                                result = {'status': 'failed'}

                            elif op_status[0]['status'] == 'cancelled':
                                result = {'status': 'cancelled'}

                            break

                        sleep(5)

                break

        except:
            result = {'status': 'timeout'}

        finally:
            db.execute('delete from transactions where transaction_hash = ?', (transaction_hash,))
            database.commit()
            database.close()

        return result

    def get_params(self, from_address, to_address, amount, balance, change):
        if change == 0:
            params = (from_address,
                      [{'address': to_address, 'amount': float(amount)}])

        else:
            params = (from_address,
                      [{'address': to_address, 'amount': float(amount)},
                       {'address': from_address, 'amount': float(change)}])

        return params

    def get_random_string(self, length = 8):
        return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(length)])

