class JBer:
    def __init__(self, English_Name, Hebrew_Name, Phone_Number, Roles, Birthdate, ID):
        self.En_Name = English_Name
        self.He_Name = Hebrew_Name
        self.Phone = Phone_Number
        self.Roles = Roles
        self.Birthday = Birthdate
        self.ID = ID

    def set_English_Name(self, value):
        self.En_Name = value

    def set_Hebrew_Name(self, value):
        self.He_Name = value

    def set_Phone_Number(self, value):
        self.Phone = value

    def set_Roles(self, value):
        self.Roles = value

    def set_Birthdate(self, value):
        self.Birthday = value

    def set_User_ID(self, value):
        self.ID = value
