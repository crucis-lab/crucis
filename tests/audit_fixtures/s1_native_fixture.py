"""Deterministic offline S1 process fixture, never a scientific system (DLV-09).

Line-delimited JSON protocol lets tests stop/reconnect to one native episode,
observe duplicate submissions and callback responses, and restart from a snapshot.
No network, native libraries, credentials, randomness, or hidden provider fallback.
"""
import json
import sys


def main():
    state = {'counter':0, 'actions':{}, 'callback':None}
    print(json.dumps({'event':'started'}), flush=True)
    for line in sys.stdin:
        message = json.loads(line); op = message['op']
        if op == 'restore': state = message['state']; response = {'event':'loaded', 'components':['counter','actions','callback']}
        elif op == 'observe': response = {'event':'state', 'state':state}
        elif op == 'submit':
            key = message['key']
            if key not in state['actions']:
                state['counter'] += 1; state['actions'][key] = state['counter']
            response = {'event':'acknowledged', 'receipt':state['actions'][key]}
        elif op == 'callback': response = {'event':'action_requested', 'question':message['question']}
        elif op == 'respond': state['callback'] = message['response']; response = {'event':'response_received'}
        elif op == 'checkpoint': response = {'event':'checkpoint', 'state':state}
        elif op == 'cancel': response = {'event':'cancel_acknowledged', 'stopped':False}
        elif op == 'finish':
            print(json.dumps({'event':'finished', 'counter':state['counter'], 'callback':state['callback']}), flush=True)
            break
        else: response = {'event':'unsupported'}
        print(json.dumps(response), flush=True)


if __name__ == '__main__': main()
