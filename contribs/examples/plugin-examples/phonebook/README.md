phonebook
=========

The phonebook plugin needs the following table:

```sql
CREATE EXTENSION hstore;
CREATE TABLE phonebook_entry (
       id SERIAL,
       attributes hstore
);
GRANT ALL ON phonebook_entry TO asterisk;
GRANT ALL ON phonebook_entry_id_seq TO asterisk;
```
