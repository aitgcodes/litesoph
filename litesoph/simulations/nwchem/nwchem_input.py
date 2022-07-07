from copy import deepcopy
import os

_special_kws = ['geometry','basis',
                'set', 'symmetry', 'label', 
                'basispar', 'kpts', 'restart_kw']

_theories = ['dft', 'scf', 'tddft']
_special_keypairs = [('rt_tddft', 'field')]

def _format_line(key, val):
    if val is None:
        return key
    if isinstance(val, bool):
        return '{} .{}.'.format(key, str(val).lower())
    else:
        return ' '.join([key, str(val)])

def _get_set(**params):
    return ['set ' + _format_line(key, val) for key, val in params.items()]

def _get_field(key, val):
    
    prefix = '      '
    name = val.pop('name', '"kick"')
    _lines = [f'    {key} "{name}"']

    for subkey, subval in val.items():
        _lines.append(prefix + _format_line(subkey, subval))
    _lines.append('  ' + 'end')
    return _lines

def _format_block(key, val, nindent=0):
    prefix = '  ' * nindent
    prefix2 = '  ' * (nindent + 1)

    if val is None:
        return [prefix + key]
    
    if isinstance(val, list):
        return [prefix + ' '.join([_format_line(a, None) for a in val])]

    if not isinstance(val, dict):
        return [prefix + _format_line(key, val)]

    _lines = [prefix + key]

    for subkey, subval in val.items():
        if (key, subkey) in _special_keypairs:
            if (key, subkey) == ('rt_tddft', 'field'):
                _lines += _get_field(subkey, subval)
            else:
                _lines += _format_block(subkey, subval, nindent +1)
        else:
            if isinstance(subval, dict):
                subval = ' '.join([_format_line(a, b) for a, b in subval.items()])
            _lines.append(prefix2 + ' '.join([_format_line(subkey, subval)]))
    
    _lines.append(prefix + 'end')
    return _lines

def _get_geom(**params):
    geom_header = ['geometry units angstrom']

    geo = params.get('geometry')
    
    if isinstance(geo, str):
        geo = dict(file = geo)

    for geomkw in ['center', 'autosym', 'autoz']:
        geom_header.append(geomkw if geo.get(geomkw, None) else 'no' + geomkw)
    if 'geompar' in params:
        geom_header.append(params['geompar'])
    geom = [' '.join(geom_header)]

    geom.append('   load {}'.format(geo['file']))
    geom.append('end')

    return geom

def _get_basis(**params):

    basis_in = params.get('basis', '3-21G')
    if 'basispar' in params:
        header = 'basis {} noprint'.format(params['basispar'])
    else:
        header = 'basis noprint'
    basis_out = [header]
    if isinstance(basis_in, str):
        basis_out.append('   * library {}'.format(basis_in))
    else:
        for symbol, ibasis in basis_in.items():
            basis_out.append('{:>4} library {}'.format(symbol, ibasis))
    basis_out.append('end')
    return basis_out

def _get_task(params):
    
    theory = 'dft'
    task = 'energy'
    if 'rt_tddft' in params:
        task = 'rt_tddft'

    return theory, task

def _get_other(**params):
    _lines = []
    for kw, block in params.items():
        if kw in _special_kws:
            continue
        _lines += _format_block(kw, block)
    return _lines
    
def nwchem_create_input(echo = False, **kwargs) -> str:
    
    params = deepcopy(kwargs)
    _lines = []

    theory, task = _get_task(params)
    label = params.get('label', 'nwchem')
    perm = os.path.abspath(params.pop('perm', label))
    scratch = os.path.abspath(params.pop('scratch', label))
    restart_kw = params.get('restart_kw', 'start')
    if restart_kw not in ('start', 'restart'):
        raise ValueError("Unrecognised restart keyword: {}!"
                         .format(restart_kw))
    short_label = label.rsplit('/', 1)[-1]
    if echo:
        _lines = ['echo']
    
    _lines.extend(['title "{}"'.format(short_label),
                'permanent_dir {}'.format(perm),
                'scratch_dir {}'.format(scratch),
                '{} {}'.format(restart_kw, short_label),
                '\n'.join(_get_geom(**params)),
                '\n'.join(_get_basis(**params)),
                '\n'.join(_get_other(**params)),
                '\n'.join(_get_set(**params.get('set', dict()))),
                'task {} {}'.format(theory, task)])

    input = "\n\n".join(_lines)
    
    return input 
