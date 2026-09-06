"""Patch torch infer_schema.py to support PEP 585 (list[int]) and PEP 604 (float | None)."""
import sys

path = r'D:\digital_human\venv\lib\site-packages\torch\_library\infer_schema.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if '_normalize_annotation' in content:
    print('Already patched, skipping.')
    sys.exit(0)

norm_func = '''
def _normalize_annotation(annotation_type):
    import types as _types
    origin = typing.get_origin(annotation_type)
    if isinstance(annotation_type, _types.UnionType):
        args = typing.get_args(annotation_type)
        normalized_args = tuple(_normalize_annotation(a) for a in args)
        if type(None) in normalized_args:
            non_none = tuple(a for a in normalized_args if a is not type(None))
            if len(non_none) == 1:
                return typing.Optional[non_none[0]]
            return typing.Optional[typing.Union[non_none]]
        return typing.Union[normalized_args]
    if origin is list:
        args = typing.get_args(annotation_type)
        if args:
            return typing.List[_normalize_annotation(args[0])]
        return typing.List
    if origin is tuple:
        args = typing.get_args(annotation_type)
        if args:
            return typing.Tuple[tuple(_normalize_annotation(a) for a in args)]
        return typing.Tuple
    return annotation_type


'''

# Insert before the infer_schema function
marker = '@exposed_in("torch.library")\ndef infer_schema('
if marker in content:
    content = content.replace(marker, norm_func + marker, 1)
    print('Added normalization function')
else:
    print('ERROR: marker not found')
    # Debug: find infer_schema
    for i, line in enumerate(content.split('\n')):
        if 'def infer_schema' in line:
            print(f'  Line {i+1}: {repr(line)}')
    sys.exit(1)

# Add normalization call after param string conversion
old_block = 'if type(annotation_type) == str:\n            annotation_type = convert_type_string(annotation_type)'
new_block = old_block + '\n        annotation_type = _normalize_annotation(annotation_type)'
if old_block in content:
    content = content.replace(old_block, new_block, 1)
    print('Added normalization call for params')
else:
    print('WARNING: param block not found')

# Add normalization call after return string conversion
old_ret = 'if type(return_annotation) == str:\n        return_annotation = convert_type_string(return_annotation)'
new_ret = old_ret + '\n    return_annotation = _normalize_annotation(return_annotation)'
if old_ret in content:
    content = content.replace(old_ret, new_ret, 1)
    print('Added normalization call for return')
else:
    print('WARNING: return block not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('File saved successfully')
