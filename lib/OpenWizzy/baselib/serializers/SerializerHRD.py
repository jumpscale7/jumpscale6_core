from OpenWizzy import o

class SerializerHRD():
    def __init__(self):
        self._primitiveTypes = (int, str, float, bool)

    def _formatPrepends(self, prepend, type):
        prepend = prepend+'.' if prepend and prepend[-1] != '.' else prepend
        return '%s = %s\n' % (prepend, type)

    def dumps(self, data, prepend=''):
        if data == None:
            return self._formatPrepends(prepend, 'None')
        if isinstance(data, dict):
            processed = self._dumpDict(data, prepend)
        elif isinstance(data, list):
            processed = self._dumpList(data, prepend)
        elif isinstance(data, self._primitiveTypes):
            processed = data
            if not isinstance(data, str):
                processed = '%s.' % data
        return processed

    def _dumpDict(self, dictdata, prepend=''):
        dictified = ''
        if not dictdata:
            dictified += self._formatPrepends(prepend, '{}')
        for k, v in dictdata.iteritems():
            if not (isinstance(v, self._primitiveTypes)):
                v = self.dumps(v, '%s%s.' % (prepend,k))
                dictified += v
            else:
                if not isinstance(v, str):
                    dictified += '%s%s. = %s\n' % (prepend, k, v)
                else:
                    dictified += '%s%s = %s\n' % (prepend, k, v)
        return dictified

    def _dumpList(self, listdata, prepend=''):
        listified = ''
        if not listdata:
            listified += self._formatPrepends(prepend, '[]')
        for index, item in enumerate(listdata):
            if prepend:
                listprepend = '%s[%s].' % (prepend, index)
            else:
                listprepend = '[%s].' % index
            if not (isinstance(item, self._primitiveTypes)):
                item = self.dumps(item, listprepend)
                listified += '%s' % item
            else:
                if not isinstance(item, str):
                    listified += '%s. = %s\n' % (listprepend[:-1], str(item))
                else:
                    listified += '%s = %s\n' % (listprepend[:-1], str(item))
        return listified



    def loads(self, data):
        dataresult = [] if data.startswith('[') else {}
        for line in data.splitlines():
            if '=' not in line:
                if line.endswith('.'):
                    return self._getType(line[:-1])
                return line
            key, value = line.split('=')
            dataresult = self._processKey(key.strip(), value.strip(), dataresult)
        return dataresult

    def _processKey(self, key, value, result):
        if result == None:
            result = [] if key.startswith('[') else {}
        if key.endswith('.'):
            key = key[:-1]
            value = self._getType(value)
        if key.find('.') == -1:
            if key.startswith('['):
                index = int(key[1:-1])
                result.insert(index, value)
            else:
                result[key] = value
        else:
            keypart, keyrest = key.split('.', 1)
            if keypart.startswith('['):
                index = int(keypart[1:-1])
                if len(result) <= index:
                    result.append(None)
                value = self._processKey(keyrest, value, result[index])
                result[index] = value
            else:
                if not keypart in result:
                    result[keypart] = None
                value = self._processKey(keyrest, value, result[keypart])
                result[keypart] = value
        return result

    def _getType(self, value):
        values = {'{}': {}, '[]': [], 'None': None}
        if value in values:
            return values[value]
        elif o.basetype.integer.checkString(value):
            primitive = o.basetype.integer.fromString(value)
        elif o.basetype.float.checkString(value):
            primitive = o.basetype.float.fromString(value)
        elif o.basetype.boolean.checkString(value):
            primitive = o.basetype.boolean.fromString(value)
        return primitive