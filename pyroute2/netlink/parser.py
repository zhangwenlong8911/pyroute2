import struct


nlmsg_header_fields = (('length', 'I'),
                       ('type', 'H'),
                       ('flags', 'H'),
                       ('sequence_number', 'I'),
                       ('pid', 'I'))

nla_header_fields = (('length', 'H'),
                     ('type', 'H'))


def align(length, word=4):
    '''
    Align the length by the word size, e.g with word 4 bytes.

    :param int length: the length value to be aligned
    :param int word: the word size (optional, default 4)
    :return: the aligned value
    :rtype: int

    Examples:

        >>> align(3)
        4
        >>> align(8)
        8
    '''
    return (length + word - 1) & ~ (word - 1)


def get_fields_fmt(fields_spec, length=0):
    '''
    Return the format string for a standard fields tuple.

    :param fields_spec: standard fields spec
    :param int length: the data length (optional, default 0)
    :return: the struct format string
    :rtype: str

    Examples:

        >>> spec = (('length', 'H'), ('type', 'H'))
        >>> get_fields_fmt(spec)
        'HH'

    Some NLA have no fixed data structure or length. In that
    case the format string is simply 's', which would give
    1 byte length aligned to word, by default 4 bytes.

    But here we use the real data length value that gives
    the final format string.

    Please notice that `length` is only the data length without
    the header. This function has nothing to do with headers
    and does not implicitly subtract any header length from the
    `length` value. The proper `length` value must be calculated
    outside of the function.
    '''
    fmt = ''.join((x[1] for x in fields_spec))
    if fmt == 's' and length > 0:
        fmt = '%is' % length
    return fmt


def get_fields_names(fields_spec):
    '''
    Return field names for a standard fields tuple.

    :param fields_spec: standard fields spec
    :return: the field names tuple
    :rtype: tuple

    Examples:

        >>> spec = (('length', 'H'), ('type', 'H'))
        >>> get_fields_names(spec)
        ('length', 'type')
    '''
    return tuple(x[0] for x in fields_spec)


def get_fields_decoded(data, offset, fields_spec, length=0):
    '''
    Return a dict of decoded fields.

    :param bytes data: the raw data
    :param int offset: offset from 0 byte
    :param fields_spec: standard fields spec
    :param int length: the data length (optional, default 0)
    :return: dictionary of the decoded fields
    :rtype: dict

    Examples:

        >>> data = b'\x10\x00\x02\x00\x00\x00\x00\x00'
        >>> offset = 0
        >>> spec = (('length', 'H'), ('type', 'H'))
        >>> get_fields_decoded(data, offset, spec)
        {'length': 16, 'type': 2}

    '''
    names = get_fields_names(fields_spec)
    fmt = get_fields_fmt(fields_spec, length)
    return dict(zip(names, struct.unpack_from(fmt, data, offset)))


def get_headers(data, offset, limit, fields_spec):
    '''
    Returns an iterator through the headers within the
    specified data range.

    The spec must contain the `length` field.

    :param bytes data: the raw data
    :param int offset: offset from 0 byte
    :param int limit: limit in bytes from 0 byte
    :param fields_spec: standard fields spec
    :return: iterator

    The iterator yields tuples `(offset, header)`, where the
    header is a dictionary.
    '''
    while offset < limit:
        parsed = get_fields_decoded(data, offset, fields_spec)
        yield (offset, parsed)
        offset += align(parsed['length'])


def get_cls_by_type(parent, hdr_type):
    '''
    Returns NLA class fetched from the parent using type.

    :param parent: nlmsg class
    :param int hdr_type: the message type to lookup
    :return: NLA class
    :raises KeyError: if no such type defined
    '''
    return parent.prepare_msg_mappings()[0][hdr_type]['class']


def get_name_by_type(parent, hdr_type):
    '''
    Returns NLA name fetched from the parent using type.

    :param parent: nlmsg class
    :param int hdr_type: the message type to lookup
    :return: NLA name
    :raises KeyError: if no such type defined
    '''
    return parent.prepare_msg_mappings()[0][hdr_type]['name']


def get_offsets_map(data, offset, header_fields, msg_fields, length=0):
    '''
    The packet structure is like that::

        offset ->
                    header (length, type, ...)
        offset_h ->
                    fields (...)
        offset_f ->
                    NLA chain (NLA, ...)

    Where every NLA has the same layout.

    This function requires `offset` and returns tuple `(offset_h, offset_f)`.

    :param bytes data: the raw data
    :param int offset: offset from 0 byte
    :param header_fields: standard fields spec
    :param msg_fields: standard fields spec
    :param int length: the data length (optional, default 0)
    :return: tuple of offsets within a message
    :rtype: tuple
    '''

    offset_h = align(
        offset + struct.calcsize(get_fields_fmt(header_fields)))
    offset_f = align(
        offset_h + struct.calcsize(
            get_fields_fmt(msg_fields, offset + length - offset_h)))
    return (offset_h, offset_f)


def get_msg(data, offset, cls, header):
    '''
    The entry point to decode a message.

    Is not ready yet.
    '''

    offset_h, offset_f = get_offsets_map(
        data, offset, cls.header, cls.fields, header['length'])

    parsed = get_fields_decoded(
        data, offset_h, cls.fields, offset_f - offset_h)
    parsed['attrs'] = []

    limit = align(header['length'] + offset)

    for nla_offset, nla_header in get_headers(
            data, offset_f, limit, nla_header_fields):
        nla_cls = get_cls_by_type(cls, nla_header['type'])
        nla_name = get_name_by_type(cls, nla_header['type'])
        try:
            parsed['attrs'].append(
                (nla_name, get_msg(data, nla_offset, nla_cls, nla_header)))
        except Exception:
            parsed['attrs'].append((nla_name, None))

    return parsed
