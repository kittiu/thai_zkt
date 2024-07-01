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

##### ZK Command

- ID
- Terminal (FK "ZK Terminal")
- Terminal Name
- Command
- Status
- Sent Time
- Done Time


#### TODO

##### Frappe
- [x] Guest URL /iclock
- [ ] Read/Write File (Bio Photo)
- [X] ZK Terminal Page
    - [ ] Import User
    - [ ] Export User
    - [ ] Restore User
    - [ ] Log
- [ ] ZK User Page
- [X] ZK Command Page

##### /iclock command

- [X] Get ZK Terminal Info
- [ ] Get Users
- [ ] Set Users
- [ ] Get Face Template
- [ ] Set Face Template
- [ ] Get Fingerprint Template
- [ ] Set Fingerprint Template
- [ ] Get Photo
- [ ] Set Photo
- [x] Get Attendance