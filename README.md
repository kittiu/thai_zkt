## Thai ZKT

ZKTeco Terminal Integration

#### License

mit

#### DocType

##### ZK Terminal

- Serial Number (Frappe "Name")
- Alias
- Device Type
- Push Version
- IP Address
- Model
- Platform
- FW Version
- Last Activity
- Registry Code


##### ZK Terminal Option

- Frappe "Name" (Autoincrement)
- ZK Terminal (FK "ZK Terminal")
- Option Name
- Option Value


##### ZK User

- ID (Frappe "Name")
- User Name
- Password
- Privilege
- Group


##### ZK Bio Data

- Frappe "Name" (Autoincrement)
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

- Frappe "Name" (Autoincrement)
- Terminal (FK "ZK Terminal")
- Terminal Alias
- Command
- Status
- Sent Time
- Done Time


#### TODO

##### Frappe
- [X] Guest URL /iclock
- [ ] Read/Write File (Bio Photo)
- [X] ZK Terminal Page
    - [ ] Upload Users to Server
    - [ ] Download Users to ZK Terminal
    - [ ] Restore Users to ZK Terminal
    - [ ] Log
- [X] ZK User Page
- [X] ZK Command Page

##### /iclock command

- [X] Initialize ZK Terminal
    - [X] Push V.3
- [X] Get ZK Terminal Info
    - [X] Push V.2
    - [ ] Push V.3
- [X] Get Users
    - [X] Push V.2
    - [ ] Push V.3
- [ ] Clear Users
- [X] Set Users
    - [X] Push V.2
    - [ ] Push V.3
- [X] Get Face Template
    - [X] Push V.2
    - [ ] Push V.3
- [X] Set Face Template
    - [X] Push V.2
    - [ ] Push V.3
- [ ] Get Fingerprint Template
    - [ ] Push V.3
- [ ] Set Fingerprint Template
    - [ ] Push V.3
- [X] Get Attendance
    - [X] Push V.2
    - [X] Push V.3