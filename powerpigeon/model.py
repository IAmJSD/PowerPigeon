from .exceptions import NoMetaFound, InvalidAttributeType, NoIDAttribute,\
    NoConnectionFound, TableOrDBDoesNotExist, DoesNotExist, NotAllRequired, \
    TableCreationError, SaveFailed
from .attributes import BaseAttribute
from .index import Index
import rethinkdb as r


def dict_difference(x, y):
    return {
        k: y[k] for k in set(x) - set(y)
    }
# Gets a dict of the differences between the 2 dicts.


class Model:
    """
    This is a standard model.
    """
    raw_result = None
    _ready = False
    _id_attribute = None
    _meta = None
    _required_attributes = {}
    _normie_attributes = {}
    _index_attributes = {}
    _added_attributes = {}
    _model_normie_attributes = [
        "database", "exists", "get", "raw_result", "table_name",
        "create_table", "save", "index", "from_raw_data", "delete",
        "delete_table"
    ]

    @property
    def table_name(self):
        """Gets the table name."""
        if self._meta:
            try:
                return self._meta.table_name
            except AttributeError:
                pass

        return self.__name__

    @property
    def database(self):
        """Gets the database this table is in."""
        if self._meta:
            try:
                return self._meta.database
            except AttributeError:
                pass

        return "powerpigeon"

    async def _to_database_item(self):
        """Converts the model to how it'll look in the database."""
        _encoded_data = {}

        for key in self._required_attributes:
            if key in self._added_attributes:
                _encoded_data[key] = await self._required_attributes[
                    key].encode(self._added_attributes[key])
            else:
                raise NotAllRequired(
                    "Not all required attributes are in this item."
                )

        for key in self._normie_attributes:
            if key in self._added_attributes:
                _encoded_data[key] = await self._normie_attributes[
                    key].encode(self._added_attributes[key])

        if self._id_attribute:
            if self._id_attribute.__name__ in self._added_attributes:
                _encoded_data["id"] = await self._id_attribute.encode(
                    self._added_attributes[self._id_attribute.__name__]
                )
            else:
                raise NotAllRequired(
                    "The ID attribute is required."
                )

        return _encoded_data

    async def delete(self):
        """Deletes a item from the table."""
        db_item = await self._to_database_item()
        try:
            connection = self._meta.connection
        except AttributeError:
            raise NoConnectionFound(
                'Connection not found in "Meta" class.'
            )

        try:
            (
                await r.db(self.database).table(self.table_name).
                get(db_item['id']).delete().run(connection)
            )
        except r.ReqlOpFailedError:
            raise TableOrDBDoesNotExist(
                'The database "{}" or table "{}" does not exist.'.format(
                    self.database, self.table_name
                )
            )

        return True

    @classmethod
    async def delete_table(cls):
        """Deletes the table."""
        model = cls()
        try:
            connection = model._meta.connection
        except AttributeError:
            raise NoConnectionFound(
                'Connection not found in "Meta" class.'
            )

        try:
            (
                await r.db(model.database).table(model.table_name).
                delete().run(connection)
            )
        except r.ReqlOpFailedError:
            raise TableOrDBDoesNotExist(
                'The database "{}" or table "{}" does not exist.'.format(
                    model.database, model.table_name
                )
            )

        return True

    async def save(self):
        """Saves this model into the database."""
        db_item = await self._to_database_item()

        try:
            connection = self._meta.connection
        except AttributeError:
            raise NoConnectionFound(
                'Connection not found in "Meta" class.'
            )

        if self.raw_result:
            if self.raw_result == db_item:
                return

            difference = dict_difference(self.raw_result, db_item)

            del difference['id']

            _ = db_item['id']

            try:
                await r.db(self.database).table(self.table_name).get(_).update(
                    difference).run(connection)
            except r.ReqlOpFailedError:
                raise TableOrDBDoesNotExist(
                    'The database "{}" or table "{}" does not exist.'.format(
                        self.database, self.table_name
                    )
                )

            return

        try:
            is_error = (
                await r.db(self.database).table(self.table_name).insert(
                    db_item).run(connection)
            )['errors'] == 1
        except r.ReqlOpFailedError:
            raise TableOrDBDoesNotExist(
                'The database "{}" or table "{}" does not exist.'.format(
                    self.database, self.table_name
                )
            )

        if is_error:
            _ = db_item['id']
            del db_item['id']
            try:
                await r.db(self.database).table(self.table_name).get(_).update(
                    db_item).run(connection)
            except r.ReqlOpFailedError:
                raise SaveFailed("Could not save the model to the database.")

        self.raw_result = db_item

    @classmethod
    async def from_raw_data(cls, returned_data):
        """Creates a model from raw data."""
        model = cls()

        model.raw_result = returned_data

        if model._id_attribute:
            model._added_attributes[
                model._id_attribute.__name__
            ] = await model._id_attribute.encode(returned_data["id"])

        for key in model._required_attributes:
            if key in returned_data:
                i = returned_data[key]
                if i is not None:
                    model._added_attributes[key] = await \
                        model._required_attributes[key].decode(i)
                else:
                    raise NotAllRequired(
                        "Not all required attributes are in this item."
                    )
            else:
                raise NotAllRequired(
                    "Not all required attributes are in this item."
                )

        for key in model._normie_attributes:
            if key in returned_data:
                model._added_attributes[key] = await \
                    model._normie_attributes[key].decode(i)
            else:
                model._added_attributes[key] = None

        return model

    @classmethod
    async def get(cls, item_id):
        """Gets a item from the database via the ID."""
        stock_model = cls()

        if not stock_model._id_attribute:
            raise NoIDAttribute(
                "There was no attribute given for a ID."
            )

        _encoded_id = await stock_model._id_attribute.encode(item_id)

        try:
            connection = stock_model._meta.connection
        except AttributeError:
            raise NoConnectionFound(
                'Connection not found in "Meta" class.'
            )

        table_name = stock_model.table_name
        database = stock_model.database

        try:
            returned_data = await r.db(database).table(table_name).get(
                _encoded_id).run(connection)
        except r.ReqlOpFailedError:
            raise TableOrDBDoesNotExist(
                'The database "{}" or table "{}" does not exist.'.format(
                    database, table_name
                )
            )

        if not returned_data:
            raise DoesNotExist(
                "The record with the ID specified does not exist."
            )

        return await cls.from_raw_data(returned_data)

    @classmethod
    async def exists(cls):
        """
            Checks if a table exists (also returns False if the database
            doesn't exist).
        """
        model = cls()
        db = model.database
        table = model.table_name

        try:
            connection = model._meta.connection
        except AttributeError:
            raise NoConnectionFound(
                'Connection not found in "Meta" class.'
            )

        try:
            await r.db(db).table(table).run(connection)
            return True
        except r.ReqlOpFailedError:
            return False

    @classmethod
    async def create_table(cls):
        """Creates the table (and DB if that does not exist)."""
        model = cls()
        db = model.database
        table = model.table_name

        try:
            connection = model._meta.connection
        except AttributeError:
            raise NoConnectionFound(
                'Connection not found in "Meta" class.'
            )

        try:
            await r.db_create(db).run(connection)
        except r.ReqlOpFailedError:
            pass

        try:
            await r.db(db).table_create(table).run(connection)
        except r.ReqlOpFailedError:
            raise TableCreationError(
                'Could not create the table "{}".'.format(table)
            )

        for key in model._index_attributes:
            try:
                i = model._index_attributes[key].index
                if isinstance(i, list):
                    i = [r.row[x] for x in i]
                else:
                    i = r.row[i]
                await r.db(db).table(table).index_create(key, i).run(
                    connection)
            except r.ReqlOpFailedError:
                raise TableCreationError(
                    'Could not create the index "{}" in table "{}".'.format(
                        key, table
                    )
                )

    @classmethod
    def index(cls, item):
        """Gets a index from a initialised model."""
        model = cls()
        _index = model._index_attributes[item]
        return _index

    def __getattribute__(self, item):
        """Modifies how attributes are fetched."""
        try:
            return super().__getattribute__("_added_attributes")[item]
        except KeyError:
            _id_attribute = super().__getattribute__("_id_attribute")
            if _id_attribute and _id_attribute.__name__ == item:
                return _id_attribute
            return super().__getattribute__(item)

    def __getattr__(self, item):
        """Aliases __getattribute__"""
        return self.__getattribute__(item)

    def __setattr__(self, key, value):
        """Sets each item into the dictionary."""
        self._added_attributes[key] = value

    def __init__(self, **kwargs):
        """Initialises the class."""
        if self._ready:
            return

        get = super().__getattribute__

        set_attr = super().__setattr__

        try:
            set_attr("_meta", get("Meta"))
        except AttributeError:
            raise NoMetaFound(
                'No "Meta" class was found in your model.'
            )

        self_keys = [
            x for x in dir(self) if not x.startswith("_") and x not in
            self._model_normie_attributes and x != "Meta"
        ]

        for key in self_keys:
            attribute = get(key)
            if isinstance(attribute, Index):
                attribute.model = self
                attribute.__name__ = key
                self._index_attributes[key] = attribute
                continue
            elif isinstance(attribute, BaseAttribute):
                attribute.model = self
                attribute.__name__ = key
                if attribute.item_id:
                    set_attr("_id_attribute", attribute)
                elif attribute.required:
                    self._required_attributes[key] = attribute
                else:
                    self._normie_attributes[key] = attribute
            else:
                raise InvalidAttributeType(
                    "{} is not a valid attribute type or a index. If "
                    "you have made a custom attribute, please make it "
                    "inherit powerpigeon.attributes.BaseAttribute.".format(
                        type(self.__getattribute__(key))
                    )
                )

        for arg in kwargs:
            self._added_attributes[arg] = kwargs[arg]

        set_attr("_ready", True)
