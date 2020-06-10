# Sample Data for Bluetail Demo app

## Data input requirements

For speed of setup and avoiding complexity some assumptions are made on the data entered into Bluetail.


### OCDS data requirements

- Each contracting process represented by an OCID has a single release (or is compiled into a single release) before storing in Bluetail
- For linking to BODS the Org `scheme` and `id` fields are used 

### BODS data requirements

- To link the BODS to OCDS There is a `scheme` and `id` that match. `schemeName` is ignored.  


## Data Summary

### Prototype data

This data is replicated from the original prototype by MySociety here https://mysociety.github.io/bods-dashboard-prototype/

### Contracts Finder Data

These have OCIDs beginning with 
    
    ocds-b5fd17-

For example

    ocds-b5fd17-0c8a03bf-dcb1-4978-a59f-0fd7c364d7dd