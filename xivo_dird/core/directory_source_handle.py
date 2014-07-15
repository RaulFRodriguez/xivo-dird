import Queue


class DirectorySourceHandle(object):
    '''
    Proxy for the Plugin interface that dispatches commands to the
    AsyncPluginWrapper
    '''

    def __init__(self, plugin_class, source_configuration):
        self._source = plugin_class(source_configuration)
        self._source.load()
        self._name = self._source.name()

    def name(self):
        return self._name

    def reverse_lookup(self, term):
        q = Queue.Queue()
        q.name = self._name
        result = self._source.reverse_lookup(term)
        if result:
            q.put(result)
        else:
            q.put(None)
        return q

    def lookup(self, term, args):
        q = Queue.Queue()
        results = self._source.lookup(term, args)
        q. put(results)
        return q
