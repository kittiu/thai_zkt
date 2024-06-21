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

##### Frappe
- [x] Guest URL /iclock
- [ ] Read/Write File (Bio Photo)
- [ ] ZK Terminal Page
    - [ ] Import User
    - [ ] Export User
    - [ ] Restore User
    - [ ] Log
- [ ] ZK User Page


##### /iclock command

- [ ] Get ZK Terminal Info
- [ ] Get Users from ZK Terminal
- [ ] Set Users from ZK Terminal
- [ ] Get Face Template
- [ ] Set Face Template
- [ ] Get Fingerprint Template
- [ ] Set Fingerprint Template
- [ ] Get Photo
- [ ] Set Photo
