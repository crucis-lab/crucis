"""Scoped history invariants and exact recorded response replay (DLV-08/09).

These checks observe supplied episodes. They neither schedule retries nor choose
actions, budgets, scientific completion, or a native state restoration strategy.
"""
import copy
from dataclasses import dataclass
from decimal import Decimal

from .codec import WireError
from .model import known, number, unresolved
from .validation import Check, decimal_value


def check_history(package, report):
    from .semantics import _cycle
    records = {r['id']: r for r in package['records']}
    def get(ref, kind=None):
        r = records.get(ref.get('target')) if isinstance(ref, dict) and ref.get('binding') == 'internal' else None
        return r['payload'] if r and (kind is None or r['record_type'] == 's1.' + kind) else None
    def check(rid, name, valid, details=''):
        report.checks.append(Check(rid, 's1.' + name, 'unknown' if valid is None else 'pass' if valid else 'fail', details))
    event_edges = []; recovery_edges = []; session_edges = []; sequences = {}
    unknown_order={'event':False,'recovery':False,'session':False}
    for r in package['records']:
        rid, p, kind = r['id'], r['payload'], r['record_type']
        if kind == 's1.event':
            resolved=[x for x in p['predecessors'] if get(x,'event') is not None]
            unknown_order['event'] |= len(resolved)!=len(p['predecessors'])
            predecessors = [x['target'] for x in resolved]
            valid = len(predecessors) == len(set(predecessors)) and rid not in predecessors
            event_edges.extend((x, rid) for x in predecessors)
            seq = p['local_sequence']
            if seq['state'] == 'known':
                s = seq['value']; key = (s['producer'].get('target'), s['stream'])
                if get(s['producer'],'component') is None:
                    unknown_order['event']=True
                    check(rid,'event_links',None,'sequence producer is unresolved');continue
                position = int(s['position']); slots = sequences.setdefault(key, {})
                if position in slots: valid = False
                slots[position] = rid
            check(rid, 'event_links', valid, 'capture/native timestamps alone do not establish precedence')
        elif kind == 's1.session':
            parent = p['parent']
            if parent['state'] == 'known':
                if get(parent['value'],'session') is None:unknown_order['session']=True
                else:
                    pid = parent['value']['target']; session_edges.append((pid, rid))
                    check(rid, 'session_parent', pid != rid)
            check(rid, 'session_completion', None, 'child completion and exhausted observation do not establish parent completion')
        elif kind == 's1.recovery':
            a, b = get(p['successor'], 'attempt'), get(p['predecessor'], 'attempt')
            if a and b:recovery_edges.append((p['predecessor']['target'],p['successor']['target']))
            else:unknown_order['recovery']=True
            valid = p['successor'] != p['predecessor']
            if a and b:
                same = a['request'] == b['request']
                valid &= same == (p['request_relation'] == 'same_request')
                if p['recovery_kind'] == 'warm_start': valid &= not same
                check(rid, 'recovery_identity', valid)
            else: check(rid, 'recovery_identity', None, 'attempt/request identity unresolved')
            if p['recovery_kind'] == 'checkpoint_continuation':
                load = get(p['load'].get('value', {}), 'state_load')
                state = p['state']
                valid = None
                if load and state['state'] == 'known':
                    valid = load['attempt'] == p['successor'] and load['snapshot'] == state['value']
                    if a and a['initial_state']['state'] == 'known': valid &= a['initial_state']['value'] == state['value']
                check(rid, 'checkpoint_binding', valid, 'intent is separate from observed component restoration')
        elif kind == 's1.state_load':
            requested = p['requested_components']; observed = p['observed_components']
            names = [x['component'] for x in observed]
            valid = len(names) == len(set(names)) and len(requested) == len(set(requested))
            established = {x['component'] for x in observed if x['loaded'].get('state') == 'known'
                and x['loaded']['value'] is True and x['identity']['state'] == 'known'
                and x['availability']['state'] == 'known' and x['evidence']}
            if p['continuity'] == 'exact_within_scope': valid &= set(requested) <= established and bool(requested)
            check(rid, 'state_continuity', valid, 'exact applies only to evidenced listed components; unknown RNG/history is not exact')
        elif kind == 's1.action_request':
            authority = get(p['authority'], 'authority_evidence'); endpoint = get(p['endpoint'], 'endpoint')
            if authority and endpoint:
                action_ref = {'binding':'internal', 'target':rid, 'target_type':'s1.action_request'}
                scoped = action_ref in authority['subjects'] or p['attempt'] in authority['subjects']
                check(rid, 'action_authority', authority['decision'] == 'permitted' and scoped
                      and authority['operation'] == endpoint['operation'], 'recording a request does not grant execution')
            else: check(rid, 'action_authority', None)
            session = get(p['session'], 'session'); attempt = get(p['attempt'], 'attempt')
            check(rid, 'action_membership', session['request'] == attempt['request'] if session and attempt else None)
        elif kind == 's1.action_response':
            check(rid, 'response_correlation', get(p['request'], 'action_request') is not None)
        elif kind == 's1.cancellation':
            from .model import contract
            stop = get(p['observed_stop'].get('value', {}), 'event')
            established = (stop is not None and stop['subject'] == p['subject']
                and stop['event_contract'] == contract('native_stop') and bool(stop['source']['evidence']))
            check(rid, 'cancellation_stop', True if established else None,
                  'acknowledgment alone does not establish stop; later outputs remain admissible evidence')
        elif kind == 's1.replay':
            keys = [x['occurrence_key'] for x in p['consumed']]
            sources = [x['source_event'].get('target') for x in p['consumed']]
            valid = len(keys) == len(set(keys)) and len(sources) == len(set(sources))
            valid &= p['attempt'] != p['source_attempt']
            attempt = get(p['attempt'], 'attempt'); original = get(p['source_attempt'], 'attempt')
            if attempt: valid &= attempt['request'] == p['request']
            if original: valid &= original['request'] != p['request']
            for match in p['consumed']:
                response = get(match['response'], 'action_response')
                valid &= response is not None and response['request'] == match['action']
                action=get(match['action'],'action_request')
                valid &= action is not None and action['attempt']==p['attempt']
            check(rid, 'replay_occurrences', valid, 'no implicit response reuse or fresh-provider fallback')
        elif kind == 's1.accounting':
            check(rid, 'accounting_aggregation', None if p['coverage'] != 'disjoint_members' else True,
                  'inclusive/overlapping totals cannot be added to children; aggregation needs explicit membership')
    for slots in sequences.values():
        order = [slots[k] for k in sorted(slots)]
        event_edges.extend(zip(order, order[1:]))
    # Only episode/history edges are constrained here, never native causal links.
    for kind, edges, name in [('event', event_edges, 'event_precedence'),
                               ('recovery', recovery_edges, 'recovery_ancestry'),
                               ('session', session_edges, 'session_ancestry')]:
        cyclic = _cycle(edges)
        for r in package['records']:
            if r['record_type'] == 's1.' + kind:check(r['id'],name,False if cyclic else None if unknown_order[kind] else True)
    return report


def native_action_count(package, transmissions):
    """A narrowly named idempotent-receipt contract; ordinary acks cannot deduplicate."""
    records = {r['id']:r for r in package['records']}; receipts = {}
    for ref in transmissions:
        r = records.get(ref.get('target'))
        if not r or r['record_type'] != 's1.transmission': raise WireError('transmission reference required')
        p = r['payload']; receipt = p['native_receipt']
        from .model import contract
        if (p['transport'] != contract('idempotent_receipt') or p['outcome'] != 'acknowledged'
                or receipt['state'] != 'known' or not receipt['value']['source']['evidence']):
            return unresolved('s1.unresolved_native_multiplicity', transmissions)
        native = receipt['value']; key = (native['authority'], native['namespace'], native['native_id'])
        if key in receipts and receipts[key] != p['message']:
            return unresolved('s1.unresolved_native_multiplicity', transmissions)
        receipts[key] = p['message']
    return known(number(len(receipts)), transmissions)


def accounting_total(package, accounting_refs):
    """Explicit disjoint sum with exact units/statistic identity and no restart reset."""
    from fractions import Fraction
    from .model import contract
    if not accounting_refs:return unresolved('s1.unresolved_usage')
    records = {r['id']:r for r in package['records']}; covered = set(); signature = None; total = Fraction(0)
    for ref in accounting_refs:
        r = records.get(ref.get('target'))
        if not r or r['record_type'] != 's1.accounting': raise WireError('accounting reference required')
        p = r['payload']
        if p['aggregation'] != contract('disjoint_sum') or p['coverage'] != 'disjoint_members' or p['revised']:
            raise WireError('only explicitly selected unrevised disjoint sums are supported')
        members = [x.get('target') for x in p['members']]
        if not members or len(members) != len(set(members)) or covered.intersection(members):
            raise WireError('empty, repeated or overlapping accounting membership')
        covered.update(members)
        if len(p['quantities']) != 1: raise WireError('one explicitly selected quantity per accounting entry required')
        q = records.get(p['quantities'][0].get('target'))
        if q is None:return unresolved('s1.unresolved_usage',accounting_refs)
        if q['record_type'] != 's1.output' or q['payload']['output_type'] != 'quantity': raise WireError('quantity output required')
        body = q['payload']['body']; v = body['value']
        if v.get('state') != 'known' or body['units']['state'] != 'known' or body['associated_rule']['state'] != 'known':
            return unresolved('s1.unresolved_usage', accounting_refs)
        sig = (body['quantity_kind'], body['units'], body['associated_rule'])
        if signature is not None and sig != signature: raise WireError('different units, measurement or resource kinds cannot be summed')
        signature = sig
        if body['quantity_kind'] == 's1.duration': raise WireError('elapsed durations require an explicit interval-union procedure')
        n = decimal_value(v['value'])
        if not n.is_finite() or n < 0: raise WireError('invalid resource quantity')
        total += Fraction(n)
    # Exact finite decimals only. No Decimal-context rounding on cumulative costs.
    numerator, denominator = total.numerator, total.denominator
    twos = fives = 0
    while denominator % 2 == 0: denominator //= 2; twos += 1
    while denominator % 5 == 0: denominator //= 5; fives += 1
    if denominator != 1: raise WireError('sum has no finite decimal representation')
    digits = max(twos, fives); scaled = numerator * 2**(digits-twos) * 5**(digits-fives)
    text = str(scaled).rjust(digits+1, '0')
    if digits: text = text[:-digits] + '.' + text[-digits:]
    return known(number(text), accounting_refs)


@dataclass(frozen=True)
class ReplayEntry:
    occurrence_key: str
    request: bytes
    context: dict
    response: bytes


class ReplayExhausted(WireError): pass


class RecordedReplay:
    """Ordered exact-byte/context replay. There is deliberately no fallback callback."""
    def __init__(self, entries, exhaustion='stop'):
        if exhaustion not in ('stop', 'return_unresolved'): raise WireError('unsupported exhaustion rule')
        self.entries = tuple(copy.deepcopy(entries)); self.position = 0; self.exhaustion = exhaustion
        keys = [e.occurrence_key for e in self.entries]
        if len(keys) != len(set(keys)): raise WireError('replay occurrence keys must be unique')
    def respond(self, request, context, occurrence_key):
        if self.position >= len(self.entries):
            if self.exhaustion == 'return_unresolved': return unresolved('s1.replay_exhausted')
            raise ReplayExhausted('recorded transcript exhausted')
        entry = self.entries[self.position]
        if entry.request != bytes(request) or entry.context != context or entry.occurrence_key != occurrence_key:
            raise ReplayExhausted('exact recorded occurrence did not match; cursor unchanged')
        self.position += 1
        return entry.response
