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
- Options


##### ZK Terminal Option

- Frappe "Name" (Autoincrement)
- ZK Terminal (FK "ZK Terminal")
- Option Name
- Option Value


##### ZK User

- ID (Frappe "Name") (ZKTeco 'pin')
- User Name
- Password
- Privilege
- Group
- UID

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
- [X] ZK Terminal Page
    - [X] Clear Users in ZK Terminal
    - [X] Download Users to ZK Terminal
    - [ ] Upload Users to Server
    - [ ] Restore Users to ZK Terminal
    - [ ] Log
- [X] ZK User Page
- [X] ZK Command Page

##### /iclock command

- [X] Initialize ZK Terminal
    - [X] Push V.3 (/registry, /push)
- [X] Get ZK Terminal Info
    - [X] Push V.2 (ZK Command : 'INFO', /devicecmd)
    - [X] Push V.3 (ZK Command : '_GET_OPTIONS')
- [X] Get Users
    - [X] Push V.2 (ZK Command : 'CHECK', /cdata?table=OPERLOG)
    - [X] Push V.3 (ZK Command : 'DATA QUERY tablename=user,fielddesc=*,filter=*')
- [X] Set Users
    - [X] Push V.2 (ZK Command : '_UPDATE')
    - [X] Push V.3 (ZK Command : 'DATA UPDATE user CardNo= Pin=1 Password=234 Group=0 StartTime=0 EndTime=0 Name= Privilege=0')
- [X] Get Face Photo
    - [X] Push V.3 (ZK Command : 'DATA QUERY tablename=biophoto,fielddesc=*,filter=*')
- [X] Set Face Photo
    - [X] Push V.3 (ZK Command : 'DATA UPDATE biophoto PIN=1 Type=9 Size=10000 Content=${XXX} Format=0 Url=${XXX} PostBackTmpFlag=0')
- [X] Get Face Template
    - [X] Push V.2 (ZK Command : 'CHECK', /cdata?table=BIODATA)
    - [X] Push V.3 (ZK Command : 'DATA QUERY tablename=biodata,fielddesc=*,filter=Type=9')
- [X] Set Face Template
    - [X] Push V.2 (ZK Command : '_UPDATE')
    - [X] Push V.3 (ZK Command : 'DATA UPDATE biodata Pin=2 No=0 Index=0 Valid=1 Duress=0 Type=9 Majorver=5 Minorver=8 Format=0 Tmp=${XXX}')
- [X] Get Fingerprint Template
    - [X] Push V.3 (ZK Command : 'DATA QUERY tablename=biodata,fielddesc=*,filter=Type=1')
- [X] Set Fingerprint Template
    - [X] Push V.3 (ZK Command : 'DATA UPDATE biodata Pin=2 No=0 Index=0 Valid=1 Duress=0 Type=1 Majorver=5 Minorver=8 Format=0 Tmp=${XXX}')
- [X] Delete User
      [x] Push V.3 (ZK Command : 'DATA DELETE user Pin=${XXX}')
- [X] Delete Bio Data
      [x] Push V.3 (ZK Command : 'DATA DELETE biodata$ Type=${XXX}')
- [X] Delete Bio Photo
      [x] Push V.3 (ZK Command : 'DATA DELETE biophoto$ PIN=${XXX}')
- [X] Get Attendance
    - [X] Push V.2
    - [X] Push V.3