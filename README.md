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

- ID (Frappe "Name")
- User Name
- Password
- Privilege
- Group


##### ZK Bio Data

- Frappe "Name"
- ZK User (FK "ZK User")
- Type
- No
- Index
- Valid
- Template
- Format
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

- ID (Frappe "Name")
- Terminal (FK "ZK Terminal")
- Terminal Alias
- Command
- Status
- Sent Time
- Done Time


#### TODO

##### Frappe
- [x] Guest URL /iclock
- [ ] Read/Write File (Bio Photo)
- [X] ZK Terminal Page
    - [ ] Upload Users to Server
    - [ ] Download Users to ZK Terminal
    - [ ] Restore Users to ZK Terminal
    - [ ] Log
- [X] ZK User Page
- [X] ZK Command Page

##### /iclock command

- [X] Get ZK Terminal Info
- [X] Get Users
- [ ] Set Users
- [X] Get Face Template
- [ ] Set Face Template
- [ ] Get Fingerprint Template
- [ ] Set Fingerprint Template
- [ ] Get Photo
- [ ] Set Photo
- [x] Get Attendance