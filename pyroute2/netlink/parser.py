import struct


def align(length, word=4):
    '''
    Align the length by the word size, e.g with word 4 bytes::

        3 -> 4
        7 -> 8
        8 -> 8
    '''
    return (length + word - 1) & ~ (word - 1)


def get_fields_fmt(fields_spec):
    '''
    Return the format string for a standard fields tuple::

        fields_spec = (('length', 'H'), ('type', 'H'))

        -> 'HH'
    '''
    return ''.join((x[1] for x in fields_spec))


def get_fields_names(fields_spec):
    '''
    Return field names for a standard fields tuple::

        fields_spec = (('length', 'H'), ('type', 'H'))

        -> ('length', 'type')
    '''
    return tuple(x[0] for x in fields_spec)


def get_fields_decoded(data, offset, fields_spec):
    '''
    Return a dict of decoded fields::

        data = b'\x10\x00\x02\x00\x00\x00\x00\x00'
        offset = 0
        fields_spec = (('length', 'H'), ('type', 'H'))

        -> {'length': 16, 'type': 2}
    '''
    names = get_fields_names(fields_spec)
    fmt = get_fields_fmt(fields_spec)
    return dict(zip(names, struct.unpack_from(fmt, data, offset)))
