Searching RfHub2
----------------

Browsing tables
^^^^^^^^^^^^^^^
All collected libraries and resoures are available on both on left-hand side menu and main table,
allowing You to browse general information on each asset. Drilling down into each resource will redirect to
detailed asset information, with all of the information it could collect.

With search bar
^^^^^^^^^^^^^^^
Apart from searching with plain text, search queries can be narrowed down, using following search commands:

 - | ``name:`` using this operator search will be done only in keywords names, but not in keywords documentation.
   | Using ``name: Log`` will search for keywords with Log in their names.
 - | ``in:`` operator will narrow search only to library or resource, with matching name.
   | Using ``Should in: BuiltIn`` will search for all keywords
   | with Should in their names, coming from BuilIn library.
 - | ``tags:`` operator will narrow search to keywords tags.
   | Using ``Tags: Manual`` will search for all keywords with Manual tag.

Combining search operators:
'''''''''''''''''''''''''''
Search operators can be combined together. Possible combinations are:

 - | ``name: in:`` will search only in keywords name in assets with matching names.
   | ``name: Should in: BuiltIn`` will search for all keywords
   | with Should in their names in BuiltIn library.
 - | ``tags: in:`` will narrow search to tags in assets with matching names.
   | ``tags: Manual in: keywords`` will search for keywords with Manual tag in
   | keyword resource.
