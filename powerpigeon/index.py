from .exceptions import IndexParametersInvalid, NoConnectionFound
import rethinkdb as r


class Index:
    """Defines a index."""
    def __init__(self, *index):
        self.model = None
        if len(index) == 1:
            self.index = index[0]
        else:
            self.index = list(index)

    @property
    def name(self):
        return self.__name__

    async def query(self, *query_items):
        is_str = isinstance(self.index, str)
        if is_str and len(query_items) == 1:
            raw_query = query_items[0]
        elif is_str:
            raise IndexParametersInvalid(
                "There was only {} parameters given when the index "
                "only takes one parameter.".format(len(query_items))
            )
        elif len(query_items) != len(self.index):
            raise IndexParametersInvalid(
                "There was only {} parameters given when the index "
                "takes {} parameters.".format(
                    len(query_items), len(self.index)
                )
            )
        else:
            raw_query = list(query_items)

        if isinstance(self.index, str):
            try:
                converter = self.model._required_attributes[self.index]
            except KeyError:
                try:
                    converter = self.model._normie_attributes[self.index]
                except KeyError:
                    raise IndexParametersInvalid(
                        "Could not find the converter for the attribute."
                    )
        else:
            converters = []
            for key in self.index:
                try:
                    converters.append(self.model._required_attributes[key])
                except KeyError:
                    try:
                        converters.append(self.model._normie_attributes[key])
                    except KeyError:
                        raise IndexParametersInvalid(
                            "Could not find the converter for the attributes."
                        )

        try:
            conn = self.model._meta.connection
        except AttributeError:
            raise NoConnectionFound(
                'Connection not found in "Meta" class.'
            )

        try:
            converted = await converter.encode(raw_query)
        except NameError:
            converted = []
            for i in range(0, len(converters)):
                index = converters[i]
                query = raw_query[i]
                converted.append(await index.encode(query))

        cursor = (
            await r.db(self.model.database).table(self.model.table_name).
            get_all(converted, index=self.name).run(conn)
        )
        while (await cursor.fetch_next()):
            item = await cursor.next()
            yield await self.model.from_raw_data(item)
