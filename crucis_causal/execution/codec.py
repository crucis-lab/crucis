"""Bounded strict bytes, immutable pins and explicit resolution (DLV-08/09)."""
import base64
import copy
import datetime
import json
import re
from decimal import Decimal
from functools import lru_cache
from jsonschema import Draft202012Validator
from .api import Limits, PinnedView, ReadCapability, supplied_read
from .model import ExecutionError, canonical, digest, walk
from .schema import _schema, _catalog, fields, validate_binding, validate_family, validate_record

def _pairs(pairs):
    out = {}
    for key, val in pairs:
        if key in out: raise ExecutionError('s3.duplicate_property')
        out[key] = val
    return out

def _numeric(text):
    raise ExecutionError('s3.tagged_numeric_value_required')

def _depth(text, maximum):
    depth = 0; quoted = False; escaped = False
    for char in text:
        if quoted:
            if escaped: escaped = False
            elif char == '\\': escaped = True
            elif char == '"': quoted = False
        elif char == '"': quoted = True
        elif char in '[{':
            depth += 1
            if depth > maximum: raise ExecutionError('s3.depth_limit')
        elif char in ']}': depth -= 1

def check_tree(value, limits):
    refs = 0
    for path, val, depth in walk(value):
        if depth > int(limits.max_depth): raise ExecutionError('s3.depth_limit', path)
        if val is None or isinstance(val, (int, float)) and not isinstance(val, bool):
            raise ExecutionError('s3.structural_null_or_number', path)
        if isinstance(val, str):
            if any(0xD800 <= ord(c) <= 0xDFFF for c in val): raise ExecutionError('s3.invalid_unicode_scalar', path)
            if len(val.encode('utf-8')) > int(limits.max_scalar_utf8_bytes): raise ExecutionError('s3.scalar_limit', path)
        elif isinstance(val, (dict, list)):
            if len(val) > int(limits.max_collection_items): raise ExecutionError('s3.collection_limit', path)
            if isinstance(val, dict):
                for key in val:
                    if not isinstance(key, str) or any(0xD800 <= ord(c) <= 0xDFFF for c in key): raise ExecutionError('s3.invalid_property', path)
                    if len(key.encode('utf-8')) > int(limits.max_scalar_utf8_bytes): raise ExecutionError('s3.scalar_limit', path)
                if 'binding' in val and 'target_type' in val:
                    refs += 1
                    if refs > int(limits.max_total_reference_nodes): raise ExecutionError('s3.reference_count_limit', path)
        elif not isinstance(val, bool):
            raise ExecutionError('s3.non_json_runtime_object', path)

def loads(data, limits):
    if not isinstance(data, bytes): raise ExecutionError('s3.immutable_bytes_required')
    if len(data) > int(limits.max_manifest_bytes): raise ExecutionError('s3.manifest_limit')
    try:
        text = data.decode('utf-8', errors='strict')
        _depth(text, int(limits.max_depth))
        value = json.loads(text, object_pairs_hook=_pairs, parse_int=_numeric, parse_float=_numeric, parse_constant=_numeric)
        check_tree(value, limits)
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ExecutionError('s3.invalid_json_or_unicode') from exc

@lru_cache(maxsize=1)
def _validator():
    envelope = copy.deepcopy(_schema())
    # The same exact record schema is checked separately, allowing bounded
    # successful immutable-record validation reuse across history revisions.
    envelope['properties']['records']['items'] = {}
    return Draft202012Validator(envelope)

def _semantics(package):
    for path, item, _ in walk(package):
        if not isinstance(item, dict): continue
        if item.get('extent') == 'not_examined' and item.get('members'):
            raise ExecutionError('s3.unexamined_members', path)
        if item.get('kind') == 'byte_range' or item.get('selector_type') == 'byte_range':
            if int(item['end_exclusive']) < int(item['start']): raise ExecutionError('s3.invalid_byte_range', path)
        if item.get('content_form') == 'inline_base64':
            try:
                raw = base64.b64decode(item['data'], validate=True)
                if base64.b64encode(raw).decode('ascii') != item['data']: raise ValueError()
            except (ValueError, UnicodeError) as exc:
                raise ExecutionError('s3.invalid_base64', path) from exc
        if item.get('selector_type') == 'json_pointer':
            pointer = item['pointer']
            if pointer and (not pointer.startswith('/') or re.search(r'~(?![01])', pointer)):
                raise ExecutionError('s3.invalid_json_pointer', path)
        if item.get('time_type') == 'utc_instant':
            pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:[0-5]\d' + (r'\.\d+Z' if item['precision'] == 'fractional_second' else 'Z')
            try:
                if not re.fullmatch(pattern, item['value']): raise ValueError()
                datetime.datetime.fromisoformat(item['value'].replace('Z', '+00:00'))
                uncertainty = item['uncertainty_seconds']
                if uncertainty['state'] == 'known':
                    number = uncertainty['value']
                    if number['number_type'] == 'nonfinite' or Decimal(number['text']) < 0: raise ValueError()
            except (ValueError, TypeError) as exc:
                raise ExecutionError('s3.invalid_utc_time_or_uncertainty', path) from exc
    for record in package['records']:
        kind, p = record['record_type'], record['payload']
        if kind == 's3.operation_binding': validate_binding(p)
        elif kind == 's3.requirement_case': validate_family(p)
        elif kind == 's3.support_claim':
            axes = {a['axis']: a for a in p['axes']}
            allowed = _catalog()['support_axis_statuses']
            if len(axes) != len(p['axes']) or set(axes) != set(allowed): raise ExecutionError('s3.eight_unique_axes_required')
            if any(a['status'] not in allowed[k] for k, a in axes.items()): raise ExecutionError('s3.axis_status')
        elif kind == 's3.disposition':
            count = len(p['operations']['members'])
            if p['kind'] == 'selected' and count == 0 or p['kind'] == 'no_effect_selected' and count:
                raise ExecutionError('s3.disposition_cardinality')
        elif kind == 's3.delivery':
            if not p['actions']['members'] or not p['responses']['members']:
                raise ExecutionError('s3.delivery_empty_correlation')
        elif kind == 's3.resource_entry' and p['quantity']['state'] == 'known':
            value = p['quantity']['value']
            if value['number_type'] == 'nonfinite' or Decimal(value['text']) < 0:
                raise ExecutionError('s3.finite_nonnegative_quantity_required')

def validate_package(package, limits):
    check_tree(package, limits)
    if not isinstance(package, dict): raise ExecutionError('s3.package_required')
    if len(package.get('records', [])) > int(limits.max_records): raise ExecutionError('s3.record_limit')
    if len(package.get('external_packages', [])) > int(limits.max_external_packages): raise ExecutionError('s3.external_package_limit')
    error = next(_validator().iter_errors(package), None)
    if error: raise ExecutionError('s3.schema', '/' + '/'.join(map(str, error.absolute_path)))
    for i, record in enumerate(package['records']):
        try: validate_record(record)
        except ExecutionError as exc:
            raise ExecutionError(exc.code, '/records/' + str(i) + exc.path) from exc
    records = {r['id']: r for r in package['records']}
    if len(records) != len(package['records']): raise ExecutionError('s3.duplicate_record_identity')
    externals = {d['package_id']: d for d in package['external_packages']}
    if len(externals) != len(package['external_packages']) or package['package_id'] in externals:
        raise ExecutionError('s3.duplicate_or_self_dependency')
    if package['roots'][0]['binding'] != 'internal': raise ExecutionError('s3.local_root_required')
    for path, ref, _ in walk(package):
        if not isinstance(ref, dict): continue
        if ref.get('binding') == 'internal':
            target = records.get(ref['target'])
            if target is None or target['record_type'] != ref['target_type']: raise ExecutionError('s3.reference_target', path)
        elif ref.get('binding') == 'external' and ref['package_id'] not in externals:
            raise ExecutionError('s3.undeclared_external_package', path)
    _semantics(package)
    return package

def dumps(package, limits):
    validate_package(package, limits)
    raw = canonical(package)
    if len(raw) > int(limits.max_manifest_bytes): raise ExecutionError('s3.manifest_limit')
    return raw

def _parse_snapshot_uncached(data, limits, *, access=None):
    # S1/S2 retain their own exact codecs. The initial format peek never repairs.
    from crucis_causal.connections.codec import loads as peek
    if not isinstance(data, bytes) or len(data) > int(limits.max_manifest_bytes): raise ExecutionError('s3.manifest_limit')
    try:
        _depth(data.decode('utf-8'), int(limits.max_depth))
        p = peek(data)
        name = p.get('format', {}).get('name')
        if name == 's3.account_package':
            p = validate_package(loads(data, limits), limits)
        elif name in ('s1.connection_package', 's2.experiment_package'):
            from crucis_causal.experiments import ReaderLimits
            from crucis_causal.experiments.resolver import parse_snapshot as parse_prior
            prior = parse_prior(data, ReaderLimits(limits.max_manifest_bytes, limits.max_records,
                limits.max_external_packages, limits.max_external_bytes, limits.max_reference_depth, limits.max_depth))
            p = prior.package
        else: raise ExecutionError('s3.unsupported_package_contract')
    except ExecutionError: raise
    except (ValueError, TypeError, AttributeError, RecursionError, UnicodeError) as exc:
        raise ExecutionError('s3.invalid_supplied_snapshot') from exc
    cap = supplied_read([p['package_id']]) if access is None else access
    if not isinstance(cap, ReadCapability) or not cap.permits(p['package_id']): raise ExecutionError('s3.read_denied')
    return PinnedView(p['package_id'], copy.deepcopy(p['format']), digest(data), data, cap)


# Cache only successful immutable-byte validation, bounded by retained key bytes.
# No decoded mutable record, read capability, native handle or authorization is
# cached. Exact reader limits are part of the key; access is checked every time.
from collections import OrderedDict
import threading
_VALIDATED = OrderedDict()
_VALIDATED_LOCK = threading.RLock()
_VALIDATED_BYTES = 0
_VALIDATED_MAX_BYTES = 67108864


def parse_snapshot(data, limits, *, access=None):
    global _VALIDATED_BYTES
    if not isinstance(data, bytes) or len(data) > int(limits.max_manifest_bytes):
        raise ExecutionError('s3.manifest_limit')
    cache_key = (data, limits)
    with _VALIDATED_LOCK:
        metadata = _VALIDATED.get(cache_key)
        if metadata is not None: _VALIDATED.move_to_end(cache_key)
    if metadata is None:
        view = _parse_snapshot_uncached(data, limits, access=access)
        metadata = (view.package_id, copy.deepcopy(view.format), copy.deepcopy(view.digest))
        if len(data) <= _VALIDATED_MAX_BYTES:
            with _VALIDATED_LOCK:
                if cache_key not in _VALIDATED:
                    while _VALIDATED and _VALIDATED_BYTES + len(data) > _VALIDATED_MAX_BYTES:
                        removed, _ = _VALIDATED.popitem(last=False)
                        _VALIDATED_BYTES -= len(removed[0])
                    _VALIDATED[cache_key] = metadata
                    _VALIDATED_BYTES += len(data)
    pid, format_contract, content_digest = metadata
    cap = supplied_read([pid]) if access is None else access
    if not isinstance(cap, ReadCapability) or not cap.permits(pid): raise ExecutionError('s3.read_denied')
    return PinnedView(pid, copy.deepcopy(format_contract), copy.deepcopy(content_digest), data, cap)

class _ImmutableDict(dict):
    def _immutable(self, *args, **kwargs): raise TypeError('private immutable snapshot index')
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _immutable
    def __deepcopy__(self, memo):
        return {copy.deepcopy(k, memo): copy.deepcopy(v, memo) for k, v in self.items()}

class _ImmutableList(list):
    def _immutable(self, *args, **kwargs): raise TypeError('private immutable snapshot index')
    __setitem__ = __delitem__ = append = extend = insert = pop = remove = clear = reverse = sort = __iadd__ = __imul__ = _immutable
    def __deepcopy__(self, memo): return [copy.deepcopy(v, memo) for v in self]

def _immutable_tree(value):
    if isinstance(value, dict): return _ImmutableDict((k, _immutable_tree(v)) for k, v in value.items())
    if isinstance(value, list): return _ImmutableList(_immutable_tree(v) for v in value)
    return value

_INDEXES = OrderedDict()
_INDEX_LOCK = threading.RLock()
_INDEX_BYTES = 0
_INDEX_MAX_BYTES = 33554432

def _snapshot_index(data):
    # Caller has already validated exact bytes/limits and the supplied read cap.
    # Only immutable JSON and immutable canonical bytes are shared, never rights.
    global _INDEX_BYTES
    with _INDEX_LOCK:
        indexed = _INDEXES.get(data)
        if indexed is not None:
            _INDEXES.move_to_end(data)
            return indexed
    package = _immutable_tree(json.loads(data))
    signatures = _ImmutableDict((r['id'], canonical(r)) for r in package['records'])
    references = tuple(ref for _, ref, _ in walk(package) if isinstance(ref, dict) and 'binding' in ref and 'target_type' in ref)
    indexed = (package, signatures, references)
    if len(data) <= _INDEX_MAX_BYTES:
        with _INDEX_LOCK:
            if data not in _INDEXES:
                while _INDEXES and (_INDEX_BYTES + len(data) > _INDEX_MAX_BYTES or len(_INDEXES) >= 512):
                    removed, _ = _INDEXES.popitem(last=False); _INDEX_BYTES -= len(removed)
                _INDEXES[data] = indexed; _INDEX_BYTES += len(data)
    return indexed

class Resolver:
    """Finite caller-supplied byte closure. No locator handlers or ambient imports."""
    def __init__(self, views=(), *, limits):
        self.limits = limits
        self._views, self._records, self._record_bytes = {}, {}, {}
        # Private indexes of validated immutable snapshots. Public access still
        # checks capabilities/pins and returns copies, never these dictionaries.
        self._packages, self._by_package, self._descriptors, self._references = {}, {}, {}, {}
        for view in views:
            self.add(view)

    def add(self, view):
        if isinstance(view, bytes): view = parse_snapshot(view, self.limits)
        if not isinstance(view, PinnedView): raise ExecutionError('s3.pinned_view_required')
        actual = parse_snapshot(view.source_bytes, self.limits, access=view.read_scope)
        if (actual.package_id, actual.format, actual.digest) != (view.package_id, view.format, view.digest):
            raise ExecutionError('s3.pinned_view_mismatch')
        old = self._views.get(actual.package_id)
        if old and old.source_bytes != actual.source_bytes: raise ExecutionError('s3.package_identity_conflict')
        if old:
            self._views[actual.package_id] = PinnedView(actual.package_id, copy.deepcopy(actual.format), copy.deepcopy(actual.digest), actual.source_bytes, actual.read_scope)
            return actual
        if not old and len(self._views) >= int(self.limits.max_external_packages): raise ExecutionError('s3.external_package_limit')
        total = sum(len(v.source_bytes) for k,v in self._views.items() if k != actual.package_id) + len(actual.source_bytes)
        if total > int(self.limits.max_external_bytes): raise ExecutionError('s3.external_byte_limit')
        package, signatures, references = _snapshot_index(actual.source_bytes)
        self._references[actual.package_id] = references
        for record in package['records']:
            old_record = self._record_bytes.get(record['id'])
            if old_record is not None and old_record != signatures[record['id']]: raise ExecutionError('s3.record_identity_conflict')
        self._views[actual.package_id] = PinnedView(actual.package_id, copy.deepcopy(actual.format), copy.deepcopy(actual.digest), actual.source_bytes, actual.read_scope)
        self._packages[actual.package_id] = package
        self._by_package[actual.package_id] = {r['id']: r for r in package['records']}
        self._descriptors[actual.package_id] = {d['package_id']: d for d in package['external_packages']}
        for record in package['records']:
            self._records[record['id']] = record
            self._record_bytes[record['id']] = signatures[record['id']]
        return actual

    def view(self, package_id):
        view = self._views.get(package_id)
        if view is None: raise ExecutionError('s3.dependency_unresolved')
        if not view.read_scope.permits(package_id): raise ExecutionError('s3.read_denied')
        return PinnedView(view.package_id, copy.deepcopy(view.format), copy.deepcopy(view.digest), view.source_bytes, view.read_scope)

    def record(self, reference, anchor):
        found, pid = self._locate(reference, anchor)
        return copy.deepcopy(found), pid

    def _locate(self, reference, anchor):
        """Internal validation only; callers must not expose the returned record."""
        if reference.get('binding') == 'unresolved': raise ExecutionError('s3.identity_unestablished')
        origin = self.view(anchor)
        pid = anchor if reference['binding'] == 'internal' else reference['package_id']
        target = self.view(pid)
        if pid != anchor:
            descriptor = self._descriptors[anchor].get(pid)
            if descriptor is None: raise ExecutionError('s3.undeclared_external_package')
            if descriptor.get('format', target.format) != target.format: raise ExecutionError('s3.package_format_mismatch')
            pin = descriptor['expected_digest']
            if pin['state'] != 'known': raise ExecutionError('s3.dependency_pin_unresolved')
            if pin['value'] != target.digest: raise ExecutionError('s3.integrity_mismatch')
        found = self._by_package[pid].get(reference['target'])
        if found is None or found['record_type'] != reference['target_type']: raise ExecutionError('s3.reference_target')
        return found, pid

    def closure(self, package_id):
        seen, active, ordered = set(), set(), []
        reference_count = 0
        def visit(pid, depth):
            nonlocal reference_count
            if depth > int(self.limits.max_reference_depth): raise ExecutionError('s3.reference_depth_limit')
            if pid in active: raise ExecutionError('s3.package_dependency_cycle')
            if pid in seen: return
            view = self.view(pid); active.add(pid); seen.add(pid); ordered.append(view)
            package = self._packages[pid]
            for descriptor in package['external_packages']:
                other = self.view(descriptor['package_id'])
                pin = descriptor['expected_digest']
                if pin['state'] != 'known' or pin['value'] != other.digest: raise ExecutionError('s3.integrity_mismatch')
                if descriptor.get('format', other.format) != other.format: raise ExecutionError('s3.package_format_mismatch')
                visit(other.package_id, depth + 1)
            for ref in self._references[pid]:
                reference_count += 1
                if reference_count > int(self.limits.max_total_reference_nodes): raise ExecutionError('s3.reference_count_limit')
                if ref['binding'] in ('internal', 'external'): self._locate(ref, pid)
            active.remove(pid)
        visit(package_id, 0)
        return tuple(ordered)

    def payload(self, typed_ref, anchor, registry):
        record, owner_pid = self.record(typed_ref, anchor)
        if record['record_type'] != 's3.typed_payload': raise ExecutionError('s3.typed_payload_required')
        typed = record['payload']; context = typed['reference_context']
        context_view = self.view(context['package_id'])
        if context_view.format != context['format']: raise ExecutionError('s3.payload_context_format')
        if context_view.package_id != owner_pid:
            desc = next((d for d in self.view(owner_pid).package['external_packages'] if d['package_id'] == context_view.package_id), None)
            if desc is None or desc['expected_digest'].get('value') != context_view.digest: raise ExecutionError('s3.payload_context_pin')
        artifact, _ = self.record(typed['content']['artifact'], owner_pid)
        selector = typed['content']['selector']
        if selector['state'] != 'not_applicable' and not (selector['state'] == 'known' and selector['value'] == {'selector_type': 'json_pointer', 'pointer': ''}):
            raise ExecutionError('s3.whole_parameter_payload_required')
        from crucis_causal.connections.validation import content_bytes
        try: raw = content_bytes(artifact['payload']['content'])
        except (ValueError, OSError) as exc: raise ExecutionError('s3.payload_bytes_unavailable') from exc
        value = loads(raw, self.limits)
        registry.decode(typed['payload_contract'], value)
        for _, ref, _ in walk(value):
            if isinstance(ref, dict) and ref.get('binding') in ('internal','external') and 'target_type' in ref:
                self.record(ref, context_view.package_id)
        return copy.deepcopy(value)
