**This is a beta project. This is not promised to be stable or bug free!**

# PowerPigeon

[![PyPi version](https://pypip.in/v/PowerPigeon/badge.png)](https://crate.io/packages/PowerPigeon/)

PowerPigeon is a async model-based RethinkDB handler. It allows for more structured RethinkDB data, which can be hard to get with NoSQL databases.

## Installation

To install, simply download `PowerPigeon` from PyPi.

## Usage

PowerPigeon is meant to be used inside of async functions. However, we need to create the connection first and in most situations this will want to be done outside of the async function. You can use something like the following code for this:

```py
import rethinkdb as r

r.set_loop_type("asyncio")
connection = <loop>.run_until_complete(r.connect(<connection args>))
```

Everything in the rest of this guide assumes that you are inside of a async function.

PowerPigeon is based on models. A model is a class that contains attributes and meta data. Attributes tell the model what items should be in database items, what type they should be and what they do (whether they are a ID, required or have a default). Attributes should be based on the `BaseAttribute` class which contains the initialisation code needed and the is the base class for attributes. Attributes must also contain a async `encode` and `decode` function. PowerPigeon contains several default attributes:
- `BooleanAttribute` - The attribute used for booleans.
- `TextAttribute` - The attribute used for text.
- `NumberAttribute` - The attribute used for numbers (accounts for the int32 limitation in RethinkDB).
- `JSONAttribute` - The attribute used for JSON.
- `BytesAttribute` - The attribute used for bytes.
- `UTCDateTimeAttribute` - The attribute used for UTC date/time.
- `DateTimeAttribute` - The attribute used for timezone aware date/time.

Attributes are to be initialised in the model. You can use the following keyword arguments with them:
- `required` - This sets if a item is required.
- `item_id` - This sets the item ID. One of these attributes is required.
- `default` - This sets the default item that goes here if the item does not contain it.

This makes our example model look like the following (we will add the `Meta` class later):
```py
class DemoModel(PowerPigeon.Model):
    name = TextAttribute(item_id=True)
    cool = BooleanAttribute(required=True)
```

Our meta data is very important. This will be a class that goes inside of the model named `Meta` that contains the following:
- `connection` - The RethinkDB connection that is explained earlier.
- `table_name` - The name of the table.
- `database` - The name of the database.

This will make the class look like this in our example:
```py
class DemoModel(PowerPigeon.Model):
    class Meta:
        connection = connection
        table_name = "demo_table"
        database = "demo_db"

    name = PowerPigeon.TextAttribute(item_id=True)
    cool = PowerPigeon.BooleanAttribute(required=True)
```

This will allow us to do the rest of the model-related stuff.

### Check Existence/Create Table
We can check if the table/DB actually exists. This is useful if we want to check and then create the table if it doesn't exist. This would look like this:
```py
if not await DemoTable.exists():
    await DemoTable.create_table()
```
This would create the table if it does not exist.

### Deleting A Table
You can call `delete_table` in order to delete the table:
```py
await DemoTable.delete_table()
```

### Model Initialisation
We can initialise a model in order to create a item based off it like the following:
```py
initialised_model = DemoTable(name="Jake", cool=True)
```
The keyword arguments could of also be written like this:
```py
initialised_model.name = "Jake"
initialised_model.cool = True
```
This would of made the initialisation line `initialised_model = DemoTable()` but I personally prefer writing them as keyword arguments.

### Getting The Database/Table Name
These are property attributes of the model named `database` and `table_name`:
```py
print(initialised_model.database)
# Prints: demo_db
print(initialised_model.table_name)
# Prints: demo_table
```

### Saving A Model
In order to save the model, we can simply call the `save` function:
```py
await initialised_model.save()
```

### Getting From The Table
In order to get from the table, you can simply call `get` with the item ID:
```py
initialised_model = await DemoTable.get("Jake")
print(initialised_model.cool)
# Prints: True
```
If the item does not exist, it will throw a `DoesNotExist` exception.

### Deleting From The Table
In order to delete a pre-initialised model from the table, we can simply call the `delete` function:
```py
await initialised_model.delete()
```

## Indexes
Indexes can be added into models just like attributes where the arguments are each row name that you want the index to apply to:
```py
cool_index = PowerPigeon.Index("cool")
```
Indexes can then be queried like a regular async generator with the arguments being the results you want in the order of the table rows you gave. However, note that instead of directly going to the index, you have to use the `index` function:
```py
async for item in DemoTable.index("cool_index").query(True):
    print(item.name)
# Prints: Jake
```
