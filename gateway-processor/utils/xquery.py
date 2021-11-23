# class UniswapTrade:
#     def __init__(self, txid, idx):
#         self.txid = txid
#         self.idx = idx


class XQuery:
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
    def __str__(self):
        return '\n'.join([f'{x}: {getattr(self,x)}' for x in list(self.__dict__)])