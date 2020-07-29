# Sample Data for Bluetail Demo app


## Data Summary

The `script/setup` and `script/insert_example_data` commands will insert all the sample data from these directories into the database

     /bluetail/data/prototype/ocds
     /bluetail/data/prototype/bods
     /bluetail/data/prototype/flags
     /bluetail/data/contracts_finder/ocds
     /bluetail/data/contracts_finder/bods
     /bluetail/data/contracts_finder/flags
     
     
## Data input requirements

For speed of setup and avoiding complexity some assumptions are made on the data entered into Bluetail.


### OCDS data requirements

- OCDS is a valid 1.1 release 
- Each contracting process represented by an OCID has a single release (or is compiled into a single release) before storing in Bluetail
- For linking to BODS the Org `scheme` and `id` fields are used 

### BODS data requirements

- To link the BODS to OCDS There is a `scheme` and `id` that match and org. `schemeName` is ignored.


### Prototype data

This data is replicated from the original prototype by mySociety here https://mysociety.github.io/bods-dashboard-prototype/

This has the OCID 

    ocds-123abc-PROC-20-0001
    
View just this data by appending the `ocid_prefix` param

    ?ocid_prefix=ocds-123abc-

like this
 
    http://127.0.0.1:8000/ocds/?ocid_prefix=ocds-123abc-
    

### Contracts Finder Data

These have OCIDs beginning with 
    
    ocds-b5fd17-

For example

    ocds-b5fd17-0c8a03bf-dcb1-4978-a59f-0fd7c364d7dd
    

View just this data by appending the `ocid_prefix` param

    ?ocid_prefix=ocds-b5fd17

like this
 
    http://127.0.0.1:8000/ocds/?ocid_prefix=ocds-b5fd17
    
