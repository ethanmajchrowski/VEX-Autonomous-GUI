*BUGS*
- [x] 1 When removing item from custom arguments, the value in the main arguments list is not reset to default.
- [x] 2 Error when adding a simple argument to custom arguments.
- [x] 3 Issue with verifying types of complex arguments (any data is considered invalid, likely some error within the code being caught by the try/except isntead of going through)
- [x] 4 Selecting a pneumatic in the dropdown does not persist
- [x] 5 If we remove or add arguments to the point where there are no arguments in the list, the add button does not update (disappear/appear)
- [x] 6 When selecting a motor object then a pneumatic object the pneumatic dropdown is not properly hidden
  - [x] ![alt text](image.png)
*TODO*
- [x] Formalize argument JSON syntax
  - [x] Get working simple types and complex types
  - [ ] Complex types:
    - [x] default - starting value (can be null/None if given type_ref)
    - [x] type_ref - data value to get expected type from (single value, not null/None)
    - [x] incompatible_with - other arguments that are exclusive with this one (list of strings)
    - [x] valid_types - list of values that are accepted for this argument
- [ ] Path Events
  - [x] When selecting a path, there should be an option that appears in the bottom right to manage events
  - [ ] Events should be handled in their own GUI with a:
    - [ ] scrollable list of events
    - [ ] button to edit a specific event
      - [ ] editing an event can change:
        - [ ] function (probably store in JSON?)
        - [ ] function arguments
        - [ ] EITHER:
          - [ ] Time after start of path to trigger event
                OR
          - [ ] Click and drag event point in path (maybe always have events draggable when selecting a path?)
    - [ ] button to add new event
    - [ ] button to remove event
*WANT TO DO*
- [ ] Robot simulation with timing
- [ ] Robot simulation path results
