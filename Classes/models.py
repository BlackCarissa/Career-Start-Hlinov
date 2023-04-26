
class Order():
    table = 'CURRENCY_ORDER'
    def __init__(self,db,ondate): # СЕТТЕР
        self.__db = db
        self.date= ondate
        self._id=self.__db.save(self,(ondate))
    def __str__(self): # Геттер
        return f"Курс ЦБ РФ за {self.date}"

class Rates():
    table = "CURRENCY_RATES"
    def __init__(self, db,count,name,numeric_code,alphabetic_code ,scale,rate ): # СЕТТЕР
        self.__db = db
        self._id = self.__db.save(self,(count,name, numeric_code, alphabetic_code, scale, rate))