Develop
======

Dump live database using::

    docker exec postgresql_single_container pg_dump --no-owner --no-unlogged-table-data --no-tablespaces --no-security-labels --data-only --inserts tuckshop > tuckshop_sqlite_20160909.sql


Edit dump::

    sed -i 's/true/1/g' ./tuckshop_sqlite_20160909.sql
    sed -i 's/false/0/g' ./tuckshop_sqlite_20160909.sql

Remove the SET lines at the start of the DUMP

Sync the db in the devel environment::

    python ./manage.py syncdb

Import the dump::

    sqlite3 ./db.sqlite < ./tuckshop_sqlite_20160909.sql

Run the devel server::

    TUCKSHOP_DEVEL=True python ./tuckshopaccountant.py

''Note:'' See Dockerfile for package prerequesites


Todo
====

##Done
* Find templating system:
  * Use one of the following: https://wiki.python.org/moin/Templating
* Setup user panel:
  * See balance
* Implement LDAP authentication
* Backend:
  * Split classes into seperate files
  * Complete inventory work
* Setup user panel:
  * Chose items to purchase/general items
* Setup Admin panel
  * Add items
  * View/Edit transaction history and rebuild credit cache
* Setup Admin panel
  * Add monies to user accounts
