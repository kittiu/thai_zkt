## Thai ZKT

ZKTeco Terminal Integration

#### License

mit

#### DocType

##### ZK Terminal

- Serial Number (Frappe "Name")
- Alias
- IP Address
- Model
- Platform
- FW Version
- Push Protocol
- Push Version
- Last Activity


##### ZK User

- User ID (Frappe "Name")
- User Name
- User Role
- Password


##### ZK Bio Data

- ZK User (FK "ZK User")
- Template
- Type
- Major Version
- Minor Version


##### ZK Bio Photo

- ZK User (FK "ZK User")
- Register Photo
- Register Time
- Approval Photo
- Approval Time
- Enroll Terminal (FK "ZK Terminal")


#### TODO

##### Common

- Read/Write File (Bio Photo)


##### Frappe
- Guest URL /iclock
- ZK Terminal Page
    - Import User
    - Export User
    - Restore User
    - Log
- ZK User Page


##### zkpush (In case Frappe can't make Guest URL /iclock)

- Call Frappe CRUD Rest API


##### /iclock command

- Get ZK Terminal Info
- Get Users from ZK Terminal
- Get Face Template
- Get Fingerprint Template
- Get Photo
